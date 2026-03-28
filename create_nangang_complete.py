#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立南港展覽館完整會議室資料結構
根據官方收費基準 PDF (2021)
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def create_complete_room_structure():
    """建立完整 30 欄位會議室資料結構"""
    return {
        # 基本資料
        'id': None,
        'name': None,
        'nameEn': None,
        'floor': None,
        # 面積資料
        'area': None,
        'areaUnit': None,
        'areaSqm': None,
        'areaPing': None,
        # 尺寸
        'dimensions': {'length': None, 'width': None, 'height': None},
        # 容量資料
        'capacity': {
            'theater': None,
            'banquet': None,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        # 價格資料
        'price': {
            'weekday': None,
            'holiday': None,
            'morning': None,
            'afternoon': None,
            'evening': None,
            'fullDay': None,
            'hourly': None,
            'note': None
        },
        # 設備資料
        'equipment': None,
        'equipmentList': [],
        # 其他
        'features': None,
        'source': None,
        'lastUpdated': None
    }


def parse_dimensions(dim_str):
    """解析尺寸字串 '9.6 x 8.7 x 3.9' -> {'length': 9.6, 'width': 8.7, 'height': 3.9}"""
    if not dim_str:
        return {'length': None, 'width': None, 'height': None}

    try:
        # 清理字串
        dim_str = str(dim_str).replace('x', ' ').replace('×', ' ').strip()
        parts = dim_str.split()

        if len(parts) >= 2:
            length = float(parts[0]) if parts[0].replace('.', '').isdigit() else None
            width = float(parts[1]) if len(parts) > 1 and parts[1].replace('.', '').isdigit() else None
            height = float(parts[2]) if len(parts) > 2 and parts[2].replace('.', '').isdigit() else None
            return {'length': length, 'width': width, 'height': height}
        return {'length': None, 'width': None, 'height': None}
    except:
        return {'length': None, 'width': None, 'height': None}


def parse_price(price_str):
    """解析價格字串 '13,800' -> 13800"""
    if not price_str:
        return None
    try:
        return int(str(price_str).replace(',', '').replace('$', '').strip())
    except:
        return None


def main():
    print('=' * 80)
    print('建立南港展覽館完整會議室資料結構')
    print('=' * 80)
    print()

    # PDF 提取的完整資料（根據實際解析結果）
    rooms_data = [
        # 3樓
        {
            'name': '福軒',
            'nameEn': 'Fu Xuan',
            'floor': '3樓',
            'sqm': 83.5,
            'ping': 25.3,
            'dimensions': '9.6 x 8.7 x 3.9',
            'theater': 60, 'classroom': 32, 'banquet': 48, 'uShape': 20, 'cocktail': 28,
            'price_day': 13800, 'price_night': 16600
        },
        # 4樓
        {
            'name': '401會議室',
            'nameEn': 'Meeting Room 401',
            'floor': '4樓',
            'sqm': 375.7,
            'ping': 113.7,
            'dimensions': '20.2 x 18.6 x 3.5',
            'theater': 384, 'classroom': 144, 'banquet': 216, 'uShape': 52, 'cocktail': 72,
            'price_day': 39900, 'price_night': 47900
        },
        {
            'name': '402會議室',
            'nameEn': 'Meeting Room 402',
            'floor': '4樓',
            'sqm': 372.6,
            'ping': 112.7,
            'dimensions': '27.0 x 13.8 x 3.5',
            'theater': 396, 'classroom': 168, 'banquet': 224, 'uShape': 62, 'cocktail': 80,
            'price_day': 39400, 'price_night': 47300
        },
        {
            'name': '402a會議室',
            'nameEn': 'Meeting Room 402a',
            'floor': '4樓',
            'sqm': 121.4,
            'ping': 36.7,
            'dimensions': '8.8 x 13.8 x 3.5',
            'theater': 100, 'classroom': 56, 'banquet': 72, 'uShape': 26, 'cocktail': 36,
            'price_day': 12900, 'price_night': 15500
        },
        {
            'name': '402b會議室',
            'nameEn': 'Meeting Room 402b',
            'floor': '4樓',
            'sqm': 122.8,
            'ping': 37.1,
            'dimensions': '8.9 x 13.8 x 3.5',
            'theater': 110, 'classroom': 56, 'banquet': 72, 'uShape': 26, 'cocktail': 36,
            'price_day': 12900, 'price_night': 15500
        },
        {
            'name': '402c會議室',
            'nameEn': 'Meeting Room 402c',
            'floor': '4樓',
            'sqm': 128.3,
            'ping': 38.8,
            'dimensions': '9.3 x 13.8 x 3.5',
            'theater': 110, 'classroom': 56, 'banquet': 72, 'uShape': 26, 'cocktail': 36,
            'price_day': 13600, 'price_night': 16300
        },
        {
            'name': '402a+b會議室',
            'nameEn': 'Meeting Room 402a+b',
            'floor': '4樓',
            'sqm': 244.3,
            'ping': 73.9,
            'dimensions': '17.7 x 13.8 x 3.5',
            'theater': 234, 'classroom': 108, 'banquet': 144, 'uShape': 42, 'cocktail': 56,
            'price_day': 25800, 'price_night': 31000
        },
        {
            'name': '402b+c會議室',
            'nameEn': 'Meeting Room 402b+c',
            'floor': '4樓',
            'sqm': 251.2,
            'ping': 76.0,
            'dimensions': '18.2 x 13.8 x 3.5',
            'theater': 234, 'classroom': 108, 'banquet': 144, 'uShape': 42, 'cocktail': 56,
            'price_day': 26500, 'price_night': 31800
        },
        {
            'name': '403會議室',
            'nameEn': 'Meeting Room 403',
            'floor': '4樓',
            'sqm': 149.5,
            'ping': 45.2,
            'dimensions': '8.4 x 17.8 x 3.5',
            'theater': 125, 'classroom': 68, 'banquet': 92, 'uShape': 34, 'cocktail': 44,
            'price_day': 15600, 'price_night': 18700
        },
        {
            'name': '404會議室',
            'nameEn': 'Meeting Room 404',
            'floor': '4樓',
            'sqm': 133.5,
            'ping': 40.4,
            'dimensions': '9.3 x 14.3 x 3.5',
            'theater': 90, 'classroom': 48, 'banquet': 72, 'uShape': 26, 'cocktail': 36,
            'price_day': 14000, 'price_night': 16800
        },
        # 5樓
        {
            'name': '500會議室',
            'nameEn': 'Meeting Room 500',
            'floor': '5樓',
            'sqm': 159.8,
            'ping': 48.3,
            'dimensions': '9.7 x 16.5 x 2.8',
            'theater': 140, 'classroom': 72, 'banquet': 116, 'uShape': 46, 'cocktail': 52,
            'price_day': 16700, 'price_night': 20000
        },
        {
            'name': '501會議室',
            'nameEn': 'Meeting Room 501',
            'floor': '5樓',
            'sqm': 131.1,
            'ping': 39.7,
            'dimensions': '9.3 x 14.1 x 2.8',
            'theater': 105, 'classroom': 56, 'banquet': 84, 'uShape': 30, 'cocktail': 36,
            'price_day': 13800, 'price_night': 16600
        },
        {
            'name': '502會議室',
            'nameEn': 'Meeting Room 502',
            'floor': '5樓',
            'sqm': 102.3,
            'ping': 30.9,
            'dimensions': '7.6 x 13.5 x 2.8',
            'theater': 95, 'classroom': 34, 'banquet': 68, 'uShape': 26, 'cocktail': 32,
            'price_day': 10700, 'price_night': 12800
        },
        {
            'name': '503會議室',
            'nameEn': 'Meeting Room 503',
            'floor': '5樓',
            'sqm': 150.9,
            'ping': 45.7,
            'dimensions': '9.7 x 15.6 x 2.8',
            'theater': 110, 'classroom': 56, 'banquet': 84, 'uShape': 30, 'cocktail': 36,
            'price_day': 15600, 'price_night': 18700
        },
        {
            'name': '504會議室',
            'nameEn': 'Meeting Room 504',
            'floor': '5樓',
            'sqm': 505.4,
            'ping': 152.9,
            'dimensions': '26.6 x 19.0 x 2.8',
            'theater': 504, 'classroom': 224, 'banquet': 360, 'uShape': 68, 'cocktail': 84,
            'price_day': 52700, 'price_night': 63300
        },
        {
            'name': '504a會議室',
            'nameEn': 'Meeting Room 504a',
            'floor': '5樓',
            'sqm': 184.3,
            'ping': 55.8,
            'dimensions': '9.7 x 19.0 x 2.8',
            'theater': 165, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 19300, 'price_night': 23200
        },
        {
            'name': '504b會議室',
            'nameEn': 'Meeting Room 504b',
            'floor': '5樓',
            'sqm': 169.1,
            'ping': 51.2,
            'dimensions': '8.9 x 19.0 x 2.8',
            'theater': 150, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 17600, 'price_night': 21100
        },
        {
            'name': '504c會議室',
            'nameEn': 'Meeting Room 504c',
            'floor': '5樓',
            'sqm': 152.0,
            'ping': 46.0,
            'dimensions': '8.0 x 19.0 x 2.8',
            'theater': 150, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 15800, 'price_night': 19000
        },
        {
            'name': '504a+b會議室',
            'nameEn': 'Meeting Room 504a+b',
            'floor': '5樓',
            'sqm': 353.4,
            'ping': 106.9,
            'dimensions': '18.6 x 19.0 x 2.8',
            'theater': 336, 'classroom': 144, 'banquet': 216, 'uShape': 48, 'cocktail': 64,
            'price_day': 36900, 'price_night': 44300
        },
        {
            'name': '504b+c會議室',
            'nameEn': 'Meeting Room 504b+c',
            'floor': '5樓',
            'sqm': 321.1,
            'ping': 97.1,
            'dimensions': '16.9 x 19.0 x 2.8',
            'theater': 312, 'classroom': 128, 'banquet': 216, 'uShape': 48, 'cocktail': 64,
            'price_day': 33400, 'price_night': 40100
        },
        {
            'name': '505會議室',
            'nameEn': 'Meeting Room 505',
            'floor': '5樓',
            'sqm': 511.1,
            'ping': 154.6,
            'dimensions': '26.9 x 19.0 x 2.7',
            'theater': 504, 'classroom': 224, 'banquet': 360, 'uShape': 68, 'cocktail': 84,
            'price_day': 53300, 'price_night': 64000
        },
        {
            'name': '505a會議室',
            'nameEn': 'Meeting Room 505a',
            'floor': '5樓',
            'sqm': 178.6,
            'ping': 54.0,
            'dimensions': '9.4 x 19.0 x 2.7',
            'theater': 165, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 18600, 'price_night': 22300
        },
        {
            'name': '505b會議室',
            'nameEn': 'Meeting Room 505b',
            'floor': '5樓',
            'sqm': 171.0,
            'ping': 51.7,
            'dimensions': '9.0 x 19.0 x 2.7',
            'theater': 150, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 17800, 'price_night': 21400
        },
        {
            'name': '505c會議室',
            'nameEn': 'Meeting Room 505c',
            'floor': '5樓',
            'sqm': 161.5,
            'ping': 48.9,
            'dimensions': '8.5 x 19.0 x 2.7',
            'theater': 150, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 16900, 'price_night': 20300
        },
        {
            'name': '505a+b會議室',
            'nameEn': 'Meeting Room 505a+b',
            'floor': '5樓',
            'sqm': 349.6,
            'ping': 105.7,
            'dimensions': '18.4 x 19.0 x 2.7',
            'theater': 336, 'classroom': 144, 'banquet': 216, 'uShape': 48, 'cocktail': 64,
            'price_day': 36400, 'price_night': 43700
        },
        {
            'name': '505b+c會議室',
            'nameEn': 'Meeting Room 505b+c',
            'floor': '5樓',
            'sqm': 332.5,
            'ping': 100.6,
            'dimensions': '17.5 x 19.0 x 2.7',
            'theater': 312, 'classroom': 128, 'banquet': 216, 'uShape': 48, 'cocktail': 64,
            'price_day': 34700, 'price_night': 41700
        },
        {
            'name': '506會議室',
            'nameEn': 'Meeting Room 506',
            'floor': '5樓',
            'sqm': 176.7,
            'ping': 53.5,
            'dimensions': '9.3 x 19.0 x 2.7',
            'theater': 165, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 18500, 'price_night': 22200
        },
        {
            'name': '507會議室',
            'nameEn': 'Meeting Room 507',
            'floor': '5樓',
            'sqm': 176.7,
            'ping': 53.5,
            'dimensions': '9.3 x 19.0 x 2.7',
            'theater': 165, 'classroom': 80, 'banquet': 120, 'uShape': 38, 'cocktail': 44,
            'price_day': 18500, 'price_night': 22200
        },
    ]

    complete_rooms = []

    for idx, room_data in enumerate(rooms_data, 1):
        room = create_complete_room_structure()

        room['id'] = f'1500-{idx:02d}'
        room['name'] = room_data['name']
        room['nameEn'] = room_data['nameEn']
        room['floor'] = room_data['floor']

        # 面積
        room['area'] = room_data['sqm']
        room['areaUnit'] = '㎡'
        room['areaSqm'] = room_data['sqm']
        room['areaPing'] = room_data['ping']

        # 尺寸
        room['dimensions'] = parse_dimensions(room_data['dimensions'])

        # 容量
        room['capacity'] = {
            'theater': room_data['theater'],
            'banquet': room_data['banquet'],
            'classroom': room_data['classroom'],
            'uShape': room_data['uShape'],
            'cocktail': room_data['cocktail'],
            'roundTable': None
        }

        # 價格
        room['price'] = {
            'weekday': room_data['price_day'],
            'holiday': room_data['price_night'],  # 夜間/例假日
            'morning': None,
            'afternoon': None,
            'evening': None,
            'fullDay': None,
            'hourly': None,
            'note': '日間: 08:00-12:00/13:00-17:00, 夜間: 18:00-22:00'
        }

        # 設備
        room['equipment'] = '免費提供基本配備：無線麥克風2支、主講桌1座、接待桌1桌、資訊看板1個、海報架(直)2支'
        room['equipmentList'] = [
            '無線麥克風 2支',
            '主講桌 1座',
            '接待桌 1桌',
            '資訊看板 1個',
            '海報架(直) 2支'
        ]

        # 特色
        room['features'] = f"挑高 {room['dimensions']['height']} 公尺" if room['dimensions']['height'] else None

        # 資料來源
        room['source'] = '官方 PDF: 外貿協會台北南港展覽館1館會議室租用收費基準 (2021)'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 顯示結果
    print(f'成功建立 {len(complete_rooms)} 個會議室')
    print()

    # 統計
    total_rooms = len(complete_rooms)
    has_area = sum(1 for r in complete_rooms if r['areaSqm'])
    has_dimensions = sum(1 for r in complete_rooms if r['dimensions']['length'])
    has_theater = sum(1 for r in complete_rooms if r['capacity']['theater'])
    has_price = sum(1 for r in complete_rooms if r['price']['weekday'])

    print('=' * 80)
    print('資料完整性統計')
    print('=' * 80)
    print(f'總會議室: {total_rooms}')
    print(f'面積覆蓋: {has_area}/{total_rooms} (100%)')
    print(f'尺寸覆蓋: {has_dimensions}/{total_rooms} (100%)')
    print(f'容量覆蓋: {has_theater}/{total_rooms} (100%)')
    print(f'價格覆蓋: {has_price}/{total_rooms} (100%)')
    print()

    # 儲存
    with open('nangang_rooms_complete.json', 'w', encoding='utf-8') as f:
        json.dump(complete_rooms, f, ensure_ascii=False, indent=2)

    print('✅ 已儲存到 nangang_rooms_complete.json')
    print()
    print('下一步: 更新 venues.json')


if __name__ == '__main__':
    main()
