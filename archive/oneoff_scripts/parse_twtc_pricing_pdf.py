#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並解析台北世貿會議室暨設備價目表 PDF
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
    print('台北世貿會議室暨設備價目表 - PDF 解析')
    print('=' * 80)
    print()

    # PDF URL（使用編碼後的 URL）
    pdf_url = 'https://www.twtc.com.tw/file/DB/images_G1/2025會議室價目表2025.10版.pdf'
    pdf_filename = 'twtc_pricing_2025.pdf'

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

                # 顯示前 20 行
                print(f'顯示前 20 行:')
                for i, row in enumerate(first_table[:20], 1):
                    # 只顯示前 8 欄，每欄最多 40 字元
                    display_row = []
                    for cell in row[:8]:
                        if cell:
                            cell_str = str(cell)[:40].replace('\n', ' ')
                            display_row.append(cell_str)
                        else:
                            display_row.append('')
                    print(f'Row {i}: {display_row}')

                # 尋找包含會議室名稱的行
                print()
                print(f'[4/4] 尋找會議室和價格資訊...')

                room_data = []
                for i, row in enumerate(first_table):
                    row_text = ' '.join([str(cell) for cell in row if cell])

                    # 尋找會議室關鍵字
                    room_keywords = ['第一會議室', '第二會議室', '第三會議室', '第四會議室',
                                     '第五會議室', 'A+會議室', '貴賓室', '廊廳']

                    if any(keyword in row_text for keyword in room_keywords):
                        # 尋找價格
                        price_pattern = r'[nN][tT]\$?\s*[\d,]+|[\d,]+\s*元'
                        import re
                        prices = re.findall(price_pattern, row_text)

                        room_data.append({
                            'row': i,
                            'data': [str(c)[:50] for c in row[:6]],
                            'has_price': len(prices) > 0,
                            'prices': prices
                        })

                if room_data:
                    print(f'✅ 找到 {len(room_data)} 個會議室資料:')
                    for data in room_data[:10]:
                        print(f'  Row {data["row"]}: {data["data"]}')
                        if data['has_price']:
                            print(f'    價格: {data["prices"]}')
                else:
                    print('⚠️  未找到明顯的會議室資料行')

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
                        for t in all_tables
                    ]
                }

                with open('twtc_pricing_extraction.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print()
                print('✅ 提取資料已儲存到 twtc_pricing_extraction.json')

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
    print('1. 檢查 twtc_pricing_extraction.json')
    print('2. 識別會議室、容量、價格的對應關係')
    print('3. 更新 venues.json')
    print()


if __name__ == '__main__':
    main()
