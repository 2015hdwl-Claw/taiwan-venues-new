#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC - 下載並解析用戶提供的 PDF
"""

import requests
import pdfplumber
import json
import sys
from datetime import datetime
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - 下載並解析 PDF")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 用戶提供的 PDF URL
pdf_url = "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf"

print(f"PDF URL: {pdf_url}\n")

# 下載 PDF
print("下載 PDF...")
response = requests.get(pdf_url, timeout=60, verify=False)
print(f"HTTP 狀態: {response.status_code}")
print(f"檔案大小: {len(response.content)} bytes ({len(response.content)/1024:.1f} KB)")

# 儲存 PDF
pdf_filename = f'ticc_official_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
with open(pdf_filename, 'wb') as f:
    f.write(response.content)
print(f"✅ PDF 已儲存: {pdf_filename}\n")

# 解析 PDF
print("=" * 100)
print("解析 PDF")
print("=" * 100)

try:
    with pdfplumber.open(pdf_filename) as pdf:
        print(f"PDF 頁數: {len(pdf.pages)}\n")

        # 提取所有頁面的文字
        all_text = ""
        all_tables = []

        for i, page in enumerate(pdf.pages, 1):
            print(f"頁面 {i}:")

            # 提取文字
            text = page.extract_text()
            if text:
                all_text += text + "\n\n"
                print(f"  文字: {len(text)} 字元")

            # 提取表格
            tables = page.extract_tables()
            if tables:
                print(f"  表格: {len(tables)} 個")
                all_tables.extend(tables)

        # 儲存文字
        text_filename = f'ticc_pdf_text_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write(all_text)
        print(f"\n✅ PDF 文字已儲存: {text_filename}")

        # 尋找會議室資訊
        print("\n" + "=" * 100)
        print("尋找會議室資訊")
        print("=" * 100)

        # 尋找會議室名稱模式
        room_patterns = [
            r'(\d+[F樓]?\s*會議室)',
            r'(\d+\s*會議室)',
            r'(國際會議廳)',
            r'(宴會廳)',
            r'([A-Z]\s*展覽館)',
        ]

        rooms_found = []
        for pattern in room_patterns:
            matches = re.findall(pattern, all_text)
            rooms_found.extend(matches)

        if rooms_found:
            print(f"\n找到會議室: {len(set(rooms_found))} 個")
            for room in sorted(set(rooms_found)):
                print(f"  - {room}")

        # 尋找容量資訊
        print("\n尋找容量資訊...")
        capacity_patterns = [
            r'(\d+)\s*[人名]',
            r'容量[：:]\s*(\d+)',
        ]

        capacities = []
        for pattern in capacity_patterns:
            matches = re.findall(pattern, all_text)
            capacities.extend(matches)

        if capacities:
            print(f"找到容量資訊: {len(capacities)} 處")
            print(f"範圍: {min(int(c) for c in capacities)} - {max(int(c) for c in capacities)} 人")

        # 尋找坪數
        print("\n尋找坪數資訊...")
        area_patterns = [
            r'(\d+\.?\d*)\s*[坪平米]',
        ]

        areas = []
        for pattern in area_patterns:
            matches = re.findall(pattern, all_text)
            areas.extend(matches)

        if areas:
            print(f"找到坪數資訊: {len(areas)} 處")
            print(f"範圍: {min(float(a) for a in areas)} - {max(float(a) for a in areas)} 坪")

        # 尋找價格
        print("\n尋找價格資訊...")
        price_patterns = [
            r'(\d{2,6}[,.]?\d{0,3})\s*元',
            r'NT\$\s*(\d+[,.]?\d*)',
            r'TWD\s*(\d+[,.]?\d*)',
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, all_text)
            prices.extend(matches)

        if prices:
            print(f"找到價格資訊: {len(prices)} 處")
            print(f"範例: {prices[:5]}")

        # 表格分析
        if all_tables:
            print(f"\n表格分析:")
            print(f"總表格數: {len(all_tables)}")

            for i, table in enumerate(all_tables[:5], 1):
                print(f"\n表格 {i}:")
                print(f"  行數: {len(table)}")
                if table:
                    print(f"  欄數: {len(table[0]) if table[0] else 0}")
                    # 顯示前 3 行
                    print(f"  前 3 行:")
                    for row in table[:3]:
                        print(f"    {row}")

        # 儲存結果
        result = {
            'venue': 'TICC',
            'venue_id': 1448,
            'pdf_url': pdf_url,
            'pdf_file': pdf_filename,
            'text_file': text_filename,
            'total_pages': len(pdf.pages),
            'rooms_found': list(set(rooms_found)) if rooms_found else [],
            'capacities': capacities[:10] if capacities else [],
            'areas': areas[:10] if areas else [],
            'prices': prices[:10] if prices else [],
            'tables_count': len(all_tables),
            'timestamp': datetime.now().isoformat()
        }

        result_filename = f'ticc_pdf_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(result_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 解析結果已儲存: {result_filename}")

except Exception as e:
    print(f"❌ 解析失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
print("✅ TICC PDF 處理完成")
print("=" * 100)
