#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
處理有URL的剩餘場地
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
print("處理有URL的剩餘場地")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.scrape_remaining_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

# 有URL但尚未完整處理的場地
target_venues = [
    (1510, '新莊典華', 'https://www.denwell.com/xinzhuang-banquet-venue/'),
    (1511, '翡麗詩莊園', 'https://www.felicite-wed.com/'),
    (1513, '汐止福泰大飯店', 'https://www.fortehotelxizhi.com.tw/banquet-detail/meeting/'),
    (1516, '彭園婚宴會館 新店館', 'https://www.pengyuan.com.tw/'),
    (1517, '頤品大飯店 新莊晶冠館', 'https://www.palaiscollection.com/'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

for venue_id, venue_name, url in target_venues:
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if not venue:
        print(f"Venue {venue_id} not found!\n")
        continue

    print(f"\n{'=' * 100}")
    print(f"[{venue_id}] {venue_name}")
    print("=" * 100)

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

        # 顯示部分內容
        lines = [l.strip() for l in page_text.split('\n') if 15 < len(l.strip()) < 300]
        print(f"\n頁面內容（前60行）:")
        for line in lines[:60]:
            print(f"  {line[:100]}")

        # 提取關鍵資訊
        print(f"\n{'=' * 100}")
        print("關鍵資訊提取")
        print("=" * 100)

        # 會議室
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            unique_rooms = list(set(rooms))[:15]
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

        # PDF
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                pdf_url = link['href']
                if not pdf_url.startswith('http'):
                    base = '/'.join(url.split('/')[:3])
                    pdf_url = base + pdf_url if pdf_url.startswith('/') else base + '/' + pdf_url
                pdf_links.append(pdf_url)

        if pdf_links:
            print(f"PDF: {len(pdf_links)} 個")
            for pdf_url in pdf_links[:5]:
                print(f"  {pdf_url}")

        # 聯絡資訊
        phone = None
        phone_patterns = [
            r'0\d-\d{3,4}-\d{3,4}',
            r'\+886-\d[\d-]{7,9}',
            r'\+886\s?\d[\d\s-]{7,9}'
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, page_text)
            if match:
                phone = match.group()
                break

        if phone:
            print(f"電話: {phone}")
            venue['contact']['phone'] = phone

        email = None
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        if email_match:
            email_candidate = email_match.group()
            if 'noreply' not in email_candidate.lower() and 'no-reply' not in email_candidate.lower():
                email = email_candidate
                print(f"Email: {email}")
                venue['contact']['email'] = email

        # 建立會議室資料
        rooms_data = []
        if capacities:
            caps_int = [int(c) for c in capacities if 5 <= int(c) <= 2000]
            if caps_int:
                max_cap = max(caps_int)

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

        print(f"\n✅ 更新完成，品質分數: {venue['metadata']['qualityScore']}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        import traceback
        traceback.print_exc()
        continue

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("處理完成")
print("=" * 100)
print(f"備份: {backup_file}")
