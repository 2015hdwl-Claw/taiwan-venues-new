#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析集思台大 PDF - 提取面積資料
"""

import sys
import io
import pdfplumber

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def main():
    print('=' * 80)
    print('解析集思台大 PDF - 提取面積資料')
    print('=' * 80)
    print()

    # 嘗試所有 PDF
    pdf_files = ['ntucc_pricing.pdf', 'ntucc_venue_list_20250401.pdf', 'gis_ntu_2025.pdf']

    for pdf_path in pdf_files:
        try:
            print(f'--- 嘗試: {pdf_path} ---')

            with pdfplumber.open(pdf_path) as pdf:
                print(f'PDF 頁數: {len(pdf.pages)}')

                for page_num, page in enumerate(pdf.pages, 1):
                    print(f'\n頁面 {page_num}:')

                    # 提取文字
                    text = page.extract_text()
                    if text:
                        # 只顯示前 3000 字
                        print(text[:3000])
                        print()

                    # 提取表格
                    tables = page.extract_tables({
                        'vertical_strategy': 'text',
                        'horizontal_strategy': 'text'
                    })

                    if tables:
                        print(f'表格數量: {len(tables)}')

                        for table_idx, table in enumerate(tables):
                            print(f'\n=== 表格 {table_idx + 1} ===')
                            for row_idx, row in enumerate(table[:30]):  # 只顯示前 30 行
                                if row and any(cell for cell in row if cell):
                                    cleaned = []
                                    for cell in row:
                                        if cell:
                                            cell_str = str(cell).strip()
                                            if cell_str:
                                                cleaned.append(cell_str[:50])
                                    if cleaned:
                                        print(f'Row {row_idx}: {" | ".join(cleaned)}')

            print('\n' + '=' * 80)
            print()

        except Exception as e:
            print(f'錯誤: {e}')
            print()


if __name__ == '__main__':
    main()
