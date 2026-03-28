#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析台北世貿 2025 會議室價目表 PDF - 完整資料提取
使用 pdfplumber
"""

import sys
import io
import pdfplumber
import json
import re

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


def parse_dimensions(dim_str):
    """解析尺寸字串 '20.2 x 18.6 x 3.5' -> {'length': 20.2, 'width': 18.6, 'height': 3.5}"""
    if not dim_str:
        return {'length': None, 'width': None, 'height': None}

    try:
        dim_str = str(dim_str).replace('x', ' ').replace('×', ' ').replace('公尺', '').replace('m', '').strip()
        parts = dim_str.split()

        if len(parts) >= 2:
            length = float(parts[0]) if parts[0].replace('.', '').isdigit() else None
            width = float(parts[1]) if len(parts) > 1 and str(parts[1]).replace('.', '').isdigit() else None
            height = float(parts[2]) if len(parts) > 2 and str(parts[2]).replace('.', '').isdigit() else None
            return {'length': length, 'width': width, 'height': height}
        return {'length': None, 'width': None, 'height': None}
    except:
        return {'length': None, 'width': None, 'height': None}


def main():
    print('=' * 80)
    print('解析台北世貿 2025 會議室價目表 PDF')
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
                print('  無表格')
                continue

            for table_idx, table in enumerate(tables):
                print(f'  表格 {table_idx + 1}: {len(table)} 行')

                # 顯示前幾行以了解結構
                print('  表格結構（前5行）:')
                for row_idx, row in enumerate(table[:5]):
                    cleaned_row = [str(cell).strip()[:30] if cell else '' for cell in row]
                    print(f'    Row {row_idx}: {cleaned_row}')

                # 尋找包含會議室資料的行
                for row_idx, row in enumerate(table):
                    if not row or len(row) < 3:
                        continue

                    # 檢查是否包含會議室名稱（如第一會議室、201、202等）
                    row_text = ' '.join([str(cell) for cell in row if cell])

                    # 跳過標題行
                    if '會議室' in row_text and '樓層' in row_text:
                        continue
                    if '使用人數' in row_text or '坪數' in row_text:
                        continue

                    # 尋找會議室資料行
                    if re.search(r'會議室|第一|二|三|四|\d{3}', row_text):
                        # 檢查是否有數字資料（容量、面積等）
                        has_numbers = any(bool(clean_number(str(cell))) for cell in row if cell)

                        if has_numbers:
                            print(f'  找到會議室資料行: {row_idx}')
                            all_rooms.append({
                                'page': page_num,
                                'table': table_idx,
                                'row': row_idx,
                                'data': row,
                                'text': row_text
                            })

            print()

        # 整理並顯示會議室資料
        print('=' * 80)
        print(f'找到 {len(all_rooms)} 筆會議室資料')
        print('=' * 80)
        print()

        # 顯示前10筆資料
        for idx, room in enumerate(all_rooms[:10], 1):
            print(f'{idx}. 頁面 {room["page"]}: {room["text"][:100]}')
            row = room['data']
            for col_idx, cell in enumerate(row):
                if cell and col_idx < 15:
                    cell_str = str(cell).strip()
                    if cell_str:
                        print(f'   [{col_idx}] {cell_str[:60]}')
            print()


if __name__ == '__main__':
    main()
