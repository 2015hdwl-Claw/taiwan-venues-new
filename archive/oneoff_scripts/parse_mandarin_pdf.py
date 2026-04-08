#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接解析文華東方 PDF
"""

import sys
import io
import requests
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('解析文華東方 PDF')
    print('=' * 80)
    print()

    # 用戶提供的 PDF URL
    pdf_url = 'https://cdn-assets-dynamic.frontify.com/4001946/eyJhc3NldF9pZCI6NTk4NzIsInNjb3BlIjoiYXNzZXQ6dmlldyJ9:mandarin-oriental-hotel-group:DPQPeMI4kSiRw7PDc5axDqPeG3bMRlvOUH4Pu1hby18'

    print(f'URL: {pdf_url}')
    print()

    # 下載 PDF
    print('[1/3] 下載 PDF...')

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, timeout=30, headers=headers)
        response.raise_for_status()

        filename = 'mandarin_oriental_meeting.pdf'
        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f'✅ 下載完成: {filename}')
        print(f'大小: {len(response.content):,} bytes')
        print()

    except Exception as e:
        print(f'❌ 下載失敗: {e}')
        return

    # 解析 PDF
    print('[2/3] 解析 PDF...')

    try:
        import pdfplumber

        with pdfplumber.open(filename) as pdf:
            print(f'頁數: {len(pdf.pages)}')
            print()

            all_data = []

            for page_num, page in enumerate(pdf.pages, 1):
                print(f'--- 頁面 {page_num} ---')

                # 提取文字
                text = page.extract_text()
                if text:
                    print(f'文字內容（前 500 字）:')
                    print(text[:500])
                    print()

                # 提取表格
                tables = page.extract_tables({
                    'vertical_strategy': 'text',
                    'horizontal_strategy': 'text'
                })

                if tables:
                    print(f'找到 {len(tables)} 個表格')

                    for table_num, table in enumerate(tables, 1):
                        print(f'\\n表格 {table_num}（前 5 行）:')

                        for row_num, row in enumerate(table[:5], 1):
                            if row:
                                display_row = [str(cell)[:40] if cell else '' for cell in row[:8]]
                                print(f'  Row {row_num}: {display_row}')

                        all_data.append({
                            'page': page_num,
                            'table_num': table_num,
                            'data': table
                        })
                else:
                    print('未找到表格')

                print()

            # 儲存提取資料
            result = {
                'pdf_url': pdf_url,
                'filename': filename,
                'total_pages': len(pdf.pages),
                'extraction_date': datetime.now().isoformat(),
                'tables': all_data
            }

            with open('mandarin_pdf_extraction.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print('[3/3] 儲存結果...')
            print(f'✅ 已儲存到 mandarin_pdf_extraction.json')
            print()

            # 分析並建立會議室資料
            if all_data:
                print('=' * 80)
                print('分析並建立會議室資料')
                print('=' * 80)
                print()

                analyze_and_create_rooms(result)
            else:
                print('⚠️  未找到表格資料')

    except ImportError:
        print('❌ pdfplumber 未安裝')
        print('   請執行: pip install pdfplumber')

    except Exception as e:
        print(f'❌ 解析失敗: {e}')
        import traceback
        traceback.print_exc()


def analyze_and_create_rooms(pdf_data):
    """分析 PDF 資料並建立會議室"""

    print('分析 PDF 結構...')
    print()

    # 檢查第一個表格
    if not pdf_data['tables']:
        print('⚠️  PDF 中沒有表格資料')
        return

    first_table = pdf_data['tables'][0]['data']

    print('表格結構分析（前 10 行）:')
    for row_num, row in enumerate(first_table[:10], 1):
        if row:
            display_row = [str(cell)[:30] if cell else '' for cell in row[:6]]
            print(f'  Row {row_num}: {display_row}')

    print()
    print('根據表格資料建立會議室...')
    print()

    # TODO: 根據實際表格結構解析會議室
    # 這裡需要先看到實際的表格結構才能寫解析邏輯

    print('⚠️  需要根據實際表格結構編寫解析邏輯')
    print('   請查看 mandarin_pdf_extraction.json 了解表格結構')


if __name__ == '__main__':
    main()
