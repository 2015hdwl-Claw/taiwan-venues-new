#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF Parser using pdfplumber
Better table extraction for multi-line and complex data
"""
import pdfplumber
import json
import re
from datetime import datetime

def parse_ticc_pdf(pdf_path):
    """
    使用 pdfplumber 解析 TICC PDF，支援複雜表格結構
    """
    rooms = []

    print(f"正在解析 PDF: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"PDF 頁數: {len(pdf.pages)}")

            # 處理每一頁
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"\n處理第 {page_num} 頁...")
                text = page.extract_text()

                if not text:
                    print(f"  第 {page_num} 頁沒有文字")
                    continue

                # 分割成行
                lines = text.split('\n')

                # 尋找表格數據開始標記
                data_start = False
                room_data_buffer = {}  # 用於累積多行的會議室資料

                for i, line in enumerate(lines):
                    line = line.strip()

                    # 跳過空行
                    if not line:
                        continue

                    # 檢測表格標題行
                    if '場地名稱' in line or '平日' in line or '假日' in line:
                        data_start = True
                        print(f"  找到表格標題: {line}")
                        continue

                    if not data_start:
                        continue

                    # 檢查是否為頁碼或頁尾
                    if re.match(r'^[\d\s\-]*$', line) and len(line) < 10:
                        continue

                    # 解析會議室資料
                    room = parse_room_line(line, lines, i)

                    if room:
                        rooms.append(room)
                        print(f"  ✓ {room['name']}: {room.get('capacity_theater', 'N/A')} 人")

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

    return rooms


def parse_room_line(line, all_lines, current_index):
    """
    解析單一行或跨多行的會議室資料
    """
    # 跳過明顯的非資料行
    if any(keyword in line for keyword in ['場地名稱', '註', '備註', '聯絡']):
        return None

    # 檢查是否為頁碼
    if re.match(r'^[\d\s\-]*$|^\d+\s*\/\s*\d+$', line) and len(line) < 20:
        return None

    # 檢查是否有價格數字（表示這是資料行）
    has_price = bool(re.search(r'\d{3,5},?\d*', line))
    has_capacity = bool(re.search(r'\d{2,4}', line))

    if not (has_price or has_capacity):
        return None

    # 使用正則表達式提取資料
    # 模式：場地名稱 價格1 價格2 ... 容量/面積 ... 其他價格
    room = {
        'name': '',
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

    # 提取場地名稱（通常是第一個非數字部分）
    # 移除前面的數字和空格
    name_match = re.match(r'^([^0-9\‐\−]+)', line)
    if name_match:
        potential_name = name_match.group(1).strip()
        # 清理名稱
        if len(potential_name) > 1 and potential_name not in ['－', '—', '']:
            room['name'] = potential_name

    # 檢查下一行是否有括號說明（如 "(1-27 排)"）
    if current_index + 1 < len(all_lines):
        next_line = all_lines[current_index + 1].strip()
        if next_line.startswith('(') and ')' in next_line:
            # 這可能是補充資訊，合併到名稱或記錄為說明
            if room['name']:
                room['name'] += ' ' + next_line
            # 繼續處理下一行的數字資料
            line += ' ' + all_lines[current_index + 1]

    # 提取所有數字（包括逗號分隔）
    all_numbers = re.findall(r'[\d,]+', line)
    numbers = [int(n.replace(',', '')) for n in all_numbers if n.replace(',', '').isdigit()]

    if len(numbers) < 2:
        return None

    # 智能判斷數字欄位
    # TICC PDF 格式：價格(平日) 價格(假日) 容量/面積 價格(展覽) ...
    # 需要根據數字大小範圍判斷

    idx = 0
    capacity_found = False

    for num in numbers:
        if idx >= len(numbers):
            break

        num = numbers[idx]

        # 價格通常 > 10000
        if num > 10000:
            if room['price_weekday'] is None:
                room['price_weekday'] = num
            elif room['price_weekend'] is None:
                room['price_weekend'] = num
            elif room['price_exhibition'] is None:
                room['price_exhibition'] = num

        # 容量通常在 10-2000 之間
        elif 10 <= num <= 2000:
            if not capacity_found:
                room['capacity_theater'] = num
                capacity_found = True
            elif room['capacity_classroom'] is None:
                room['capacity_classroom'] = num
            elif room['capacity_u'] is None:
                room['capacity_u'] = num

        # 面積通常在 10-10000 之間
        elif 10 <= num <= 10000:
            # 判斷是平方公尺或坪
            if room['area_sqm'] is None:
                room['area_sqm'] = num
            elif room['area_ping'] is None:
                room['area_ping'] = num

        idx += 1

    # 如果名稱為空但有數字，嘗試從行首提取
    if not room['name']:
        # 移除所有數字和符號，看看剩下什麼
        text_parts = re.split(r'[\d,\/\‐\−\s]+', line)
        for part in text_parts:
            if part and len(part) > 1 and part not in ['－', '—', '']:
                room['name'] = part
                break

    # 只有當有名稱時才返回
    if room['name'] and any([room['capacity_theater'], room['price_weekday']]):
        return room

    return None


def save_parsed_data(rooms, output_path):
    """儲存解析結果"""
    data = {
        'venue': 'TICC',
        'parsed_at': datetime.now().isoformat(),
        'total_rooms': len(rooms),
        'rooms': rooms
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n已儲存到: {output_path}")
    return data


if __name__ == '__main__':
    import sys

    print("="*80)
    print("TICC PDF 解析器 (pdfplumber 版本)")
    print("="*80)
    print()

    # PDF 路徑
    pdf_path = "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf"

    # 檢查是否有本地的 PDF 檔案
    import os
    local_pdf = "ticc_pricing.pdf"

    if os.path.exists(local_pdf):
        print(f"使用本地 PDF: {local_pdf}")
        pdf_path = local_pdf
    else:
        print(f"使用網路 PDF: {pdf_path}")
        print("提示：建議先下載 PDF 到本地")
        print()

    # 下載 PDF（如果需要）
    if pdf_path.startswith('http'):
        import requests
        print("下載 PDF 中...")
        try:
            response = requests.get(pdf_path, timeout=30)
            with open(local_pdf, 'wb') as f:
                f.write(response.content)
            pdf_path = local_pdf
            print(f"已下載到: {local_pdf}")
        except Exception as e:
            print(f"下載失敗: {e}")
            sys.exit(1)

    # 解析 PDF
    rooms = parse_ticc_pdf(pdf_path)

    if rooms:
        print()
        print("="*80)
        print(f"解析完成：共 {len(rooms)} 個會議室")
        print("="*80)

        # 儲存結果
        output = f"parsed_ticc_pdfplumber_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_parsed_data(rooms, output)

        # 顯示前 5 個
        print("\n前 5 個會議室：")
        for i, room in enumerate(rooms[:5], 1):
            print(f"{i}. {room['name']}")
            if room['capacity_theater']:
                print(f"   容量(劇院): {room['capacity_theater']} 人")
            if room['area_sqm']:
                print(f"   面積: {room['area_sqm']} ㎡")
            if room['price_weekday']:
                print(f"   平日價: ${room['price_weekday']:,}")
            print()

        if len(rooms) > 5:
            print(f"... 還有 {len(rooms) - 5} 個會議室")
    else:
        print("解析失敗或沒有找到會議室資料")
