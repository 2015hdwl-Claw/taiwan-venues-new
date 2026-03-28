#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北國賓大飯店 - 階段1：技術檢測與網站結構分析
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北國賓大飯店 - 階段1：技術檢測")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json 取得正確 URL
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1069), None)

if not venue:
    print("Venue 1069 not found!")
    sys.exit(1)

base_url = venue['url']
print(f"URL: {base_url}\n")

# 1.1 訪問主頁
print("1.1 Main Page Access")
print("-" * 100)

try:
    response = requests.get(base_url, timeout=15, verify=False)
    print(f"HTTP Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Size: {len(response.content):,} bytes")
except Exception as e:
    print(f"Error accessing main page: {e}")
    sys.exit(1)

if response.status_code != 200:
    print("Failed to access main page")
    sys.exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# 1.2 檢測是否有動態內容
print("\n1.2 Dynamic Content Detection")
print("-" * 100)

scripts = soup.find_all('script')
print(f"Script tags: {len(scripts)}")

# 檢查 JS 框架
js_frameworks = []
framework_keywords = {
    'react': 'React',
    'vue': 'Vue.js',
    'angular': 'Angular',
    'jquery': 'jQuery'
}

script_text = ' '.join([s.string or '' for s in scripts])
for keyword, name in framework_keywords.items():
    if keyword in script_text.lower():
        js_frameworks.append(name)

if js_frameworks:
    print(f"JS Frameworks detected: {', '.join(js_frameworks)}")
else:
    print("No major JS framework detected")

# 1.3 尋找會議/宴會相關連結
print("\n1.3 Meeting/Banquet Links Discovery")
print("-" * 100)

meeting_links = []

for link in soup.find_all('a', href=True):
    href = link['href'].lower()
    text = link.get_text().lower()

    # 尋找包含會議/宴會/活動等關鍵字的連結
    keywords = ['meeting', 'banquet', 'conference', 'event', 'mice', 'wedding', '會議', '宴會', '會議室', '婚宴', '國賓']

    if any(keyword in href or keyword in text for keyword in keywords):
        full_url = link['href'] if link['href'].startswith('http') else base_url + link['href']
        meeting_links.append({
            'text': link.get_text(strip=True)[:60],
            'url': full_url
        })

# 去重並顯示
seen = set()
unique_links = []
for link in meeting_links:
    if link['url'] not in seen:
        seen.add(link['url'])
        unique_links.append(link)

print(f"Found {len(unique_links)} meeting/banquet related links:")
for link in unique_links[:15]:
    print(f"  - {link['text']}: {link['url']}")

# 1.4 尋找 PDF 連結
print("\n1.4 PDF Discovery")
print("-" * 100)

pdf_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if '.pdf' in href.lower():
        if not href.startswith('http'):
            href = href if href.startswith('/') else base_url + href
        pdf_links.append(href)

print(f"Found {len(pdf_links)} PDF links on main page")
if pdf_links:
    for pdf in pdf_links[:5]:
        print(f"  - {pdf}")

# 1.5 檢查現有資料
print("\n1.5 Check Existing Data")
print("-" * 100)

if venue:
    print(f"Current venue: {venue.get('name')}")
    print(f"Rooms: {len(venue.get('rooms', []))}")
    print(f"Quality score: {venue.get('metadata', {}).get('qualityScore', 'N/A')}")

    # 檢查會議室資料完整度
    rooms = venue.get('rooms', [])
    rooms_with_capacity = 0
    rooms_with_area = 0
    rooms_with_price = 0

    for r in rooms:
        # Check capacity (could be dict or int)
        cap = r.get('capacity')
        if cap:
            if isinstance(cap, dict):
                if any(cap.values()):
                    rooms_with_capacity += 1
            elif isinstance(cap, int):
                rooms_with_capacity += 1

        # Check area
        if r.get('areaSqm') or r.get('area'):
            rooms_with_area += 1

        # Check price
        if r.get('price'):
            rooms_with_price += 1

    print(f"Rooms with capacity: {rooms_with_capacity}/{len(rooms)}")
    print(f"Rooms with area: {rooms_with_area}/{len(rooms)}")
    print(f"Rooms with price: {rooms_with_price}/{len(rooms)}")

    # 檢查聯絡資訊
    has_contact = 'contact' in venue
    print(f"Has contact info: {has_contact}")

    # 檢查前幾個會議室
    print("\nFirst 3 rooms:")
    for room in rooms[:3]:
        name = room.get('name', 'N/A')
        cap = room.get('capacity')
        if isinstance(cap, dict):
            capacity = cap.get('theater', 'N/A')
        else:
            capacity = cap if cap else 'N/A'
        area = room.get('areaSqm', 'N/A')
        price = room.get('price', {})
        price_str = str(price) if price else 'N/A'
        print(f"  - {name}: cap={capacity}, area={area}㎡, price={price_str[:30]}")

# 儲存階段1結果
stage1_result = {
    "venue": "台北國賓大飯店",
    "venue_id": 1069,
    "timestamp": datetime.now().isoformat(),
    "main_page": {
        "url": base_url,
        "status": response.status_code,
        "size": len(response.content),
        "js_frameworks": js_frameworks
    },
    "meeting_links": unique_links,
    "pdf_links": pdf_links
}

with open('ambassador_stage1_results.json', 'w', encoding='utf-8') as f:
    json.dump(stage1_result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("Stage 1 Complete")
print("=" * 100)
print(f"Meeting links: {len(unique_links)}")
print(f"PDF links: {len(pdf_links)}")
print(f"Result saved: ambassador_stage1_results.json")
