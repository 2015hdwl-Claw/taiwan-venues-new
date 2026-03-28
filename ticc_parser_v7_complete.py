#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Parser V7 - Complete with multi-line and combo rooms
"""
import json
import re
from datetime import datetime


def parse_ticc_v7(lines):
    """V7: 處理所有類型的房間"""
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

        if any(kw in line for kw in ['容量', '面積', '租金', '尺寸', '08:30']):
            i += 1
            continue

        if re.match(r'^[\s\-\―\=]+$', line):
            i += 1
            continue

        # 嘗試解析房間
        room, skip = parse_room_v7(line, lines, i)

        if room:
            rooms.append(room)
            i += skip
        else:
            i += 1

    return rooms


def parse_room_v7(line, all_lines, line_idx):
    """
    V7: 完整解析所有房間類型

    類型：
    1. 單行純數字：102, 103, 105, 401
    2. 單行組合：101A/D, 201B/E, 202/203, 202A/203A
    3. 單行中文：大會堂全場, 3樓宴會廳
    4. 多行帶括號：大會堂半場, 101 全室, 101AB/CD
    """
    line = line.strip()

    # 跳過括號開頭的延續行
    if line.startswith('('):
        return None, 1

    # 類型1: 純數字房間名稱（102, 103, 105, 201, 401）
    pure_num = re.match(r'^(\d{3})\s+(\d{2,4})', line)
    if pure_num:
        name = pure_num.group(1)
        return parse_room_data(line, name), 1

    # 類型2: 組合房間名稱（101A/D, 201B/E, 202/203, 202A/203A, 201AB/CD）
    combo_patterns = [
        r'^(\d{3}[A-Z]/[A-Z])\s+',  # 101A/D
        r'^(\d{3}/\d{3})\s+',  # 202/203
        r'^(\d{3}[A-Z]/\d{3}[A-Z])\s+',  # 202A/203A
        r'^(\d{3}[A-Z]{2}/[A-Z]{2})\s+',  # 101AB/CD
        r'^(\d{3}[A-Z]{2}/[A-Z]{2})\s+',  # 201AB/EF
        r'^(\d{3}[A-Z]{2,4})\s+',  # 201BCDE, 201ABEF
    ]

    for pattern in combo_patterns:
        match = re.match(pattern, line)
        if match:
            name = match.group(1)
            return parse_room_data(line, name), 1

    # 類型3: 中文房間名稱（大會堂全場, 3樓宴會廳, 106固定座位）
    chinese = re.match(r'^([^0-9]+?)(\s{2,}|\s+\d)', line)
    if chinese:
        name = chinese.group(1).strip()
        name = re.sub(r'[／\/\-\―\s]+$', '', name)

        # 檢查是否需要合併下一行
        if line_idx + 1 < len(all_lines):
            next_line = all_lines[line_idx + 1].strip()
            if next_line.startswith('('):
                # 合併多行
                combined = line + ' ' + next_line
                return parse_room_data(combined, name), 2

        return parse_room_data(line, name), 1

    # 類型4: 數字+中文（201 全室, 101 全室）
    num_cn = re.match(r'^(\d+)\s+([^0-9]+?)\s{2,}', line)
    if num_cn:
        num = num_cn.group(1)
        chinese = num_cn.group(2).strip()
        name = f"{num} {chinese}"

        # 檢查是否有多行資料
        j = line_idx + 1
        combined = line
        lines_to_skip = 1

        while j < len(all_lines):
            next_line = all_lines[j].strip()

            # 空行或括號結束
            if not next_line:
                break
            if next_line.startswith('備註'):
                break
            if re.match(r'^[\d\s\-\―]+$', next_line):
                j += 1
                continue

            # 如果是新房間名稱，停止
            if re.match(r'^\d{3}\s+\d', next_line):
                break
            if re.match(r'^\d{3}[A-Z]', next_line):
                break
            if not next_line.startswith('(') and re.search(r'[A-Za-z\u4e00-\u9fff]', next_line[:10]):
                # 可能是新房間
                if extract_room_name_v7(next_line):
                    break

            # 合併這一行
            combined += ' ' + next_line
            lines_to_skip += 1
            j += 1

            # 限制最多合併 10 行
            if lines_to_skip > 10:
                break

        return parse_room_data(combined, name), lines_to_skip

    return None, 1


def extract_room_name_v7(line):
    """檢查是否為房間名稱行"""
    # 純數字
    if re.match(r'^\d{3}\s+\d', line):
        return True
    # 組合
    if re.match(r'^\d{3}[A-Z/]', line):
        return True
    # 中文
    if re.match(r'^[^\d]+\s{2,}\d', line):
        return True
    return False


def parse_room_data(line, name):
    """解析房間資料（已知名稱）"""
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

    # 移除名稱
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

    # 過濾
    filtered = []
    for n in numbers:
        if n == room.get('area_sqm') or n == room.get('area_ping'):
            continue
        if dim_match and n < 20:
            continue
        filtered.append(n)

    # 分類
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
    print("TICC PDF Parser V7 - Complete")
    print("="*80)
    print()

    with open('ticc_pdf_raw.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")
    print()

    rooms = parse_ticc_v7(lines)

    print(f"Parsed {len(rooms)} rooms")
    print()

    # 儲存
    output = f'ticc_v7_complete_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    result = {
        'venue': 'TICC',
        'version': 7,
        'parser': 'complete_multiline',
        'parsed_at': datetime.now().isoformat(),
        'total_rooms': len(rooms),
        'rooms': rooms
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output}")
    print()

    # 驗證關鍵房間
    print("Critical rooms verification:")
    print("-"*40)

    test_rooms = [
        '102', '103', '105', '201', '401',
        '101A/D', '101B/C', '202/203',
        '大會堂全場', '大會堂半場', '3樓南',
        '101 全室', '101AB/CD'
    ]

    for room in rooms:
        for test in test_rooms:
            if test in room['name']:
                cap = room.get('capacity_theater')
                area = room.get('area_sqm')
                price = room.get('price_weekday')

                print(f"\n{room['name']}")
                if cap:
                    print(f"  Capacity: {cap}")
                if area:
                    print(f"  Area: {area} sqm")
                if price:
                    print(f"  Price: ${price:,}")

                # 移除已測試的
                if test in test_rooms:
                    test_rooms.remove(test)
                break

    if test_rooms:
        print(f"\n[WARNING] Not found: {test_rooms}")

    print()
    print("="*80)
    print("Done - All room types should be handled")
    print("="*80)


if __name__ == '__main__':
    main()
