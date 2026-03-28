#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析南港展覽館收費基準 PDF - 完整會議室資料
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
        cleaned = str(num_str).replace(',', '').replace('$', '').replace('NT', '').strip()
        if cleaned and cleaned.replace('.', '').isdigit():
            return float(cleaned) if '.' in cleaned else int(cleaned)
        return None
    except:
        return None


def parse_area(area_str):
    """解析面積字串 '236坪' 或 '236㎡'"""
    if not area_str:
        return None, None, None

    area_str = str(area_str).strip()

    # 提取數字
    match = re.search(r'([\d.]+)', area_str)
    if not match:
        return None, None, None

    value = float(match.group(1))

    # 判斷單位
    if '坪' in area_str:
        # 坪 → ㎡ (1 坪 = 3.3058 ㎡)
        return value * 3.3058, value, '㎡'
    elif '㎡' in area_str or 'sqm' in area_str.lower():
        return value, value / 3.3058, '㎡'
    else:
        # 預設為 ㎡
        return value, value / 3.3058, '㎡'


def main():
    print('=' * 80)
    print('解析南港展覽館收費基準 PDF')
    print('=' * 80)
    print()

    pdf_path = 'nangang_pricing_2021.pdf'

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

                # 跳過前4行標題，從第5行開始是實際會議室資料
                data_rows = table[4:] if len(table) > 4 else []

                for row_idx, row in enumerate(data_rows):
                    if not row or len(row) < 8:
                        continue

                    # 檢查第一欄是否為樓層（數字或包含「樓」）
                    first_col = str(row[0]).strip() if row[0] else ''

                    # 檢查第二欄是否為會議室名稱
                    second_col = str(row[1]).strip() if row[1] else ''

                    # 跳過空行或標題行
                    if not first_col and not second_col:
                        continue

                    # 跳過說明文字
                    if '本中心' in first_col or '租用' in first_col or '會議室內' in first_col:
                        continue

                    if len(first_col) > 20:  # 說明文字通常很長
                        continue

                    # 顯示可能的會議室資料行
                    if first_col or second_col:
                        print(f'  Row {row_idx + 4}: [{first_col}] [{second_col}]')

                        # 儲存完整資料
                        all_rooms.append({
                            'page': page_num,
                            'row': row_idx + 4,
                            'floor': first_col,
                            'name': second_col,
                            'data': row
                        })

            print()

        # 整理並顯示會議室資料
        print('=' * 80)
        print(f'找到 {len(all_rooms)} 筆可能的會議室資料')
        print('=' * 80)
        print()

        for idx, room in enumerate(all_rooms, 1):
            print(f'{idx}. 樓層: [{room["floor"]}] 名稱: [{room["name"]}]')
            row = room['data']
            for col_idx, cell in enumerate(row):
                if cell and col_idx < 15:  # 限制顯示欄位數
                    cell_str = str(cell).strip()
                    if cell_str:
                        print(f'   [{col_idx}] {cell_str[:50]}')  # 限制長度
            print()


if __name__ == '__main__':
    main()
