#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/extractors.py - 資料提取器
三種策略：PDF > HTML結構化 > 正則（品質遞減）
"""

import re
from urllib.parse import urljoin
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .config import REQUEST_HEADERS, CONFIRM_ROOM_KEYWORDS
from .validators import is_meeting_room


class PDFExtractor:
    """PDF 提取器 - 品質最好"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.session.verify = False

    def extract(self, pdf_url: str) -> list:
        """
        從 PDF 提取會議室資料
        返回 [{name, capacity, area, price, ...}, ...]
        """
        try:
            import pdfplumber
        except ImportError:
            print('  [PDF] pdfplumber 未安裝，跳過 PDF 提取')
            return []

        try:
            r = self.session.get(pdf_url, timeout=30)
            if r.status_code != 200:
                return []

            import io
            pdf = pdfplumber.open(io.BytesIO(r.content))
            rooms = []

            for page in pdf.pages:
                # 先嘗試表格提取
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        extracted = self._parse_table(table)
                        rooms.extend(extracted)

                # 表格提取失敗 → 嘗試文字提取
                if not rooms:
                    text_rooms = self._extract_from_pdf_text(page.extract_text() or '')
                    rooms.extend(text_rooms)

            pdf.close()

            # 去重同頁同名房間（取資料最完整的）
            rooms = self._deduplicate_rooms(rooms)

            # 過濾垃圾名稱
            rooms = [r for r in rooms if self._is_valid_room_name(r.get('name', ''))]

            # 過濾客房
            rooms = [r for r in rooms if is_meeting_room(r.get('name', ''), r)]

            return rooms

        except Exception as e:
            print(f'  [PDF] 提取失敗: {e}')
            return []

    # === PDF 文字提取（通用，無硬編碼）===

    def _extract_from_pdf_text(self, text: str) -> list:
        """
        從 PDF 純文字中提取會議室資料
        通用方法：透過模式偵測房間名稱和價格

        核心邏輯：
        1. 掃描所有行，追蹤樓層上下文
        2. 偵測含名稱+價格的行（強信號）
        3. 偵測含確認關鍵字的行（中信號）
        4. 將連續的價格行歸屬到最近的房間名稱
        5. 最後去重：同名/相似名的房間合併資料
        """
        rooms = []
        lines = text.split('\n')
        current_floor = ''
        current_room = None
        price_labels = self._detect_price_columns(text)

        for i in range(len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # 偵測樓層
            floor = self._detect_floor(line)
            if floor:
                current_floor = floor
                if re.match(r'^(?:Level\s*\d+|\d+\s*[F樓])', line, re.IGNORECASE):
                    continue

            # 偵測是否為房間名稱行
            if self._is_room_name_line(line):
                # 儲存前一個房間
                if current_room:
                    rooms.append(current_room)

                # 提取行內價格
                name_part, inline_prices = self._split_name_and_prices(line)

                current_room = {
                    'name': name_part.strip(),
                    'floor': current_floor,
                    'source': 'pdf',
                }

                if inline_prices:
                    self._assign_prices(current_room, inline_prices, price_labels)

                continue

            # 如果有目前房間，嘗試從後續行提取價格
            if current_room:
                prices = self._extract_price_numbers(line)

                if prices:
                    self._assign_prices(current_room, prices, price_labels)
                    continue

                # 偵測容量
                cap_match = re.search(r'(\d+)\s*(?:人|名|位|pax|guests?|seats?)', line, re.IGNORECASE)
                if cap_match:
                    current_room['capacity'] = {'theater': int(cap_match.group(1))}

                # 偵測面積
                area, unit = self._parse_area(line)
                if area:
                    current_room['area'] = area
                    current_room['areaUnit'] = unit

        if current_room:
            rooms.append(current_room)

        return rooms

    def _is_valid_room_name(self, name: str) -> bool:
        """過濾掉從 PDF 提取的垃圾名稱"""
        if not name or len(name) < 2:
            return False

        # 垃圾模式：包含太多不同類型的詞彙（通常是多行合併錯誤）
        # 例: "SEA MOUNTAIN FOREST 超新星 大宴會廳 宴會廳/會議廳"
        cn_words = len(re.findall(r'[\u4e00-\u9fff]{2,}', name))
        en_words = len(re.findall(r'[A-Za-z]{3,}', name))
        if cn_words >= 3 and en_words >= 3:
            return False

        # 垃圾模式：太長（超過 60 字）
        if len(name) > 60:
            return False

        # 垃圾模式：包含表格標題詞彙
        garbage_kw = ['一覽表', '容納及面積', '以人數計算', '以桌數計算',
                      'Theatre', 'Classroom', 'Hollow', 'Cocktail',
                      'Sq.Meters', '樓高', '.cnI']
        for kw in garbage_kw:
            if kw in name:
                return False

        return True

    def _is_room_name_line(self, line: str) -> bool:
        """
        判斷一行是否為會議室名稱
        """
        # 排除純數字行
        if re.match(r'^[\d,.\s]+$', line):
            return False

        # 排除地址、電話、版權等行
        skip_patterns = [
            r'^No\.', r'^\d{3,}', r'^T:', r'^Tel',
            r'©', r'Effective from', r'Prices are subject',
            r'^All prices', r'^\*',
        ]
        for pat in skip_patterns:
            if re.search(pat, line, re.IGNORECASE):
                return False

        # 排除只含價格的行
        stripped = re.sub(r'[\d,]+', '', line).strip()
        if len(stripped) <= 2:
            return False

        # 排除標題和頁首行
        title_kw = ['rental chart', 'floor plan', '價目表', '平面圖', '場地規格',
                     '場地價格', 'banquet function room', '宴會廳平面',
                     '宴會廳場地', 'morning', 'afternoon', 'evening', 'additional',
                     'full day', 'overnight', 'level', 'copyright',
                     'morning 上午', 'afternoon 下午', 'evening 晚上',
                     '08:00', '13:00', '18:00', '超時計費', '全日', '夜間佈置']
        line_lower = line.lower()
        for kw in title_kw:
            if kw in line_lower:
                return False

        # 正面判斷：含確認關鍵字
        for kw in CONFIRM_ROOM_KEYWORDS:
            if kw.lower() in line_lower:
                return True

        # 正面判斷：短文字 + 英文或中文
        text_part = re.sub(r'[\d,.\s]+', ' ', line).strip()
        if 2 <= len(text_part) <= 30:
            if re.search(r'[A-Za-z]', text_part):
                non_room = ['Morning', 'Afternoon', 'Evening', 'Additional',
                            'Full Day', 'Overnight', 'Level', 'Copyright',
                            'Rental', 'Charge', 'Chart', 'Plan', 'Function',
                            'Capacity', 'Dimension']
                if not any(nr.lower() in line_lower for nr in non_room):
                    return True
            elif re.search(r'[\u4e00-\u9fff]', text_part):
                if len(text_part) >= 2 or (len(text_part) == 1 and text_part in '海山林水精雲風光'):
                    return True

        return False

    def _split_name_and_prices(self, line: str) -> tuple:
        """分離房間名稱和行內價格"""
        # 找到第一個價格數字的位置
        price_match = re.search(r'[\d,]{4,}', line)
        if not price_match:
            return line, []

        name_part = line[:price_match.start()].strip()
        price_str = line[price_match.start():]
        prices = self._extract_price_numbers(price_str)

        return name_part, prices

    def _detect_floor(self, line: str) -> str:
        """偵測樓層資訊"""
        # "Level 7" or "Level 7｜..."
        m = re.search(r'Level\s*(\d+)', line, re.IGNORECASE)
        if m:
            return f'{m.group(1)}F'
        # "7F" or "9F"
        m = re.search(r'(\d+)\s*F', line, re.IGNORECASE)
        if m:
            return f'{m.group(1)}F'
        # "7樓" or "3樓"
        m = re.search(r'(\d+)\s*樓', line)
        if m:
            return f'{m.group(1)}F'
        return ''

    def _detect_price_columns(self, text: str) -> list:
        """
        偵測價格欄位的含義（上午/下午/晚上/全日等）
        返回標籤列表，例如 ['weekday', 'evening', 'fullDay', ...]
        """
        labels = []
        lines = text.split('\n')

        for line in lines:
            lower = line.lower()
            if 'morning' in lower or '上午' in lower:
                labels.append('weekday')
            elif 'afternoon' in lower or '下午' in lower:
                labels.append('afternoon')
            elif 'evening' in lower or '晚上' in lower or '晚' in lower:
                labels.append('evening')
            elif 'additional' in lower or '超時' in lower or 'overtime' in lower:
                labels.append('overtime')
            elif 'full day' in lower or '全日' in lower:
                labels.append('fullDay')
            elif 'overnight' in lower or '夜間' in lower:
                labels.append('overnightSetup')

        return labels if labels else ['weekday', 'evening', 'overtime', 'fullDay']

    def _extract_price_numbers(self, text: str) -> list:
        """提取文字中的價格數字（≥1000）"""
        nums = re.findall(r'([\d,]+)', text)
        prices = []
        for n in nums:
            n_clean = n.replace(',', '')
            if n_clean.isdigit():
                val = int(n_clean)
                if val >= 1000:
                    prices.append(val)
        return prices

    def _assign_prices(self, room: dict, prices: list, labels: list):
        """將價格數字分配到正確的欄位"""
        if 'price' not in room:
            room['price'] = {}

        for idx, price in enumerate(prices):
            if idx < len(labels):
                key = labels[idx]
            else:
                # 超出標籤數量的價格，用通用鍵
                key = f'price{idx}'

            # 只在尚未有值時填入
            if not room['price'].get(key):
                room['price'][key] = price

    def _deduplicate_rooms(self, rooms: list) -> list:
        """
        去重同名/相似名稱的房間
        合併策略：保留資料最完整的版本
        """
        if not rooms:
            return rooms

        deduped = []
        for room in rooms:
            name = room.get('name', '').strip()
            merged = False

            for existing in deduped:
                if self._names_match(existing.get('name', ''), name):
                    # 合併：補充缺少的欄位
                    for key in ['price', 'capacity', 'area', 'areaUnit', 'floor', 'images']:
                        new_val = room.get(key)
                        old_val = existing.get(key)
                        if new_val and (not old_val or old_val == '' or old_val == {} or old_val == []):
                            existing[key] = new_val
                        elif isinstance(new_val, dict) and isinstance(old_val, dict):
                            for k, v in new_val.items():
                                if v and not old_val.get(k):
                                    old_val[k] = v
                    # 保留較長的名稱
                    if len(name) > len(existing.get('name', '')):
                        existing['name'] = name
                    merged = True
                    break

            if not merged:
                deduped.append(dict(room))

        return deduped

    def _names_match(self, name1: str, name2: str) -> bool:
        """
        判斷兩個名稱是否指同一個房間
        使用多種策略進行模糊匹配
        """
        if not name1 or not name2:
            return False

        n1 = name1.strip().lower()
        n2 = name2.strip().lower()

        # 完全相同
        if n1 == n2:
            return True

        # 一個包含另一個
        if n1 in n2 or n2 in n1:
            return True

        # 移除樓層前綴後比較
        n1_no_floor = re.sub(r'^\d+\s*[f樓]\s*', '', n1).strip()
        n2_no_floor = re.sub(r'^\d+\s*[f樓]\s*', '', n2).strip()
        if n1_no_floor and n2_no_floor and (n1_no_floor in n2_no_floor or n2_no_floor in n1_no_floor):
            return True

        # 提取中英文關鍵字後比較
        cn1 = re.findall(r'[\u4e00-\u9fff]+', n1)
        cn2 = re.findall(r'[\u4e00-\u9fff]+', n2)
        en1 = re.findall(r'[a-zA-Z]+', n1)
        en2 = re.findall(r'[a-zA-Z]+', n2)

        # 中文關鍵字有交集
        if cn1 and cn2:
            overlap = set(''.join(cn1)) & set(''.join(cn2))
            total = set(''.join(cn1)) | set(''.join(cn2))
            if total and len(overlap) / len(total) >= 0.6:
                return True

        # 英文關鍵字有交集
        if en1 and en2:
            set1 = set(w.lower() for w in en1 if len(w) > 1)
            set2 = set(w.lower() for w in en2 if len(w) > 1)
            if set1 & set2:
                return True

        return False

    # === PDF 表格提取 ===

    def _parse_table(self, table: list) -> list:
        """解析 PDF 表格"""
        if not table or len(table) < 2:
            return []

        header = [str(c).strip().lower() if c else '' for c in table[0]]
        rooms = []

        for row in table[1:]:
            if not row or all(not c or str(c).strip() == '' for c in row):
                continue

            room = {}
            for i, cell in enumerate(row):
                if i >= len(header):
                    break
                cell_text = str(cell).strip() if cell else ''
                col_name = header[i]

                if self._is_name_column(col_name):
                    room['name'] = cell_text
                elif self._is_capacity_column(col_name):
                    cap = self._parse_number(cell_text)
                    if cap:
                        room['capacity'] = {'theater': cap}
                elif self._is_area_column(col_name):
                    area, unit = self._parse_area(cell_text)
                    if area:
                        room['area'] = area
                        room['areaUnit'] = unit
                        if unit == '㎡':
                            room['areaSqm'] = area
                            room['areaPing'] = round(area / 3.3058, 2)
                        elif unit == '坪':
                            room['areaPing'] = area
                            room['areaSqm'] = round(area * 3.3058, 2)
                elif self._is_price_column(col_name):
                    price = self._parse_price(cell_text)
                    if price:
                        if 'price' not in room:
                            room['price'] = {}
                        if '平日' in col_name or 'weekday' in col_name:
                            room['price']['weekday'] = price
                        elif '假日' in col_name or 'holiday' in col_name:
                            room['price']['holiday'] = price
                        else:
                            room['price']['weekday'] = price

            if room.get('name'):
                room['source'] = 'pdf'
                rooms.append(room)

        return rooms

    def _is_name_column(self, col: str) -> bool:
        return any(kw in col for kw in ['名稱', '場地', '會議室', 'room', 'venue', 'hall', 'name'])

    def _is_capacity_column(self, col: str) -> bool:
        return any(kw in col for kw in ['容', '人數', 'capacity', 'pax', 'seat'])

    def _is_area_column(self, col: str) -> bool:
        return any(kw in col for kw in ['面積', '坪', '㎡', '平方', 'area', 'size', 'sqm'])

    def _is_price_column(self, col: str) -> bool:
        return any(kw in col for kw in ['價', '費', '格', 'price', 'rate', 'fee'])

    def _parse_number(self, text: str) -> int:
        nums = re.findall(r'[\d,]+', text.replace(',', ''))
        if nums:
            try:
                return int(nums[0])
            except ValueError:
                return None
        return None

    def _parse_area(self, text: str) -> tuple:
        m = re.search(r'([\d.]+)\s*坪', text)
        if m:
            return float(m.group(1)), '坪'
        m = re.search(r'([\d.]+)\s*(?:㎡|平方公尺|m²)', text)
        if m:
            return float(m.group(1)), '㎡'
        return None, None

    def _parse_price(self, text: str) -> int:
        m = re.search(r'[\$NT nt]*([\d,]+)', text)
        if m:
            try:
                return int(m.group(1).replace(',', ''))
            except ValueError:
                return None
        return None


class HTMLExtractor:
    """HTML 結構化提取器 - 品質中等"""

    def extract_from_tables(self, soup: BeautifulSoup, base_url: str) -> list:
        """從 HTML <table> 提取會議室資料"""
        rooms = []
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue

            header = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]
            if not self._is_meeting_table(header):
                continue

            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue

                room = self._parse_html_row(cells, header)
                if room and is_meeting_room(room.get('name', ''), room):
                    room['source'] = 'html_table'
                    rooms.append(room)

        return rooms

    def _is_meeting_table(self, header: list) -> bool:
        header_text = ' '.join(header)
        meeting_kw = ['會議', '場地', '廳', '室', 'room', 'venue', 'hall', 'meeting']
        return any(kw in header_text for kw in meeting_kw)

    def _parse_html_row(self, cells, header: list) -> dict:
        room = {}
        for i, cell in enumerate(cells):
            if i >= len(header):
                break
            text = cell.get_text(strip=True)
            col = header[i]

            if any(kw in col for kw in ['名稱', '場地', 'room', 'name']):
                room['name'] = text
            elif any(kw in col for kw in ['容', '人數', 'capacity']):
                cap = self._extract_number(text)
                if cap:
                    room['capacity'] = {'theater': cap}
            elif any(kw in col for kw in ['面積', '坪', 'area', 'size']):
                area, unit = self._extract_area(text)
                if area:
                    room['area'] = area
                    room['areaUnit'] = unit
                    if unit == '㎡':
                        room['areaSqm'] = area
                        room['areaPing'] = round(area / 3.3058, 2)
                    elif unit == '坪':
                        room['areaPing'] = area
                        room['areaSqm'] = round(area * 3.3058, 2)
            elif any(kw in col for kw in ['價', '費', 'price', 'rate']):
                price = self._extract_price(text)
                if price:
                    room['price'] = {'weekday': price}
            elif any(kw in col for kw in ['樓', 'floor']):
                room['floor'] = text
            elif any(kw in col for kw in ['設備', 'equipment']):
                room['equipment'] = text

        return room if room.get('name') else None

    def extract_from_cards(self, soup: BeautifulSoup, base_url: str) -> list:
        """從卡片/列表元素提取會議室資料"""
        rooms = []
        card_selectors = [
            '[class*="room"]', '[class*="venue"]', '[class*="meeting"]',
            '[class*="banquet"]', '[class*="hall"]', '[class*="space"]',
        ]

        for selector in card_selectors:
            cards = soup.select(selector)
            for card in cards:
                room = self._parse_card(card, base_url)
                if room and is_meeting_room(room.get('name', ''), room):
                    room['source'] = 'html_card'
                    rooms.append(room)

        return rooms

    def _parse_card(self, card, base_url: str) -> dict:
        room = {}
        name_el = card.find(['h2', 'h3', 'h4', 'h5'])
        if not name_el:
            name_el = card.find(class_=lambda c: c and any(
                kw in str(c).lower() for kw in ['title', 'name']
            ))
        if name_el:
            room['name'] = name_el.get_text(strip=True)

        text = card.get_text()
        cap_match = re.search(r'(\d+)\s*(?:人|名|位|pax|seats?)', text, re.IGNORECASE)
        if cap_match:
            room['capacity'] = {'theater': int(cap_match.group(1))}

        area, unit = self._extract_area(text)
        if area:
            room['area'] = area
            room['areaUnit'] = unit
            if unit == '㎡':
                room['areaSqm'] = area
                room['areaPing'] = round(area / 3.3058, 2)
            elif unit == '坪':
                room['areaPing'] = area
                room['areaSqm'] = round(area * 3.3058, 2)

        price = self._extract_price(text)
        if price:
            room['price'] = {'weekday': price}

        img = card.find('img')
        if img and img.get('src'):
            room['images'] = {'main': urljoin(base_url, img['src'])}

        return room if room.get('name') else None

    def extract_images(self, soup: BeautifulSoup, base_url: str, page_type: str = '') -> list:
        images = []
        seen = set()

        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('data:'):
                continue

            abs_url = urljoin(base_url, src)
            src_lower = src.lower()
            skip_patterns = ['logo', 'icon', 'avatar', 'banner', 'button',
                             'arrow', 'social', 'menu', 'favicon', 'spacer']
            if any(p in src_lower for p in skip_patterns):
                continue

            if abs_url not in seen:
                seen.add(abs_url)
                images.append(abs_url)

        return images

    def _extract_number(self, text: str) -> int:
        m = re.search(r'(\d+)', text.replace(',', ''))
        return int(m.group(1)) if m else None

    def _extract_area(self, text: str) -> tuple:
        m = re.search(r'([\d.]+)\s*坪', text)
        if m:
            return float(m.group(1)), '坪'
        m = re.search(r'([\d.]+)\s*(?:㎡|平方公尺|m²)', text)
        if m:
            return float(m.group(1)), '㎡'
        return None, None

    def _extract_price(self, text: str) -> int:
        m = re.search(r'(?:NT\$|NTD|\$|台幣)\s*([\d,]+)', text, re.IGNORECASE)
        if m:
            try:
                return int(m.group(1).replace(',', ''))
            except ValueError:
                return None
        m = re.search(r'([\d,]+)\s*元', text)
        if m:
            try:
                return int(m.group(1).replace(',', ''))
            except ValueError:
                return None
        return None


class RegexExtractor:
    """正則提取器 - 品質最差，最後手段"""

    def extract(self, text: str) -> list:
        rooms = []

        name_pattern = re.compile(
            r'((?:\d+[F樓]\s*)?'
            r'(?:[\w]+\s*)?'
            r'(?:[\u4e00-\u9fff]+)?'
            r'(?:會議|宴會|展覽|演講|活動)?廳|室|館)'
        )
        capacity_pattern = re.compile(r'(\d+)\s*(?:人|名|位|pax|seats?)', re.IGNORECASE)
        area_ping_pattern = re.compile(r'([\d.]+)\s*坪')
        area_sqm_pattern = re.compile(r'([\d.]+)\s*(?:㎡|平方公尺|m²)')
        price_pattern = re.compile(r'(?:NT\$|NTD|\$)\s*([\d,]+)', re.IGNORECASE)

        lines = text.split('\n')
        current_room = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            name_match = name_pattern.search(line)
            if name_match and is_meeting_room(name_match.group(0)):
                if current_room and current_room.get('name'):
                    rooms.append(current_room)
                current_room = {'name': name_match.group(0).strip(), 'source': 'regex'}
                continue

            if current_room:
                cap_match = capacity_pattern.search(line)
                if cap_match:
                    current_room['capacity'] = {'theater': int(cap_match.group(1))}

                area_m = area_ping_pattern.search(line)
                if area_m:
                    current_room['area'] = float(area_m.group(1))
                    current_room['areaUnit'] = '坪'
                else:
                    area_m = area_sqm_pattern.search(line)
                    if area_m:
                        current_room['area'] = float(area_m.group(1))
                        current_room['areaUnit'] = '㎡'

                price_m = price_pattern.search(line)
                if price_m:
                    try:
                        current_room['price'] = {'weekday': int(price_m.group(1).replace(',', ''))}
                    except ValueError:
                        pass

        if current_room and current_room.get('name'):
            rooms.append(current_room)

        return rooms


class KnowledgeExtractor:
    """知識提取器 — 從 PDF/HTML 提取 rules, limitations, loadIn, equipment specs"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.session.verify = False
        from .knowledge_config import RULES_KEYWORDS, LOADIN_KEYWORDS, EQUIPMENT_SPEC_KEYWORDS
        self.rules_keywords = RULES_KEYWORDS
        self.loadin_keywords = LOADIN_KEYWORDS
        self.equipment_keywords = EQUIPMENT_SPEC_KEYWORDS

    def extract_from_pdf(self, pdf_url: str, venue_url: str = None) -> dict:
        """
        從 PDF 提取知識型資料（rules, limitations, loadIn, equipment）
        返回 ai_knowledge_base schema 格式的 dict
        """
        try:
            import pdfplumber
        except ImportError:
            print('  [Knowledge] pdfplumber 未安裝，跳過 PDF 知識提取')
            return {}

        try:
            import io
            r = self.session.get(pdf_url, timeout=30)
            if r.status_code != 200:
                return {}

            pdf = pdfplumber.open(io.BytesIO(r.content))
            full_text = '\n'.join(
                page.extract_text() or '' for page in pdf.pages
            )
            pdf.close()

            source = {
                "type": "pdf",
                "url": pdf_url,
                "venue_url": venue_url,
                "extractedAt": datetime.now().strftime("%Y-%m-%d")
            }
            return self._extract_knowledge_from_text(full_text, source)

        except Exception as e:
            print(f'  [Knowledge] PDF 提取失敗: {e}')
            return {}

    def extract_from_html(self, url: str, venue_url: str = None) -> dict:
        """從 HTML 頁面（FAQ、場地須知、租借辦法）提取知識"""
        try:
            r = self.session.get(url, timeout=20)
            if r.status_code != 200:
                return {}

            soup = BeautifulSoup(r.text, 'html.parser')

            # 嘗試找 FAQ / 注意事項區塊
            knowledge_text = self._extract_knowledge_sections(soup)

            if not knowledge_text:
                # 回退：全文提取
                knowledge_text = soup.get_text()

            source = {
                "type": "html",
                "url": url,
                "venue_url": venue_url,
                "extractedAt": datetime.now().strftime("%Y-%m-%d")
            }
            return self._extract_knowledge_from_text(knowledge_text, source)

        except Exception as e:
            print(f'  [Knowledge] HTML 提取失敗: {e}')
            return {}

    def extract_from_text(self, text: str, source: dict = None) -> dict:
        """直接從文字提取知識（用於本地 PDF 或已有文字）

        Args:
            text: 要提取的文字內容
            source: 來源資訊 {"type": "pdf|html|manual", "url": "...", "file": "..."}
        """
        return self._extract_knowledge_from_text(text, source)

    # === 內部方法 ===

    def _extract_knowledge_from_text(self, text: str, source: dict = None) -> dict:
        """從文字提取所有知識型資料

        Args:
            text: 要提取的文字內容
            source: 來源資訊 {"type": "pdf|html|manual", "url": "...", "file": "..."}
        """
        result = {
            "rules": {},
            "limitations": [],
            "loadIn": {},
            "equipmentDetails": [],
        }

        rules = self._extract_rules(text, source=source)
        if rules:
            result["rules"] = rules

        load_in = self._extract_load_in(text)
        if load_in:
            result["loadIn"] = load_in

        equipment = self._extract_equipment_specs(text)
        if equipment:
            result["equipmentDetails"] = equipment

        limitations = self._extract_limitations(text)
        if limitations:
            result["limitations"] = limitations

        return result

    def _extract_rules(self, text: str, source: dict = None) -> dict:
        """提取場地規定 — 雙層匹配（嚴格 + 寬鬆）

        Args:
            text: 要提取的文字內容
            source: 來源資訊 {"type": "pdf|html|manual", "url": "...", "file": "..."}
        """
        rules = {}
        lines = text.split('\n')

        for category, keywords in self.rules_keywords.items():
            strict_rules = []
            loose_rules = []

            for line in lines:
                line_stripped = line.strip()
                if not line_stripped or len(line_stripped) < 4:
                    continue

                # 檢查是否含該分類的關鍵字
                zh_kw = keywords.get('zh', [])
                en_kw = keywords.get('en', [])
                has_category_kw = any(kw in line_stripped for kw in zh_kw + en_kw)
                if not has_category_kw:
                    continue

                # 嚴格匹配：含指示性文字（禁止/不得/限制等）
                strict_imperatives = [
                    '禁止', '不得', '不可', '限制', '必須', '僅限',
                    '不允許', '請勿', '嚴禁', '違規', '違反',
                ]
                has_strict = any(kw in line_stripped for kw in strict_imperatives)

                # 寬鬆匹配：含描述性/服務性文字
                loose_indicators = [
                    '提供', '安排', '可', '收費', '費用', '須', '需', '應',
                    '限', '方案', '服務', '包含', '另計', '加收', '優惠',
                    '請', '提前', '預約', '申請', '洽詢', '聯絡',
                ]
                has_loose = any(kw in line_stripped for kw in loose_indicators)

                if has_strict:
                    rule_obj = {
                        "rule": line_stripped,
                        "confidence": "confirmed",
                        "exception": None,
                        "penalty": None,
                        "negotiable": None,
                    }
                    if source:
                        rule_obj["source"] = source
                    strict_rules.append(rule_obj)
                elif has_loose and len(line_stripped) >= 15:
                    rule_obj = {
                        "rule": line_stripped,
                        "confidence": "unverified",
                        "exception": None,
                        "penalty": None,
                        "negotiable": None,
                    }
                    if source:
                        rule_obj["source"] = source
                    loose_rules.append(rule_obj)

            # 合併：嚴格優先，寬鬆去重後追加
            all_rules = strict_rules[:]
            strict_texts = {r["rule"] for r in strict_rules}
            for r in loose_rules:
                if r["rule"] not in strict_texts:
                    all_rules.append(r)

            if all_rules:
                rules[category] = all_rules

        return rules

    def _extract_load_in(self, text: str) -> dict:
        """提取進場資訊"""
        load_in = {}
        lines = text.split('\n')

        # 貨梯
        elevator_lines = []
        elevator_spec_lines = []
        vehicle_lines = []
        setup_lines = []

        for line in lines:
            ls = line.strip()
            if not ls:
                continue

            for kw in self.loadin_keywords["elevator"]["zh"] + self.loadin_keywords["elevator"]["en"]:
                if kw.lower() in ls.lower():
                    elevator_lines.append(ls)
                    break

            for kw in self.loadin_keywords["elevator_spec"]["zh"] + self.loadin_keywords["elevator_spec"]["en"]:
                if kw.lower() in ls.lower():
                    elevator_spec_lines.append(ls)
                    break

            for kw in self.loadin_keywords["vehicle"]["zh"] + self.loadin_keywords["vehicle"]["en"]:
                if kw.lower() in ls.lower():
                    vehicle_lines.append(ls)
                    break

            for kw in self.loadin_keywords["setup_teardown"]["zh"] + self.loadin_keywords["setup_teardown"]["en"]:
                if kw.lower() in ls.lower():
                    setup_lines.append(ls)
                    break

        if elevator_lines or elevator_spec_lines:
            combined = elevator_lines + [
                s for s in elevator_spec_lines if s not in elevator_lines
            ]
            load_in["elevatorCapacity"] = '; '.join(combined[:3])

        if vehicle_lines:
            load_in["loadingDock"] = '; '.join(vehicle_lines[:3])

        if setup_lines:
            for line in setup_lines:
                # 嘗試提取時間
                time_match = re.search(
                    r'(\d{1,2}[:：]\d{2})\s*[-~至到]\s*(\d{1,2}[:：]\d{2})', line
                )
                if time_match:
                    load_in["loadInTime"] = time_match.group(1)
                    load_in["loadOutTime"] = time_match.group(2)
                    break

            if "loadInTime" not in load_in:
                load_in["loadInTime"] = '; '.join(setup_lines[:2])

        return load_in

    def _extract_equipment_specs(self, text: str) -> list:
        """提取設備規格"""
        specs = []
        lines = text.split('\n')

        for line in lines:
            ls = line.strip()
            if not ls:
                continue

            for eq_type, keywords in self.equipment_keywords.items():
                zh_kw = keywords.get('zh', [])
                en_kw = keywords.get('en', [])

                if any(kw in ls for kw in zh_kw + en_kw):
                    # 嘗試提取規格數值
                    spec_value = self._extract_spec_value(ls)

                    detail = {
                        "name": eq_type,
                        "spec": spec_value or ls,
                        "externalAllowed": None,
                        "extraCharge": None,
                    }

                    # 避免重複
                    if not any(s["name"] == eq_type for s in specs):
                        specs.append(detail)
                    break

        return specs

    def _extract_spec_value(self, text: str) -> str:
        """從文字中提取規格值"""
        patterns = [
            (r'(\d{4,})\s*流明', '流明'),
            (r'(\d+(?:\.\d+)?)\s*(?:吋|英吋|inch)', '吋'),
            (r'(\d+)\s*(?:支|隻|個)\s*(?:麥克風|MIC|mic)', '支'),
            (r'(\d+)\s*(?:聲道|channel)', 'ch'),
            (r'(\d+(?:\.\d+)?)\s*(?:Mbps|Gbps|MB/s)', ''),
            (r'(\d+)\s*[x×]\s*(\d+)', ''),
        ]

        for pattern, unit in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return m.group(0)

        return ''

    def _extract_limitations(self, text: str) -> list:
        """提取場地隱藏限制"""
        limitations = []
        lines = text.split('\n')

        limitation_patterns = [
            r'高度.*?(?:限制|僅|不得超過|上限)',
            r'天花板.*?(?:高度|限制|僅)',
            r'載重.*?(?:限制|上限|不得超過)',
            r'電力.*?(?:限制|上限|不足)',
            r'(?:禁止|不得|不可).*(?:吊掛|懸吊|安裝|施工)',
            r'超過.*?(?:需|須|應).*(?:申請|確認|核准)',
            r'(?:限|僅限|限制).*(?:使用|進入|攜帶)',
            r'(?:無|沒有).*(?:貨梯|電梯|停車位)',
        ]

        for line in lines:
            ls = line.strip()
            if not ls or len(ls) < 6:
                continue

            for pat in limitation_patterns:
                if re.search(pat, ls):
                    if ls not in limitations:
                        limitations.append(ls)
                    break

        return limitations

    def _extract_knowledge_sections(self, soup: BeautifulSoup) -> str:
        """從 HTML 中尋找知識相關區塊"""
        knowledge_selectors = [
            '[class*="faq"]', '[class*="notice"]', '[class*="rule"]',
            '[class*="policy"]', '[class*="terms"]', '[class*="attention"]',
            '[class*="notice"]', '[class*="注意"]', '[class*="須知"]',
            '[id*="faq"]', '[id*="notice"]', '[id*="rule"]',
        ]

        sections = []
        for selector in knowledge_selectors:
            elements = soup.select(selector)
            for el in elements:
                text = el.get_text(strip=True)
                if len(text) > 50:
                    sections.append(text)

        return '\n'.join(sections) if sections else ''


def extract_venue_data(soup: BeautifulSoup, url: str, strategy: str) -> list:
    """
    統一提取入口：根據策略選擇提取方式
    優先順序：HTML 表格 > HTML 卡片 > 正則
    """
    html_ext = HTMLExtractor()
    all_rooms = []

    table_rooms = html_ext.extract_from_tables(soup, url)
    if table_rooms:
        all_rooms.extend(table_rooms)
        print(f'  [提取] HTML 表格: {len(table_rooms)} 個會議室')

    if len(all_rooms) < 2:
        card_rooms = html_ext.extract_from_cards(soup, url)
        if card_rooms:
            all_rooms.extend(card_rooms)
            print(f'  [提取] HTML 卡片: {len(card_rooms)} 個會議室')

    if len(all_rooms) < 2 and strategy != 'dynamic_js':
        text = soup.get_text()
        regex_ext = RegexExtractor()
        regex_rooms = regex_ext.extract(text)
        if regex_rooms:
            all_rooms.extend(regex_rooms)
            print(f'  [提取] 正則: {len(regex_rooms)} 個會議室')

    images = html_ext.extract_images(soup, url)
    if images:
        print(f'  [提取] 圖片: {len(images)} 張')
        if len(all_rooms) == 1:
            all_rooms[0]['images'] = {'main': images[0], 'gallery': images[:5]}

    return all_rooms
