#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動驗證引擎 v2.0 - 自動比對官網資料並生成差異報告

功能：
1. 自動爬取官網資料
2. 與 venues.json 比對
3. 生成差異報告
4. 自動修正明顯錯誤
5. 支援批次處理

作者：Jobs (Global CTO)
日期：2026-03-24
版本：2.0
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

# Windows UTF-8 相容
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


class AutoVerificationEngine:
    """自動驗證引擎"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.results = []

    def verify_hotel(self, hotel_id: int, venues_data: List[Dict]) -> Dict:
        """
        驗證單一飯店

        Args:
            hotel_id: 飯店 ID
            venues_data: 場地資料列表

        Returns:
            驗證結果字典
        """
        # 找到目標飯店
        hotel = next((v for v in venues_data if v['id'] == hotel_id), None)
        if not hotel:
            return {
                'hotelId': hotel_id,
                'status': 'ERROR',
                'message': f'找不到飯店 ID: {hotel_id}'
            }

        if self.verbose:
            print(f"\n{'='*70}")
            print(f"[{hotel_id}] {hotel['name']}")
            print(f"{'='*70}")

        result = {
            'hotelId': hotel_id,
            'hotelName': hotel['name'],
            'url': hotel.get('url', ''),
            'verifiedAt': datetime.now().isoformat(),
            'rooms': [],
            'summary': {
                'totalRooms': 0,
                'verified': 0,
                'differences': 0,
                'errors': 0
            }
        }

        try:
            # 1. 爬取官網
            if self.verbose:
                print(f"  📡 爬取官網...")

            official_data = self._scrape_official_website(hotel)

            if not official_data:
                result['status'] = 'WARNING'
                result['message'] = '無法爬取官網資料'
                if self.verbose:
                    print(f"  ⚠️  無法爬取官網，跳過驗證")
                return result

            # 2. 比對會議室資料
            rooms = hotel.get('rooms', [])
            result['summary']['totalRooms'] = len(rooms)

            if self.verbose:
                print(f"  📊 比對 {len(rooms)} 個會議室...")

            for room in rooms:
                room_result = self._verify_room(room, official_data)
                result['rooms'].append(room_result)

                # 更新統計
                if room_result['status'] == 'VERIFIED':
                    result['summary']['verified'] += 1
                elif room_result['status'] == 'DIFFERENCE':
                    result['summary']['differences'] += 1
                else:
                    result['summary']['errors'] += 1

            # 3. 決定整體狀態
            if result['summary']['errors'] > 0:
                result['status'] = 'ERROR'
            elif result['summary']['differences'] > 0:
                result['status'] = 'DIFFERENCE'
            else:
                result['status'] = 'VERIFIED'

            if self.verbose:
                print(f"\n  ✅ 驗證完成")
                print(f"     總數: {result['summary']['totalRooms']}")
                print(f"     ✓ 已驗證: {result['summary']['verified']}")
                print(f"     ⚠️  有差異: {result['summary']['differences']}")
                print(f"     ❌ 錯誤: {result['summary']['errors']}")

        except Exception as e:
            result['status'] = 'ERROR'
            result['message'] = str(e)
            if self.verbose:
                print(f"  ❌ 錯誤: {e}")
            import traceback
            traceback.print_exc()

        return result

    def _scrape_official_website(self, hotel: Dict) -> Optional[Dict]:
        """
        爬取官網資料

        根據飯店類型使用不同的爬取策略
        """
        url = hotel.get('url', '')
        if not url:
            return None

        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'

            # 根據飯店 ID 選擇爬取策略
            hotel_id = hotel['id']

            if hotel_id == 1086:  # 晶華酒店
                return self._scrape_regent(response.text, url)
            elif hotel_id == 1085:  # 文華東方
                return self._scrape_mandarin(response.text, url)
            elif hotel_id == 1122:  # 維多麗亞
                return self._scrape_victoria(response.text, url)
            elif hotel_id == 1090:  # 茹曦
                return self._scrape_illumme(response.text, url)
            else:
                return self._scrape_generic(response.text, url)

        except Exception as e:
            if self.verbose:
                print(f"    ❌ 爬取失敗: {e}")
            return None

    def _scrape_regent(self, html: str, url: str) -> Dict:
        """爬取晶華酒店"""
        soup = BeautifulSoup(html, 'html.parser')

        rooms = {}
        tables = soup.find_all('table', class_='table-comparison')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = [cell.get_text(strip=True) for cell in row.find_all('td')]
                if not cells:
                    continue

                row_text = '|'.join(cells)
                room_data = self._parse_regent_row(row_text)
                if room_data:
                    rooms[room_data['name']] = room_data

        return {'rooms': rooms}

    def _parse_regent_row(self, row_text: str) -> Optional[Dict]:
        """解析晶華表格行"""
        parts = [p.strip() for p in row_text.split('|')]

        if len(parts) < 8:
            return None

        venue_name = parts[0].strip()
        if venue_name in ['場地', '功能空間']:
            return None

        # 解析尺寸：776 / 8508 (sqm / sqft)
        size_text = parts[1]
        match = re.match(r'(\d+(?:\.\d+)?)\s*/\s*(\d+)', size_text)
        if not match:
            return None

        sqm = float(match.group(1))
        capacity = self._safe_int(parts[5])  # 劇院式

        return {
            'name': venue_name,
            'sqm': sqm,
            'capacity': capacity
        }

    def _scrape_mandarin(self, html: str, url: str) -> Dict:
        """爬取文華東方"""
        # 文華東方使用 JSON-LD 或特定 HTML 結構
        soup = BeautifulSoup(html, 'html.parser')

        rooms = {}

        # 嘗試從 JSON-LD 提取
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # 解析 JSON-LD 資料
            except:
                pass

        return {'rooms': rooms}

    def _scrape_victoria(self, html: str, url: str) -> Dict:
        """爬取維多麗亞"""
        soup = BeautifulSoup(html, 'html.parser')
        rooms = {}

        # 查找宴會廳資訊
        venue_cards = soup.find_all('div', class_=re.compile(r'venue|ballroom', re.I))

        for card in venue_cards:
            name_elem = card.find(['h2', 'h3', 'h4'])
            if name_elem:
                room_name = name_elem.get_text(strip=True)
                rooms[room_name] = {'name': room_name}

        return {'rooms': rooms}

    def _scrape_illumme(self, html: str, url: str) -> Dict:
        """爬取茹曦酒店"""
        soup = BeautifulSoup(html, 'html.parser')
        rooms = {}

        # 茹曦使用 WordPress 架構
        venue_sections = soup.find_all('section', class_=re.compile(r'venue|meeting', re.I))

        for section in venue_sections:
            name_elem = section.find(['h2', 'h3'])
            if name_elem:
                room_name = name_elem.get_text(strip=True)
                rooms[room_name] = {'name': room_name}

        return {'rooms': rooms}

    def _scrape_generic(self, html: str, url: str) -> Dict:
        """通用爬取策略"""
        soup = BeautifulSoup(html, 'html.parser')
        rooms = {}

        # 嘗試多種常見的結構
        selectors = [
            'div[class*="room"]',
            'div[class*="venue"]',
            'div[class*="meeting"]',
            'section[class*="banquet"]'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                name_elem = elem.find(['h1', 'h2', 'h3', 'h4'])
                if name_elem:
                    room_name = name_elem.get_text(strip=True)
                    if room_name and len(room_name) > 2:
                        rooms[room_name] = {'name': room_name}

        return {'rooms': rooms}

    def _verify_room(self, room: Dict, official_data: Dict) -> Dict:
        """
        驗證單一會議室

        比對項目：
        1. 場地名稱
        2. 面積 (sqm)
        3. 容納人數 (capacity.theater)
        """
        result = {
            'roomId': room.get('id'),
            'roomName': room.get('name'),
            'status': 'UNKNOWN',
            'differences': [],
            'corrections': {}
        }

        official_rooms = official_data.get('rooms', {})

        # 尋找對應的官網場地
        official_room = None
        room_name = room.get('name', '')

        # 精確匹配
        if room_name in official_rooms:
            official_room = official_rooms[room_name]
        else:
            # 模糊匹配
            for official_name, official_data in official_rooms.items():
                if room_name in official_name or official_name in room_name:
                    official_room = official_data
                    break

        if not official_room:
            result['status'] = 'NOT_FOUND'
            result['differences'].append('官網找不到對應場地')
            return result

        # 比對面積
        if 'sqm' in official_room and room.get('sqm'):
            room_sqm = room['sqm']
            official_sqm = official_room['sqm']

            if abs(room_sqm - official_sqm) > 5:  # 允許 5 平方公尺誤差
                result['differences'].append({
                    'field': 'sqm',
                    'current': room_sqm,
                    'official': official_sqm,
                    'message': f'面積不一致：{room_sqm} vs {official_sqm} sqm'
                })

                # 自動修正明顯錯誤（如單位混淆）
                if self._should_auto_correct_sqm(room_sqm, official_sqm):
                    result['corrections']['sqm'] = official_sqm
                    result['autoCorrected'] = True

        # 比對容量
        if 'capacity' in official_room and room.get('capacity'):
            room_capacity = room['capacity'].get('theater')
            official_capacity = official_room['capacity']

            if room_capacity and official_capacity:
                if abs(room_capacity - official_capacity) > 10:  # 允許 10 人誤差
                    result['differences'].append({
                        'field': 'capacity',
                        'current': room_capacity,
                        'official': official_capacity,
                        'message': f'容量不一致：{room_capacity} vs {official_capacity} 人'
                    })

                    result['corrections']['capacity.theater'] = official_capacity

        # 決定狀態
        if len(result['differences']) == 0:
            result['status'] = 'VERIFIED'
        elif result.get('autoCorrected'):
            result['status'] = 'AUTO_CORRECTED'
        else:
            result['status'] = 'DIFFERENCE'

        return result

    def _should_auto_correct_sqm(self, current: float, official: float) -> bool:
        """判斷是否應該自動修正面積"""

        # 檢測單位混淆：如果 current 比 official 大 10 倍以上
        if current > official * 10:
            return True

        # 檢測坪數混淆：1 坪 ≈ 3.3 平方公尺
        if abs(current - official * 3.3058) < 1:
            return True

        return False

    def _safe_int(self, s):
        """安全轉換為整數"""
        if not s or s == '-':
            return None
        try:
            return int(re.sub(r'[^\d]', '', str(s)))
        except:
            return None

    def batch_verify(self, hotel_ids: List[int], venues_file: str = 'venues.json',
                    max_workers: int = 3) -> Dict:
        """
        批次驗證多個飯店

        Args:
            hotel_ids: 飯店 ID 列表
            venues_file: venues.json 路徑
            max_workers: 最大並行數

        Returns:
            批次驗證結果
        """
        # 讀取場地資料
        with open(venues_file, 'r', encoding='utf-8') as f:
            venues_data = json.load(f)

        print(f"\n{'='*70}")
        print(f"批次驗證 {len(hotel_ids)} 個飯店")
        print(f"{'='*70}\n")

        results = []

        # 使用執行緒池並行處理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_hotel = {
                executor.submit(self.verify_hotel, hotel_id, venues_data): hotel_id
                for hotel_id in hotel_ids
            }

            for future in as_completed(future_to_hotel):
                hotel_id = future_to_hotel[future]
                try:
                    result = future.result()
                    results.append(result)

                    # 顯示進度
                    status_icon = {
                        'VERIFIED': '✅',
                        'DIFFERENCE': '⚠️',
                        'ERROR': '❌',
                        'WARNING': '⚠️'
                    }.get(result['status'], '❓')

                    print(f"{status_icon} [{result['hotelId']}] {result['hotelName']}")

                except Exception as e:
                    print(f"❌ [{hotel_id}] 錯誤: {e}")

        # 統計結果
        stats = {
            'total': len(results),
            'verified': sum(1 for r in results if r['status'] == 'VERIFIED'),
            'difference': sum(1 for r in results if r['status'] == 'DIFFERENCE'),
            'error': sum(1 for r in results if r['status'] == 'ERROR'),
            'warning': sum(1 for r in results if r['status'] == 'WARNING')
        }

        print(f"\n{'='*70}")
        print(f"批次驗證完成")
        print(f"{'='*70}")
        print(f"總計: {stats['total']}")
        print(f"✅ 已驗證: {stats['verified']}")
        print(f"⚠️  有差異: {stats['difference']}")
        print(f"❌ 錯誤: {stats['error']}")
        print(f"⚠️  警告: {stats['warning']}")

        return {
            'results': results,
            'stats': stats,
            'verifiedAt': datetime.now().isoformat()
        }

    def apply_corrections(self, verification_result: Dict, venues_file: str = 'venues.json'):
        """
        應用自動修正

        Args:
            verification_result: 驗證結果
            venues_file: venues.json 路徑
        """
        # 讀取場地資料
        with open(venues_file, 'r', encoding='utf-8') as f:
            venues_data = json.load(f)

        # 找到目標飯店
        hotel = next(
            (v for v in venues_data if v['id'] == verification_result['hotelId']),
            None
        )

        if not hotel:
            print(f"❌ 找不到飯店 ID: {verification_result['hotelId']}")
            return

        corrections_count = 0

        # 應用修正
        for room_result in verification_result.get('rooms', []):
            if room_result.get('autoCorrected') and room_result.get('corrections'):
                room_id = room_result['roomId']
                corrections = room_result['corrections']

                # 找到對應的會議室
                room = next((r for r in hotel['rooms'] if r['id'] == room_id), None)
                if not room:
                    continue

                # 應用修正
                for field, value in corrections.items():
                    if field == 'sqm':
                        old_value = room.get('sqm')
                        room['sqm'] = value
                        print(f"  ✓ {room['name']}: sqm {old_value} → {value}")
                        corrections_count += 1

                    elif field.startswith('capacity.'):
                        capacity_field = field.split('.')[1]
                        old_value = room['capacity'].get(capacity_field)
                        room['capacity'][capacity_field] = value
                        print(f"  ✓ {room['name']}: capacity.{capacity_field} {old_value} → {value}")
                        corrections_count += 1

        if corrections_count > 0:
            # 備份
            import shutil
            backup = f'venues.json.backup.auto_corrected_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            shutil.copy(venues_file, backup)

            # 儲存
            with open(venues_file, 'w', encoding='utf-8') as f:
                json.dump(venues_data, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 已應用 {corrections_count} 項修正")
            print(f"📄 備份: {backup}")
        else:
            print(f"\nℹ️  無需修正的項目")


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(
        description='自動驗證引擎 - 自動比對官網資料',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 驗證單一飯店
  python auto_verification_engine.py --hotel 1086

  # 批次驗證多個飯店
  python auto_verification_engine.py --batch 1086,1085,1122

  # 驗證並自動修正
  python auto_verification_engine.py --hotel 1086 --auto-correct

  # 生成報告
  python auto_verification_engine.py --batch 1086,1085 --report verification_report.json
        """
    )

    parser.add_argument(
        '--hotel',
        type=int,
        help='驗證單一飯店 ID'
    )

    parser.add_argument(
        '--batch',
        type=str,
        help='批次驗證多個飯店 ID（逗號分隔）'
    )

    parser.add_argument(
        '--auto-correct',
        action='store_true',
        help='自動應用修正'
    )

    parser.add_argument(
        '--report',
        type=str,
        help='生成 JSON 報告檔案'
    )

    parser.add_argument(
        '--venues',
        type=str,
        default='venues.json',
        help='venues.json 路徑（預設：venues.json）'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='安靜模式'
    )

    args = parser.parse_args()

    engine = AutoVerificationEngine(verbose=not args.quiet)

    # 執行驗證
    if args.hotel:
        # 單一飯店
        with open(args.venues, 'r', encoding='utf-8') as f:
            venues_data = json.load(f)

        result = engine.verify_hotel(args.hotel, venues_data)

        # 自動修正
        if args.auto_correct and result.get('status') in ['DIFFERENCE', 'AUTO_CORRECTED']:
            print("\n🔧 應用自動修正...")
            engine.apply_corrections(result, args.venues)

        # 生成報告
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n📄 報告已保存: {args.report}")

    elif args.batch:
        # 批次驗證
        hotel_ids = [int(id.strip()) for id in args.batch.split(',')]
        result = engine.batch_verify(hotel_ids, args.venues)

        # 生成報告
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n📄 報告已保存: {args.report}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
