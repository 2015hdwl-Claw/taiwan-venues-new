#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Parser V6 - Precise name extraction
Fixes: 102, 103, 105, 201, 401 etc. room names
"""
import json
import re
from datetime import datetime


def parse_ticc_v6(lines):
    """V6: 精確提取會議室名稱"""
    rooms = []
    i = 0
    in_data = False

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if '劇院型' in line and '教室型' in line:
            in_data = True
            i += 1
            continue

        if not in_data:
            i += 1
            continue

        if '備註' in line or line.startswith('註'):
            break

        if any(kw in line for kw in ['容量', '面積', '租金', '尺寸']):
            i += 1
            continue

        if re.match(r'^[\s\-\―\=]+$', line):
            i += 1
            continue

        room = parse_room_v6(line, lines, i)
        if room:
            rooms.append(room)
            i += 1
        else:
            i += 1

    return rooms


def parse_room_v6(line, all_lines, line_idx):
    """
    V6: 更精確的名稱提取

    命名模式分析：
    1. 純數字：102, 103, 105, 201, 401 等
    2. 數字+字母：101A/D, 201A/F, 202B/203B 等
    3. 中文：大會堂全場, 3樓南/北軒, 106固定座位 等
    4. 數字+中文：201 全室, 3樓宴會廳 等
    """
    line = line.strip()

    if line.startswith('('):
        return None

    # 策略1: 檢查是否以純數字開頭（102, 103, 201, 401 等）
    pure_num_match = re.match(r'^(\d{3})\s+(\d+)', line)
    if pure_num_match:
        name = pure_num_match.group(1)
        return parse_room_data(line, name)

    # 策略2: 檢查數字+字母模式（101A/D, 201A/F 等）
    combo_match = re.match(r'^(\d+[A-Z]\/[A-Z])\s+', line)
    if combo_match:
        name = combo_match.group(1)
        return parse_room_data(line, name)

    # 策略3: 檢查中文開頭（大會堂、3樓、106固定座位等）
    chinese_match = re.match(r'^([^0-9\s]+)\s+(\d)', line)
    if chinese_match:
        name = chinese_match.group(1).strip()
        # 清理尾部分隔符
        name = re.sub(r'[／\/\-\―\s]+$', '', name)
        if len(name) >= 2:
            return parse_room_data(line, name)

    # 策略4: 數字+中文（201 全室等）
    num_chinese_match = re.match(r'^(\d+)\s+([^0-9]+?)\s{2,}', line)
    if num_chinese_match:
        num = num_chinese_match.group(1)
        chinese = num_chinese_match.group(2).strip()
        name = f"{num} {chinese}"
        return parse_room_data(line, name)

    return None


def parse_room_data(line, name):
    """解析會議室資料（已知名稱後）"""
    room = {
        'name': name,
        'capacity_theater': None,
        'capacity_classroom': None,
        'capacity_u': None,
        'capacity_negotiate': None,
        'area_sqm': None,
        'area_ping': None,
        'dimensions': None,
        'price_weekday': None,
        'price_weekend': None,
        'price_exhibition': None
    }

    # 移除名稱後提取數字
    name_pattern = re.escape(name)
    data_part = re.sub(f'^{name_pattern}\\s*', '', line)

    # 提取分數面積
    fraction = re.search(r'(\d+),?(\d+)/(\d+)', data_part)
    if fraction:
        room['area_sqm'] = int(fraction.group(1) + fraction.group(2))
        room['area_ping'] = int(fraction.group(3))

    # 提取尺寸
    dim_match = re.search(r'(\d+\.?\d*)[×x](\d+\.?\d*)[×x](\d+\.?\d*)', data_part)
    if dim_match:
        room['dimensions'] = f"{dim_match.group(1)}×{dim_match.group(2)}×{dim_match.group(3)}"

    # 提取所有數字
    numbers = extract_numbers(data_part)

    # 過濾掉面積和尺寸中的數字
    filtered = []
    for n in numbers:
        if n == room.get('area_sqm') or n == room.get('area_ping'):
            continue
        if dim_match and n < 20:
            continue
        filtered.append(n)

    # 分類：容量(10-5000)，價格(>5000)
    capacities = [n for n in filtered if 10 <= n <= 5000]
    prices = [n for n in filtered if n > 5000]

    # 分配容量
    if capacities:
        if len(capacities) >= 1:
            room['capacity_theater'] = capacities[0]
        if len(capacities) >= 2:
            room['capacity_classroom'] = capacities[1]
        if len(capacities) >= 3:
            room['capacity_u'] = capacities[2]
        if len(capacities) >= 4:
            room['capacity_negotiate'] = capacities[3]

    # 分配價格
    if prices:
        prices_sorted = sorted(prices)
        if len(prices_sorted) >= 1:
            room['price_weekday'] = prices_sorted[0]
        if len(prices_sorted) >= 2:
            room['price_weekend'] = prices_sorted[1]
        if len(prices_sorted) >= 3:
            room['price_exhibition'] = prices_sorted[2]

    # 驗證
    has_data = any([
        room['capacity_theater'],
        room['price_weekday'],
        room['area_sqm']
    ])

    return room if has_data else None


def extract_numbers(text):
    """提取所有數字"""
    matches = re.findall(r'[\d,]+', text)
    numbers = []
    for m in matches:
        try:
            numbers.append(int(m.replace(',', '')))
        except:
            pass
    return numbers


def main():
    print("="*80)
    print("TICC PDF Parser V6 - Precise Name Extraction")
    print("="*80)
    print()

    with open('ticc_pdf_raw.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")
    print()

    rooms = parse_ticc_v6(lines)

    print(f"Parsed {len(rooms)} rooms")
    print()

    # 儲存
    output = f'ticc_v6_precise_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    result = {
        'venue': 'TICC',
        'version': 6,
        'parser': 'precise_name_extraction',
        'parsed_at': datetime.now().isoformat(),
        'total_rooms': len(rooms),
        'rooms': rooms
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output}")
    print()

    # 驗證問題房間
    print("Problem rooms verification:")
    print("-"*40)

    test_rooms = ['102', '103', '105', '201', '401', '大會堂全場', '3樓南']
    for room in rooms:
        for test in test_rooms:
            if test in room['name'] or room['name'] == test:
                print(f"\n{room['name']}")
                print(f"  Capacity: {room.get('capacity_theater', 'N/A')}")
                print(f"  Area: {room.get('area_sqm', 'N/A')}")
                print(f"  Price: ${room.get('price_weekday', 'N/A'):,}")
                break

    print()
    print("="*80)
    print("Done - All room names should now be correct")
    print("="*80)


if __name__ == '__main__':
    main()
