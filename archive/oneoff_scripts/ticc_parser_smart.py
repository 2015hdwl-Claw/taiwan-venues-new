#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Smart Parser
直接處理已提取的文字，解決多行資料和特殊字元的問題
"""
import json
import re
from datetime import datetime


def parse_ticc_raw_text(raw_text_path):
    """
    智能解析 TICC PDF 原始文字，處理：
    1. 多行資料（大會堂半場）
    2. 特殊字元（3樓南/北軒）
    3. 複雜格式（斜線、括號）
    """
    rooms = []

    print(f"讀取原始文字: {raw_text_path}")

    with open(raw_text_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"共 {len(lines)} 行")
    print()

    # 狀態機
    in_data_section = False
    current_room = None
    line_number = 0

    for line in lines:
        line_number += 1
        line = line.strip()

        # 跳過空行
        if not line:
            continue

        # 檢測資料開始
        if '場地名稱' in line and '平日' in line:
            in_data_section = True
            print(f"[{line_number}] 找到資料開始標記")
            continue

        if not in_data_section:
            continue

        # 檢測資料結束
        if '註' in line or '備註' in line:
            print(f"[{line_number}] 資料結束")
            break

        # 跳過頁碼行
        if re.match(r'^\-+[\d\s]+\-+$', line) or re.match(r'^[\d\s\/]+$', line):
            continue

        # 解析會議室資料
        room, has_more = parse_line_smart(line, current_room)

        if room:
            if has_more:
                # 資料延續到下一行
                current_room = room
            else:
                # 會議室資料完整
                rooms.append(room)
                current_room = None

                # 只顯示前幾個
                if len(rooms) <= 10:
                    print(f"[{line_number}] {room['name']}: {room.get('capacity_theater', 'N/A')}人")

    return rooms


def parse_line_smart(line, previous_room=None):
    """
    智能解析單行，考慮：
    1. 是否為新會議室（有名稱）
    2. 是否為延續資料（以括號開頭）
    3. 特殊格式處理（斜線、分數）
    """
    room = None
    has_more = False

    # 檢查是否為括號開頭（表示上一行的延續）
    if line.startswith('('):
        if previous_room:
            # 合併到上一個會議室
            room = previous_room
            has_more = True

            # 解析括號後的數字
            numbers = extract_numbers(line)

            # 這些數字可能是容量
            if numbers and room.get('capacity_theater') is None:
                room['capacity_theater'] = numbers[0]
                if len(numbers) > 1:
                    room['capacity_classroom'] = numbers[1]

            # 尋找價格
            prices = [n for n in numbers if n > 10000]
            if prices:
                if room.get('price_weekday') is None:
                    room['price_weekday'] = prices[0]
                if len(prices) > 1 and room.get('price_weekend') is None:
                    room['price_weekend'] = prices[1]

        return room, has_more

    # 提取場地名稱
    name = extract_room_name(line)

    if not name:
        # 沒有名稱，可能是延續資料
        if previous_room:
            room = previous_room
            has_more = False  # 應該是最後一行了
            update_room_with_numbers(room, line)
        return room, has_more

    # 創建新會議室
    room = {
        'name': name,
        'capacity_theater': None,
        'capacity_classroom': None,
        'capacity_u': None,
        'area_sqm': None,
        'area_ping': None,
        'dimensions': None,
        'price_weekday': None,
        'price_weekend': None,
        'price_exhibition': None
    }

    # 解析數字
    update_room_with_numbers(room, line)

    # 檢查是否有更多資料在下一行
    # 如果這一行只有名稱而沒有足夠的數字資料，可能有下一行
    numbers = extract_numbers(line)
    if len(numbers) < 3:
        has_more = True

    return room, has_more


def extract_room_name(line):
    """
    提取會議室名稱，處理特殊情況：
    - 3樓南/北軒（斜線）
    - 101A/D（字母組合）
    - 集會堂1-4（數字範圍）
    """
    # 移除前面的數字和空格
    line = re.sub(r'^[\d\s]+', '', line)

    # 場地名稱通常在第一個數字之前
    # 但有些名稱包含數字（如 3樓、101）

    # 策略：找第一個大數字（價格或容量）之前的部分
    match = re.search(r'([^0-9]*?)(\d{2,4})', line)

    if match:
        potential_name = match.group(1).strip()

        # 清理特殊字元
        potential_name = potential_name.rstrip('／/\\—－')

        # 過濾掉太短或無意義的字串
        if len(potential_name) >= 2:
            return potential_name

    # 備用策略：如果沒有大數字，直接用非數字部分
    parts = re.split(r'[\d,]+', line)
    for part in parts:
        part = part.strip().rstrip('／/\\—－')
        if len(part) >= 2 and part not in ['－', '—', '']:
            return part

    return None


def extract_numbers(line):
    """提取所有數字"""
    numbers = re.findall(r'[\d,]+', line)
    result = []
    for n in numbers:
        try:
            result.append(int(n.replace(',', '')))
        except:
            continue
    return result


def update_room_with_numbers(room, line):
    """從文字中提取並更新會議室的數字資料"""
    numbers = extract_numbers(line)

    if not numbers:
        return

    # 智能分類數字
    for num in numbers:
        # 價格 > 10000
        if num > 10000:
            if room['price_weekday'] is None:
                room['price_weekday'] = num
            elif room['price_weekend'] is None:
                room['price_weekend'] = num
            elif room['price_exhibition'] is None:
                room['price_exhibition'] = num

        # 容量 10-2000
        elif 10 <= num <= 2000:
            if room['capacity_theater'] is None:
                room['capacity_theater'] = num
            elif room['capacity_classroom'] is None:
                room['capacity_classroom'] = num
            elif room['capacity_u'] is None:
                room['capacity_u'] = num

        # 面積 10-10000
        elif 10 <= num <= 10000:
            if room['area_sqm'] is None:
                room['area_sqm'] = num
            elif room['area_ping'] is None:
                room['area_ping'] = num

    # 提取尺寸（如 18×7.5×3.7）
    dimension_match = re.search(r'(\d+\.?\d*)[×x](\d+\.?\d*)[×x](\d+\.?\d*)', line)
    if dimension_match:
        room['dimensions'] = f"{dimension_match.group(1)}×{dimension_match.group(2)}×{dimension_match.group(3)}"

    # 提取分數格式（如 2,973/899）
    fraction_match = re.search(r'(\d+),?(\d+)/(\d+)', line)
    if fraction_match:
        # 可能是 面積㎡/面積坪
        sqm = int(fraction_match.group(1) + fraction_match.group(2))
        ping = int(fraction_match.group(3))
        if room['area_sqm'] is None:
            room['area_sqm'] = sqm
        if room['area_ping'] is None:
            room['area_ping'] = ping


def main():
    print("="*80)
    print("TICC PDF 智能解析器")
    print("="*80)
    print()

    # 解析原始文字
    raw_text_path = "ticc_pdf_raw.txt"

    import os
    if not os.path.exists(raw_text_path):
        print(f"錯誤：找不到檔案 {raw_text_path}")
        return

    rooms = parse_ticc_raw_text(raw_text_path)

    if rooms:
        print()
        print("="*80)
        print(f"解析完成：共 {len(rooms)} 個會議室")
        print("="*80)

        # 儲存結果
        output_path = f"ticc_parsed_smart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        result = {
            'venue': 'TICC',
            'parsed_at': datetime.now().isoformat(),
            'parser': 'smart_raw_text',
            'total_rooms': len(rooms),
            'rooms': rooms
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n已儲存到: {output_path}")

        # 驗證關鍵會議室
        print("\n關鍵會議室驗證：")
        key_rooms = ['大會堂全場', '大會堂半場', '3樓南']
        found_count = 0

        for room in rooms:
            for key in key_rooms:
                if key in room['name']:
                    print(f"\n{room['name']}:")
                    print(f"  容量(劇院): {room.get('capacity_theater', 'N/A')}")
                    print(f"  面積(㎡): {room.get('area_sqm', 'N/A')}")
                    print(f"  平日價: ${room.get('price_weekday', 'N/A')}")
                    found_count += 1
                    break

        if found_count == 0:
            print("  [警告] 找不到關鍵會議室")

        # 顯示統計
        print("\n資料統計：")
        with_capacity = sum(1 for r in rooms if r.get('capacity_theater'))
        with_area = sum(1 for r in rooms if r.get('area_sqm'))
        with_price = sum(1 for r in rooms if r.get('price_weekday'))

        print(f"  有容量資料: {with_capacity}/{len(rooms)} ({with_capacity*100//len(rooms)}%)")
        print(f"  有面積資料: {with_area}/{len(rooms)} ({with_area*100//len(rooms)}%)")
        print(f"  有價格資料: {with_price}/{len(rooms)} ({with_price*100//len(rooms)}%)")

    else:
        print("解析失敗")


if __name__ == '__main__':
    main()
