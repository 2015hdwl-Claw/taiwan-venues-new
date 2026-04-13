#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/spa_extractor.py - SPA 動態網站提取器
使用 Playwright 渲染 JavaScript，解決 Angular/React/Vue 等 SPA 網站無法用 requests 抓取的問題
"""

import json
import re
from urllib.parse import urljoin

from .config import CONFIRM_ROOM_KEYWORDS
from .validators import is_meeting_room, is_valid_room_name


class SPExtractor:
    """SPA 動態網站提取器 — 用 Playwright 渲染 JS 後提取資料"""

    # 會議室相關 CSS 選擇器（常見 class/id 模式）
    ROOM_SELECTORS = [
        # 通用會議室卡片/區塊
        '[class*="room"]', '[class*="Room"]',
        '[class*="venue"]', '[class*="Venue"]',
        '[class*="hall"]', '[class*="Hall"]',
        '[class*="banquet"]', '[class*="Banquet"]',
        '[class*="meeting"]', '[class*="Meeting"]',
        '[class*="space"]', '[class*="Space"]',
        '[class*="ballroom"]', '[class*="Ballroom"]',
        # 列表項目
        '[class*="card"]', '[class*="Card"]',
        '[class*="item"]', '[class*="Item"]',
        # 表格
        'table',
    ]

    # 圖片過濾：排除 logo/icon/banner 等
    IMAGE_SKIP_PATTERNS = [
        'logo', 'icon', 'avatar', 'button', 'arrow',
        'social', 'menu', 'favicon', 'spacer', 'banner',
        'arrow', 'close', 'search', 'hamburger',
        'tag.gif', 'pixel', 'tracking', 'analytics', 'tr?id',
        'facebook.com/tr', 'doubleclick', 'googletag',
        'noscript=1', 'c_t=lap', 'e=pv',  # Line/FB 追蹤參數
    ]

    def __init__(self):
        self._browser = None
        self._playwright = None

    def _get_browser(self):
        """延遲初始化瀏覽器"""
        if self._browser is None:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-gpu']
            )
        return self._browser

    def close(self):
        """關閉瀏覽器"""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def render_page(self, url: str, wait_seconds: int = 5) -> dict:
        """
        用 Playwright 渲染 SPA 頁面
        返回 {html, api_responses, title, url}
        """
        browser = self._get_browser()
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
        )

        # 攔截 API 請求
        api_responses = []
        def handle_response(response):
            ct = response.headers.get('content-type', '')
            if 'json' in ct and response.status == 200:
                try:
                    data = response.json()
                    api_responses.append({
                        'url': response.url,
                        'data': data,
                    })
                except Exception:
                    pass

        page = context.new_page()
        page.on('response', handle_response)

        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            # 額外等待動態內容載入
            page.wait_for_timeout(wait_seconds * 1000)

            html = page.content()
            title = page.title()
            final_url = page.url

            return {
                'html': html,
                'api_responses': api_responses,
                'title': title,
                'url': final_url,
            }
        except Exception as e:
            print(f'  [SPA] 渲染失敗 {url}: {e}')
            return {
                'html': '',
                'api_responses': api_responses,
                'title': '',
                'url': url,
            }
        finally:
            context.close()

    def extract_from_api(self, api_responses: list) -> list:
        """
        從攔截到的 API JSON 回應中提取會議室資料
        """
        rooms = []
        for resp in api_responses:
            data = resp['data']
            # 遞迴搜尋 JSON 中看起來像會議室的物件
            found = self._find_rooms_in_json(data)
            rooms.extend(found)
        return rooms

    def _find_rooms_in_json(self, obj, depth=0) -> list:
        """遞迴搜尋 JSON 中包含會議室資訊的物件"""
        if depth > 5:
            return []

        rooms = []
        if isinstance(obj, dict):
            # 檢查是否看起來像會議室物件
            name = obj.get('name') or obj.get('title') or obj.get('roomName') or obj.get('room_name')
            if name and isinstance(name, str) and self._looks_like_room(obj):
                room = self._parse_room_from_json(obj)
                if room:
                    rooms.append(room)

            # 繼續遞迴子物件
            for key, val in obj.items():
                if isinstance(val, (dict, list)):
                    rooms.extend(self._find_rooms_in_json(val, depth + 1))

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    rooms.extend(self._find_rooms_in_json(item, depth + 1))

        return rooms

    def _looks_like_room(self, obj: dict) -> bool:
        """判斷 JSON 物件是否像會議室資料"""
        room_indicators = [
            'capacity', 'area', 'floor', 'size', 'dimension',
            'price', 'pricing', 'cost',
            'equipment', 'amenities', 'facilities',
            'image', 'photo', 'imageUrl',
            'maxCapacity', 'minCapacity', 'seating',
            'theater', 'classroom', 'banquet',
        ]
        # 物件中至少有 2 個會議室相關欄位
        match_count = sum(1 for k in room_indicators if k in obj)
        return match_count >= 2

    def _parse_room_from_json(self, obj: dict) -> dict:
        """從 JSON 物件解析會議室"""
        name = obj.get('name') or obj.get('title') or obj.get('roomName') or obj.get('room_name')
        if not name or not is_valid_room_name(str(name)):
            return None

        room = {'name': str(name).strip()}

        # Capacity
        cap = obj.get('capacity') or obj.get('maxCapacity') or obj.get('max_capacity')
        if cap:
            if isinstance(cap, dict):
                room['capacity'] = cap
            elif isinstance(cap, (int, float)):
                room['capacity'] = {'theater': int(cap)}

        # Area
        area = obj.get('area') or obj.get('size') or obj.get('areaPing') or obj.get('ping')
        if area:
            try:
                room['area'] = float(area)
                room['areaUnit'] = '坪'
            except (ValueError, TypeError):
                pass

        # Floor
        floor = obj.get('floor') or obj.get('level')
        if floor:
            room['floor'] = str(floor)

        # Images
        img = obj.get('image') or obj.get('imageUrl') or obj.get('photo') or obj.get('mainImage')
        if img:
            room['images'] = {'main': str(img)}

        # Equipment
        equip = obj.get('equipment') or obj.get('amenities') or obj.get('facilities')
        if equip and isinstance(equip, list):
            room['equipment'] = [str(e) for e in equip]

        return room

    def extract_from_rendered_html(self, html: str, base_url: str) -> list:
        """
        從 Playwright 渲染後的 HTML 提取會議室
        複用現有 HTMLExtractor 的邏輯，但用渲染後的完整 HTML
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        all_rooms = []

        # 方法 1: 表格提取
        table_rooms = self._extract_from_tables(soup, base_url)
        if table_rooms:
            all_rooms.extend(table_rooms)
            print(f'  [SPA-HTML] 表格: {len(table_rooms)} 個會議室')

        # 方法 2: 卡片/區塊提取
        if len(all_rooms) < 2:
            card_rooms = self._extract_from_cards(soup, base_url)
            if card_rooms:
                all_rooms.extend(card_rooms)
                print(f'  [SPA-HTML] 卡片: {len(card_rooms)} 個會議室')

        # 方法 3: 正則提取（渲染後的文字通常比空殼豐富很多）
        if len(all_rooms) < 2:
            text = soup.get_text()
            from .extractors import RegexExtractor
            regex_ext = RegexExtractor()
            regex_rooms = regex_ext.extract(text)
            if regex_rooms:
                all_rooms.extend(regex_rooms)
                print(f'  [SPA-HTML] 正則: {len(regex_rooms)} 個會議室')

        return all_rooms

    def _extract_from_tables(self, soup, base_url: str) -> list:
        """從渲染後的 HTML 表格提取"""
        rooms = []
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue

            # 解析表頭
            header_cells = rows[0].find_all(['th', 'td'])
            headers = [cell.get_text(strip=True).lower() for cell in header_cells]

            name_col = self._find_column(headers, ['廳', '名稱', 'room', 'name', '會議室', '場地'])
            cap_col = self._find_column(headers, ['人', '容量', 'capacity', 'seating', '劇院'])
            area_col = self._find_column(headers, ['坪', '面積', 'area', 'size', '平方'])
            price_col = self._find_column(headers, ['價', '費', 'price', 'cost', '租金', '收費'])

            if name_col is None:
                continue

            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) <= name_col:
                    continue

                name = cells[name_col].get_text(strip=True)
                if not name or not is_valid_room_name(name):
                    continue

                room = {'name': name}

                if cap_col is not None and cap_col < len(cells):
                    cap_text = cells[cap_col].get_text(strip=True)
                    cap = self._parse_number(cap_text)
                    if cap and cap > 0:
                        room['capacity'] = {'theater': cap}

                if area_col is not None and area_col < len(cells):
                    area_text = cells[area_col].get_text(strip=True)
                    area = self._parse_number(area_text)
                    if area and area > 0:
                        room['area'] = area
                        room['areaUnit'] = '坪'

                if price_col is not None and price_col < len(cells):
                    price_text = cells[price_col].get_text(strip=True)
                    price = self._parse_price(price_text)
                    if price:
                        room['pricing'] = price

                if room.get('capacity') or room.get('area'):
                    rooms.append(room)

        return rooms

    def _extract_from_cards(self, soup, base_url: str) -> list:
        """從渲染後的 HTML 卡片/區塊提取"""
        rooms = []

        # 找可能包含會議室的容器
        containers = []
        for selector in self.ROOM_SELECTORS:
            try:
                containers.extend(soup.select(selector))
            except Exception:
                continue

        for container in containers:
            # 找標題
            name = None
            for tag in ['h2', 'h3', 'h4', 'h5']:
                heading = container.find(tag)
                if heading:
                    name = heading.get_text(strip=True)
                    break

            if not name:
                # 嘗試找帶有標題屬性的元素
                named_el = container.find(attrs={'class': re.compile(r'name|title|heading', re.I)})
                if named_el:
                    name = named_el.get_text(strip=True)

            if not name or not is_valid_room_name(name):
                continue

            text = container.get_text()

            room = {'name': name}

            # 容量
            cap = self._parse_capacity_from_text(text)
            if cap:
                room['capacity'] = cap

            # 面積
            area = self._parse_area_from_text(text)
            if area:
                room['area'] = area
                room['areaUnit'] = '坪'

            # 圖片
            img = container.find('img')
            if img:
                src = img.get('src') or img.get('data-src') or ''
                if src:
                    room['images'] = {'main': urljoin(base_url, src)}

            if room.get('capacity') or room.get('area'):
                rooms.append(room)

        return rooms

    def extract_images(self, soup, base_url: str) -> list:
        """提取場地主圖片，過濾追蹤像素和無關圖片"""
        images = []

        # 只保留這些副檔名的圖片
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg')

        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or ''
            if not src:
                continue

            alt = img.get('alt', '').lower()
            cls = ' '.join(img.get('class', []))
            src_lower = src.lower()

            # 跳過不相關圖片
            if any(p in src_lower or p in alt or p in cls for p in self.IMAGE_SKIP_PATTERNS):
                continue

            # 跳過尺寸太小的圖片（追蹤像素通常是 1x1）
            width = img.get('width')
            height = img.get('height')
            if width and int(width) < 50:
                continue
            if height and int(height) < 50:
                continue

            # 檢查副檔名（如果 URL 有副檔名）
            has_valid_ext = any(src_lower.endswith(ext) for ext in valid_extensions)
            has_ext = any(src_lower.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.php', '.aspx', '.jsp'))

            # 如果有副檔名但不是圖片格式，跳過
            if has_ext and not has_valid_ext:
                continue

            full_url = urljoin(base_url, src)
            if full_url not in images:
                images.append(full_url)

        # 優先選擇場地相關圖片
        def image_priority(img_url):
            url_lower = img_url.lower()
            priority_keywords = [
                'room', 'hall', 'banquet', 'meeting', 'conference',
                '廳', '會議', '宴會', '空間', '空照'
            ]
            for i, kw in enumerate(priority_keywords):
                if kw in url_lower:
                    return len(priority_keywords) - i
            return 0

        images.sort(key=image_priority, reverse=True)
        return images

    # === 工具方法 ===

    def _find_column(self, headers: list, keywords: list) -> int:
        """找包含關鍵字的欄位索引"""
        for kw in keywords:
            for i, h in enumerate(headers):
                if kw in h:
                    return i
        return None

    def _parse_number(self, text: str) -> float:
        """從文字中提取數字"""
        nums = re.findall(r'([\d.]+)', text.replace(',', ''))
        if nums:
            try:
                return float(nums[0])
            except ValueError:
                pass
        return None

    def _parse_price(self, text: str) -> dict:
        """從文字中解析價格"""
        prices = re.findall(r'[\$NT]?\s*([\d,]+)', text)
        if not prices:
            return None

        nums = [int(p.replace(',', '')) for p in prices if p.replace(',', '').isdigit()]

        if len(nums) >= 2:
            return {'halfDay': min(nums), 'fullDay': max(nums)}
        elif len(nums) == 1:
            return {'fullDay': nums[0]}
        return None

    def _parse_capacity_from_text(self, text: str) -> dict:
        """從文字中提取容量"""
        patterns = [
            (r'(\d+)\s*人', 'theater'),
            (r'劇院[式型]?\s*(\d+)', 'theater'),
            (r'教室[式型]?\s*(\d+)', 'classroom'),
            (r'宴會?\s*(\d+)\s*桌', 'banquet'),
            (r'容納?\s*(\d+)', 'theater'),
        ]
        cap = {}
        for pattern, key in patterns:
            m = re.search(pattern, text)
            if m:
                cap[key] = int(m.group(1))
        return cap if cap else None

    def _parse_area_from_text(self, text: str) -> float:
        """從文字中提取面積"""
        m = re.search(r'([\d.]+)\s*坪', text)
        if m:
            return float(m.group(1))
        m = re.search(r'([\d.]+)\s*(?:平方公尺|m²|m2)', text)
        if m:
            return round(float(m.group(1)) / 3.3058, 1)
        return None

    def extract(self, url: str) -> list:
        """
        主入口：渲染 SPA 頁面並提取會議室
        優先使用 API 攔截，後備使用 HTML 解析
        """
        print(f'  [SPA] Playwright 渲染: {url}')
        result = self.render_page(url)

        if not result['html']:
            return []

        rooms = []

        # 方法 1: 從攔截到的 API 回應提取
        if result['api_responses']:
            api_rooms = self.extract_from_api(result['api_responses'])
            if api_rooms:
                rooms.extend(api_rooms)
                print(f'  [SPA-API] 攔截到 {len(result["api_responses"])} 個 API，提取 {len(api_rooms)} 個會議室')

        # 方法 2: 從渲染後的 HTML 提取
        if len(rooms) < 2:
            html_rooms = self.extract_from_rendered_html(result['html'], url)
            rooms.extend(html_rooms)

        # 提取圖片
        if rooms:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result['html'], 'html.parser')
            images = self.extract_images(soup, url)
            if images:
                print(f'  [SPA] 圖片: {len(images)} 張')
                if len(rooms) == 1 and not rooms[0].get('images'):
                    rooms[0]['images'] = {'main': images[0], 'gallery': images[:5]}

        return rooms
