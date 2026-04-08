#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3: 飯店+婚宴場地專用品質提升工具

特點:
- 專注於飯店和婚宴場地
- 深度提取會議廳/宴會廳資訊
- 優先提取價格資訊（飯店通常有完整價格表）
- 提取設施與服務資訊

目標: 將 26 個場地的品質分數從平均 35 → 65+
"""
import sys
import io
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class HotelBanquetBooster:
    """飯店+婚宴場地專用品質提升工具"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 飯店/婚宴常見關鍵字
        self.hotel_keywords = [
            '會議室', '會議廳', '宴會廳', '宴會', '會議', 'meeting',
            'conference', 'ballroom', 'banquet', 'function'
        ]

    def calculate_room_quality(self, room):
        """計算單一會議室品質分數"""
        score = 0

        # 名稱 (必需)
        if room.get('name'):
            score += 10

        # 容量 (25分 - 飯店通常有多種配置)
        if room.get('capacity'):
            if isinstance(room['capacity'], dict):
                # 多種配置類型
                score += 25
            elif isinstance(room['capacity'], (int, float)):
                score += 20

        # 面積 (20分)
        if room.get('area'):
            score += 20

        # 價格 (30分 - 最重要)
        if room.get('price'):
            if isinstance(room['price'], dict):
                score += 30
        elif room.get('priceHalfDay') or room.get('priceFullDay'):
            score += 25

        # 設備 (10分)
        if room.get('equipment'):
            score += 10

        # 圖片 (5分)
        if room.get('images'):
            score += 5

        return score

    def calculate_venue_quality(self, venue):
        """計算場地整體品質分數"""
        rooms = venue.get('rooms', [])

        if not rooms:
            return 0

        # 會議室平均品質
        room_scores = [self.calculate_room_quality(room) for room in rooms]
        avg_room_score = sum(room_scores) / len(room_scores)

        # 會議室數量加成
        room_count_bonus = min(len(rooms) * 2, 20)

        # 聯絡資訊加成
        contact_bonus = 0
        if venue.get('contact', {}).get('phone') or venue.get('phone'):
            contact_bonus += 5
        if venue.get('contact', {}).get('email') or venue.get('email'):
            contact_bonus += 5

        # 交通加成
        transport_bonus = 0
        if venue.get('transportation') or venue.get('traffic'):
            transport_bonus = 10

        total_score = avg_room_score + room_count_bonus + contact_bonus + transport_bonus
        return min(int(total_score), 100)

    def extract_price_from_html(self, soup, base_url):
        """從 HTML 提取價格資訊（飯店優化版）"""
        price_data = {
            'hasPriceInfo': False,
            'priceInHTML': False,
            'hasPDF': False,
            'pdfUrls': [],
            'extractedPrices': {},
            'pricePages': []  # 飯店通常有獨立價格頁面
        }

        page_text = soup.get_text()

        # 檢查 PDF 連結
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
        if pdf_links:
            price_data['hasPDF'] = True
            for link in pdf_links:
                href = link.get('href', '')
                text = link.get_text().lower()
                if any(kw in href.lower() or kw in text
                       for kw in ['價格', '價目', '收費', 'rate', 'price', '費率', '報價']):
                    full_url = urljoin(base_url, href)
                    price_data['pdfUrls'].append(full_url)

        # 飯店/婚宴價格模式（更詳細）
        price_patterns = [
            # 平日/假日
            (r'平日[：:]\s*NT\$?\s*([\d,]+)', 'weekday'),
            (r'假日[：:]\s*NT\$?\s*([\d,]+)', 'holiday'),
            (r'週一至週五[：:]\s*NT\$?\s*([\d,]+)', 'weekday'),
            (r'週末[：:]\s*NT\$?\s*([\d,]+)', 'holiday'),
            # 時段
            (r'全日[：:]\s*NT\$?\s*([\d,]+)', 'full_day'),
            (r'半天[：:]\s*NT\$?\s*([\d,]+)', 'half_day'),
            (r'半日[：:]\s*NT\$?\s*([\d,]+)', 'half_day'),
            (r'小時[：:]\s*NT\$?\s*([\d,]+)', 'hourly'),
            # 飯店特有
            (r'時數租借[：:]\s*NT\$?\s*([\d,]+)', 'hourly'),
            (r'套餐[：:]\s*NT\$?\s*([\d,]+)', 'package'),
            # 宴會特有
            (r'每桌[：:]\s*NT\$?\s*([\d,]+)', 'per_table'),
            (r'每桌\$?\s*([\d,]+)\s*元', 'per_table'),
            (r'自助餐[：:]\s*NT\$?\s*([\d,]+)', 'buffet'),
        ]

        for pattern, key in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                try:
                    price_value = int(matches[0].replace(',', ''))
                    price_data['extractedPrices'][key] = price_value
                    price_data['priceInHTML'] = True
                    price_data['hasPriceInfo'] = True
                except ValueError:
                    continue

        # 尋找價格/會議頁面連結
        price_page_links = soup.find_all('a', href=True)
        for link in price_page_links:
            href = link['href']
            text = link.get_text().lower()
            combined = (text + ' ' + href).lower()

            if any(kw in combined for kw in [
                '價格', '收費', '報價', 'rate', 'price', '會議價',
                '宴會價', '婚宴價', '餐飲價'
            ]):
                full_url = urljoin(base_url, href)
                if full_url not in price_data['pricePages']:
                    price_data['pricePages'].append(full_url)

        return price_data

    def extract_rooms_from_page(self, soup, base_url, venue_id):
        """從頁面提取會議室資訊"""
        rooms = []

        # 飯店/婚宴常見的會議室結構
        room_patterns = [
            # 表格結構
            soup.find_all('table'),
            # 卡片結構
            soup.find_all(['div', 'section'], class_=re.compile(r'room|meeting|banquet', re.I)),
            # 列表結構
            soup.find_all(['li', 'div'], class_=re.compile(r'item|card|entry', re.I)),
        ]

        for pattern in room_patterns:
            if not pattern:
                continue

            for element in pattern[:20]:  # 限制數量
                room_data = self._extract_single_room(element, base_url, venue_id, len(rooms))
                if room_data and room_data.get('name'):
                    rooms.append(room_data)

        return rooms

    def _extract_single_room(self, element, base_url, venue_id, index):
        """提取單個會議室資訊"""
        text_content = element.get_text()

        room = {
            'id': f'r{venue_id}{index:03d}',
            'name': self._extract_room_name(element, text_content),
            'capacity': self._extract_capacity(text_content),
            'area': self._extract_area(text_content),
            'equipment': self._extract_equipment(text_content),
            'price': self._extract_room_price(text_content),
            'images': self._extract_images(element, base_url)
        }

        return room if room.get('name') else None

    def _extract_room_name(self, element, text):
        """提取會議室名稱"""
        # 從標題提取
        for tag in ['h1', 'h2', 'h3', 'h4', 'strong', 'b', 'th']:
            elem = element.find(tag)
            if elem:
                name = elem.get_text().strip()
                name = re.sub(r'\s+', ' ', name)
                if len(name) > 2 and len(name) < 100:
                    return name[:50]

        # 從文本第一行提取
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if 3 < len(line) < 50:
                # 可能是會議室名稱
                if any(kw in line for kw in ['廳', '室', 'Room', 'Hall', '場']):
                    return line

        return None

    def _extract_capacity(self, text):
        """提取容量（支援多種配置）"""
        capacity = {}

        # 多種配置模式
        layout_patterns = {
            'theater': [
                r'劇場[式型][：:]\s*(\d+)\s*人',
                r'theater[：:]\s*(\d+)',
                r'劇院式[：:]\s*(\d+)\s*人'
            ],
            'classroom': [
                r'教室[式型][：:]\s*(\d+)\s*人',
                r'classroom[：:]\s*(\d+)',
                r'課桌式[：:]\s*(\d+)\s*人'
            ],
            'banquet': [
                r'宴會[式型][：:]\s*(\d+)\s*人',
                r'banquet[：:]\s*(\d+)',
                r'圍桌式[：:]\s*(\d+)\s*人'
            ],
            'discussion': [
                r'討論[式型][：:]\s*(\d+)\s*人',
                r'discussion[：:]\s*(\d+)'
            ],
            'u-shape': [
                r'U型[：:]\s*(\d+)\s*人',
                r'u-shape[：:]\s*(\d+)'
            ]
        }

        for layout, patterns in layout_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        capacity[layout] = int(match.group(1))
                        break
                    except ValueError:
                        continue

        # 如果沒有找到特定配置，提取通用容量
        if not capacity:
            generic_patterns = [
                r'容納[：:]\s*(\d+)\s*人',
                r'可容納\s*(\d+)\s*人',
                r'容量[：:]\s*(\d+)\s*人',
                r'(\d{2,4})\s*[人名]',
                r'max[：:]\s*(\d+)',
            ]

            for pattern in generic_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        cap_value = int(match.group(1))
                        if 10 <= cap_value <= 5000:
                            capacity['theater'] = cap_value
                            break
                    except ValueError:
                        continue

        return capacity if capacity else None

    def _extract_area(self, text):
        """提取面積"""
        area_patterns = [
            r'(\d+\.?\d*)\s*坪',
            r'(\d+\.?\d*)\s*平方公尺',
            r'(\d+\.?\d*)\s*㎡',
            r'(\d+\.?\d*)\s*m²',
            r'(\d+\.?\d*)\s*sqm',
        ]

        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return None

    def _extract_equipment(self, text):
        """提取設備清單"""
        equipment_keywords = {
            '投影機': ['投影機', '投影', '投影幕', 'projector'],
            '音響設備': ['音響', 'sound', '揚聲器'],
            '麥克風': ['麥克風', 'microphone', 'mic'],
            '螢幕': ['螢幕', '屏幕', 'screen'],
            '白板': ['白板', 'whiteboard'],
            '無線網路': ['無線網路', 'WiFi', 'Wi-Fi', 'wifi'],
            '視訊會議': ['視訊會議', 'video conference', 'zoom'],
            '錄影設備': ['錄影', '錄音', 'recording'],
        }

        found_equipment = []
        for equipment, keywords in equipment_keywords.items():
            if any(kw.lower() in text.lower() for kw in keywords):
                found_equipment.append(equipment)

        return found_equipment if found_equipment else None

    def _extract_room_price(self, text):
        """提取會議室價格"""
        price = {}

        price_patterns = [
            (r'平日[：:]\s*NT\$?\s*([\d,]+)', 'weekday'),
            (r'假日[：:]\s*NT\$?\s*([\d,]+)', 'holiday'),
            (r'全日[：:]\s*NT\$?\s*([\d,]+)', 'full_day'),
            (r'半日[：:]\s*NT\$?\s*([\d,]+)', 'half_day'),
            (r'每小時[：:]\s*NT\$?\s*([\d,]+)', 'hourly'),
        ]

        for pattern, key in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    price_value = int(match.group(1).replace(',', ''))
                    price[key] = price_value
                except ValueError:
                    continue

        return price if price else None

    def _extract_images(self, element, base_url):
        """提取圖片"""
        images = []

        imgs = element.find_all('img')
        for img in imgs[:3]:  # 最多 3 張
            src = img.get('src', '')
            if src:
                full_url = urljoin(base_url, src)
                images.append(full_url)

        return images if images else None

    def process_venue(self, venue):
        """處理單一場地"""
        venue_id = venue.get('id')
        venue_url = venue.get('url')

        if not venue_url:
            return {
                'success': False,
                'id': venue_id,
                'error': 'No URL'
            }

        try:
            # 計算當前品質
            current_quality = self.calculate_venue_quality(venue)

            # 獲取頁面
            response = self.session.get(venue_url, timeout=15, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取價格資訊
            price_data = self.extract_price_from_html(soup, venue_url)

            # 提取會議室資訊
            extracted_rooms = self.extract_rooms_from_page(soup, venue_url, venue_id)

            # 與現有會議室合併
            existing_rooms = venue.get('rooms', [])

            # 去重並合併
            enhanced_rooms = existing_rooms.copy()

            # 添加新提取的會議室
            for new_room in extracted_rooms:
                # 檢查是否已存在
                exists = False
                for existing_room in enhanced_rooms:
                    if existing_room.get('name') == new_room.get('name'):
                        exists = True
                        # 更新缺失的資料
                        for key, value in new_room.items():
                            if value and not existing_room.get(key):
                                existing_room[key] = value
                        break

                if not exists:
                    enhanced_rooms.append(new_room)

            # 計算新品質
            test_venue = venue.copy()
            test_venue['rooms'] = enhanced_rooms
            new_quality = self.calculate_venue_quality(test_venue)

            return {
                'success': True,
                'id': venue_id,
                'currentQuality': current_quality,
                'newQuality': new_quality,
                'qualityImprovement': new_quality - current_quality,
                'rooms': enhanced_rooms,
                'roomsCount': len(enhanced_rooms),
                'priceData': price_data,
                'newRoomsFound': len(extracted_rooms)
            }

        except Exception as e:
            return {
                'success': False,
                'id': venue_id,
                'error': str(e)
            }


def main():
    """主程式"""
    print('='*70)
    print('Phase 3: 飯店+婚宴場地品質提升')
    print('='*70)

    # 載入場地
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 篩選飯店+婚宴場地
    target_venues = []
    for v in venues:
        if v.get('city') == '台北市' and v.get('status') != 'discontinued':
            venue_type = v.get('venueType', '')
            if any(kw in venue_type for kw in ['飯店', '酒店', 'Hotel']):
                target_venues.append(v)
            elif any(kw in venue_type for kw in ['婚宴', '宴會']):
                target_venues.append(v)

    print(f'\n找到 {len(target_venues)} 個台北市飯店+婚宴場地')
    print()

    # 執行品質提升
    booster = HotelBanquetBooster()

    results = []
    total_improvement = 0

    for i, venue in enumerate(target_venues, 1):
        venue_id = venue['id']
        venue_name = venue.get('name', 'Unknown')
        venue_type = venue.get('venueType', '')

        print(f'[{i}/{len(target_venues)}] [{venue_id:4d}] {venue_name[:35]}... ({venue_type})')

        result = booster.process_venue(venue)
        results.append(result)

        if result['success']:
            improvement = result['qualityImprovement']
            total_improvement += improvement

            status = '✓' if improvement > 0 else '→'
            print(f'  {status} 品質: {result["currentQuality"]} → {result["newQuality"]} (+{improvement})')
            print(f'     會議室: {result["roomsCount"]} 個 (+{result["newRoomsFound"]})')

            if result['priceData']['hasPriceInfo']:
                if result['priceData']['priceInHTML']:
                    print(f'     💰 HTML 價格: {len(result["priceData"]["extractedPrices"])} 項')
                if result['priceData']['hasPDF']:
                    print(f'     📄 PDF: {len(result["priceData"]["pdfUrls"])} 個')
                if result['priceData']['pricePages']:
                    print(f'     🔗 價格頁: {len(result["priceData"]["pricePages"])} 個')
        else:
            print(f'  ✗ 錯誤: {result.get("error", "Unknown")}')

        print()

    # 摘要
    print('='*70)
    print('摘要')
    print('='*70)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f'處理場地: {len(results)}')
    print(f'成功: {len(successful)}')
    print(f'失敗: {len(failed)}')

    if successful:
        avg_improvement = total_improvement / len(successful)
        print(f'\n平均品質提升: +{avg_improvement:.1f} 分')

        # 品質分數分布
        current_scores = [r['currentQuality'] for r in successful]
        new_scores = [r['newQuality'] for r in successful]

        print(f'\n品質分數分布:')
        print(f'  處理前 - 最低: {min(current_scores)}, 最高: {max(current_scores)}, 平均: {sum(current_scores)/len(current_scores):.1f}')
        print(f'  處理後 - 最低: {min(new_scores)}, 最高: {max(new_scores)}, 平均: {sum(new_scores)/len(new_scores):.1f}')

        # 價格資訊統計
        venues_with_price = sum(1 for r in successful if r['priceData']['hasPriceInfo'])
        venues_with_html_price = sum(1 for r in successful if r['priceData']['priceInHTML'])
        venues_with_pdf = sum(1 for r in successful if r['priceData']['hasPDF'])

        print(f'\n價格資訊:')
        print(f'  有價格資訊: {venues_with_price}/{len(successful)} ({venues_with_price/len(successful)*100:.1f}%)')
        print(f'  HTML 價格: {venues_with_html_price}/{len(successful)} ({venues_with_html_price/len(successful)*100:.1f}%)')
        print(f'  PDF 價格: {venues_with_pdf}/{len(successful)} ({venues_with_pdf/len(successful)*100:.1f}%)')

        # 會議室統計
        total_rooms = sum(r['roomsCount'] for r in successful)
        new_rooms_found = sum(r['newRoomsFound'] for r in successful)

        print(f'\n會議室:')
        print(f'  總會議室數: {total_rooms}')
        print(f'  新發現會議室: {new_rooms_found}')
        print(f'  平均每個場地: {total_rooms/len(successful):.1f} 個會議室')

    # 儲存結果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'hotel_banquet_enhancement_{timestamp}.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'\n詳細結果已儲存: {output_file}')

    # 生成更新建議
    print('\n' + '='*70)
    print('下一步建議')
    print('='*70)

    if venues_with_pdf > 0:
        print(f'1. 處理 {venues_with_pdf} 個有 PDF 價格表的場地（優先級最高）')
        print('   - 下載 PDF')
        print('   - AI 輔助解析')
        print('   - 人工驗證')

    venues_with_price_pages = sum(1 for r in successful if r['priceData']['pricePages'])
    if venues_with_price_pages > 0:
        print(f'\n2. 深入爬取 {venues_with_price_pages} 個場地的價格頁面')
        print('   - 提取完整價格表')
        print('   - 提取會議室詳細資訊')

    print(f'\n3. 將增強後的資料更新到 venues.json')
    print(f'   - 預期品質分數提升: +{avg_improvement:.1f} 分/場地')
    print(f'   - 預期整體品質: ~{sum(current_scores)/len(current_scores) + avg_improvement:.1f} 分')


if __name__ == '__main__':
    main()
