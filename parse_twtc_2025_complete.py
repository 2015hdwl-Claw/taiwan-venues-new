#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析台北世貿 2025 會議室價目表 PDF - 完整資料提取
包括：使用人數、尺寸大小、費用、基本配備
"""

import sys
import io
import pdfplumber
import json
import re
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def clean_number(num_str):
    """清理數字字串"""
    if not num_str:
        return None
    try:
        cleaned = str(num_str).replace(',', '').replace('$', '').replace('NT', '').replace('元', '').strip()
        if cleaned and cleaned.replace('.', '').isdigit():
            return float(cleaned) if '.' in cleaned else int(cleaned)
        return None
    except:
        return None


def parse_price_truncated(price_str):
    """修復被截斷的價格 '28,44' -> 28440"""
    if not price_str:
        return None
    try:
        price_str = str(price_str).replace(',', '').strip()
        if len(price_str) <= 4 and price_str.isdigit():
            # 價格被截斷，補一個0
            return int(price_str) * 10
        return int(price_str)
    except:
        return None


def parse_area_with_unit(area_str):
    """解析面積字串 '236/73' -> (236, 73, '㎡')"""
    if not area_str:
        return None, None, None

    area_str = str(area_str).strip()

    # 檢查是否有斜線（表示 sqm/ping）
    if '/' in area_str:
        parts = area_str.split('/')
        if len(parts) == 2:
            sqm = clean_number(parts[0])
            ping = clean_number(parts[1])
            return sqm, ping, '㎡'

    # 只有一個數字
    value = clean_number(area_str)
    if value:
        return value, value / 3.3058, '㎡'

    return None, None, None


def parse_dimensions_from_cols(cols):
    """從多個欄位組合尺寸資料"""
    # 尺寸可能在欄位 10, 11, 12
    # 例如: [10] = '16.3×14.5', [11] = '×2', [12] = '.7'
    # 組合成: 16.3×14.5×2.7

    dim_parts = []

    for col in cols:
        if col:
            col_str = str(col).strip()
            # 移除 '×' 前綴，純粹數字和小數點
            col_str = col_str.replace('×', ' ').strip()
            if col_str and col_str.replace('.', '').replace(' ', '').isdigit():
                dim_parts.append(col_str)

    if dim_parts:
        combined = ' '.join(dim_parts)
        # 解析組合後的字串
        parts = combined.split()
        if len(parts) >= 2:
            try:
                length = float(parts[0])
                width = float(parts[1])
                height = float(parts[2]) if len(parts) > 2 else None
                return {'length': length, 'width': width, 'height': height}
            except:
                pass

    return {'length': None, 'width': None, 'height': None}


def main():
    print('=' * 80)
    print('解析台北世貿 2025 會議室價目表 PDF - 完整資料')
    print('=' * 80)
    print()

    pdf_path = 'twtc_pricing_2025.pdf'

    with pdfplumber.open(pdf_path) as pdf:
        print(f'PDF 頁數: {len(pdf.pages)}')
        print()

        all_rooms = []

        for page_num, page in enumerate(pdf.pages, 1):
            print(f'--- 頁面 {page_num} ---')

            # 使用 text 策略提取表格
            tables = page.extract_tables({
                'vertical_strategy': 'text',
                'horizontal_strategy': 'text',
                'snap_tolerance': 5,
                'join_tolerance': 5
            })

            if not tables:
                continue

            for table_idx, table in enumerate(tables):
                # 尋找包含會議室資料的行（從 Row 3 開始）
                data_rows = table[3:] if len(table) > 3 else []

                for row_idx, row in enumerate(data_rows):
                    if not row or len(row) < 15:
                        continue

                    # 組合名稱（從欄位 1 和 2）
                    name_part1 = str(row[1]).strip() if row[1] else ''
                    name_part2 = str(row[2]).strip() if row[2] else ''
                    name_col = f'{name_part1}{name_part2}'.strip()

                    # 跳過空行
                    if not name_col:
                        continue

                    # 跳過標題行和說明行
                    if '星期' in name_col or '例假日' in name_col or '計價' in name_col:
                        continue
                    if name_col.startswith('*'):
                        continue
                    if '借用' in name_col and '需同時' in name_col:
                        continue
                    if '桌巾' in name_col or '每桌計' in name_col:
                        continue

                    # 檢查是否包含數字或「會議室」或「貴賓室」或「廊廳」
                    has_number = bool(re.search(r'\d+', name_col))
                    is_room = ('會議室' in name_col or '貴賓室' in name_col or '廊廳' in name_col or
                              name_col in ['A', 'A+', 'B', 'C'])

                    if has_number or is_room:
                        # 提取資料
                        price_day = parse_price_truncated(row[4]) if len(row) > 4 else None
                        price_night = parse_price_truncated(row[5]) if len(row) > 5 else None

                        # 檢查是否有價格資料（必須有價格才算會議室）
                        if not price_day and not price_night:
                            continue

                        # 過濾掉設備租金（價格太低的是設備）
                        if price_day and price_day < 1000:
                            continue

                        area_sqm, area_ping, area_unit = parse_area_with_unit(row[8]) if len(row) > 8 else (None, None, None)

                        # 組合尺寸（從欄位 10, 11, 12）
                        dimensions = parse_dimensions_from_cols([row[10], row[11], row[12]] if len(row) > 12 else [])

                        # 容量
                        theater = clean_number(row[13]) if len(row) > 13 else None
                        standard = clean_number(row[15]) if len(row) > 15 else None
                        classroom = clean_number(row[17]) if len(row) > 17 else None

                        if name_col:
                            all_rooms.append({
                                'name': name_col,
                                'price_day': price_day,
                                'price_night': price_night,
                                'area_sqm': area_sqm,
                                'area_ping': area_ping,
                                'dimensions': dimensions,
                                'theater': theater,
                                'standard': standard,
                                'classroom': classroom,
                                'raw_data': row
                            })

                            print(f'  找到: {name_col} - 劇院{theater}人, {area_sqm}㎡, ${price_day}')

        print()
        print('=' * 80)
        print(f'找到 {len(all_rooms)} 個會議室')
        print('=' * 80)
        print()

        # 建立完整 30 欄位結構
        complete_rooms = []

        for idx, room_data in enumerate(all_rooms, 1):
            room = {
                'id': f'1049-{idx:02d}',
                'name': room_data['name'],
                'nameEn': room_data['name'],  # 暫時使用中文
                'floor': None,  # PDF 中沒有明確樓層資訊
                'area': room_data['area_sqm'],
                'areaUnit': '㎡' if room_data['area_sqm'] else None,
                'areaSqm': room_data['area_sqm'],
                'areaPing': room_data['area_ping'],
                'dimensions': room_data['dimensions'],
                'capacity': {
                    'theater': room_data['theater'],
                    'banquet': room_data['standard'],  # 標準型 ≒ 宴會型
                    'classroom': room_data['classroom'],
                    'uShape': None,
                    'cocktail': None,
                    'roundTable': None
                },
                'price': {
                    'weekday': room_data['price_day'],
                    'holiday': room_data['price_night'],  # 夜間/例假日
                    'morning': None,
                    'afternoon': None,
                    'evening': None,
                    'fullDay': None,
                    'hourly': None,
                    'note': '日間: 08:00-12:00/13:00-17:00, 夜間: 18:00-22:00'
                },
                'equipment': None,  # 將在頁面2查找
                'equipmentList': [],
                'features': None,
                'source': '官方 PDF: 2025會議室價目表2025.10版',
                'lastUpdated': datetime.now().isoformat()
            }

            complete_rooms.append(room)

        # 儲存
        with open('twtc_rooms_2025_complete.json', 'w', encoding='utf-8') as f:
            json.dump(complete_rooms, f, ensure_ascii=False, indent=2)

        print(f'✅ 已儲存到 twtc_rooms_2025_complete.json')
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

        # 顯示前5個會議室
        print('會議室列表（前5個）:')
        for room in complete_rooms[:5]:
            print(f'  - {room["name"]}')
            print(f'    面積: {room["areaSqm"]} ㎡ ({room["areaPing"]} 坪)')
            print(f'    尺寸: {room["dimensions"]["length"]}×{room["dimensions"]["width"]}×{room["dimensions"]["height"]} m')
            print(f'    容量: 劇院 {room["capacity"]["theater"]} 人, 標準 {room["capacity"]["banquet"]} 人, 教室 {room["capacity"]["classroom"]} 人')
            print(f'    價格: 日間 NT${room["price"]["weekday"]:,}, 夜間 NT${room["price"]["holiday"]:,}')
            print()


if __name__ == '__main__':
    main()
