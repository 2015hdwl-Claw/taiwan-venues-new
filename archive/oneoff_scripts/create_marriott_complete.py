#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
為台北萬豪建立完整 30 欄位會議室資料結構
根據 PDF 提取的資料
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
    """解析尺寸字串 '9.8 x 7.5 x 3.6' -> {'length': 9.8, 'width': 7.5, 'height': 3.6}"""
    if not dim_str:
        return {'length': None, 'width': None, 'height': None}

    try:
        # 處理跨多欄的尺寸資料
        parts = dim_str.replace('x', ' ').split()
        numbers = [float(p) for p in parts if p.replace('.', '').isdigit()]

        if len(numbers) >= 3:
            return {'length': numbers[0], 'width': numbers[1], 'height': numbers[2]}
        elif len(numbers) == 2:
            return {'length': numbers[0], 'width': numbers[1], 'height': None}
        else:
            return {'length': None, 'width': None, 'height': None}
    except:
        return {'length': None, 'width': None, 'height': None}


def clean_number(num_str):
    """清理數字字串"""
    if not num_str:
        return None
    try:
        # 移除逗號和其他非數字字符（保留小數點）
        cleaned = str(num_str).replace(',', '').strip()
        if cleaned and cleaned.replace('.', '').isdigit():
            return float(cleaned) if '.' in cleaned else int(cleaned)
        return None
    except:
        return None


def main():
    print('=' * 80)
    print('建立台北萬豪完整會議室資料結構')
    print('=' * 80)
    print()

    # 載入 PDF 提取資料
    with open('marriott_pdf_extraction.json', 'r', encoding='utf-8') as f:
        pdf_data = json.load(f)

    table = pdf_data['pdfs'][0]['tables'][0]['data']

    # 定義欄位索引（根據 PDF 表格結構）
    # 欄位 0: Venue Name (第1部分)
    # 欄位 1: Venue Name (第2部分)
    # 欄位 2-4: Dimensions (L x W x H)
    # 欄位 5: SQM
    # 欄位 6: Ping
    # 欄位 7: Theater
    # 欄位 8: Classroom
    # 欄位 9: U-Shape
    # 欄位 10: Boardroom
    # 欄位 11-12: Round table (split)
    # 欄位 13-14: Party min/max (split)
    # 欄位 15: Setup (09:00-16:30 價格)
    # 欄位 16: Full Day (08:00-21:30 價格)
    # 欄位 17: Overnight (24 hours 價格)
    # 欄位 18: Setup (2300-0700 價格)
    # 欄位 19: Hour 價格

    complete_rooms = []

    # 解析每個會議室
    room_rows = [
        (4, 'Spring 春'),
        (6, 'Summer 夏'),
        (8, 'Autumn 秋'),
        (10, 'Winter 冬'),
        (12, 'Spring – Winter 四季'),
        (14, 'Salon I 會議一'),
        (16, 'Salon II 會議二'),
        (18, 'Salon III 會議三'),
        (20, 'Salon IV 會議四'),
        (22, 'Salon I+II 會議一+二'),
        (24, 'Salon III+IV 會議三+四'),
        (30, 'Ballroom I 萬豪一廳'),
        (32, 'Ballroom II 萬豪二廳'),
        (34, 'Grand Ballroom 萬豪廳'),
        (36, 'Fortune 福'),
        (38, 'Prosperity 祿'),
        (40, 'Longevity 壽'),
        (42, 'Fortune – Longevity 福祿'),
        (44, 'Junior I 宜華一廳'),
        (46, 'Junior II 宜華二廳'),
        (48, 'Junior Ballroom 宜華廳'),
        (52, 'Garden Villa'),
        (54, 'Panorama 寰宇廳')
    ]

    room_counter = 1

    for row_idx, room_name_hint in room_rows:
        if row_idx >= len(table):
            continue

        row = table[row_idx]

        # 組合會議室名稱
        name_parts = [row[0], row[1]]
        room_name = ' '.join([p for p in name_parts if p]).strip()

        # 處理尺寸（跨 3 個欄位）
        dim_parts = [row[2] if len(row) > 2 else '',
                     row[3] if len(row) > 3 else '',
                     row[4] if len(row) > 4 else '']
        dim_str = ' '.join([p for p in dim_parts if p])
        dimensions = parse_dimensions(dim_str)

        # 面積
        area_sqm = clean_number(row[5]) if len(row) > 5 else None
        area_ping = clean_number(row[6]) if len(row) > 6 else None

        # 容量
        theater = clean_number(row[7]) if len(row) > 7 else None
        classroom = clean_number(row[8]) if len(row) > 8 else None
        u_shape = clean_number(row[9]) if len(row) > 9 else None
        boardroom = clean_number(row[10]) if len(row) > 10 else None
        round_table = clean_number(row[12]) if len(row) > 12 else None

        # 價格（根據 PDF 實際欄位）
        # Column 18: Setup (09:00-16:30) 平日時段
        # Column 19: Full Day (08:00-21:30) 全天
        # Column 20: Overnight (24 hours) 24小時
        # Column 21: Setup (2300-0700) 夜間設定
        # Column 22: Hour 每小時
        setup_price = clean_number(row[18]) if len(row) > 18 else None
        full_day_price = clean_number(row[19]) if len(row) > 19 else None
        overnight_price = clean_number(row[20]) if len(row) > 20 else None
        setup_night_price = clean_number(row[21]) if len(row) > 21 else None
        hourly_price = clean_number(row[22]) if len(row) > 22 else None

        # 建立完整資料結構
        room = create_complete_room_structure()
        room['id'] = f'1103-{room_counter:02d}'
        room['name'] = room_name
        room['nameEn'] = None  # PDF 沒有英文名稱
        room['floor'] = None
        room['area'] = area_sqm
        room['areaUnit'] = '㎡'
        room['areaSqm'] = area_sqm
        room['areaPing'] = area_ping
        room['dimensions'] = dimensions
        room['capacity'] = {
            'theater': int(theater) if theater else None,
            'banquet': None,
            'classroom': int(classroom) if classroom else None,
            'uShape': int(u_shape) if u_shape else None,
            'cocktail': None,
            'roundTable': int(round_table) if round_table else None,
            'boardroom': int(boardroom) if boardroom else None
        }
        room['price'] = {
            'weekday': setup_price,
            'holiday': None,
            'morning': None,
            'afternoon': None,
            'evening': None,
            'fullDay': full_day_price,
            'hourly': hourly_price,
            'setup': setup_price,
            'overnight': overnight_price,
            'setupNight': setup_night_price,
            'note': 'Price from PDF: 09:00-16:30, 08:00-21:30 (24h), Setup (2300-0700), Hour'
        }
        room['equipment'] = None
        room['equipmentList'] = []
        room['features'] = None
        room['source'] = '官方 PDF: 場租表 2026'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)
        room_counter += 1

    # 顯示結果
    print(f'成功建立 {len(complete_rooms)} 個會議室:')
    print()

    for room in complete_rooms:
        print(f'{room["name"]}')
        print(f'  ID: {room["id"]}')
        print(f'  面積: {room["areaSqm"]} ㎡ ({room["areaPing"]} 坪)' if room["areaSqm"] else '  面積: NULL')
        print(f'  容量: Theater={room["capacity"]["theater"]}, Classroom={room["capacity"]["classroom"]}')
        print(f'  價格: Setup={room["price"]["setup"]}, Full Day={room["price"]["fullDay"]}')
        print()

    # 儲存
    with open('marriott_rooms_complete.json', 'w', encoding='utf-8') as f:
        json.dump(complete_rooms, f, ensure_ascii=False, indent=2)

    print(f'✅ 已儲存到 marriott_rooms_complete.json')
    print()

    # 統計
    total_rooms = len(complete_rooms)
    has_area = sum(1 for r in complete_rooms if r['areaSqm'])
    has_theater = sum(1 for r in complete_rooms if r['capacity']['theater'])
    has_price = sum(1 for r in complete_rooms if r['price']['setup'])

    print('=' * 80)
    print('資料完整性統計:')
    print('=' * 80)
    print(f'總會議室: {total_rooms}')
    print(f'面積覆蓋: {has_area}/{total_rooms} ({has_area*100//total_rooms}%)')
    print(f'容量覆蓋: {has_theater}/{total_rooms} ({has_theater*100//total_rooms}%)')
    print(f'價格覆蓋: {has_price}/{total_rooms} ({has_price*100//total_rooms}%)')
    print()
    print('下一步: 更新 venues.json')


if __name__ == '__main__':
    main()
