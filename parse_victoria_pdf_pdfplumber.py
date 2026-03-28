#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 pdfplumber 解析維多麗亞酒店 PDF 價格表
支援中文表格和場地細分（全廳、A/B/C區、廊道、戶外庭園、貴賓室）
"""

import sys
import io
import json
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


def download_pdf(url, filename):
    """下載 PDF 檔案"""
    print(f"[1/4] 下載 PDF...")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f"✅ PDF 已下載: {filename}")
        print(f"   大小: {len(response.content):,} bytes")
        return filename
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return None


def extract_tables_from_pdf(pdf_path):
    """使用 pdfplumber 提取所有表格"""
    print(f"\n[2/4] 解析 PDF 表格...")

    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        print(f"   總頁數: {len(pdf.pages)}")

        for page_num, page in enumerate(pdf.pages, 1):
            print(f"   處理第 {page_num} 頁...")

            # 提取表格
            page_tables = page.extract_tables({
                'vertical_strategy': 'text',  # 根據文字間距判斷欄位
                'horizontal_strategy': 'text',
                'snap_tolerance': 5,  # 容忍度
                'join_tolerance': 5
            })

            if page_tables:
                print(f"     ✅ 找到 {len(page_tables)} 個表格")
                for table in page_tables:
                    tables.append({
                        'page': page_num,
                        'table': table
                    })
            else:
                print(f"     ⚠️  此頁無表格")

    print(f"\n✅ 總共提取 {len(tables)} 個表格")
    return tables


def parse_venue_tables(tables):
    """解析場地表格資料"""
    print(f"\n[3/4] 解析場地資料...")

    venues = []

    for table_data in tables:
        page_num = table_data['page']
        table = table_data['table']

        print(f"\n--- 第 {page_num} 頁表格 ---")

        # 打印表格原始資料（用於調試）
        for row_idx, row in enumerate(table[:10]):  # 只顯示前 10 行
            print(f"Row {row_idx}: {row}")

        # 這裡需要根據實際表格結構來解析
        # 維多麗亞酒店的 PDF 結構需要實際查看後才能決定
        # 先儲存原始資料

    return venues


def main():
    print('=' * 80)
    print('維多麗亞酒店 PDF 解析 - 使用 pdfplumber')
    print('=' * 80)
    print()

    # 使用本地 PDF 檔案（避免 403）
    pdf_path = 'victoria_capacity.pdf'
    pdf_url = 'https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf'

    print(f'[1/4] 使用本地 PDF 檔案: {pdf_path}')
    print(f'原始 URL: {pdf_url}')
    print()

    # 2. 提取表格
    tables = extract_tables_from_pdf(pdf_path)

    # 3. 解析場地資料
    venues = parse_venue_tables(tables)

    # 4. 儲存結果
    print(f"\n[4/4] 儲存結果...")

    result = {
        'extracted_at': datetime.now().isoformat(),
        'pdf_url': pdf_url,
        'total_tables': len(tables),
        'tables': tables
    }

    output_file = 'victoria_pdf_extraction_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 原始資料已儲存: {output_file}")

    print()
    print('=' * 80)
    print('✅ PDF 解析完成')
    print('=' * 80)
    print()
    print('下一步:')
    print('1. 檢查 victoria_pdf_extraction_raw.json')
    print('2. 根據表格結構設計解析邏輯')
    print('3. 提取場地細分資料（全廳、A/B/C區、廊道、戶外庭園、貴賓室）')


if __name__ == '__main__':
    main()
