#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
維多麗亞酒店 - 完整提取與更新
從會議宴會頁面和PDF提取所有資料
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
print("維多麗亞酒店 - 完整提取與更新")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.victoria_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1122), None)
if not venue:
    print("Venue 1122 not found!")
    sys.exit(1)

base_url = 'https://grandvictoria.com.tw'

# 要訪問的頁面
pages_to_visit = [
    ('會議宴會', '/會議宴會/'),
    ('會議專案', '/會議專案/'),
    ('白金會議專案', '/會議專案/白金會議專案/'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

all_room_data = {
    'rooms': [],
    'capacities': [],
    'areas': [],
    'prices': [],
    'features': []
}

# ========== 1. 訪問所有會議頁面 ==========
print("=" * 100)
print("1. 訪問會議頁面")
print("=" * 100)

for page_name, path in pages_to_visit:
    url = base_url + path
    print(f"\n訪問: {page_name}")
    print(f"URL: {url}")
    print("-" * 100)

    try:
        r = requests.get(url, timeout=20, verify=False, headers=headers)
        print(f"狀態: {r.status_code}")

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text()

            # 顯示頁面內容
            lines = [l.strip() for l in page_text.split('\n') if 15 < len(l.strip()) < 200]
            if lines:
                print(f"\n內容預覽（前20行）:")
                for line in lines[:20]:
                    print(f"  {line[:90]}")

            # 提取會議室名稱
            room_patterns = [
                r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])',
                r'(宴會廳|會議室|會議廳|多功能會議室)'
            ]

            for pattern in room_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    unique_rooms = list(set(matches))
                    all_room_data['rooms'].extend(unique_rooms)
                    print(f"\n會議室: {unique_rooms}")
                    break

            # 提取容量
            capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
            if capacities:
                caps = [int(c) for c in capacities if 5 <= int(c) <= 1000]
                all_room_data['capacities'].extend(caps)
                print(f"容量: {caps[:15]}")

            # 提取面積
            areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
            if areas:
                all_room_data['areas'].extend(areas[:15])
                print(f"面積: {areas[:15]}")

            # 提取價格
            prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
            if prices:
                all_room_data['prices'].extend(prices[:15])
                print(f"價格: {prices[:15]}")

    except Exception as e:
        print(f"錯誤: {e}")

# ========== 2. 解析PDF ==========
print(f"\n{'=' * 100}")
print("2. 解析PDF")
print("=" * 100)

pdf_url = 'https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf'

try:
    print(f"下載PDF...")
    r = requests.get(pdf_url, timeout=30, verify=False, headers=headers)
    print(f"狀態: {r.status_code}")
    print(f"大小: {len(r.content):,} bytes")

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

                # 提取所有文字
                all_text = ""
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"

                # 提取表格資料
                print(f"\n提取表格:")
                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    if tables:
                        print(f"第{i+1}頁: {len(tables)} 個表格")
                        for j, table in enumerate(tables):
                            print(f"  表格{j+1}:")
                            for row in table[:20]:
                                print(f"    {row}")

                # 分析文字內容
                print(f"\n分析PDF內容:")

                # 提取會議室名稱
                rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', all_text)
                if rooms:
                    unique_rooms = list(set(rooms))
                    all_room_data['rooms'].extend(unique_rooms)
                    print(f"會議室: {unique_rooms}")

                # 提取容量
                capacities = re.findall(r'(\d+)\s*[人名桌者席位]', all_text)
                if capacities:
                    caps = [int(c) for c in capacities if 5 <= int(c) <= 1000]
                    all_room_data['capacities'].extend(caps)
                    print(f"容量: {caps[:20]}")

                # 提取面積
                areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', all_text)
                if areas:
                    all_room_data['areas'].extend(areas[:20])
                    print(f"面積: {areas[:20]}")

                # 提取價格
                prices = re.findall(r'(\d+,?\d*)\s*元', all_text)
                if prices:
                    all_room_data['prices'].extend(prices[:20])
                    print(f"價格: {prices[:20]}")

        except ImportError:
            print("pdfplumber 未安裝，無法解析PDF")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

# ========== 3. 匯總並更新 venues.json ==========
print(f"\n{'=' * 100}")
print("3. 更新 venues.json")
print("=" * 100)

print(f"\n提取摘要:")
print(f"  會議室: {len(set(all_room_data['rooms']))}")
print(f"  容量: {len(all_room_data['capacities'])}")
print(f"  面積: {len(all_room_data['areas'])}")
print(f"  價格: {len(all_room_data['prices'])}")

print(f"\n備份: {backup_file}")
print(f"\n✅ 資料提取完成！")
