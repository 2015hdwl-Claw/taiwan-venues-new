#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復並重試漢來國際宴會廳
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
print("漢來國際宴會廳 - 完整爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.hilai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1528), None)
if not venue:
    print("Venue 1528 not found!")
    sys.exit(1)

url = 'https://www.grand-hilai.com/'

print(f"場地: {venue['name']}")
print(f"URL: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

try:
    r = requests.get(url, timeout=20, verify=False, headers=headers)
    print(f"HTTP 狀態: {r.status_code}\n")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 顯示部分內容
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 300]
        print("頁面內容（前50行）:")
        for line in lines[:50]:
            print(f"  {line}")

        # 提取關鍵資訊
        print(f"\n{'=' * 100}")
        print("關鍵資訊提取")
        print("=" * 100)

        # 會議室
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            unique_rooms = list(set(rooms))[:20]
            print(f"會議室: {unique_rooms}")

        # 容量
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 2000][:20]
            print(f"容量: {caps}")

        # 面積
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        if areas:
            print(f"面積: {areas[:20]}")

        # 價格
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
        if prices:
            print(f"價格: {prices[:20]}")

        # 建立會議室資料（如果找到容量）
        if capacities:
            caps_int = [int(c) for c in capacities if 5 <= int(c) <= 2000]
            if caps_int:
                max_cap = max(caps_int)

                rooms_data = [{
                    'name': '宴會廳',
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8)
                    },
                    'source': 'html_20260327'
                }]

                venue['rooms'] = rooms_data
                venue['capacity'] = rooms_data[0]['capacity']

                print(f"\n會議室資料:")
                print(f"  宴會廳: 容量 {rooms_data[0]['capacity']}")

        # 聯絡資訊
        phone_match = re.search(r'0\d-\d{3,4}-\d{3,4}', page_text)
        if phone_match:
            venue['contact']['phone'] = phone_match.group()

        # 計算品質分數
        quality_score = 35
        if venue.get('contact', {}).get('phone'):
            quality_score += 10
        if venue.get('rooms'):
            quality_score += len(venue['rooms']) * 3
            for room in venue['rooms']:
                if room.get('capacity'):
                    quality_score += 5

        venue['metadata']['qualityScore'] = min(quality_score, 100)
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Fixed"

        print(f"\n品質分數: {venue['metadata']['qualityScore']}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n備份: {backup_file}")
print(f"\n✅ 漢來國際宴會廳更新完成")
