#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北國賓大飯店 - 完整資料提取
Ambassador Hotel Taipei
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
print("台北國賓大飯店 (Ambassador Hotel Taipei) - 完整資料提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.ambassador_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1069), None)
if not venue:
    print("Venue 1069 not found!")
    sys.exit(1)

base_url = 'https://www.ambassadorhotel.com.tw/'
print(f"場地: {venue['name']}")
print(f"URL: {base_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# ========== 提取主頁所有連結 ==========
print("=" * 100)
print("提取主頁所有連結")
print("=" * 100)

try:
    r = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP Status: {r.status_code}")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')

        # 提取所有連結
        all_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if not href or href.startswith('javascript:') or href.startswith('#'):
                continue

            # 轉換為絕對URL
            if href.startswith('/'):
                full_url = base_url.rstrip('/') + href
            elif not href.startswith('http'):
                full_url = base_url + href
            else:
                full_url = href

            all_links.append({
                'text': text[:60],
                'url': full_url
            })

        # 分類會議/宴會相關連結
        meeting_links = []
        for link in all_links:
            text_lower = link['text'].lower()
            url_lower = link['url'].lower()

            if any(kw in text_lower or kw in url_lower for kw in ['會議', '宴會', '會議室', '婚宴', '活動', 'meeting', 'banquet', 'event', 'conference']):
                meeting_links.append(link)

        print(f"\n發現 {len(meeting_links)} 個會議/宴會相關連結:\n")
        for link in meeting_links[:20]:
            print(f"  {link['text']}")
            print(f"    URL: {link['url']}")

        # 訪問會議/宴會頁面
        print(f"\n{'=' * 100}")
        print("訪問會議/宴會頁面")
        print("=" * 100)

        all_room_data = {
            'rooms': [],
            'capacities': [],
            'areas': [],
            'prices': []
        }

        for i, link in enumerate(meeting_links[:10]):
            url = link['url']
            print(f"\n[{i+1}] 訪問: {link['text']}")
            print("-" * 100)

            try:
                r2 = requests.get(url, timeout=15, verify=False, headers=headers)
                print(f"  狀態: {r2.status_code}")

                if r2.status_code == 200:
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    page_text = soup2.get_text()

                    # 顯示頁面內容預覽
                    lines = [l.strip() for l in page_text.split('\n') if 20 < len(l.strip()) < 200]
                    if lines:
                        print(f"  內容預覽:")
                        for line in lines[:5]:
                            print(f"    {line[:90]}")

                    # 提取會議室名稱
                    rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
                    if rooms:
                        all_room_data['rooms'].extend(rooms[:10])
                        print(f"  會議室: {rooms[:10]}")

                    # 提取容量
                    capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
                    if capacities:
                        caps = [int(c) for c in capacities if 5 <= int(c) <= 1000]
                        all_room_data['capacities'].extend(caps[:10])
                        print(f"  容量: {caps[:10]}")

                    # 提取面積
                    areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
                    if areas:
                        all_room_data['areas'].extend(areas[:10])
                        print(f"  面積: {areas[:10]}")

                    # 提取價格
                    prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
                    if prices:
                        all_room_data['prices'].extend(prices[:10])
                        print(f"  價格: {prices[:10]}")

            except Exception as e:
                print(f"  錯誤: {e}")

        # 匯總
        print(f"\n{'=' * 100}")
        print("提取資料匯總")
        print("=" * 100)
        print(f"會議室: {len(set(all_room_data['rooms']))}")
        print(f"容量: {len(all_room_data['capacities'])}")
        print(f"面積: {len(all_room_data['areas'])}")
        print(f"價格: {len(all_room_data['prices'])}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
