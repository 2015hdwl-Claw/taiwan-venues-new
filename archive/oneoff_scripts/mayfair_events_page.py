#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北美福大飯店 - 深度提取 /events 頁面
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
print("台北美福大飯店 - /events 頁面深度提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1095), None)
base_url = 'https://www.grandmayfull.com/events'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

print(f"訪問: {base_url}\n")

try:
    r = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP Status: {r.status_code}")
    print(f"Content-Length: {len(r.content):,} bytes\n")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')

        # 提取所有文字
        page_text = soup.get_text()

        # 顯示完整文字內容
        print("=" * 100)
        print("完整頁面文字內容")
        print("=" * 100)

        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        for i, line in enumerate(lines):
            if len(line) > 10:
                print(f"{i+1:3d}. {line}")

        # 尋找特定關鍵資訊
        print("\n" + "=" * 100)
        print("關鍵資訊提取")
        print("=" * 100)

        # 會議室名稱
        room_patterns = [
            r'([^\s]{2,8}[廳室樓]).*?(\d+|\d+\.\d+)\s*(坪|㎡|平方公尺)',
            r'([^\s]{2,8}[廳室]).*?(\d+)\s*人',
            r'(宴會廳|會議室|會議廳)[^\n]{0,200}'
        ]

        print("\n會議室相關:")
        for pattern in room_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                for match in matches[:5]:
                    print(f"  {match}")

        # 容量
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            print(f"\n容量數據: {capacities[:20]}")

        # 面積
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        if areas:
            print(f"\n面積數據:")
            for area in areas[:20]:
                print(f"  {area}")

        # 價格
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
        if prices:
            print(f"\n價格數據: {prices[:20]}")

        # 設備
        equipment_keywords = ['LED', '音響', '投影機', '麥克風', '白板', '螢幕', 'BOSE', '舞台']
        found_equipment = []
        for keyword in equipment_keywords:
            if keyword in page_text:
                found_equipment.append(keyword)

        if found_equipment:
            print(f"\n設備: {', '.join(found_equipment)}")

        # 尋找所有連結
        print("\n" + "=" * 100)
        print("頁面內所有連結")
        print("=" * 100)

        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if text and len(text) > 2 and len(text) < 50:
                # 轉換為絕對URL
                if href.startswith('/'):
                    full_url = 'https://www.grandmayfull.com' + href
                elif not href.startswith('http'):
                    full_url = 'https://www.grandmayfull.com/' + href
                else:
                    full_url = href

                print(f"  {text[:40]:40s} -> {full_url}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
