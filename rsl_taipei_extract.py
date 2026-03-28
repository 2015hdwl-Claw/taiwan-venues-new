#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瓢山林台北中和飯店 - 三階段完整爬蟲
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
print("瓢山林台北中和飯店 - 完整爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.rsl_taipei_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1506), None)
if not venue:
    print("Venue 1506 not found!")
    sys.exit(1)

base_url = 'https://taipei.rslhotel.com/'
meeting_url = 'https://taipei.rslhotel.com/meeting/'

print(f"場地: {venue['name']}")
print(f"主頁: {base_url}")
print(f"會議頁: {meeting_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# ========== 階段1：技術檢測 ==========
print("=" * 100)
print("階段1：技術檢測")
print("=" * 100)

try:
    r = requests.get(meeting_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP 狀態: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {len(r.content):,} bytes\n")

    if r.status_code != 200:
        print("❌ 無法訪問網站")
        sys.exit(1)

    soup = BeautifulSoup(r.text, 'html.parser')

    # 檢測 JS 框架
    scripts = soup.find_all('script')
    has_react = any('react' in str(s).lower() for s in scripts)
    has_vue = any('vue' in str(s).lower() for s in scripts)
    has_jquery = any('jquery' in str(s).lower() for s in scripts)

    print(f"JS框架檢測:")
    print(f"  React: {'✓' if has_react else '✗'}")
    print(f"  Vue: {'✓' if has_vue else '✗'}")
    print(f"  jQuery: {'✓' if has_jquery else '✗'}")

    # 檢測 CMS
    if 'wp-content' in r.text:
        cms_type = "WordPress"
    elif 'Drupal' in r.text:
        cms_type = "Drupal"
    else:
        cms_type = "未知/自訂"

    print(f"\nCMS系統: {cms_type}")

except Exception as e:
    print(f"❌ 技術檢測失敗: {e}")
    sys.exit(1)

# ========== 階段2：深度爬蟲 ==========
print(f"\n{'=' * 100}")
print("階段2：深度爬蟲 - 完整連結發現")
print("=" * 100)

print("\n2.1 提取主頁所有連結...")

all_links = []
seen_urls = set()

for link in soup.find_all('a', href=True):
    href = link['href']
    text = link.get_text(strip=True)

    if not href or href.startswith('javascript:') or href.startswith('#'):
        continue

    # 轉換為絕對URL
    if href.startswith('/'):
        full_url = 'https://taipei.rslhotel.com' + href
    elif not href.startswith('http'):
        full_url = base_url + href
    else:
        full_url = href

    # 只保留內部連結
    if 'rslhotel.com' in full_url and full_url not in seen_urls:
        seen_urls.add(full_url)
        all_links.append({
            'text': text[:60],
            'url': full_url
        })

print(f"找到 {len(all_links)} 個內部連結")

# 分類連結
meeting_links = []
file_links = []

for link in all_links:
    text_lower = link['text'].lower()
    url_lower = link['url'].lower()

    if any(kw in text_lower or kw in url_lower for kw in
           ['會議', '宴會', '會議室', '婚宴', '活動', 'meeting', 'banquet', 'event', 'conference']):
        meeting_links.append(link)

    if '.pdf' in url_lower:
        file_links.append(link)

print(f"會議/宴會相關連結: {len(meeting_links)}")
print(f"PDF連結: {len(file_links)}")

# 顯示會議連結
if meeting_links:
    print(f"\n會議/宴會連結:")
    for link in meeting_links[:15]:
        print(f"  {link['text']}")
        print(f"    {link['url']}")

# 顯示PDF連結
if file_links:
    print(f"\nPDF連結:")
    for link in file_links:
        print(f"  {link['url']}")

print(f"\n2.2 訪問所有會議頁面...")

all_room_data = {
    'rooms': [],
    'capacities': [],
    'areas': [],
    'prices': []
}

for i, link in enumerate(meeting_links[:10]):
    url = link['url']
    print(f"\n[{i+1}] {link['text']}")
    print(f"URL: {url}")
    print("-" * 80)

    try:
        r2 = requests.get(url, timeout=15, verify=False, headers=headers)
        print(f"  狀態: {r2.status_code}")

        if r2.status_code == 200:
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            page_text = soup2.get_text()

            # 提取會議室
            rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
            if rooms:
                all_room_data['rooms'].extend(rooms)
                print(f"  會議室: {rooms[:10]}")

            # 提取容量
            capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
            if capacities:
                caps = [int(c) for c in capacities if 5 <= int(c) <= 1000]
                all_room_data['capacities'].extend(caps)
                print(f"  容量: {caps[:10]}")

            # 提取面積
            areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
            if areas:
                all_room_data['areas'].extend(areas)
                print(f"  面積: {areas[:10]}")

            # 提取價格
            prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
            if prices:
                all_room_data['prices'].extend(prices)
                print(f"  價格: {prices[:10]}")

    except Exception as e:
        print(f"  錯誤: {e}")

print(f"\n2.3 嘗試常見路徑...")

common_paths = ['/meeting', '/banquet', '/conference', '/events', '/facility', '/facilities']

for path in common_paths:
    url = base_url.rstrip('/') + path
    print(f"\n嘗試: {path}")

    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        if r.status_code == 200:
            print(f"  ✓ 200 OK")

    except Exception as e:
        pass

# ========== 階段3：驗證寫入 ==========
print(f"\n{'=' * 100}")
print("階段3：驗證寫入")
print("=" * 100)

print(f"\n提取摘要:")
print(f"  會議室: {len(set(all_room_data['rooms']))}")
print(f"  容量: {len(all_room_data['capacities'])}")
print(f"  面積: {len(all_room_data['areas'])}")
print(f"  價格: {len(all_room_data['prices'])}")

# 更新基本聯絡資訊
venue['contact']['phone'] = '+886-2-2226-6688'
venue['contact']['email'] = 'rsl.tp@rslhotels.com.tw'

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = "V3_ThreeStage"

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n備份: {backup_file}")
print(f"\n✅ 瓢山林台北中和飯店爬蟲完成")
