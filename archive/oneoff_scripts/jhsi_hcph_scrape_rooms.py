#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取集思竹科會議中心各會議室詳情頁（照片、容量、面積、價格）
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "https://www.meeting.com.tw/hsp/"

# 會議室列表
rooms = [
    {'name': '巴哈廳', 'file': 'bach.php'},
    {'name': '羅西尼廳', 'file': 'rossini.php'},
    {'name': '鄧肯廳', 'file': 'duncan.php'},
    {'name': '愛因斯坦廳', 'file': 'einstein.php'},
    {'name': '愛迪生廳', 'file': 'edison.php'},
]

print("=" * 100)
print("爬取集思竹科會議中心會議室詳情")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

os.makedirs('jhsi_hcph_docs', exist_ok=True)

all_rooms_data = []

for room in rooms:
    print(f"\n{'=' * 100}")
    print(f"爬取: {room['name']}")
    print('=' * 100)

    room_url = base_url + room['file']
    print(f"URL: {room_url}")

    try:
        response = requests.get(room_url, timeout=15, verify=False)

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 儲存 HTML
        html_file = f"jhsi_hcph_docs/{room['name']}_detail.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"✅ HTML 已儲存: {html_file}")

        # 提取文字內容
        page_text = soup.get_text()

        # 尋找容量
        capacity_patterns = [
            r'容量[：:]\s*(\d+)\s*人',
            r'容納[：:]\s*(\d+)\s*人',
            r'(\d+)\s*人',
        ]
        capacity = None
        for pattern in capacity_patterns:
            match = re.search(pattern, page_text)
            if match:
                capacity = int(match.group(1))
                if capacity > 1000:  # 避免匹配到錯誤的數字
                    capacity = None
                else:
                    break

        if capacity:
            print(f"  容量: {capacity} 人")

        # 尋找坪數
        area_patterns = [
            r'面積[：:]\s*(\d+\.?\d*)\s*坪',
            r'(\d+\.?\d*)\s*坪',
        ]
        area_ping = None
        for pattern in area_patterns:
            match = re.search(pattern, page_text)
            if match:
                area_ping = float(match.group(1))
                if area_ping > 1000:  # 避免匹配到錯誤的數字
                    area_ping = None
                else:
                    break

        if area_ping:
            print(f"  面積: {area_ping} 坪")

        # 尋找價格
        price_patterns = [
            r'租金[：:]\s*.*?(\d{2,6})\s*元',
            r'價格[：:]\s*.*?(\d{2,6})\s*元',
            r'\$?\s*(\d{2,6})\s*元',
        ]
        price = None
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                for p in matches:
                    p_int = int(p)
                    if 1000 <= p_int <= 500000:
                        price = p_int
                        break
                if price:
                    break

        if price:
            print(f"  價格: {price:,} 元")

        # 尋找照片
        photos = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')

            # 只保留會議室相關的照片
            if any(kw in src.lower() or kw in alt.lower() for kw in ['room', 'hall', 'meeting', '會議', '廳']):
                if not src.startswith('http'):
                    if src.startswith('/'):
                        src = 'https://www.meeting.com.tw' + src
                    else:
                        src = base_url + src

                if src not in photos:
                    photos.append(src)

        if photos:
            print(f"  照片: {len(photos)} 張")
            for i, photo in enumerate(photos[:3], 1):
                print(f"    {i}. {photo}")

        # 儲存資料
        room_data = {
            'name': room['name'],
            'url': room_url,
            'capacity': capacity,
            'areaPing': area_ping,
            'price': price,
            'photos': photos,
            'html_file': html_file
        }

        all_rooms_data.append(room_data)

    except Exception as e:
        print(f"❌ 錯誤: {e}")

# 儲存結果
output_file = 'jhsi_hcph_rooms_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_rooms_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 會議室資料已儲存: {output_file}")

# 統計
print(f"\n{'=' * 100}")
print("爬取結果統計")
print('=' * 100)
print(f"總會議室: {len(all_rooms_data)}")

with_capacity = sum(1 for r in all_rooms_data if r.get('capacity'))
with_area = sum(1 for r in all_rooms_data if r.get('areaPing'))
with_price = sum(1 for r in all_rooms_data if r.get('price'))
with_photos = sum(1 for r in all_rooms_data if r.get('photos'))

print(f"有容量: {with_capacity}/{len(all_rooms_data)}")
print(f"有面積: {with_area}/{len(all_rooms_data)}")
print(f"有價格: {with_price}/{len(all_rooms_data)}")
print(f"有照片: {with_photos}/{len(all_rooms_data)}")

print("\n" + "=" * 100)
print("✅ 爬取完成")
print("=" * 100)
