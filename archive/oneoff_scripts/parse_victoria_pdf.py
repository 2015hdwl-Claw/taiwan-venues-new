#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新解析維多麗亞 PDF - 完整資料提取
"""

import sys
import io
import pdfplumber
import json
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def clean_number(num_str):
    if not num_str:
        return None
    try:
        cleaned = str(num_str).replace(',', '').replace('$', '').replace('NT', '').replace('元', '').strip()
        if cleaned and cleaned.replace('.', '').isdigit():
            return float(cleaned) if '.' in cleaned else int(cleaned)
        return None
    except:
        return None


def parse_price_truncated(price_str):
    if not price_str:
        return None
    try:
        price_str = str(price_str).replace(',', '').strip()
        if len(price_str) <= 4 and price_str.isdigit():
            return int(price_str) * 10
        return int(price_str)
    except:
        return None


def parse_area(area_str):
    if not area_str:
        return None, None
    try:
        # 檢查是否有斜線
        if '/' in str(area_str):
            parts = str(area_str).split('/')
            if len(parts) == 2:
                sqm = clean_number(parts[0])
                ping = clean_number(parts[1])
                return sqm, ping
        value = clean_number(area_str)
        return value, None
    except:
        return None, None


def main():
    print('=' * 80)
    print('解析維多麗亞 PDF')
    print('=' * 80)
    print()

    pdf_path = 'victoria_2022.pdf'

    with pdfplumber.open(pdf_path) as pdf:
        print(f'PDF 頁數: {len(pdf.pages)}')
        print()

        all_rooms = []

        for page_num, page in enumerate(pdf.pages, 1):
            print(f'--- 頁面 {page_num} ---')

            tables = page.extract_tables({
                'vertical_strategy': 'text',
                'horizontal_strategy': 'text',
                'snap_tolerance': 5,
                'join_tolerance': 5
            })

            if not tables:
                continue

            for table_idx, table in enumerate(tables):
                print(f'  表格 {table_idx + 1}: {len(table)} 行')

                # 顯示前幾行
                for row_idx, row in enumerate(table[:5]):
                    cleaned_row = [str(cell).strip()[:40] if cell else '' for cell in row]
                    print(f'    Row {row_idx}: {cleaned_row}')

                # 尋找會議室資料
                for row_idx, row in enumerate(table):
                    if not row or len(row) < 3:
                        continue

                    row_text = ' '.join([str(cell) for cell in row if cell])

                    # 跳過空行和標題行
                    if not row_text or 'VENUE' in row_text or '場地' in row_text:
                        continue

                    # 尋找包含數字的行（可能是會議室資料）
                    if clean_number(str(row[0])) or clean_number(str(row[1])):
                        print(f'  找到資料行: {row_idx}')
                        print(f'  內容: {row_text[:80]}')
                        all_rooms.append({
                            'page': page_num,
                            'data': row
                        })

        print()
        print(f'共找到 {len(all_rooms)} 筆資料')
        print()


if __name__ == '__main__':
    main()
