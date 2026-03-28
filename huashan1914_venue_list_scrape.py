#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 場地介紹頁面詳細爬取
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import re
from datetime import datetime
from urllib.parse import urljoin

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("華山1914 - 場地介紹頁面詳細爬取")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

venue_list_url = "https://www.huashan1914.com/w/huashan1914/AppPlaceList"

print("訪問場地介紹頁面...")
session = requests.Session()
response = session.get(venue_list_url, timeout=15, verify=False)
print(f"HTTP 狀態: {response.status_code}")

if response.status_code != 200:
    print(f"❌ 頁面訪問失敗")
    sys.exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# 儲存頁面
page_file = f"huashan1914_venue_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
with open(page_file, 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
print(f"✅ 頁面已儲存: {page_file}\n")

# 分析頁面
print("=" * 100)
print("分析場地資料")
print("=" * 100)

page_text = soup.get_text()

# 尋找場地項目
venues = []

# 方法1: 尋找所有卡片或列表項目
# 華山1914 可能使用卡片式設計展示場地

# 尋找所有可能包含場地資訊的 div 或 section
for div in soup.find_all(['div', 'section', 'article'], class_=True):
    classes = ' '.join(div.get('class', []))

    # 尋找包含場地關鍵字的元素
    text = div.get_text()

    if any(kw in text for kw in ['展區', '空間', '坪', '人', '樓']) and len(text) > 20 and len(text) < 500:
        # 尋找場地名稱
        # 可能是標題 h1-h6
        title = None
        for h in div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            title_text = h.get_text(strip=True)
            if title_text and len(title_text) < 50:
                title = title_text
                break

        if not title:
            # 嘗試從 class 或 id 猜測
            if any(kw in classes.lower() for kw in ['title', 'name', 'venue', 'place', 'space']):
                title = text.split('\n')[0].strip()

        # 尋找容量
        capacity = None
        capacity_match = re.search(r'(\d+)\s*[人名]', text)
        if capacity_match:
            capacity = int(capacity_match.group(1))

        # 尋找坪數
        area = None
        area_match = re.search(r'(\d+\.?\d*)\s*[坪平米]', text)
        if area_match:
            area = float(area_match.group(1))

        # 尋找樓層
        floor = None
        floor_match = re.search(r'(\d+[F樓層])', text)
        if floor_match:
            floor = floor_match.group(1)

        # 尋找描述
        description = None
        for p in div.find_all('p'):
            p_text = p.get_text(strip=True)
            if len(p_text) > 20:
                description = p_text
                break

        # 尋找圖片
        image_url = None
        img = div.find('img')
        if img:
            src = img.get('src') or img.get('data-src')
            if src:
                image_url = urljoin('https://www.huashan1914.com/', src)

        if title or capacity or area:
            venue = {
                'name': title if title else '未命名場地',
                'floor': floor,
                'capacity': capacity,
                'area': area,
                'description': description,
                'image_url': image_url,
                'source': venue_list_url
            }
            venues.append(venue)

# 去重
seen = set()
unique_venues = []
for venue in venues:
    key = f"{venue['name']}_{venue.get('floor', '')}"
    if key not in seen and venue['name'] != '未命名場地':
        seen.add(key)
        unique_venues.append(venue)

print(f"找到場地: {len(unique_venues)} 個\n")

# 顯示場地列表
for i, venue in enumerate(unique_venues, 1):
    print(f"{i}. {venue['name']}")
    if venue['floor']:
        print(f"   樓層: {venue['floor']}")
    if venue['capacity']:
        print(f"   容量: {venue['capacity']} 人")
    if venue['area']:
        print(f"   面積: {venue['area']} 坪")
    if venue['description']:
        print(f"   說明: {venue['description'][:80]}...")
    print()

# 尋找價格資訊
price_pattern = r'(\d{2,6}[,.]?\d{0,3})\s*元'
prices = re.findall(price_pattern, page_text)

if prices:
    valid_prices = []
    for p in prices:
        try:
            price = int(p.replace(',', ''))
            if 1000 <= price <= 500000:
                valid_prices.append(price)
        except:
            pass

    if valid_prices:
        print(f"找到價格資訊: {len(valid_prices)} 處")
        print(f"範圍: ${min(valid_prices):,} - ${max(valid_prices):,}\n")

# 尋找聯絡資訊
phone_match = re.search(r'0\d-?\d{3,4}-?\d{3,4}', page_text)
email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)

if phone_match:
    print(f"電話: {phone_match.group(0)}")
if email_match:
    print(f"Email: {email_match.group(0)}")

# 儲存結果
result = {
    'venue': '華山1914文化創意產業園區',
    'venue_id': 1125,
    'url': venue_list_url,
    'total_venues': len(unique_venues),
    'venues': unique_venues,
    'prices': valid_prices if 'valid_prices' in locals() else [],
    'contact': {
        'phone': phone_match.group(0) if phone_match else None,
        'email': email_match.group(0) if email_match else None
    },
    'timestamp': datetime.now().isoformat()
}

result_file = f'huashan1914_venue_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 詳細資料已儲存: {result_file}")

print("\n" + "=" * 100)
print("✅ 華山1914場地介紹爬取完成")
print("=" * 100)
