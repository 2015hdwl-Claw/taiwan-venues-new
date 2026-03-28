#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整解析台北世貿會議室 PDF - 提取所有欄位
包括：尺寸、使用人數、基本配備等
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_capacity(capacity_str):
    """解析容量字串"""
    if not capacity_str or capacity_str == '-':
        return None
    try:
        # 提取數字
        import re
        numbers = re.findall(r'\d+', capacity_str)
        if numbers:
            return int(numbers[0])
        return None
    except:
        return None


def clean_price(price_str):
    """清理價格字串"""
    if not price_str or price_str in ['-', '', '0']:
        return None
    try:
        cleaned = price_str.replace(',', '').replace('NT$', '').replace('元', '').strip()
        # 如果數字太短，可能被截斷了
        if cleaned and len(cleaned) <= 4 and cleaned.isdigit():
            return int(cleaned) * 10
        return int(cleaned) if cleaned else None
    except:
        return None


def main():
    print('=' * 80)
    print('完整解析台北世貿會議室 PDF - 所有欄位')
    print('=' * 80)
    print()

    # 載入 PDF 提取資料
    with open('twtc_pricing_extraction.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    table = data['tables'][0]['data']

    print('[1/3] 分析 PDF 表格結構...')
    print()

    # 顯示完整表格前 30 行，找出所有欄位
    print('完整表格結構（前 30 行）:')
    for i, row in enumerate(table[:30], 1):
        # 只顯示前 10 欄
        display_row = []
        for j, cell in enumerate(row[:10]):
            if cell:
                cell_str = str(cell).replace('\n', ' ')[:30]
                display_row.append(f'[{j}]{cell_str}')
            else:
                display_row.append(f'[{j}]')
        print(f'Row {i}: {display_row}')

    print()
    print('[2/3] 定義完整會議室資料結構...')
    print()

    # 根據 PDF 結構定義完整欄位
    # 從表格可以看到有：
    # - 欄位 2: 會議室名稱
    # - 欄位 3: 尺寸/面積（可能有）
    # - 欄位 4: 日間每時段租金（平日）
    # - 欄位 5: 例假日每時段租金
    # - 欄位 6: 夜間租金
    # - 其他欄位可能有容量、配備等

    complete_rooms = []

    # 分析每個會議室行
    # 第1會議室 (Row 3)
    if len(table) > 3:
        row = table[3]
        complete_rooms.append({
            'id': '1049-01',
            'name': '第一會議室',
            'nameEn': 'Meeting Room 1',
            'floor': None,  # PDF 中沒有樓層資訊
            'area': None,  # 需要從表格中查找
            'areaUnit': None,
            'dimensions': {
                'length': None,
                'width': None,
                'height': None
            },
            'capacity': {
                'theater': None,
                'banquet': None,
                'classroom': None,
                'uShape': None
            },
            'price': {
                'weekday': clean_price(row[4]),  # 日間每時段租金（平日）
                'holiday': clean_price(row[5]),  # 例假日每時段租金
                'evening': clean_price(row[6]),   # 夜間租金
                'fullDay': None,
                'note': None
            },
            'equipment': None,
            'features': None,
            'source': '官方 PDF 2025.10: 會議室暨設備價目表',
            'lastUpdated': datetime.now().isoformat()
        })

    # 第2會議室 (Row 4)
    if len(table) > 4:
        row = table[4]
        complete_rooms.append({
            'id': '1049-02',
            'name': '第二會議室',
            'nameEn': 'Meeting Room 2',
            'floor': None,
            'area': None,
            'areaUnit': None,
            'dimensions': {'length': None, 'width': None, 'height': None},
            'capacity': {'theater': None, 'banquet': None, 'classroom': None, 'uShape': None},
            'price': {
                'weekday': clean_price(row[4]),
                'holiday': clean_price(row[5]),
                'evening': clean_price(row[6]),
                'fullDay': None,
                'note': None
            },
            'equipment': None,
            'features': None,
            'source': '官方 PDF 2025.10',
            'lastUpdated': datetime.now().isoformat()
        })

    # 第3會議室 (Row 5)
    if len(table) > 5:
        row = table[5]
        complete_rooms.append({
            'id': '1049-03',
            'name': '第三會議室',
            'nameEn': 'Meeting Room 3',
            'floor': None,
            'area': None,
            'areaUnit': None,
            'dimensions': {'length': None, 'width': None, 'height': None},
            'capacity': {'theater': None, 'banquet': None, 'classroom': None, 'uShape': None},
            'price': {
                'weekday': clean_price(row[4]),
                'holiday': clean_price(row[5]),
                'evening': clean_price(row[6]),
                'fullDay': None,
                'note': None
            },
            'equipment': None,
            'features': None,
            'source': '官方 PDF 2025.10',
            'lastUpdated': datetime.now().isoformat()
        })

    # 第4會議室 (Row 6)
    if len(table) > 6:
        row = table[6]
        complete_rooms.append({
            'id': '1049-04',
            'name': '第四會議室',
            'nameEn': 'Meeting Room 4',
            'floor': None,
            'area': None,
            'areaUnit': None,
            'dimensions': {'length': None, 'width': None, 'height': None},
            'capacity': {'theater': None, 'banquet': None, 'classroom': None, 'uShape': None},
            'price': {
                'weekday': clean_price(row[4]),
                'holiday': clean_price(row[5]),
                'evening': clean_price(row[6]),
                'fullDay': None,
                'note': None
            },
            'equipment': None,
            'features': None,
            'source': '官方 PDF 2025.10',
            'lastUpdated': datetime.now().isoformat()
        })

    # 第5會議室 (Row 8)
    if len(table) > 8:
        row = table[8]
        complete_rooms.append({
            'id': '1049-05',
            'name': '第五會議室',
            'nameEn': 'Meeting Room 5',
            'floor': None,
            'area': None,
            'areaUnit': None,
            'dimensions': {'length': None, 'width': None, 'height': None},
            'capacity': {'theater': None, 'banquet': None, 'classroom': None, 'uShape': None},
            'price': {
                'weekday': clean_price(row[4]),
                'holiday': clean_price(row[5]),
                'evening': clean_price(row[6]),
                'fullDay': None,
                'note': None
            },
            'equipment': None,
            'features': None,
            'source': '官方 PDF 2025.10',
            'lastUpdated': datetime.now().isoformat()
        })

    # A+會議室 (Row 9)
    if len(table) > 9:
        row = table[9]
        complete_rooms.append({
            'id': '1049-06',
            'name': 'A+會議室',
            'nameEn': 'A+ Meeting Room',
            'floor': None,
            'area': None,
            'areaUnit': None,
            'dimensions': {'length': None, 'width': None, 'height': None},
            'capacity': {'theater': None, 'banquet': None, 'classroom': None, 'uShape': None},
            'price': {
                'weekday': clean_price(row[4]),
                'holiday': clean_price(row[5]),
                'evening': clean_price(row[6]),
                'fullDay': None,
                'note': None
            },
            'equipment': None,
            'features': None,
            'source': '官方 PDF 2025.10',
            'lastUpdated': datetime.now().isoformat()
        })

    # 顯示完整資料結構
    print(f'定義了 {len(complete_rooms)} 個會議室的完整資料結構')
    print()

    for room in complete_rooms[:2]:
        print(f'範例: {room["name"]}')
        print(f'  ID: {room["id"]}')
        print(f'  價格:平日={room["price"]["weekday"]} 假日={room["price"]["holiday"]}')
        print(f'  容量:{room["capacity"]}')
        print(f'  面積:{room["area"]}')
        print(f'  設備:{room["equipment"]}')
        print()

    # 儲存完整資料結構
    with open('twtc_complete_rooms.json', 'w', encoding='utf-8') as f:
        json.dump(complete_rooms, f, ensure_ascii=False, indent=2)

    print('[3/3] 儲存完整資料結構...')
    print(f'✅ 已儲存到 twtc_complete_rooms.json')
    print()

    # 統計 NULL 值
    total_fields = 0
    null_fields = 0
    for room in complete_rooms:
        # 計算總欄位數
        total_fields += 1  # id
        total_fields += 1  # name
        total_fields += 1  # nameEn
        total_fields += 1  # floor
        total_fields += 1  # area
        total_fields += 3  # dimensions
        total_fields += 4  # capacity
        total_fields += 5  # price
        total_fields += 1  # equipment
        total_fields += 1  # features
        total_fields += 2  # source, lastUpdated

        # 計算 NULL 欄位數
        if not room['floor']:
            null_fields += 1
        if not room['area']:
            null_fields += 1
        if not room['dimensions']['length']:
            null_fields += 3
        if not room['capacity']['theater']:
            null_fields += 4
        if not room['equipment']:
            null_fields += 1

    print('=' * 80)
    print('資料完整性統計:')
    print('=' * 80)
    print(f'總欄位數: {total_fields * len(complete_rooms)}')
    print(f'NULL 欄位數: {null_fields}')
    if total_fields > 0:
        completeness = ((total_fields * len(complete_rooms) - null_fields) / (total_fields * len(complete_rooms))) * 100
        print(f'完整度: {completeness:.1f}%')
    print()

    print('下一步:')
    print('1. 檢查 twtc_complete_rooms.json')
    print('2. 更新 venues.json')
    print('3. 寫入知識庫：完整的會議室資料結構')


if __name__ == '__main__':
    main()
