#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Parser V5 - Final version with correct column mapping
Column format: name | cap_theater | cap_class | cap_u | cap_neg | booth | area | dim | price_wd | price_we | price_ex
"""
import json
import re
from datetime import datetime


def parse_ticc_v5(lines):
    """V5 解析器 - 使用正確的欄位對應"""
    rooms = []
    i = 0
    in_data = False

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # 檢測資料開始
        if '劇院型' in line and '教室型' in line:
            in_data = True
            i += 1
            continue

        if not in_data:
            i += 1
            continue

        # 資料結束
        if '備註' in line or line.startswith('註'):
            break

        # 跳過標題
        if '容量' in line or '面積' in line or '租金' in line or '尺寸' in line:
            i += 1
            continue

        # 跳過分隔符
        if re.match(r'^[\s\-\―\=]+$', line):
            i += 1
            continue

        # 解析會議室
        room = parse_room_v5(line, lines, i)
        if room:
            rooms.append(room)
            i += 1
        else:
            i += 1

    return rooms


def parse_room_v5(line, all_lines, line_idx):
    """
    解析會議室 V5
    格式：name | cap_theater | cap_class | cap_u | cap_neg | booth | area | dim | price_wd | price_we | price_ex
    """
    line = line.strip()

    # 跳過括號開頭（這是延續資料）
    if line.startswith('('):
        return None

    # 提取會議室名稱
    # 名稱在第一個「多位空格+數字」之前
    # 格式：room_name  num1  num2  ...

    # 找到第一個數字的位置
    num_match = re.search(r'\s{2,}\d', line)
    if num_match:
        # 使用多空格模式
        name_end = num_match.start()
        name = line[:name_end].strip()
    else:
        # 備用：找第一個空格+數字
        num_match = re.search(r'\s+\d', line)
        if not num_match:
            return None
        name_end = num_match.start()
        name = line[:name_end].strip()

    # 清理名稱
    name = re.sub(r'[／\/\-\―\s]+$', '', name)

    if len(name) < 2:
        return None

    # 移除名稱後，提取數字
    data_part = line[name_end:]

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

    # 移除名稱後，提取數字
    numbers = extract_numbers(data_part)

    # 提取分數面積
    fraction = re.search(r'(\d+),?(\d+)/(\d+)', data_part)
    if fraction:
        room['area_sqm'] = int(fraction.group(1) + fraction.group(2))
        room['area_ping'] = int(fraction.group(3))

    # 提取尺寸
    dim_match = re.search(r'(\d+\.?\d*)[×x](\d+\.?\d*)[×x](\d+\.?\d*)', data_part)
    if dim_match:
        room['dimensions'] = f"{dim_match.group(1)}×{dim_match.group(2)}×{dim_match.group(3)}"

    # 移除面積和尺寸數字
    filtered = []
    for n in numbers:
        # 跳過面積
        if n == room.get('area_sqm') or n == room.get('area_ping'):
            continue
        # 跳過尺寸中的小數（只有當有尺寸時且數字很小）
        if dim_match and n < 20:
            # 這可能是尺寸的一部分（如 3.7, 5.6 等）
            continue
        filtered.append(n)

    # 分類數字到欄位
    # 容量：10-5000（通常是前面的數字）
    # 價格：>5000（通常是後面的數字）

    # 找出所有可能的容量（10-5000）
    capacities = [n for n in filtered if 10 <= n <= 5000]

    # 找出所有可能的價格（>5000）
    prices = [n for n in filtered if n > 5000]

    # 分配容量（最多4個：劇院、教室、U、洽談）
    if capacities:
        # 特殊處理：如果第一個數字很大（>2000），可能是特殊場地
        if capacities[0] > 2000:
            room['capacity_theater'] = capacities[0]
        else:
            if len(capacities) >= 1:
                room['capacity_theater'] = capacities[0]
            if len(capacities) >= 2:
                room['capacity_classroom'] = capacities[1]
            if len(capacities) >= 3:
                room['capacity_u'] = capacities[2]
            if len(capacities) >= 4:
                room['capacity_negotiate'] = capacities[3]
            if len(capacities) >= 5:
                # 第5個可能是特殊容量
                pass

    # 分配價格（平日、假日、展覽）
    if prices:
        # 排序並分配
        prices_sorted = sorted(prices)
        if len(prices_sorted) >= 1:
            room['price_weekday'] = prices_sorted[0]
        if len(prices_sorted) >= 2:
            room['price_weekend'] = prices_sorted[1]
        if len(prices_sorted) >= 3:
            room['price_exhibition'] = prices_sorted[2]

    # 驗證：至少有一個資料
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
    print("TICC PDF Parser V5 - Final")
    print("="*80)
    print()

    with open('ticc_pdf_raw.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")
    print()

    rooms = parse_ticc_v5(lines)

    print(f"Parsed {len(rooms)} rooms")
    print()

    # 儲存
    output = f'ticc_v5_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    result = {
        'venue': 'TICC',
        'version': 5,
        'parser': 'final',
        'parsed_at': datetime.now().isoformat(),
        'total_rooms': len(rooms),
        'rooms': rooms
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output}")
    print()

    # 驗證關鍵會議室
    print("Critical rooms verification:")
    print("-"*40)

    key_tests = [
        ('大會堂全場', 3100, 2973, 159000),
        ('大會堂半場', 1208, None, 112000),
        ('3樓南', 90, 152, 18500)
    ]

    for room in rooms:
        for name, exp_cap, exp_area, exp_price in key_tests:
            if name in room['name']:
                cap = room.get('capacity_theater')
                area = room.get('area_sqm')
                price = room.get('price_weekday')

                status = []
                if exp_cap and cap == exp_cap:
                    status.append(f"Cap OK ({cap})")
                elif exp_cap:
                    status.append(f"Cap: got {cap}, expected {exp_cap}")

                if exp_area and area == exp_area:
                    status.append(f"Area OK ({area})")
                elif exp_area:
                    status.append(f"Area: got {area}, expected {exp_area}")

                if exp_price and price == exp_price:
                    status.append(f"Price OK ({price})")
                elif exp_price:
                    status.append(f"Price: got {price}, expected {exp_price}")

                print(f"\n{room['name']}")
                for s in status:
                    print(f"  {s}")
                break

    print()
    print("="*80)
    print("Done - Check ticc_v5_final_*.json for all rooms")
    print("="*80)


if __name__ == '__main__':
    main()
