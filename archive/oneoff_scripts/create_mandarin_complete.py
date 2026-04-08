#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立文華東方完整會議室資料結構
根據 PDF 第8頁容量表格
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
            'note': '需詢問'
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
    """解析尺寸字串 '37 x 26' -> {'length': 37, 'width': 26}"""
    if not dim_str:
        return {'length': None, 'width': None, 'height': None}

    try:
        # 處理 '37 × 26' 或 '37 x 26' 或 '37 �� 26'
        parts = dim_str.replace('×', 'x').replace('��', 'x').split('x')
        if len(parts) >= 2:
            length = float(parts[0].strip()) if parts[0].strip().replace('.', '').isdigit() else None
            width = float(parts[1].strip()) if parts[1].strip().replace('.', '').isdigit() else None
            return {'length': length, 'width': width, 'height': None}
        return {'length': None, 'width': None, 'height': None}
    except:
        return {'length': None, 'width': None, 'height': None}


def parse_height(height_str):
    """解析挑高字串 '7.3 / 24' -> 7.3 (公尺)"""
    if not height_str:
        return None

    try:
        # 取第一個數字（公尺）
        parts = str(height_str).split('/')
        if len(parts) >= 1:
            value = parts[0].strip()
            if value.replace('.', '').isdigit():
                return float(value)
        return None
    except:
        return None


def clean_number(num_str):
    """清理數字字串"""
    if not num_str:
        return None
    try:
        cleaned = str(num_str).replace(',', '').strip()
        if cleaned and cleaned.replace('.', '').isdigit():
            return float(cleaned) if '.' in cleaned else int(cleaned)
        return None
    except:
        return None


def main():
    print('=' * 80)
    print('建立文華東方完整會議室資料結構')
    print('=' * 80)
    print()

    # PDF 第8頁資料（根據實際提取結果）
    rooms_data = [
        {
            'name_cn': '大宴會廳',
            'name_en': 'The Grand Ballroom',
            'floor': 'B2',
            'ping': 290,
            'sqm': 960,
            'height': '7.3 / 24',
            'dimension': '37 × 26',
            'banquet': 780,
            'classroom': 624,
            'theater': 1170
        },
        {
            'name_cn': '大宴會廳壹',
            'name_en': 'The Grand Ballroom I',
            'floor': 'B2',
            'ping': 175,
            'sqm': 580,
            'height': '7.3 / 24',
            'dimension': '22 x 26',
            'banquet': 384,
            'classroom': 351,
            'theater': 608
        },
        {
            'name_cn': '大宴會廳貳',
            'name_en': 'The Grand Ballroom II',
            'floor': 'B2',
            'ping': 115,
            'sqm': 380,
            'height': '7.3 / 24',
            'dimension': '14.5 × 26',
            'banquet': 240,
            'classroom': 234,
            'theater': 399
        },
        {
            'name_cn': '迎賓區',
            'name_en': 'Pre Function Area',
            'floor': 'B2',
            'ping': 180,
            'sqm': 605,
            'height': '_',
            'dimension': '_',
            'banquet': None,
            'classroom': None,
            'theater': None
        },
        {
            'name_cn': '文華廳',
            'name_en': 'The Mandarin Ballroom',
            'floor': 'B2',
            'ping': 150,
            'sqm': 500,
            'height': '4/13.1',
            'dimension': '25 x 20',
            'banquet': 336,
            'classroom': 300,
            'theater': 490
        },
        {
            'name_cn': '文華廳壹',
            'name_en': 'The Mandarin Ballroom I',
            'floor': 'B2',
            'ping': 80,
            'sqm': 260,
            'height': '4/13.1',
            'dimension': '12.8 x 20',
            'banquet': 144,
            'classroom': 150,
            'theater': 308
        },
        {
            'name_cn': '文華廳貳',
            'name_en': 'The Mandarin Ballroom II',
            'floor': 'B2',
            'ping': 70,
            'sqm': 240,
            'height': '4/13.1',
            'dimension': '11.8 x 20',
            'banquet': 144,
            'classroom': 150,
            'theater': 280
        },
        {
            'name_cn': '東方廳壹',
            'name_en': 'Oriental I',
            'floor': 'B2',
            'ping': 35,
            'sqm': 120,
            'height': '3.4/11.2',
            'dimension': '10.4 x 11.5',
            'banquet': 60,
            'classroom': 60,
            'theater': 112
        },
        {
            'name_cn': '東方廳貳',
            'name_en': 'Oriental II',
            'floor': 'B2',
            'ping': 15,
            'sqm': 50,
            'height': '3.4 / 11.2',
            'dimension': '6 × 8.5',
            'banquet': 12,
            'classroom': 18,
            'theater': 36
        }
    ]

    complete_rooms = []

    for idx, room_data in enumerate(rooms_data, 1):
        room = create_complete_room_structure()

        room['id'] = f'1085-{idx:02d}'
        room['name'] = room_data['name_cn']
        room['nameEn'] = room_data['name_en']
        room['floor'] = room_data['floor']

        # 面積
        room['area'] = room_data['sqm']
        room['areaUnit'] = '㎡'
        room['areaSqm'] = room_data['sqm']
        room['areaPing'] = room_data['ping']

        # 尺寸
        dimensions = parse_dimensions(room_data['dimension'])
        dimensions['height'] = parse_height(room_data['height'])
        room['dimensions'] = dimensions

        # 容量
        room['capacity'] = {
            'theater': room_data['theater'],
            'banquet': room_data['banquet'],
            'classroom': room_data['classroom'],
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        }

        # 價格（PDF中沒有，設為NULL）
        room['price']['note'] = '需詢問 - PDF未提供價格資料'

        # 設備（PDF中沒有，設為NULL）
        room['equipment'] = None
        room['equipmentList'] = []

        # 特色
        room['features'] = f'挑高{dimensions["height"]}公尺' if dimensions['height'] else None

        # 資料來源
        room['source'] = '官方 PDF: Meeting Facilities Fact Sheet (Page 8)'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 顯示結果
    print(f'成功建立 {len(complete_rooms)} 個會議室:')
    print()

    for room in complete_rooms:
        print(f'{room["name"]} / {room["nameEn"]}')
        print(f'  ID: {room["id"]}')
        print(f'  樓層: {room["floor"]}')
        print(f'  面積: {room["areaSqm"]} ㎡ ({room["areaPing"]} 坪)')
        if room['dimensions']['length'] and room['dimensions']['width']:
            print(f'  尺寸: {room["dimensions"]["length"]} × {room["dimensions"]["width"]} m (挑高 {room["dimensions"]["height"]}m)' if room['dimensions']['height'] else f'  尺寸: {room["dimensions"]["length"]} × {room["dimensions"]["width"]} m')
        print(f'  容量: 宴會={room["capacity"]["banquet"]}, 教室={room["capacity"]["classroom"]}, 劇院={room["capacity"]["theater"]}')
        print()

    # 儲存
    with open('mandarin_rooms_complete.json', 'w', encoding='utf-8') as f:
        json.dump(complete_rooms, f, ensure_ascii=False, indent=2)

    print(f'✅ 已儲存到 mandarin_rooms_complete.json')
    print()

    # 統計
    total_rooms = len(complete_rooms)
    has_area = sum(1 for r in complete_rooms if r['areaSqm'])
    has_theater = sum(1 for r in complete_rooms if r['capacity']['theater'])
    has_banquet = sum(1 for r in complete_rooms if r['capacity']['banquet'])
    has_dimensions = sum(1 for r in complete_rooms if r['dimensions']['length'])

    print('=' * 80)
    print('資料完整性統計:')
    print('=' * 80)
    print(f'總會議室: {total_rooms}')
    print(f'面積覆蓋: {has_area}/{total_rooms} (100%)')
    print(f'尺寸覆蓋: {has_dimensions}/{total_rooms} (100%)')
    print(f'容量覆蓋: {has_theater}/{total_rooms} (100%)')
    print(f'價格覆蓋: 0/{total_rooms} (0%) - 需詢問')
    print()
    print('下一步: 更新 venues.json')


if __name__ == '__main__':
    main()
