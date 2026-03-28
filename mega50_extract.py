#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mega50宴會廳 - 三階段完整爬蟲
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
print("Mega50宴會廳 - 完整爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.mega50_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1507), None)
if not venue:
    print("Venue 1507 not found!")
    sys.exit(1)

base_url = 'https://www.mega50.com.tw/'
target_url = 'https://www.mega50.com.tw/ch/dingdingballroom'

print(f"場地: {venue['name']}")
print(f"主頁: {base_url}")
print(f"目標: {target_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# ========== 階段1：技術檢測 ==========
print("=" * 100)
print("階段1：技術檢測")
print("=" * 100)

try:
    r = requests.get(target_url, timeout=20, verify=False, headers=headers)
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
print("階段2：深度爬蟲")
print("=" * 100)

print("\n2.1 提取頁面內容...")

page_text = soup.get_text()
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
                pdf_url = base_url.rstrip('/') + pdf_url
        pdf_links.append(pdf_url)

if pdf_links:
    print(f"\n發現PDF:")
    for pdf_url in pdf_links[:10]:
        print(f"  {pdf_url}")

# 提取所有連結
print(f"\n2.2 提取所有連結...")

all_links = []
seen_urls = set()

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

    # 只保留內部連結
    if 'mega50.com.tw' in full_url and full_url not in seen_urls:
        seen_urls.add(full_url)
        all_links.append({
            'text': text[:60],
            'url': full_url
        })

print(f"找到 {len(all_links)} 個內部連結")

# 分類連結
meeting_links = []

for link in all_links:
    text_lower = link['text'].lower()
    url_lower = link['url'].lower()

    if any(kw in text_lower or kw in url_lower for kw in
           ['會議', '宴會', '會議室', '婚宴', '活動', 'meeting', 'banquet', 'event', 'conference']):
        meeting_links.append(link)

print(f"會議/宴會相關連結: {len(meeting_links)}")

if meeting_links:
    print(f"\n會議/宴會連結:")
    for link in meeting_links[:15]:
        print(f"  {link['text']}")
        print(f"    {link['url']}")

print(f"\n2.3 訪問主頁尋找更多資訊...")

try:
    r_home = requests.get(base_url, timeout=15, verify=False, headers=headers)
    print(f"主頁狀態: {r_home.status_code}")

    if r_home.status_code == 200:
        soup_home = BeautifulSoup(r_home.text, 'html.parser')
        page_text_home = soup_home.get_text()

        # 提取容量
        capacities_home = re.findall(r'(\d+)\s*[人名桌者席位]', page_text_home)
        if capacities_home:
            caps_home = [int(c) for c in capacities_home if 5 <= int(c) <= 2000]
            print(f"主頁容量: {caps_home[:20]}")

        # 提取面積
        areas_home = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text_home)
        if areas_home:
            print(f"主頁面積: {areas_home[:20]}")

        # 提取價格
        prices_home = re.findall(r'(\d+,?\d*)\s*元', page_text_home)
        if prices_home:
            print(f"主頁價格: {prices_home[:20]}")

        # 尋找PDF
        pdf_links_home = []
        for link in soup_home.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                pdf_url = link['href']
                if not pdf_url.startswith('http'):
                    if pdf_url.startswith('/'):
                        pdf_url = base_url.rstrip('/') + pdf_url
                pdf_links_home.append(pdf_url)

        if pdf_links_home:
            print(f"\n主頁PDF:")
            for pdf_url in pdf_links_home:
                print(f"  {pdf_url}")

except Exception as e:
    print(f"主頁訪問錯誤: {e}")

# ========== 階段3：驗證寫入 ==========
print(f"\n{'=' * 100}")
print("階段3：驗證寫入")
print("=" * 100)

print(f"\n提取摘要:")
print(f"  會議室: {len(set(rooms_found))}")
print(f"  容量: {len(capacities) if capacities else 0}")
print(f"  面積: {len(areas) if areas else 0}")
print(f"  價格: {len(prices) if prices else 0}")
print(f"  PDF: {len(pdf_links)}")

# 更新基本聯絡資訊
venue['contact']['phone'] = '+886-2-2955-8888'
venue['contact']['email'] = 'service@mega50.com.tw'

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = "V3_ThreeStage"

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n備份: {backup_file}")
print(f"\n✅ Mega50宴會廳爬蟲完成")
