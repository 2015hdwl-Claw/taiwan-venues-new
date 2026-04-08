#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
師大進修推廣學院 - 深度爬取每個會議室的詳細資料
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import re
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("師大進修推廣學院 - 深度爬取會議室詳細資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

space_url = "https://www.sce.ntnu.edu.tw/home/space/"

print("訪問場地頁面...")
session = requests.Session()
response = session.get(space_url, timeout=15, verify=False)
print(f"HTTP 狀態: {response.status_code}")

if response.status_code != 200:
    print(f"❌ 頁面訪問失敗")
    sys.exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# 儲存頁面
page_file = f"ntnu_sce_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
with open(page_file, 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
print(f"✅ 頁面已儲存: {page_file}\n")

# 尋找所有會議室項目
print("=" * 100)
print("提取會議室詳細資料")
print("=" * 100)

rooms_detailed = []

# 尋找所有包含會議室資訊的區塊
# 師大進修的結構可能是每個會議室都有獨立的描述區塊

# 方法1: 尋找所有圖片和其對應的文字說明
for img in soup.find_all('img'):
    alt = img.get('alt', '')
    src = img.get('src', '')

    # 尋找包含人數的 alt 文字
    match = re.search(r'(\d+樓)?([^（(]+)[（(]?\s*(\d+)(\s*[-~]\s*\d+)?\s*[人）)]', alt)
    if match:
        floor = match.group(1) if match.group(1) else None
        room_type = match.group(2).strip()
        capacity = int(match.group(3))
        # Group 4 is the range pattern (\s*[-~]\s*\d+)?
        capacity_range = match.group(4) if match.group(4) else None
        if capacity_range:
            # Extract the second number from range
            range_match = re.search(r'(\d+)', capacity_range)
            capacity_max = int(range_match.group(1)) if range_match else capacity
        else:
            capacity_max = capacity

        # 尋找該圖片後面的文字描述
        room_description = ""
        parent = img.find_parent()
        if parent:
            # 尋找同層級的 p, div, span 等標籤
            siblings = parent.find_all(['p', 'div', 'span'], recursive=False)
            for sibling in siblings:
                text = sibling.get_text(strip=True)
                if text and len(text) > 10:
                    room_description = text
                    break

        room_data = {
            'name': room_type,
            'floor': floor,
            'capacity_min': capacity,
            'capacity_max': capacity_max,
            'description': room_description,
            'image_url': src if src.startswith('http') else f"https://www.sce.ntnu.edu.tw/{src}" if src.startswith('/') else None
        }

        rooms_detailed.append(room_data)

print(f"找到會議室: {len(rooms_detailed)} 間\n")

# 顯示詳細資訊
for i, room in enumerate(rooms_detailed, 1):
    floor_str = f"{room['floor']} " if room['floor'] else ""
    cap_str = f"{room['capacity_min']}" if room['capacity_min'] == room['capacity_max'] else f"{room['capacity_min']}-{room['capacity_max']}"
    print(f"{i}. {floor_str}{room['name']} ({cap_str} 人)")
    if room['description']:
        print(f"   說明: {room['description'][:100]}...")
    if room['image_url']:
        print(f"   照片: {room['image_url']}")
    print()

# 尋找面積資訊
page_text = soup.get_text()
area_pattern = r'(\d+\.?\d*)\s*[坪平米]'
areas = re.findall(area_pattern, page_text)

if areas:
    print(f"找到面積資訊: {len(areas)} 處")
    print(f"範圍: {min(float(a) for a in areas)} - {max(float(a) for a in areas)} 坪\n")

# 尋找價格資訊
price_pattern = r'(\d{2,6}[,.]?\d{0,3})\s*元'
prices = re.findall(price_pattern, page_text)

if prices:
    # 轉換為數字
    valid_prices = []
    for p in prices:
        try:
            price = int(p.replace(',', ''))
            if 1000 <= price <= 50000:
                valid_prices.append(price)
        except:
            pass

    if valid_prices:
        print(f"找到價格資訊: {len(valid_prices)} 處")
        print(f"範圍: ${min(valid_prices):,} - ${max(valid_prices):,}\n")

# 尋找設備資訊
equipment_keywords = ['投影機', '麥克風', '音響', '投影', '屏幕', '網路', 'WiFi', '空調', '冷氣']
equipment_found = []
for keyword in equipment_keywords:
    if keyword in page_text:
        equipment_found.append(keyword)

if equipment_found:
    print(f"找到設備資訊: {', '.join(equipment_found)}\n")

# 儲存詳細資料
result = {
    'venue': '師大進修推廣學院',
    'venue_id': 1493,
    'url': space_url,
    'total_rooms': len(rooms_detailed),
    'rooms': rooms_detailed,
    'areas': areas[:10] if areas else [],
    'prices': [],
    'equipment': equipment_found,
    'timestamp': datetime.now().isoformat()
}

result_file = f'ntnu_sce_detailed_scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 詳細資料已儲存: {result_file}")

print("\n" + "=" * 100)
print("✅ 師大進修詳細爬取完成")
print("=" * 100)
