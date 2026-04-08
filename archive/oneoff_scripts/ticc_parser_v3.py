#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Parser V3 - Handles multi-line room data
Fixes issues with:
- "大會堂半場" data on next line
- Room names with special characters (3樓南/北軒, 101A/D)
- Parenthetical notes ((彈射椅), (1-27 排))
"""
import json
import re
from datetime import datetime


def parse_ticc_lines(lines):
    """
    解析 TICC PDF 行，處理跨行資料
    """
    rooms = []
    i = 0
    data_start = False

    while i < len(lines):
        line = lines[i].strip()

        # 跳過空行
        if not line:
            i += 1
            continue

        # 檢測資料開始
        if '會議室名稱' in line and '容量' in line:
            data_start = True
            i += 1
            continue

        if not data_start:
            i += 1
            continue

        # 檢測資料結束
        if '註' in line or '備註' in line or '聯絡' in line:
            break

        # 跳過標題行（非資料）
        if '劇院型' in line or '教室型' in line or '容量' in line:
            i += 1
            continue

        # 跳過頁碼和分隔線
        if re.match(r'^[\d\s\-\――]+$', line) and len(line) < 30:
            i += 1
            continue

        # 檢查是否為會議室名稱行
        room_name = extract_room_name_v2(line)

        if room_name:
            print(f"[DEBUG] Line {i}: Found room '{room_name}'")
            # 提取當前行的數字
            current_numbers = extract_numbers(line)
            current_dimensions = extract_dimensions(line)

            # 如果當前行沒有足夠的數字，往後看
            if len(current_numbers) < 3:
                # 讀取下一行
                j = i + 1
                combined_line = line

                while j < len(lines):
                    next_line = lines[j].strip()

                    # 空行表示結束
                    if not next_line:
                        break

                    # 如果是新的會議室名稱（不是以括號或數字開頭），停止
                    if not next_line.startswith('(') and not re.match(r'^[\d\(\[]', next_line):
                        # 檢查是否為純文字行（可能是新會議室）
                        if extract_room_name_v2(next_line):
                            break

                    # 合併到當前行
                    combined_line += ' ' + next_line
                    j += 1

                    # 限制最多合併 5 行
                    if j - i > 5:
                        break

                # 使用合併後的行解析
                room = parse_room_from_line(combined_line, room_name)
                i = j  # 跳到已處理的行
            else:
                # 當前行已經有足夠資料
                room = parse_room_from_line(line, room_name)
                i += 1

            if room:
                rooms.append(room)
        else:
            i += 1

    return rooms


def extract_room_name_v2(line):
    """
    V2: 更準確地提取會議室名稱
    處理：3樓南/北軒、101A/D、大會堂全場等
    """
    # 移除行首空白
    line = line.lstrip()

    # 跳過以括號開頭的行（這是資料延續）
    if line.startswith('(') or line.startswith('['):
        return None

    # 跳過以數字開頭的行（這是純資料行）
    if re.match(r'^\d', line):
        return None

    # 策略：會議室名稱在第一個數字之前
    # 使用簡單方法：找第一個獨立的數字（前面有空格）

    # 尋找第一個「空白+數字」的模式
    match = re.search(r'(\s+[0-9])', line)

    if match:
        # 名稱在第一個數字之前
        name_end = match.start()
        name = line[:name_end].strip()

        # 清理名稱
        name = re.sub(r'[／\/\-\―\s]+$', '', name)

        # 過濾太短或無意義
        if len(name) >= 2 and name not in ['－', '—', '']:
            return name

    # 備用：使用第一個「—」之前的部分
    match2 = re.match(r'^([^—\-]+?)[—\-]', line)
    if match2:
        name = match2.group(1).strip()
        if len(name) >= 2:
            return name

    # 備用 2：直接看行首
    parts = re.split(r'[\d\s]+', line, 1)
    if parts and parts[0]:
        name = parts[0].strip()
        if len(name) >= 2:
            return name

    return None


def parse_room_from_line(line, name_hint=None):
    """
    從單行文字（可能已合併多行）解析會議室資料
    """
    room = {
        'name': name_hint or '',
        'capacity_theater': None,
        'capacity_classroom': None,
        'capacity_u': None,
        'capacity_negotiate': None,
        'area_sqm': None,
        'area_ping': None,
        'dimensions': None,
        'price_weekday': None,
        'price_weekend': None,
        'price_exhibition': None,
        'booth_3x2': None
    }

    # 如果沒有名稱提示，嘗試提取
    if not room['name']:
        room['name'] = extract_room_name_v2(line) or 'Unknown'

    # 提取所有數字
    numbers = extract_numbers(line)

    # 智能分配數字到欄位
    # 根據 TICC PDF 的格式順序：
    # 價格(平日) 價格(假日) 容量/面積 尺寸 其他

    idx = 0
    for num in numbers:
        if num > 100000:
            # 大額價格（展覽）
            if room['price_exhibition'] is None:
                room['price_exhibition'] = num
            elif room['price_weekday'] is None:
                room['price_weekday'] = num
        elif num > 10000:
            # 一般價格
            if room['price_weekday'] is None:
                room['price_weekday'] = num
            elif room['price_weekend'] is None:
                room['price_weekend'] = num
        elif 1000 <= num <= 5000:
            # 可能是容量或面積
            if room['capacity_theater'] is None:
                room['capacity_theater'] = num
            elif room['area_sqm'] is None:
                room['area_sqm'] = num
        elif 100 <= num <= 999:
            # 中等容量或小面積
            if room['capacity_classroom'] is None:
                room['capacity_classroom'] = num
            elif room['capacity_u'] is None:
                room['capacity_u'] = num
            elif room['area_ping'] is None:
                room['area_ping'] = num
        elif 10 <= num <= 99:
            # 小容量
            if room['capacity_negotiate'] is None:
                room['capacity_negotiate'] = num

    # 提取尺寸
    dimensions = extract_dimensions(line)
    if dimensions:
        room['dimensions'] = dimensions

    # 提取面積分數（如 2,973/899）
    fraction = re.search(r'(\d+),?(\d+)/(\d+)', line)
    if fraction:
        sqm = int(fraction.group(1) + fraction.group(2))
        ping = int(fraction.group(3))
        room['area_sqm'] = sqm
        room['area_ping'] = ping

    # 驗證資料：至少有一個有意義的欄位
    has_data = any([
        room['capacity_theater'],
        room['price_weekday'],
        room['area_sqm']
    ])

    return room if has_data else None


def extract_numbers(line):
    """提取所有數字"""
    matches = re.findall(r'[\d,]+', line)
    numbers = []
    for m in matches:
        try:
            numbers.append(int(m.replace(',', '')))
        except:
            pass
    return numbers


def extract_dimensions(line):
    """提取尺寸資訊"""
    # 匹配 25.8×25.3×5.6 格式
    match = re.search(r'(\d+\.?\d*)[×x](\d+\.?\d*)[×x](\d+\.?\d*)', line)
    if match:
        return f"{match.group(1)}×{match.group(2)}×{match.group(3)}"
    return None


def main():
    print("="*80)
    print("TICC PDF Parser V3")
    print("="*80)
    print()

    # 讀取原始文字
    with open('ticc_pdf_raw.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")
    print()

    # 解析
    rooms = parse_ticc_lines(lines)

    print(f"Parsed {len(rooms)} rooms")
    print()

    # 儲存
    output = f'ticc_v3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    result = {
        'venue': 'TICC',
        'version': 3,
        'parsed_at': datetime.now().isoformat(),
        'total_rooms': len(rooms),
        'rooms': rooms
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output}")
    print()

    # 驗證關鍵會議室
    print("Key rooms verification:")
    print("-" * 40)

    key_rooms = ['大會堂全場', '大會堂半場', '3樓']
    for room in rooms:
        for key in key_rooms:
            if key in room['name']:
                print(f"\n{room['name']}")
                if room['capacity_theater']:
                    print(f"  Capacity: {room['capacity_theater']} people")
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
