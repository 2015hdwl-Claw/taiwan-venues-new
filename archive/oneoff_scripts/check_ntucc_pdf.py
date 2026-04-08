#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查集思台大會議中心 PDF 是否需要用 pdfplumber 重新解析
"""

import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pdfplumber
except ImportError:
    print("❌ 尚未安裝 pdfplumber")
    sys.exit(1)


def main():
    print('=' * 80)
    print('集思台大會議中心 PDF 檢查')
    print('=' * 80)
    print()

    pdf_path = 'ntucc_venue_list_20250401.pdf'

    print(f'[1/3] 檢查 PDF: {pdf_path}')
    print()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f'總頁數: {len(pdf.pages)}')
            print()

            print('[2/3] 提取表格結構...')
            print()

            all_tables = []
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables({
                    'vertical_strategy': 'text',
                    'horizontal_strategy': 'text',
                    'snap_tolerance': 5,
                    'join_tolerance': 5
                })

                if tables:
                    print(f'第 {page_num} 頁: {len(tables)} 個表格')
                    for table in tables:
                        print(f'  - {len(table)} 行 x {len(table[0]) if table else 0} 欄')
                        all_tables.append({
                            'page': page_num,
                            'table': table
                        })

            print()
            print(f'總共提取 {len(all_tables)} 個表格')
            print()

            print('[3/3] 分析第一個表格...')
            print()

            if all_tables:
                first_table = all_tables[0]['table']
                print('前 10 行:')
                for i, row in enumerate(first_table[:10]):
                    print(f'Row {i}: {row[:8]}')  # 只顯示前 8 欄

                # 分析結構
                print()
                print('表格分析:')
                print(f'  總行數: {len(first_table)}')
                print(f'  總欄數: {len(first_table[0]) if first_table else 0}')

                # 檢查是否有細分場地的跡象
                has_zones = any('區' in str(cell) for row in first_table for cell in row)
                has_subspaces = any('廳' in str(cell) or '室' in str(cell) for row in first_table for cell in row)

                print()
                print('細分場地跡象:')
                print(f'  有「區」字: {"✅" if has_zones else "❌"}')
                print(f'  有「廳/室」字: {"✅" if has_subspaces else "❌"}')

                if has_zones or has_subspaces:
                    print()
                    print('⚠️  發現細分場地跡象，建議使用 pdfplumber 重新解析')
                    print('    並建立 subSpaces 結構')
                else:
                    print()
                    print('✅ PDF 結構簡單，現有資料已足夠')

    except Exception as e:
        print(f'❌ 錯誤: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
