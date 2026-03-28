#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整會議室資料擷取器

功能:
1. 從場地官網找到會議室頁面
2. 提取每個會議室的完整資訊
3. 結構化儲存到 venues.json
4. 驗證資料完整性

原則:
- 官網有什麼，活動大師有什麼
- 不多也不少
- 資料來源可追蹤
"""

import sys
import io
import requests

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
from datetime import datetime
from typing import Dict, List, Optional

class CompleteMeetingRoomExtractor:
    """完整會議室資料擷取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_venue_rooms(self, venue_url: str, venue_id: int) -> Dict:
        """
        完整擷取場地的會議室資料

        Args:
            venue_url: 場地官網 URL
            venue_id: 場地 ID

        Returns:
            Dict: {
                'success': bool,
                'rooms': List[Dict],
                'source': str,
                'metadata': Dict
            }
        """

        print(f'\n{"="*60}')
        print(f'開始擷取場地 ID {venue_id}')
        print(f'URL: {venue_url}')
        print(f'{"="*60}\n')

        result = {
            'success': False,
            'rooms': [],
            'source': None,
            'metadata': {
                'venue_id': venue_id,
                'venue_url': venue_url,
                'extractedAt': datetime.now().isoformat(),
                'steps': []
            }
        }

        try:
            # 步驟1: 找到會議室頁面
            print('步驟1: 尋找會議室頁面...')
            meeting_page_url = self._find_meeting_page(venue_url)

            if not meeting_page_url:
                print('  ❌ 未找到會議室頁面')
                result['metadata']['steps'].append('尋找會議室頁面: 失敗')
                return result

            print(f'  ✅ 找到: {meeting_page_url}')
            result['source'] = meeting_page_url
            result['metadata']['steps'].append(f'尋找會議室頁面: {meeting_page_url}')

            # 步驟2: 抓取會議室頁面
            print('\n步驟2: 抓取會議室頁面...')
            response = self.session.get(meeting_page_url, timeout=15, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            print(f'  ✅ 狀態: {response.status_code}')

            # 步驟3: 識別會議室資訊結構
            print('\n步驟3: 識別會議室結構...')
            room_sections = self._identify_room_structure(soup)

            if not room_sections:
                print('  ❌ 未找到會議室資訊')
                result['metadata']['steps'].append('識別會議室結構: 失敗')
                return result

            print(f'  ✅ 找到 {len(room_sections)} 個會議室區塊')
            result['metadata']['steps'].append(f'識別會議室結構: {len(room_sections)}個')

            # 步驟4: 提取每個會議室的資料
            print('\n步驟4: 提取會議室資料...')
            rooms = []

            for i, section in enumerate(room_sections, 1):
                print(f'\n  處理會議室 {i}/{len(room_sections)}...')

                room_data = self._extract_single_room(section, venue_id, i, meeting_page_url)

                if room_data and room_data.get('name'):
                    print(f'    ✅ {room_data["name"]} - 容量: {room_data.get("capacity", "N/A")}人')
                    rooms.append(room_data)
                else:
                    print(f'    ⚠️  無法提取資料')

            result['rooms'] = rooms
            result['metadata']['steps'].append(f'提取會議室資料: {len(rooms)}個')
            result['success'] = True

            # 步驟5: 驗證資料
            print(f'\n步驟5: 驗證資料...')
            valid_rooms = [r for r in rooms if self._validate_room(r)]

            print(f'  ✅ 有效會議室: {len(valid_rooms)}/{len(rooms)}')
            result['metadata']['steps'].append(f'驗證資料: {len(valid_rooms)}/{len(rooms)}有效')

        except Exception as e:
            print(f'\n❌ 錯誤: {e}')
            result['metadata']['error'] = str(e)

        return result

    def _find_meeting_page(self, venue_url: str) -> Optional[str]:
        """找到會議室頁面 URL"""

        try:
            response = self.session.get(venue_url, timeout=10, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 尋找會議室相關連結
            keywords = ['會議', 'meeting', '宴會', 'banquet', '場地', 'space', '會議室',
                       'meeting-room', 'banquet-hall', 'conference']

            links = []
            for a in soup.find_all('a', href=True):
                text = a.get_text().strip().lower()
                href = a['href'].lower()

                # 計算關鍵字匹配數
                score = sum(1 for kw in keywords if kw in text or kw in href)

                if score > 0:
                    links.append({
                        'url': urljoin(venue_url, a['href']),
                        'text': a.get_text().strip(),
                        'score': score
                    })

            # 排序並返回最佳匹配
            if links:
                links.sort(key=lambda x: x['score'], reverse=True)
                return links[0]['url']

        except Exception as e:
            print(f'  ⚠️  找尋錯誤: {e}')

        return None

    def _identify_room_structure(self, soup: BeautifulSoup) -> List:
        """識別會議室資訊的HTML結構"""

        room_sections = []

        # 嘗試1: 表格結構
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:  # 至少有標題列+資料列
                room_sections.extend(rows[1:])  # 跳過標題列

        if room_sections:
            print(f'    使用表格結構: {len(room_sections)} 個')
            return room_sections

        # 嘗試2: 卡片結構
        cards = soup.find_all(['div', 'section'], class_=re.compile(r'room|meeting|banquet', re.I))
        if cards:
            print(f'    使用卡片結構: {len(cards)} 個')
            return cards

        # 嘗試3: 列表結構
        items = soup.find_all(['li', 'div'], class_=re.compile(r'item|card|entry', re.I))
        if len(items) > 2:  # 至少有幾個項目
            print(f'    使用列表結構: {len(items)} 個')
            return items

        # 嘗試4: 標題+內容結構
        sections = []
        for heading in soup.find_all(['h3', 'h4', 'h5']):
            text = heading.get_text().strip()
            # 檢查是否包含會議室相關字詞
            if any(kw in text for kw in ['廳', '室', 'Room', 'Hall', '空間']):
                sections.append(heading)

        if sections:
            print(f'    使用標題結構: {len(sections)} 個')
            return sections

        return []

    def _extract_single_room(self, section, venue_id: int, index: int, source_url: str) -> Optional[Dict]:
        """提取單個會議室的完整資料"""

        text_content = section.get_text()

        room_data = {
            'id': f'r{venue_id}{index:03d}',
            'name': self._extract_name(section, text_content),
            'floor': self._extract_floor(section, text_content),
            'area': self._extract_area(section, text_content),
            'areaUnit': None,
            'capacity': self._extract_capacity(section, text_content),
            'capacityType': self._extract_capacity_type(section, text_content),
            'equipment': self._extract_equipment(section, text_content),
            'priceHalfDay': self._extract_price(section, text_content, 'half'),
            'priceFullDay': self._extract_price(section, text_content, 'full'),
            'images': self._extract_images(section, source_url),
            'description': self._extract_description(section, text_content)
        }

        # 設定 areaUnit
        if room_data['area']:
            room_data['areaUnit'] = '坪'  # 預設為坪

        return room_data

    def _extract_name(self, section, text_content: str) -> Optional[str]:
        """提取會議室名稱"""

        # 從標題提取
        for tag in ['h3', 'h4', 'h5', 'strong', 'b']:
            elem = section.find(tag)
            if elem:
                name = elem.get_text().strip()
                # 清理名稱
                name = re.sub(r'\s+', ' ', name)
                return name[:50]

        # 從文本第一行提取
        lines = text_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 50:
                return line

        return None

    def _extract_floor(self, section, text_content: str) -> Optional[str]:
        """提取樓層"""

        # 從文本中尋找樓層資訊
        floor_pattern = re.compile(r'(\d+[F樓層]|B\d+|地面層|一樓|二樓|三樓|四樓|五樓)', re.I)

        match = floor_pattern.search(text_content)
        if match:
            return match.group(1)

        return None

    def _extract_area(self, section, text_content: str) -> Optional[int]:
        """提取面積"""

        # 尋找面積資訊
        area_pattern = re.compile(r'(\d+)\s*(坪|平方米|㎡|m²)', re.I)

        match = area_pattern.search(text_content)
        if match:
            return int(match.group(1))

        return None

    def _extract_capacity(self, section, text_content: str) -> Optional[int]:
        """提取容量"""

        # 尋找容量資訊
        capacity_patterns = [
            r'容量[：:]\s*(\d+)\s*人',
            r'可容納\s*(\d+)\s*人',
            r'(\d+)\s*人',
            r'capacity[：:]\s*(\d+)',
        ]

        for pattern in capacity_patterns:
            match = re.search(pattern, text_content)
            if match:
                return int(match.group(1))

        return None

    def _extract_capacity_type(self, section, text_content: str) -> Optional[str]:
        """提取容量類型"""

        types = [
            ('劇院式', '劇院式'),
            ('theater', '劇院式'),
            ('課桌式', '課桌式'),
            ('classroom', '課桌式'),
            ('宴會式', '宴會式'),
            ('banquet', '宴會式'),
        ]

        for keyword, value in types:
            if keyword in text_content.lower():
                return value

        return None

    def _extract_equipment(self, section, text_content: str) -> Optional[str]:
        """提取設備清單"""

        equipment_keywords = ['投影機', '投影', '音響', '麥克風', '螢幕', '白板',
                             'projector', 'sound', 'microphone', 'screen']

        found = []
        for keyword in equipment_keywords:
            if keyword in text_content:
                found.append(keyword)

        if found:
            return ', '.join(found)

        return None

    def _extract_price(self, section, text_content: str, price_type: str) -> Optional[int]:
        """提取價格"""

        if price_type == 'half':
            patterns = [
                r'半日[：:]\s*NT\$?\s*([\d,]+)',
                r'half\s*day[：:]\s*NT\$?\s*([\d,]+)',
            ]
        else:  # full
            patterns = [
                r'全日[：:]\s*NT\$?\s*([\d,]+)',
                r'full\s*day[：:]\s*NT\$?\s*([\d,]+)',
            ]

        for pattern in patterns:
            match = re.search(pattern, text_content, re.I)
            if match:
                return int(match.group(1).replace(',', ''))

        return None

    def _extract_images(self, section, base_url: str) -> Optional[Dict]:
        """提取圖片"""

        img = section.find('img')
        if img:
            img_url = img.get('src', '')
            if img_url:
                return {
                    'main': urljoin(base_url, img_url),
                    'source': base_url
                }

        return None

    def _extract_description(self, section, text_content: str) -> Optional[str]:
        """提取描述"""

        # 找段落文字
        paragraphs = section.find_all('p')
        if paragraphs:
            desc = ' '.join([p.get_text().strip() for p in paragraphs])
            desc = ' '.join(desc.split())  # 清理多餘空白
            return desc[:200] if desc else None

        return None

    def _validate_room(self, room: Dict) -> bool:
        """驗證會議室資料"""

        # 必備欄位
        if not room.get('name'):
            return False

        # 至少要有容量或面積其中之一
        if not room.get('capacity') and not room.get('area'):
            print(f'    ⚠️  {room.get("name")}: 缺少容量和面積資訊')

        return True


# 使用範例
if __name__ == '__main__':
    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找一個有 URL 的場地來測試
    test_venue = None
    for venue in venues:
        if venue.get('url') and venue.get('status') != 'discontinued':
            # 選一個還沒有詳細 rooms 資料的
            if not venue.get('rooms') or len(venue.get('rooms', [])) == 0:
                test_venue = venue
                break

    if not test_venue:
        # 如果都沒有，就選第一個
        for venue in venues:
            if venue.get('url'):
                test_venue = venue
                break

    if test_venue:
        extractor = CompleteMeetingRoomExtractor()
        result = extractor.extract_venue_rooms(test_venue['url'], test_venue['id'])

        print(f'\n{"="*60}')
        print(f'擷取結果')
        print(f'{"="*60}')
        print(f'成功: {result["success"]}')
        print(f'會議室數量: {len(result["rooms"])}')
        print(f'來源: {result.get("source", "N/A")}')

        if result['rooms']:
            print(f'\n會議室列表:')
            for room in result['rooms']:
                print(f'  - {room["name"]}: {room.get("capacity", "N/A")}人')

        # 儲存結果
        with open('room_extraction_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f'\n詳細結果已儲存到 room_extraction_result.json')
    else:
        print('沒有找到可測試的場地')
