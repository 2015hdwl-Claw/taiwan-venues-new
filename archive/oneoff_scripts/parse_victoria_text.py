#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析維多麗亞 PDF - 顯示所有內容
"""

import sys
import io
import pdfplumber

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('解析維多麗亞 PDF - 完整內容')
    print('=' * 80)
    print()

    pdf_path = 'victoria_2022.pdf'

    with pdfplumber.open(pdf_path) as pdf:
        print(f'PDF 頁數: {len(pdf.pages)}')
        print()

        page = pdf.pages[0]

        # 直接提取文字
        text = page.extract_text()
        print('PDF 文字內容（前2000字）:')
        print('-' * 80)
        print(text[:2000])
        print()

        # 提取表格
        tables = page.extract_tables({
            'vertical_strategy': 'text',
            'horizontal_strategy': 'text'
        })

        print(f'表格數量: {len(tables)}')
        print()

        for table_idx, table in enumerate(tables):
            print(f'=== 表格 {table_idx + 1} ===')
            for row_idx, row in enumerate(table):
                # 顯示非空行
                if row and any(cell for cell in row if cell):
                    cleaned = []
                    for cell in row:
                        if cell:
                            cell_str = str(cell).strip()
                            if cell_str:
                                cleaned.append(cell_str[:30])
                    if cleaned:
                        print(f'Row {row_idx}: {" | ".join(cleaned)}')


if __name__ == '__main__':
    main()
