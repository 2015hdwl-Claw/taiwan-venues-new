#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Parser V4 - More robust room detection
"""
import json
import re
from datetime import datetime


def is_header_line(line):
    """檢查是否為標題行"""
    header_keywords = [
        '會議室名稱', '容量', '面積', '尺寸', '租金', '展覽',
        '公尺', '坪', '週一', '週六', '劇院型', '教室型',
        '08:30', '12:30', '17:30', '22:30', '每時段'
    ]
    return any(kw in line for kw in header_keywords)


def parse_ticc_v4(lines):
    """V4 解析器 - 更準確的會議室識別"""
    rooms = []
    i = 0
    in_data = False

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # 檢測資料開始
        if '會議室名稱' in line:
            in_data = True
            i += 1
            continue

        if not in_data:
            i += 1
            continue

        # 資料結束
        if '備註' in line or '註' in line:
            break

        # 跳過標題行
        if is_header_line(line):
            i += 1
            continue

        # 跳過純分隔符
        if re.match(r'^[\s\-\――]+$', line):
            i += 1
            continue

        # 嘗試解析會議室
        room = parse_room_line(line, lines, i)
        if room:
            rooms.append(room)
            # 根據資料完整性決定是否跳過下一行
            numbers = extract_numbers(line)
            if len(numbers) >= 5:
                i += 1  # 完整資料，移到下一行
            else:
                # 資料不完整，可能需要跳過下一行
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('('):
                    i += 2  # 跳過下一行的括號資料
                else:
                    i += 1
        else:
            i += 1

    return rooms


def parse_room_line(line, all_lines, line_idx):
    """解析單行會議室資料"""
    # 檢查是否為有效的會議室行
    # 特徵：包含中文或字母數字組合的名稱 + 數字資料

    # 提取會議室名稱
    room_name = extract_room_name_v4(line)

    if not room_name:
        return None

    # 檢查下一行是否有括號資料
    next_line = ""
    if line_idx + 1 < len(all_lines):
        nl = all_lines[line_idx + 1].strip()
        if nl.startswith('('):
            next_line = nl

    # 合併當前行和可能的括號行
    combined = line + " " + next_line

    # 解析資料
    room = {
        'name': room_name,
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

    # 先提取分數面積和尺寸（這些有特殊格式）
    fraction = re.search(r'(\d+),?(\d+)/(\d+)', combined)
    if fraction:
        room['area_sqm'] = int(fraction.group(1) + fraction.group(2))
        room['area_ping'] = int(fraction.group(3))

    dim_match = re.search(r'(\d+\.?\d*)[×x](\d+\.?\d*)[×x](\d+\.?\d*)', combined)
    if dim_match:
        room['dimensions'] = f"{dim_match.group(1)}×{dim_match.group(2)}×{dim_match.group(3)}"

    # 移除會議室名稱後再提取數字
    # 這樣可以避免將名稱中的數字（如 101A/D 中的 101）計入容量
    data_part = combined
    if room_name in combined:
        # 找到名稱結束位置
        name_end = combined.find(room_name) + len(room_name)
        data_part = combined[name_end:]

    # 從資料部分提取數字
    numbers = extract_numbers(data_part)

    # 移除面積和尺寸中的數字
    filtered_nums = []
    for n in numbers:
        # 跳過面積數值
        if n == room.get('area_sqm') or n == room.get('area_ping'):
            continue
        # 跳過尺寸中的小數
        if n < 100 and '.' in data_part:
            # 可能是尺寸的一部分
            continue
        filtered_nums.append(n)

    # 智能分配：價格 > 10000，容量 10-2000
    capacities = [n for n in filtered_nums if 10 <= n <= 2000]
    prices = [n for n in filtered_nums if n > 10000]

    # 分配容量（通常前幾個是容量）
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
        # 排序價格
        prices_sorted = sorted(prices)
        if len(prices_sorted) >= 1:
            room['price_weekday'] = prices_sorted[0]
        if len(prices_sorted) >= 2:
            room['price_weekend'] = prices_sorted[1]
        if len(prices_sorted) >= 3:
            room['price_exhibition'] = prices_sorted[2]

    # 驗證：至少有一個數值欄位
    has_data = any([
        room['capacity_theater'],
        room['price_weekday'],
        room['area_sqm']
    ])

    return room if has_data else None


def extract_room_name_v4(line):
    """V4: 提取會議室名稱，更準確識別"""
    line = line.strip()

    # 跳過括號開頭
    if line.startswith('('):
        return None

    # 跳過純數字或符號
    if re.match(r'^[\d\s\-\――]+$', line):
        return None

    # 檢查是否包含數字資料（有效的會議室行應該有）
    if not re.search(r'\d', line):
        return None

    # 找第一個「多個空白+數字」的位置（至少2個空格）
    # 這是名稱的結束位置，因為數據欄位通常有多個空格分隔
    match = re.search(r'\s{2,}\d', line)

    if match:
        name = line[:match.start()].strip()

        # 清理斜線和分隔符
        name = re.sub(r'[／\/\-\―\s]+$', '', name)

        # 驗證名稱長度
        if len(name) >= 2:
            return name

    # 備用：單空格分隔
    match = re.search(r'\s\d{3}', line)  # 尋找3位數（容量通常是3位數）
    if match:
        name = line[:match.start()].strip()
        name = re.sub(r'[／\/\-\―\s]+$', '', name)
        if len(name) >= 2:
            return name

    return None


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
    print("TICC PDF Parser V4")
    print("="*80)
    print()

    with open('ticc_pdf_raw.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")
    print()

    rooms = parse_ticc_v4(lines)

    print(f"Parsed {len(rooms)} rooms")
    print()

    # 儲存
    output = f'ticc_v4_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    result = {
        'venue': 'TICC',
        'version': 4,
        'parsed_at': datetime.now().isoformat(),
        'total_rooms': len(rooms),
        'rooms': rooms
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output}")
    print()

    # 驗證關鍵會議室
    print("Key rooms check:")
    print("-"*40)

    key_keywords = ['大會堂', '3樓', '101', '201']
    for room in rooms:
        for key in key_keywords:
            if key in room['name']:
                print(f"\n{room['name']}")
                if room['capacity_theater']:
                    print(f"  Capacity: {room['capacity_theater']}")
                if room['area_sqm']:
                    print(f"  Area: {room['area_sqm']} sqm")
                if room['price_weekday']:
                    print(f"  Price: ${room['price_weekday']:,}")
                break

    print()
    print("="*80)
    print("Done")
    print("="*80)


if __name__ == '__main__':
    main()
