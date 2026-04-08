#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Parser V8 - Final version
Handles all room types including Chinese names
"""
import json
import re
from datetime import datetime


def parse_ticc_v8(lines):
    """V8: 完整解析所有房間"""
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

        if any(kw in line for kw in ['容量', '面積', '租金', '尺寸', '08:30', '每時段']):
            i += 1
            continue

        if re.match(r'^[\s\-\―\=]+$', line):
            i += 1
            continue

        # 解析房間
        room, skip = parse_room_v8(line, lines, i)

        if room:
            rooms.append(room)
            i += skip
        else:
            i += 1

    return rooms


def parse_room_v8(line, all_lines, line_idx):
    """
    V8: 完整處理所有房間

    優先順序：
    1. 純數字：102, 103, 105, 401
    2. 組合：101A/D, 202/203, 202A/203A
    3. 中文：大會堂全場, 3樓南/北軒, 106固定座位
    4. 數字+中文：101 全室, 201 全室
    """
    line = line.strip()

    # 跳過括號開頭（資料延續）
    if line.startswith('('):
        return None, 1

    # 1. 純數字房間名稱（102, 103, 105, 201, 401）
    pure_num = re.match(r'^(\d{3})\s+(\d{2,4})', line)
    if pure_num:
        name = pure_num.group(1)
        return parse_room_data(line, name), 1

    # 2. 組合房間名稱
    combo_patterns = [
        (r'^(\d{3}[A-Z]/[A-Z])\s+', '101A/D'),
        (r'^(\d{3}/\d{3})\s+', '202/203'),
        (r'^(\d{3}[A-Z]/\d{3}[A-Z])\s+', '202A/203A'),
        (r'^(\d{3}[A-Z]{2}/[A-Z]{2})\s+', '101AB/CD'),
        (r'^(\d{3}[A-Z]{2,4})\s+', '201BCDE'),
    ]

    for pattern, _ in combo_patterns:
        match = re.match(pattern, line)
        if match:
            name = match.group(1)
            return parse_room_data(line, name), 1

    # 3. 中文房間名稱（包含3樓、4樓等）
    # 匹配：中文開始 + 空格 + 數字/其他內容
    chinese_match = re.match(r'^([\u4e00-\u9fff0-9a-zA-Z\/\‐\―]+?)\s{2,}', line)
    if chinese_match:
        name = chinese_match.group(1).strip()
        # 清理尾部分隔符
        name = re.sub(r'[／\/\-\―\s]+$', '', name)

        if len(name) >= 2:
            # 檢查是否需要合併下一行
            if line_idx + 1 < len(all_lines):
                next_line = all_lines[line_idx + 1].strip()
                if next_line.startswith('('):
                    # 多行房間
                    combined = line + ' ' + next_line
                    return parse_room_data(combined, name), 2

            return parse_room_data(line, name), 1

    # 4. 數字+中文（101 全室）
    num_cn = re.match(r'^(\d+)\s+([\u4e00-\u9fff]+)', line)
    if num_cn:
        num = num_cn.group(1)
        chinese = num_cn.group(2).strip()
        name = f"{num} {chinese}"

        # 檢查多行資料
        j = line_idx + 1
        combined = line
        skip_lines = 1

        while j < len(all_lines) and skip_lines <= 10:
            next_line = all_lines[j].strip()

            if not next_line:
                break
            if '備註' in next_line:
                break

            # 檢查是否為新房間
            if re.match(r'^\d{3}\s+\d', next_line):
                break
            if re.match(r'^\d{3}[A-Z]', next_line):
                break
            if re.match(r'^[\u4e00-\u9fff]+', next_line) and not next_line.startswith('('):
                break

            combined += ' ' + next_line
            skip_lines += 1
            j += 1

        return parse_room_data(combined, name), skip_lines

    return None, 1


def parse_room_data(line, name):
    """解析房間資料"""
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
    name_escaped = re.escape(name)
    data_part = re.sub(f'^{name_escaped}\\s*', '', line)

    # 分數面積
    fraction = re.search(r'(\d+),?(\d+)/(\d+)', data_part)
    if fraction:
        room['area_sqm'] = int(fraction.group(1) + fraction.group(2))
        room['area_ping'] = int(fraction.group(3))

    # 尺寸
    dim_match = re.search(r'(\d+\.?\d*)[×x](\d+\.?\d*)[×x](\d+\.?\d*)', data_part)
    if dim_match:
        room['dimensions'] = f"{dim_match.group(1)}×{dim_match.group(2)}×{dim_match.group(3)}"

    # 數字
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

    # 容量
    if capacities:
        if len(capacities) >= 1:
            room['capacity_theater'] = capacities[0]
        if len(capacities) >= 2:
            room['capacity_classroom'] = capacities[1]
        if len(capacities) >= 3:
            room['capacity_u'] = capacities[2]
        if len(capacities) >= 4:
            room['capacity_negotiate'] = capacities[3]

    # 價格
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
    print("TICC PDF Parser V8 - FINAL")
    print("="*80)
    print()

    with open('ticc_pdf_raw.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")
    print()

    rooms = parse_ticc_v8(lines)

    print(f"Parsed {len(rooms)} rooms")
    print()

    # 儲存
    output = f'ticc_v8_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    result = {
        'venue': 'TICC',
        'version': 8,
        'parser': 'final_all_types',
        'parsed_at': datetime.now().isoformat(),
        'total_rooms': len(rooms),
        'rooms': rooms
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output}")
    print()

    # 列出所有房間名稱
    print("All rooms:")
    print("-"*40)
    for i, room in enumerate(rooms, 1):
        cap = room.get('capacity_theater')
        area = room.get('area_sqm')
        cap_str = f"{cap}" if cap else "N/A"
        area_str = f"{area}" if area else "N/A"
        print(f"{i:2}. {room['name']:20} Cap:{cap_str:>6} Area:{area_str:>6}")

    print()
    print("="*80)
    print("Done - All rooms should be captured")
    print("="*80)


if __name__ == '__main__':
    main()
