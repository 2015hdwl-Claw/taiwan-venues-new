#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並使用 pdfplumber 解析台北世貿 PDF
"""

import sys
import io
import requests
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pdfplumber
except ImportError:
    print("❌ 尚未安裝 pdfplumber")
    print("請執行: pip install pdfplumber")
    sys.exit(1)


def main():
    print('=' * 80)
    print('台北世貿中心 PDF 解析')
    print('=' * 80)
    print()

    pdf_url = 'https://www.twtc.com.tw/file/DB/images_G1/外貿協會經濟管理世貿一館場地借用實施規範.pdf'
    pdf_filename = 'twtc_venue_rental_guide.pdf'

    # 下載 PDF
    print(f'[1/4] 下載 PDF...')
    print(f'URL: {pdf_url}')
    print()

    try:
        response = requests.get(pdf_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        with open(pdf_filename, 'wb') as f:
            f.write(response.content)

        print(f'✅ PDF 已下載: {pdf_filename}')
        print(f'   大小: {len(response.content):,} bytes ({len(response.content) / 1024:.1f} KB)')
        print()

    except Exception as e:
        print(f'❌ 下載失敗: {e}')
        return

    # 解析 PDF
    print(f'[2/4] 解析 PDF 表格...')

    try:
        with pdfplumber.open(pdf_filename) as pdf:
            print(f'總頁數: {len(pdf.pages)}')
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

            # 分析第一個表格
            if all_tables:
                print(f'[3/4] 分析表格內容...')

                first_table = all_tables[0]['table']
                print(f'顯示前 20 行:')
                for i, row in enumerate(first_table[:20], 1):
                    # 只顯示前 6 欄
                    display_row = [str(cell)[:40] if cell else '' for cell in row[:6]]
                    print(f'Row {i}: {display_row}')

                # 尋找包含價格資訊的行
                print()
                print(f'[4/4] 尋找價格資訊...')

                price_rows = []
                for i, row in enumerate(first_table):
                    row_text = ' '.join([str(cell) for cell in row if cell])

                    # 尋找包含價格關鍵字的行
                    price_keywords = ['元', 'nt$', 'ntd', '租金', '收費', '價格']
                    if any(keyword in row_text.lower() for keyword in price_keywords):
                        price_rows.append((i, row))

                if price_rows:
                    print(f'找到 {len(price_rows)} 行包含價格資訊:')
                    for i, (row_idx, row) in enumerate(price_rows[:10], 1):
                        print(f'  {i}. Row {row_idx}: {[str(c)[:50] for c in row[:5]]}')

                # 儲存完整資料
                import json
                result = {
                    'extractedAt': datetime.now().isoformat(),
                    'pdfUrl': pdf_url,
                    'totalTables': len(all_tables),
                    'tables': [
                        {
                            'page': t['page'],
                            'rows': len(t['table']),
                            'cols': len(t['table'][0]) if t['table'] else 0,
                            'data': t['table']
                        }
                        for t in all_tables[:3]  # 只儲存前 3 個表格
                    ]
                }

                with open('twtc_pdf_extraction.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print()
                print('✅ 提取資料已儲存到 twtc_pdf_extraction.json')

    except Exception as e:
        print(f'❌ 解析失敗: {e}')
        import traceback
        traceback.print_exc()
        return

    print()
    print('=' * 80)
    print('下一步:')
    print('=' * 80)
    print()
    print('1. 檢查 twtc_pdf_extraction.json')
    print('2. 識別會議室和價格的對應關係')
    print('3. 更新 venues.json')


if __name__ == '__main__':
    main()
