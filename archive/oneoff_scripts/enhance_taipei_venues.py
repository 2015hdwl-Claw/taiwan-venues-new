#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北市場地資料補強爬蟲

目標：重新爬取資料缺失的場地
追蹤：記錄成功/失敗及原因
"""
import sys
import io
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import traceback

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class VenueEnhancer:
    """場地資料補強工具"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.results = []

    def get_venues_needing_enhancement(self, venues_file='venues.json'):
        """獲取需要補強的場地列表"""
        with open(venues_file, 'r', encoding='utf-8') as f:
            venues = json.load(f)

        # 找出台北市資料缺失的場地
        needs_enhancement = []

        for venue in venues:
            if venue.get('city') != '台北市':
                continue

            if venue.get('status') == 'discontinued':
                continue

            # 檢查會議室資料完整性
            rooms = venue.get('rooms', [])

            if not rooms:
                continue

            # 檢查是否有空的會議室資料
            has_empty_data = False
            for room in rooms:
                if not room.get('capacity') and not room.get('area') and not room.get('price'):
                    has_empty_data = True
                    break

            if has_empty_data:
                needs_enhancement.append(venue)

        return needs_enhancement

    def extract_room_details(self, venue_url, room_name):
        """深入爬取會議室詳情頁"""
        try:
            response = self.session.get(venue_url, timeout=15, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 尋找會議室連結或區塊
            room_data = {
                'capacity': None,
                'area': None,
                'price': None,
                'equipment': None,
                'images': None
            }

            # 從整個頁面文字中提取資料
            page_text = soup.get_text()

            # 提取容量
            import re
            capacity_patterns = [
                r'容量[：:]\s*(\d+)\s*人',
                r'可容納\s*(\d+)\s*人',
                r'(\d{2,4})\s*[人名]',
            ]
            for pattern in capacity_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room_data['capacity'] = int(match.group(1))
                        break
                    except ValueError:
                        continue

            # 提取面積
            area_patterns = [
                r'(\d+\.?\d*)\s*坪',
                r'(\d+\.?\d*)\s*平方公尺',
                r'(\d+\.?\d*)\s*㎡',
            ]
            for pattern in area_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room_data['area'] = float(match.group(1))
                        break
                    except ValueError:
                        continue

            # 提取價格
            price_patterns = [
                r'NT\$?\s*([\d,]+)\s*元',
                r'價格[：:]\s*NT\$?\s*([\d,]+)',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room_data['price'] = int(match.group(1).replace(',', ''))
                        break
                    except ValueError:
                        continue

            # 提取設備
            equipment_keywords = ['投影機', '音響', '麥克風', '螢幕', '白板']
            found_equipment = []
            for keyword in equipment_keywords:
                if keyword in page_text:
                    found_equipment.append(keyword)
            if found_equipment:
                room_data['equipment'] = ', '.join(found_equipment)

            return {
                'success': True,
                'room_name': room_name,
                'data': room_data
            }

        except Exception as e:
            return {
                'success': False,
                'room_name': room_name,
                'error': str(e)
            }

    def enhance_venue(self, venue):
        """補強單一場地的資料"""
        venue_id = venue.get('id')
        venue_name = venue.get('name')
        venue_url = venue.get('url')

        print(f'\n[{venue_id}] {venue_name[:40]}')
        print(f'URL: {venue_url}')

        if not venue_url:
            return {
                'success': False,
                'id': venue_id,
                'name': venue_name,
                'error': 'No URL',
                'reason': '缺少官網URL'
            }

        try:
            # 嘗試訪問官網
            response = self.session.get(venue_url, timeout=15, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 檢查頁面內容
            page_text = soup.get_text()
            content_length = len(page_text)

            if content_length < 1000:
                return {
                    'success': False,
                    'id': venue_id,
                    'name': venue_name,
                    'error': '頁面內容過少',
                    'reason': '可能是登入頁、重定向或404'
                }

            # 嘗試補強會議室資料
            rooms = venue.get('rooms', [])
            enhanced_rooms = []
            success_count = 0

            for room in rooms[:5]:  # 限制處理前5個會議室
                room_name = room.get('name', '')
                if not room_name:
                    continue

                result = self.extract_room_details(venue_url, room_name)

                if result['success']:
                    # 合併原有資料和新資料
                    enhanced_room = room.copy()
                    enhanced_room.update(result['data'])
                    enhanced_rooms.append(enhanced_room)
                    success_count += 1
                else:
                    enhanced_rooms.append(room)

            return {
                'success': True,
                'id': venue_id,
                'name': venue_name,
                'rooms_processed': len(rooms),
                'rooms_enhanced': success_count,
                'enhanced_data': enhanced_rooms,
                'page_content_length': content_length
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'id': venue_id,
                'name': venue_name,
                'error': 'Timeout',
                'reason': '連線超時（可能官網回應慢）'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'id': venue_id,
                'name': venue_name,
                'error': 'Connection Error',
                'reason': '無法連線（官網可能不存在或防火牆阻擋）'
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'id': venue_id,
                'name': venue_name,
                'error': f'HTTP {e.response.status_code}',
                'reason': f'HTTP錯誤（{e.response.status_code}）'
            }
        except Exception as e:
            return {
                'success': False,
                'id': venue_id,
                'name': venue_name,
                'error': str(e),
                'reason': '未知錯誤',
                'traceback': traceback.format_exc()
            }

    def run_enhancement(self, limit=10):
        """執行補強"""
        print('='*70)
        print('台北市場地資料補強爬蟲')
        print('='*70)

        # 獲取需要補強的場地
        venues = self.get_venues_needing_enhancement()

        print(f'\n找到 {len(venues)} 個需要補強的場地')
        print(f'本次處理: {min(limit, len(venues))} 個場地\n')

        # 處理場地
        target_venues = venues[:limit]

        for i, venue in enumerate(target_venues, 1):
            print(f'\n[{i}/{len(target_venues)}] 處理中...')

            result = self.enhance_venue(venue)
            self.results.append(result)

            if result['success']:
                print(f'  ✓ 成功')
                print(f'    處理會議室: {result["rooms_processed"]} 個')
                print(f'    補強成功: {result["rooms_enhanced"]} 個')
                print(f'    頁面內容: {result["page_content_length"]} 字元')
            else:
                print(f'  ✗ 失敗: {result["error"]}')
                print(f'    原因: {result["reason"]}')

        # 生成報告
        self.generate_report()

    def generate_report(self):
        """生成執行報告"""
        print('\n' + '='*70)
        print('執行報告')
        print('='*70)

        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]

        print(f'\n總處理: {len(self.results)} 個場地')
        print(f'成功: {len(successful)} 個')
        print(f'失敗: {len(failed)} 個')
        print(f'成功率: {len(successful)/len(self.results)*100:.1f}%')

        if failed:
            print(f'\n失敗場地詳情:')
            for result in failed:
                print(f'  [{result["id"]}] {result["name"][:40]}')
                print(f'    錯誤: {result["error"]}')
                print(f'    原因: {result["reason"]}')

        # 失敗原因統計
        failure_reasons = {}
        for result in failed:
            reason = result['reason']
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        if failure_reasons:
            print(f'\n失敗原因統計:')
            for reason, count in sorted(failure_reasons.items(), key=lambda x: -x[1]):
                print(f'  {reason}: {count} 個')

        # 儲存結果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'enhancement_results_{timestamp}.json'

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f'\n詳細結果已儲存: {output_file}')


def main():
    enhancer = VenueEnhancer()

    # 執行補強（先處理10個場地測試）
    enhancer.run_enhancement(limit=10)


if __name__ == '__main__':
    main()
