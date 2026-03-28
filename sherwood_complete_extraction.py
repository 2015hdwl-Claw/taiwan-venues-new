#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北喜瑞飯店 - 完整資料提取
應用從台北艾麗和台北美福學到的教訓
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
print("台北喜瑞飯店 (Sherwood Taipei) - 完整資料提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.sherwood_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1068), None)
if not venue:
    print("Venue 1068 not found!")
    sys.exit(1)

base_url = 'https://www.ambiencehotel.com.tw/'
print(f"場地: {venue['name']}")
print(f"URL: {base_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

# ========== 步驟1：提取主頁所有連結 ==========
print("=" * 100)
print("步驟1：提取主頁所有連結")
print("=" * 100)

try:
    r = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP Status: {r.status_code}")
    print(f"Content-Length: {len(r.content):,} bytes\n")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')

        # 提取所有連結
        all_links = []
        seen_urls = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if not href or href.startswith('javascript:') or href.startswith('#') or href.startswith('mailto:'):
                continue

            # 轉換為絕對URL
            if href.startswith('/'):
                full_url = base_url.rstrip('/') + href
            elif not href.startswith('http'):
                full_url = base_url + href
            else:
                full_url = href

            # 去重
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                all_links.append({
                    'text': text[:60],
                    'url': full_url
                })

        print(f"發現 {len(all_links)} 個連結\n")

        # 分類連結
        internal_links = []
        dynamic_links = []
        file_links = []
        meeting_links = []

        for link in all_links:
            url = link['url']

            # 只保留內部連結
            if 'ambiencehotel.com.tw' in url:
                internal_links.append(link)

                # 分類動態連結
                parsed = urllib.parse.urlparse(url)
                if parsed.query:
                    dynamic_links.append(link)

                # 分類檔案連結
                if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                    file_links.append(link)

                # 分類會議/宴會相關連結
                text_lower = link['text'].lower()
                url_lower = url.lower()
                if any(kw in text_lower or kw in url_lower for kw in ['會議', '宴會', '會議室', '婚宴', '活動', 'meeting', 'banquet', 'event', 'conference']):
                    meeting_links.append(link)

        print(f"內部連結: {len(internal_links)}")
        print(f"動態連結: {len(dynamic_links)}")
        print(f"檔案連結: {len(file_links)}")
        print(f"會議/宴會相關連結: {len(meeting_links)}\n")

        # 顯示會議/宴會相關連結
        if meeting_links:
            print("會議/宴會相關連結:")
            print("-" * 100)
            for link in meeting_links[:20]:
                print(f"  {link['text']}")
                print(f"    URL: {link['url']}")

        # 顯示PDF連結
        if file_links:
            print("\n檔案連結:")
            print("-" * 100)
            for link in file_links:
                print(f"  {link['text'][:60]}")
                print(f"    URL: {link['url']}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

# ========== 步驟2：訪問所有會議/宴會相關頁面 ==========
print("\n" + "=" * 100)
print("步驟2：訪問會議/宴會相關頁面")
print("=" * 100)

all_room_data = {
    'rooms': [],
    'capacities': [],
    'areas': [],
    'prices': [],
    'features': []
}

if meeting_links:
    for i, link in enumerate(meeting_links[:15]):  # 最多處理15個
        url = link['url']
        print(f"\n[{i+1}/{min(len(meeting_links), 15)}] 訪問: {link['text']}")
        print("-" * 100)

        try:
            r = requests.get(url, timeout=15, verify=False, headers=headers)
            print(f"  狀態: {r.status_code}")

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                page_text = soup.get_text()

                # 顯示頁面標題
                title = soup.find('title')
                if title:
                    print(f"  標題: {title.get_text(strip=True)[:60]}")

                # 提取會議室名稱
                room_patterns = [
                    r'([^\s]{2,10}[廳室房樓])(?:\s|[,，.。、\n])',
                    r'(會議室[^\\s]{1,5})',
                    r'([A-Z][a-z]+\s+(?:Room|Hall|Ballroom))'
                ]

                for pattern in room_patterns:
                    matches = re.findall(pattern, page_text)
                    for match in matches:
                        if match and len(match) > 2 and match not in all_room_data['rooms']:
                            all_room_data['rooms'].append(match)

                # 提取容量
                capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
                if capacities:
                    caps = [int(c) for c in capacities if 5 <= int(c) <= 1000]
                    all_room_data['capacities'].extend(caps)
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

                # 顯示部分內容
                lines = [l.strip() for l in page_text.split('\n') if 20 < len(l.strip()) < 150]
                if lines:
                    print(f"  內容預覽:")
                    for line in lines[:5]:
                        print(f"    {line[:90]}")

        except Exception as e:
            print(f"  錯誤: {e}")

# ========== 步驟3：嘗試常見會議路徑 ==========
print("\n" + "=" * 100)
print("步驟3：嘗試常見會議路徑")
print("=" * 100)

meeting_paths = ['/meeting', '/meetings', '/banquet', '/banquets', '/conference',
                  '/event', '/events', '/wedding', '/facility', '/facilities',
                  '/會議', '/宴會', '/會議室', '/婚宴', '/活動', '/宴會廳']

for path in meeting_paths:
    url = base_url.rstrip('/') + path
    print(f"\n嘗試: {path}")

    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        print(f"  狀態: {r.status_code}")

        if r.status_code == 200 and url not in [l['url'] for l in meeting_links]:
            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text()

            # 檢查是否包含會議相關內容
            if '會議' in page_text or '宴會' in page_text or '會議室' in page_text:
                print(f"  ✓ 包含會議相關內容")

                # 提取關鍵資訊
                lines = [l.strip() for l in page_text.split('\n') if 20 < len(l.strip()) < 150]
                if lines:
                    print(f"  內容預覽:")
                    for line in lines[:3]:
                        print(f"    {line[:80]}")

    except Exception as e:
        print(f"  ✗ 錯誤: {e}")

# ========== 匯總結果 ==========
print("\n" + "=" * 100)
print("提取資料匯總")
print("=" * 100)

print(f"\n會議室數量: {len(set(all_room_data['rooms']))}")
if all_room_data['rooms']:
    print(f"  發現的會議室: {list(set(all_room_data['rooms']))[:20]}")

print(f"\n容量數據: {len(all_room_data['capacities'])} 個")
if all_room_data['capacities']:
    print(f"  範圍: {min(all_room_data['capacities'])} - {max(all_room_data['capacities'])} 人")

print(f"\n面積數據: {len(all_room_data['areas'])} 個")
if all_room_data['areas']:
    print(f"  範例: {all_room_data['areas'][:10]}")

print(f"\n價格數據: {len(all_room_data['prices'])} 個")
if all_room_data['prices']:
    print(f"  範例: {all_room_data['prices'][:10]}")

print(f"\n備份: {backup_file}")
print(f"\n下一步: 根據發現的資料更新 venues.json")
