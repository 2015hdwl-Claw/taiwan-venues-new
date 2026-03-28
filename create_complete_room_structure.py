#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定義完整的會議室資料結構標準
並更新台北世貿的所有會議室欄位
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_area(area_str):
    """解析面積字串：236/73 -> 平方公尺/坪"""
    if not area_str or area_str == '-':
        return {'sqm': None, 'ping': None}

    try:
        parts = str(area_str).split('/')
        if len(parts) == 2:
            sqm = float(parts[0]) if parts[0].replace('.', '').isdigit() else None
            ping = float(parts[1]) if parts[1].replace('.', '').isdigit() else None
            return {'sqm': sqm, 'ping': ping}
        return {'sqm': None, 'ping': None}
    except:
        return {'sqm': None, 'ping': None}


def clean_price(price_str):
    """清理價格字串"""
    if not price_str or price_str in ['-', '', '0']:
        return None
    try:
        cleaned = price_str.replace(',', '').replace('NT$', '').replace('元', '').strip()
        if cleaned and len(cleaned) <= 4 and cleaned.isdigit():
            return int(cleaned) * 10
        return int(cleaned) if cleaned else None
    except:
        return None


def create_complete_room_structure():
    """定義完整的會議室資料結構標準"""

    return {
        # 基本資料
        'id': None,                    # 場地唯一 ID (string)
        'name': None,                  # 中文名稱 (string)
        'nameEn': None,                # 英文名稱 (string | null)
        'floor': None,                 # 樓層 (string | null)

        # 面積資料
        'area': None,                  # 面積 (number | null)
        'areaUnit': None,              # 面積單位: "坪" | "㎡" (string | null)
        'areaSqm': None,               # 面積-平方公尺 (number | null)
        'areaPing': None,              # 面積-坪 (number | null)

        # 尺寸
        'dimensions': {
            'length': None,           # 長度 (公尺)
            'width': None,            # 寬度 (公尺)
            'height': None            # 高度 (公尺)
        },

        # 容量資料
        'capacity': {
            'theater': None,          # 劇院式 (number | null)
            'banquet': None,           # 宴會式 (number | null)
            'classroom': None,        # 教室式 (number | null)
            'uShape': None,            # U型 (number | null)
            'cocktail': None,          # 雞尾酒會 (number | null)
            'roundTable': None         # 圓桌 (number | null)
        },

        # 價格資料
        'price': {
            'weekday': None,           # 平日價格 (number | null)
            'holiday': None,           # 假日價格 (number | null)
            'morning': None,           # 上午時段 (number | null)
            'afternoon': None,         # 下午時段 (number | null)
            'evening': None,           # 晚上時段 (number | null)
            'fullDay': None,           # 全天時段 (number | null)
            'hourly': None,            # 每小時 (number | null)
            'note': None               # 價格備註 (string | null)
        },

        # 設備資料
        'equipment': None,             # 設備清單 (string | array | null)
        'equipmentList': [],          # 詳細設備列表 (array)

        # 特色
        'features': None,              # 特色描述 (string | null)

        # 資料來源
        'source': None,                # 資料來源 (string)
        'lastUpdated': None            # 最後更新時間 (ISO 8601)
    }


def main():
    print('=' * 80)
    print('定義完整會議室資料結構標準')
    print('=' * 80)
    print()

    # 顯示完整資料結構
    structure = create_complete_room_structure()

    print('完整會議室資料結構:')
    print(json.dumps(structure, ensure_ascii=False, indent=2))
    print()

    # 儲存標準
    with open('room_structure_standard.json', 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)

    print('✅ 已儲存完整資料結構標準到 room_structure_standard.json')
    print()

    # 現在解析 PDF 並創建完整的台北世貿會議室資料
    print('=' * 80)
    print('解析台北世貿 PDF - 完整資料')
    print('=' * 80)
    print()

    # 載入 PDF 提取資料
    with open('twtc_pricing_extraction.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    table = data['tables'][0]['data']

    # 根據 PDF 創建完整會議室資料
    complete_rooms = []

    # 第1會議室 (Row 3) - 面積: 236/73 sqm/ping
    if len(table) > 3:
        row = table[3]
        area = parse_area(row[8])  # 236/73

        room = create_complete_room_structure()
        room['id'] = '1049-01'
        room['name'] = '第一會議室'
        room['nameEn'] = 'Meeting Room 1'
        room['areaSqm'] = area['sqm']      # 236
        room['areaPing'] = area['ping']     # 73
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])    # 23,700
        room['price']['holiday'] = clean_price(row[5])    # 28,440
        room['price']['hourly'] = room['price']['weekday']  # 價格是每時段
        room['source'] = '官方 PDF 2025.10: 會議室暨設備價目表'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 第2會議室 (Row 4) - 面積: 169/52
    if len(table) > 4:
        row = table[4]
        area = parse_area(row[8])

        room = create_complete_room_structure()
        room['id'] = '1049-02'
        room['name'] = '第二會議室'
        room['nameEn'] = 'Meeting Room 2'
        room['areaSqm'] = area['sqm']
        room['areaPing'] = area['ping']
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])
        room['price']['holiday'] = clean_price(row[5])
        room['price']['hourly'] = room['price']['weekday']
        room['source'] = '官方 PDF 2025.10'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 第3會議室 (Row 5) - 面積: 220/68
    if len(table) > 5:
        row = table[5]
        area = parse_area(row[8])

        room = create_complete_room_structure()
        room['id'] = '1049-03'
        room['name'] = '第三會議室'
        room['nameEn'] = 'Meeting Room 3'
        room['areaSqm'] = area['sqm']
        room['areaPing'] = area['ping']
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])
        room['price']['holiday'] = clean_price(row[5])
        room['price']['hourly'] = room['price']['weekday']
        room['source'] = '官方 PDF 2025.10'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 第4會議室 (Row 6) - 面積: 145/45
    if len(table) > 6:
        row = table[6]
        area = parse_area(row[8])

        room = create_complete_room_structure()
        room['id'] = '1049-04'
        room['name'] = '第四會議室'
        room['nameEn'] = 'Meeting Room 4'
        room['areaSqm'] = area['sqm']
        room['areaPing'] = area['ping']
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])
        room['price']['holiday'] = clean_price(row[5])
        room['price']['hourly'] = room['price']['weekday']
        room['source'] = '官方 PDF 2025.10'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 第5會議室 (Row 8) - 面積: 236/73
    if len(table) > 8:
        row = table[8]
        area = parse_area(row[8])

        room = create_complete_room_structure()
        room['id'] = '1049-05'
        room['name'] = '第五會議室'
        room['nameEn'] = 'Meeting Room 5'
        room['areaSqm'] = area['sqm']
        room['areaPing'] = area['ping']
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])
        room['price']['holiday'] = clean_price(row[5])
        room['price']['hourly'] = room['price']['weekday']
        room['source'] = '官方 PDF 2025.10'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # A+會議室 (Row 9) - 面積: 145/45
    if len(table) > 9:
        row = table[9]
        area = parse_area(row[8])

        room = create_complete_room_structure()
        room['id'] = '1049-06'
        room['name'] = 'A+會議室'
        room['nameEn'] = 'A+ Meeting Room'
        room['areaSqm'] = area['sqm']
        room['areaPing'] = area['ping']
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])
        room['price']['holiday'] = clean_price(row[5])
        room['price']['hourly'] = room['price']['weekday']
        room['source'] = '官方 PDF 2025.10'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 第1、5間廊廳 (Row 10) - 面積: 04.5/31.6
    if len(table) > 10:
        row = table[10]
        area = parse_area(row[8])

        room = create_complete_room_structure()
        room['id'] = '1049-07'
        room['name'] = '第1、5間廊廳'
        room['nameEn'] = 'Lobby 1&5'
        room['areaSqm'] = area['sqm']
        room['areaPing'] = area['ping']
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])
        room['price']['holiday'] = clean_price(row[5])
        room['price']['hourly'] = room['price']['weekday']
        room['features'] = '位於第1及第5會議室之間的廊廳'
        room['source'] = '官方 PDF 2025.10'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 1樓貴賓室 (Row 11) - 面積: 104/31.4
    if len(table) > 11:
        row = table[11]
        area = parse_area(row[8])

        room = create_complete_room_structure()
        room['id'] = '1049-08'
        room['name'] = '1樓貴賓室'
        room['nameEn'] = 'VIP Room 1F'
        room['areaSqm'] = area['sqm']
        room['areaPing'] = area['ping']
        room['areaUnit'] = '㎡'
        room['price']['weekday'] = clean_price(row[4])
        room['price']['holiday'] = clean_price(row[5])
        room['price']['hourly'] = room['price']['weekday']
        room['features'] = '1樓貴賓室'
        room['source'] = '官方 PDF 2025.10'
        room['lastUpdated'] = datetime.now().isoformat()

        complete_rooms.append(room)

    # 顯示完整資料
    print(f'成功建立 {len(complete_rooms)} 個會議室的完整資料:')
    print()

    for room in complete_rooms:
        print(f'{room["name"]} / {room["nameEn"]}')
        print(f'  ID: {room["id"]}')
        print(f'  面積: {room["areaSqm"]} ㎡ ({room["areaPing"]} 坪)' if room["areaSqm"] else '  面積: NULL')
        print(f'  價格: 平日 NT${room["price"]["weekday"]:,}/時段' if room["price"]["weekday"] else '  價格: NULL')
        print(f'       假日 NT${room["price"]["holiday"]:,}/時段' if room["price"]["holiday"] else '')
        print(f'  容量: {room["capacity"]}')
        print(f'  設備: {room["equipment"]}')
        print(f'  來源: {room["source"]}')
        print()

    # 儲存完整資料
    with open('twtc_rooms_complete.json', 'w', encoding='utf-8') as f:
        json.dump(complete_rooms, f, ensure_ascii=False, indent=2)

    print('✅ 已儲存完整資料到 twtc_rooms_complete.json')
    print()

    # 統計 NULL 值
    print('=' * 80)
    print('資料完整性統計:')
    print('=' * 80)

    total_fields = 0
    null_fields = 0

    for room in complete_rooms:
        # 計算欄位數
        total_fields += 30  # 大約30個主要欄位

        # 計算 NULL
        if not room['floor']: null_fields += 1
        if not room['areaSqm']: null_fields += 1
        if not room['dimensions']['length']: null_fields += 3
        if not room['capacity']['theater']: null_fields += 6
        if not room['price']['weekday']: null_fields += 7
        if not room['equipment']: null_fields += 1

    print(f'總欄位數: {total_fields * len(complete_rooms)}')
    print(f'NULL 欄位數: {null_fields}')

    if total_fields * len(complete_rooms) > 0:
        completeness = ((total_fields * len(complete_rooms) - null_fields) / (total_fields * len(complete_rooms))) * 100
        print(f'完整度: {completeness:.1f}%')

    print()
    print('下一步: 更新 venues.json...')


if __name__ == '__main__':
    main()
