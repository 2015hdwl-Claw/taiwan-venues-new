#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
維多麗亞酒店 - 完整資料提取
從會議室頁面和PDF提取完整資料
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import re
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("維多麗亞酒店 - 完整資料提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.victoria_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1122), None)
if not venue:
    print("Venue 1122 not found!")
    sys.exit(1)

base_url = 'https://grandvictoria.com.tw/'
meeting_url = 'https://grandvictoria.com.tw/%e6%9c%83%e8%ad%b0%e5%ae%a4%e6%9c%83/'
pdf_url = 'https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf'

print(f"場地: {venue['name']}")
print(f"會議頁面: {meeting_url}")
print(f"PDF檔案: {pdf_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# ========== 1. 提取會議室頁面 ==========
print("=" * 100)
print("1. 提取會議室頁面")
print("=" * 100)

try:
    r = requests.get(meeting_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP Status: {r.status_code}")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 顯示完整內容
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 200]
        print(f"\n頁面內容（前50行）:")
        for line in lines[:50]:
            print(f"  {line[:100]}")

        # 提取會議室名稱
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            print(f"\n會議室: {rooms}")

        # 提取容量
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            print(f"容量: {capacities}")

        # 提取面積
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        if areas:
            print(f"面積: {areas}")

except Exception as e:
    print(f"錯誤: {e}")

# ========== 2. 下載並解析PDF ==========
print(f"\n{'=' * 100}")
print("2. 下載並解析PDF")
print("=" * 100)

try:
    print(f"下載PDF: {pdf_url}")
    r = requests.get(pdf_url, timeout=30, verify=False)
    print(f"HTTP Status: {r.status_code}")
    print(f"檔案大小: {len(r.content):,} bytes")

    if r.status_code == 200 and len(r.content) > 1000:
        # 保存PDF
        pdf_filename = 'victoria_2022_event_venue.pdf'
        with open(pdf_filename, 'wb') as f:
            f.write(r.content)
        print(f"✓ 已保存: {pdf_filename}")

        # 使用pdfplumber解析
        try:
            import pdfplumber

            with pdfplumber.open(pdf_filename) as pdf:
                print(f"\nPDF頁數: {len(pdf.pages)}")

                # 提取所有頁面的文字
                all_text = ""
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"

                    # 顯示每頁的前500字
                    print(f"\n第{i+1}頁內容（前500字）:")
                    print(text[:500] if text else "(空白)")

                # 嘗試提取表格
                print(f"\n提取表格資料:")
                for i, page in enumerate(pdf.pages[:3]):
                    tables = page.extract_tables()
                    if tables:
                        print(f"第{i+1}頁發現 {len(tables)} 個表格:")
                        for j, table in enumerate(tables):
                            print(f"  表格{j+1}:")
                            for row in table[:15]:
                                print(f"    {row}")

                # 分析提取的文字
                print(f"\n分析PDF內容:")
                print("-" * 100)

                # 提取容量
                capacities = re.findall(r'(\d+)\s*[人名桌者席位]', all_text)
                if capacities:
                    print(f"容量數字: {capacities}")

                # 提取面積
                areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', all_text)
                if areas:
                    print(f"面積數字: {areas}")

                # 提取價格
                prices = re.findall(r'(\d+,?\d*)\s*元', all_text)
                if prices:
                    print(f"價格數字: {prices}")

                # 提取會議室名稱
                room_patterns = [
                    r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])',
                    r'(宴會廳|會議室|會議廳)'
                ]

                for pattern in room_patterns:
                    matches = re.findall(pattern, all_text)
                    if matches:
                        print(f"會議室: {matches}")
                        break

        except ImportError:
            print("pdfplumber 未安裝")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'=' * 100}")
print("提取完成")
print(f"備份: {backup_file}")
