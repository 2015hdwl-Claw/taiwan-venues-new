#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並解析台北萬豪的 PDF 檔案
使用 pdfplumber 提取完整資料
"""

import sys
import io
import pdfplumber
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def download_pdf(url, filename):
    """下載 PDF 檔案"""
    import requests

    print(f'下載: {url}')
    print(f'儲存: {filename}')
    print()

    try:
        response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f'✅ 下載完成: {filename}')
        print(f'大小: {len(response.content)} bytes')
        print()
        return True

    except Exception as e:
        print(f'❌ 下載失敗: {e}')
        return False


def extract_tables_from_pdf(filename):
    """使用 pdfplumber 提取表格"""
    print(f'解析: {filename}')
    print()

    try:
        with pdfplumber.open(filename) as pdf:
            print(f'頁數: {len(pdf.pages)}')
            print()

            all_tables = []

            for page_num, page in enumerate(pdf.pages, 1):
                print(f'--- 頁面 {page_num} ---')

                # 使用 pdfplumber 的 text 策略
                tables = page.extract_tables({
                    'vertical_strategy': 'text',
                    'horizontal_strategy': 'text',
                    'snap_tolerance': 5,
                    'join_tolerance': 5
                })

                if tables:
                    print(f'找到 {len(tables)} 個表格')

                    for table_num, table in enumerate(tables, 1):
                        print(f'\\n表格 {table_num}:')

                        # 顯示前 10 行
                        for row_num, row in enumerate(table[:10], 1):
                            if row:
                                # 只顯示前 8 欄
                                display_row = [str(cell)[:30] if cell else '' for cell in row[:8]]
                                print(f'  Row {row_num}: {display_row}')

                        all_tables.append({
                            'page': page_num,
                            'table_num': table_num,
                            'data': table
                        })
                else:
                    print('未找到表格')

                print()

            return all_tables

    except Exception as e:
        print(f'❌ 解析失敗: {e}')
        import traceback
        traceback.print_exc()
        return None


def main():
    print('=' * 80)
    print('下載並解析台北萬豪 PDF')
    print('=' * 80)
    print()

    # PDF URLs
    pdf_urls = [
        ('https://www.taipeimarriott.com.tw/files/page_176778676814ut99b82.pdf', 'marriott_pricing.pdf'),
        ('https://www.taipeimarriott.com.tw/files/page_157062443710javl802.pdf', 'marriott_venue_intro.pdf')
    ]

    all_data = []

    for url, filename in pdf_urls:
        # 下載
        if download_pdf(url, filename):
            # 解析
            tables = extract_tables_from_pdf(filename)

            if tables:
                all_data.append({
                    'url': url,
                    'filename': filename,
                    'tables': tables
                })

    # 儲存結果
    result = {
        'extraction_date': datetime.now().isoformat(),
        'pdfs': all_data
    }

    with open('marriott_pdf_extraction.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print('=' * 80)
    print('✅ 已儲存到 marriott_pdf_extraction.json')
    print('=' * 80)
    print()
    print('下一步: 分析並建立完整會議室資料結構')


if __name__ == '__main__':
    main()
