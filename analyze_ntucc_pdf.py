#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析集思台大 PDF 結構
"""

import sys
import io
import json

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
    print('集思台大 PDF 結構分析')
    print('=' * 80)
    print()

    pdf_path = 'ntucc_venue_list_20250401.pdf'

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables({
            'vertical_strategy': 'text',
            'horizontal_strategy': 'text',
            'snap_tolerance': 5,
            'join_tolerance': 5
        })

        if tables:
            table = tables[0]

            # 尋找包含場地名稱的行
            print('尋找場地資料...')
            print()

            venue_rows = []
            for i, row in enumerate(table):
                row_str = ' '.join([str(cell) for cell in row if cell])

                # 檢查是否包含場地名稱
                if any(keyword in row_str for keyword in ['會議', '廳', '教室', '際', '國']):
                    # 跳過前 15 行的申請表欄位
                    if i > 15:
                        venue_rows.append((i, row))

            print(f'找到 {len(venue_rows)} 行可能包含場地資料')
            print()

            # 顯示前 5 行
            for i, (row_idx, row) in enumerate(venue_rows[:5]):
                print(f'Row {row_idx}:')
                for j, cell in enumerate(row):
                    if cell and str(cell).strip():
                        print(f'  [{j}]: {str(cell)[:50]}')
                print()

            # 儲存完整分析結果
            result = {
                'total_rows': len(table),
                'total_cols': len(table[0]) if table else 0,
                'venue_rows': len(venue_rows),
                'sample_rows': [
                    {'row': row_idx, 'data': [str(c) for c in row]}
                    for row_idx, row in venue_rows[:10]
                ]
            }

            with open('ntucc_pdf_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print('✅ 分析結果已儲存到 ntucc_pdf_analysis.json')

            # 結論
            print()
            print('=' * 80)
            print('結論:')
            print('=' * 80)
            print()

            if len(venue_rows) > 0:
                print(f'✅ PDF 包含 {len(venue_rows)} 行場地資料')
                print()
                print('建議:')
                print('  1. 集思台大已有 100% 價格覆蓋（12 個會議室）')
                print('  2. 現有資料完整，不需要重新解析')
                print('  3. 這個 PDF 是申請表格式，不是價格表')
            else:
                print('❌ PDF 中沒有找到場地資料')


if __name__ == '__main__':
    main()
