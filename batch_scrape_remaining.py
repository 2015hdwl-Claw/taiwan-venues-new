#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次爬取剩餘高優先級場地
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
print("批次爬取剩餘高優先級場地")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.batch_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

# 高優先級場地（有完整URL）
priority_venues = [
    1515,  # 晶宴會館 府中館
    1518,  # 靚點宴會館
    1519,  # 葳格國際會議中心
    1522,  # 天圓地方婚宴會館
    1525,  # 潮港城宴會廳 南屯店
    1528,  # 漢來國際宴會廳
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

for venue_id in priority_venues:
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if not venue:
        print(f"Venue {venue_id} not found!\n")
        continue

    print(f"\n{'=' * 100}")
    print(f"[{venue_id}] {venue['name']}")
    print("=" * 100)

    url = venue.get('url', '')
    if not url or url == 'TBD':
        print(f"❌ 無URL或URL為TBD，跳過\n")
        continue

    print(f"URL: {url}\n")

    try:
        # 訪問網站
        r = requests.get(url, timeout=20, verify=False, headers=headers)
        print(f"HTTP 狀態: {r.status_code}")

        if r.status_code != 200:
            print(f"❌ 無法訪問\n")
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 提取關鍵資訊
        print(f"提取資訊...")

        # 會議室
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            unique_rooms = list(set(rooms))[:10]
            print(f"  會議室: {unique_rooms}")

        # 容量
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 2000][:10]
            print(f"  容量: {caps}")

        # 面積
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        if areas:
            print(f"  面積: {areas[:10]}")

        # 價格
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
        if prices:
            print(f"  價格: {prices[:10]}")

        # PDF
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                pdf_url = link['href']
                if not pdf_url.startswith('http'):
                    if pdf_url.startswith('/'):
                        base_url = url.rstrip('/')
                        while '/'.join(base_url.rstrip('/').split('/')[:-1]):
                            base_url = '/'.join(base_url.rstrip('/').split('/')[:-1])
                        pdf_url = base_url + pdf_url
                pdf_links.append(pdf_url)

        if pdf_links:
            print(f"  PDF: {len(pdf_links)} 個")

        # 建立基本會議室資料
        rooms_data = []
        if capacities:
            max_cap = max([int(c) for c in capacities if 5 <= int(c) <= 2000])
            if max_cap > 10:
                rooms_data.append({
                    'name': '宴會廳',
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8)
                    },
                    'source': 'html_batch_20260327'
                })

        # 更新場地
        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # 更新聯絡資訊（如果頁面有）
        phone_match = re.search(r'0\d-\d{3,4}-\d{3,4}', page_text)
        if phone_match:
            venue['contact']['phone'] = phone_match.group()

        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        if email_match:
            email = email_match.group()
            if 'noreply' not in email.lower() and 'no-reply' not in email.lower():
                venue['contact']['email'] = email

        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Batch"

        # 計算品質分數
        quality_score = 35
        if venue.get('contact', {}).get('phone'):
            quality_score += 10
        if venue.get('contact', {}).get('email'):
            quality_score += 10
        if venue.get('rooms'):
            quality_score += len(venue['rooms']) * 3
            for room in venue['rooms']:
                if room.get('capacity'):
                    quality_score += 5

        venue['metadata']['qualityScore'] = min(quality_score, 100)

        print(f"✅ 更新完成，品質分數: {venue['metadata']['qualityScore']}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        continue

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("批次爬取完成")
print("=" * 100)
print(f"備份: {backup_file}")
print(f"\n已處理: {len(priority_venues)} 個場地")
print(f"下一步: 繼續處理剩餘場地")
