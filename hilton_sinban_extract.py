#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北新板希爾頓酒店 - 三階段完整爬蟲
Hilton Taipei Sinban - 完整會議室資料提取
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import re
import urllib.parse
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北新板希爾頓酒店 - 完整爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.hilton_sinban_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1512), None)
if not venue:
    print("Venue 1512 not found!")
    sys.exit(1)

base_url = 'https://www.hilton.com.cn/zh-hk/hotel/taipei/hilton-taipei-sinban-TSATCHI/'
event_url = 'https://www.hilton.com.cn/zh-hk/hotel/taipei/hilton-taipei-sinban-TSATCHI/event.html'

print(f"場地: {venue['name']}")
print(f"主頁: {base_url}")
print(f"會議頁: {event_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# ========== 步驟1：訪問會議頁面 ==========
print("=" * 100)
print("步驟1：訪問會議活動頁面")
print("=" * 100)

try:
    r = requests.get(event_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP 狀態: {r.status_code}")
    print(f"Content-Length: {len(r.content):,} bytes\n")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 顯示完整內容（前100行）
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 200]
        print(f"頁面內容（前100行）:")
        for line in lines[:100]:
            print(f"  {line[:110]}")

        # 提取關鍵資訊
        print(f"\n{'=' * 100}")
        print("關鍵資訊提取")
        print("=" * 100)

        # 提取會議室名稱
        room_patterns = [
            r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])',
            r'(宴會廳|會議室|會議廳|多功能廳)'
        ]

        rooms_found = []
        for pattern in room_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                rooms_found.extend(matches)

        if rooms_found:
            unique_rooms = list(set(rooms_found))
            print(f"會議室: {unique_rooms}")

        # 提取容量
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 2000]
            print(f"容量: {caps[:20]}")

        # 提取面積
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        if areas:
            print(f"面積: {areas[:20]}")

        # 提取價格
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
        if prices:
            print(f"價格: {prices[:20]}")

        # 尋找PDF
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                pdf_url = link['href']
                if not pdf_url.startswith('http'):
                    if pdf_url.startswith('/'):
                        pdf_url = 'https://www.hilton.com.cn' + pdf_url
                pdf_links.append(pdf_url)

        if pdf_links:
            print(f"\n發現PDF:")
            for pdf_url in pdf_links[:10]:
                print(f"  {pdf_url}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

print(f"\n備份: {backup_file}")
print(f"\n✅ 資料提取完成")
print(f"下一步: 更新 venues.json")
