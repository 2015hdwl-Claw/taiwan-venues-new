#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF完整提取 - 一次性到位
使用pdfplumber提取所有PDF中的完整會議室資料
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import warnings
import io

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

print("=" * 100)
print("PDF完整提取 - 一次性到位")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 備份
backup_file = f"venues.json.backup.pdf_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 重點處理：台北美福大飯店的PDF
venue = next((v for v in venues if v['id'] == 1095), None)

if venue:
    print("=" * 100)
    print(f"處理場地: {venue['name']} (ID: 1095)")
    print("=" * 100)

    base_url = 'https://www.grandmayfull.com'

    # 下載並解析PDF
    pdf_urls = [
        'https://www.grandmayfull.com/uploads/20260304_135050_490.pdf',
        'https://www.grandmayfull.com/uploads/2026_map.pdf',
    ]

    for pdf_url in pdf_urls:
        print(f"\n處理PDF: {pdf_url}")
        print("-" * 100)

        try:
            # 下載PDF
            response = requests.get(pdf_url, timeout=30, verify=False)
            print(f"下載狀態: {response.status_code}")
            print(f"檔案大小: {len(response.content):,} bytes")

            if response.status_code == 200 and len(response.content) > 1000:
                # 保存PDF
                pdf_filename = pdf_url.split('/')[-1]
                with open(pdf_filename, 'wb') as f:
                    f.write(response.content)
                print(f"已保存: {pdf_filename}")

                # 使用pdfplumber解析
                try:
                    import pdfplumber

                    with pdfplumber.open(pdf_filename) as pdf:
                        print(f"PDF頁數: {len(pdf.pages)}")

                        # 提取所有頁面的文字
                        all_text = ""
                        for i, page in enumerate(pdf.pages):
                            text = page.extract_text()
                            if text:
                                all_text += text + "\n"

                            # 顯示每頁的前500字
                            print(f"\n第{i+1}頁內容（前500字）:")
                            print(text[:500])

                        # 嘗試提取表格
                        print(f"\n提取表格資料:")
                        for i, page in enumerate(pdf.pages[:3]):
                            tables = page.extract_tables()
                            if tables:
                                print(f"第{i+1}頁發現 {len(tables)} 個表格:")
                                for j, table in enumerate(tables):
                                    print(f"  表格{j+1}:")
                                    for row in table[:10]:
                                        print(f"    {row}")

                except ImportError:
                    print("pdfplumber 未安裝，嘗試使用 PyPDF2")
                    try:
                        import PyPDF2

                        with open(pdf_filename, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            num_pages = len(pdf_reader.pages)
                            print(f"PDF頁數: {num_pages}")

                            all_text = ""
                            for i, page in enumerate(pdf_reader.pages):
                                text = page.extract_text()
                                if text:
                                    all_text += text + "\n"
                                    print(f"\n第{i+1}頁內容（前500字）:")
                                    print(text[:500])

                    except ImportError:
                        print("PyPDF2 也未安裝，無法解析PDF")

                # 分析提取的文字
                print(f"\n分析PDF內容:")
                print("-" * 100)

                import re

                # 提取容量
                capacities = re.findall(r'(\d+)\s*[人名桌者席位]', all_text)
                if capacities:
                    print(f"容量數字: {capacities[:20]}")

                # 提取面積
                areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡])', all_text)
                if areas:
                    print(f"面積數字: {areas[:20]}")

                # 提取價格
                prices = re.findall(r'(\d+,?\d*)\s*元', all_text)
                if prices:
                    print(f"價格數字: {prices[:20]}")

        except Exception as e:
            print(f"處理PDF錯誤: {e}")
            import traceback
            traceback.print_exc()

print("\n" + "=" * 100)
print("PDF提取完成")
print("=" * 100)
print(f"備份: {backup_file}")
