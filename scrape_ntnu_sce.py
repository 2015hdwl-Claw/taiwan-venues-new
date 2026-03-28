#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
師大進修推廣學院 - 深度爬取場地租借頁面
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from datetime import datetime
from urllib.parse import urljoin
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("師大進修推廣學院 - 深度爬取場地租借頁面")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.sce.ntnu.edu.tw/"
space_url = "https://www.sce.ntnu.edu.tw/home/space/"

print(f"訪問場地租借頁面...")
print(f"URL: {space_url}\n")

try:
    response = requests.get(space_url, timeout=30, verify=False)
    print(f"HTTP 狀態: {response.status_code}")

    if response.status_code != 200:
        print("❌ 頁面訪問失敗")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 儲存頁面
    page_file = f"ntnu_sce_space_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    print(f"✅ 頁面已儲存: {page_file}\n")

    # 尋找會議室資訊
    print("尋找會議室資訊...\n")

    # 方法 1: 尋找所有連結
    print("尋找會議室連結...")
    room_links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        # 尋找會議室相關連結
        if len(text) > 1 and len(text) < 100:
            if any(kw in text for kw in ['會議室', '教室', '演講廳', '會議', '空間']):
                full_url = urljoin(base_url, href)
                room_links.append({
                    'name': text,
                    'url': full_url
                })

    print(f"找到 {len(room_links)} 個會議室連結:")
    for link in room_links[:15]:
        print(f"  - {link['name']}")
        print(f"    {link['url']}")

    # 方法 2: 尋找標題
    print("\n尋找會議室標題...")
    titles = []

    for tag in ['h1', 'h2', 'h3', 'h4']:
        for element in soup.find_all(tag):
            text = element.get_text(strip=True)
            if any(kw in text for kw in ['會議室', '教室', '演講廳', '會議']):
                titles.append(text)

    if titles:
        print(f"找到 {len(titles)} 個標題:")
        for title in titles[:10]:
            print(f"  - {title}")

    # 方法 3: 尋找列表或表格
    print("\n尋找表格和列表...")
    tables = soup.find_all('table')
    lists = soup.find_all(['ul', 'ol'])

    print(f"表格數量: {len(tables)}")
    print(f"列表數量: {len(lists)}")

    # 解析頁面文字
    page_text = soup.get_text()

    # 尋找容量
    capacity_pattern = r'(\d+)\s*[人名]'
    capacities = re.findall(capacity_pattern, page_text)
    if capacities:
        print(f"\n找到容量資訊: {len(capacities)} 處")
        print(f"容量範圍: {min(int(c) for c in capacities)} - {max(int(c) for c in capacities)} 人")

    # 尋找坪數
    area_pattern = r'(\d+\.?\d*)\s*[坪平米]'
    areas = re.findall(area_pattern, page_text)
    if areas:
        print(f"找到面積資訊: {len(areas)} 處")
        print(f"面積範圍: {min(float(a) for a in areas)} - {max(float(a) for a in areas)} 坪")

    # 尋找樓層
    floor_pattern = r'(\d+[F樓層])'
    floors = re.findall(floor_pattern, page_text)
    if floors:
        print(f"找到樓層資訊: {len(set(floors))} 種")
        print(f"樓層: {', '.join(set(floors[:10]))}")

    # 深度爬取各會議室詳細頁面
    if room_links:
        print(f"\n{'=' * 100}")
        print("深度爬取前 5 個會議室")
        print("=" * 100)

        for i, link in enumerate(room_links[:5], 1):
            print(f"\n會議室 {i}: {link['name']}")
            print(f"URL: {link['url']}")

            try:
                time.sleep(1)
                response = requests.get(link['url'], timeout=15, verify=False)
                print(f"  HTTP 狀態: {response.status_code}")

                if response.status_code == 200:
                    room_soup = BeautifulSoup(response.text, 'html.parser')
                    room_text = room_soup.get_text()

                    # 尋找詳細資訊
                    caps = re.findall(capacity_pattern, room_text)
                    if caps:
                        print(f"  容量: {caps}")

                    ars = re.findall(area_pattern, room_text)
                    if ars:
                        print(f"  面積: {ars}")

                    # 尋找設備
                    equipment_keywords = ['投影機', '麥克風', '音響', '白板', '屏幕', '投影']
                    found_equipment = []
                    for kw in equipment_keywords:
                        if kw in room_text:
                            found_equipment.append(kw)

                    if found_equipment:
                        print(f"  設備: {', '.join(found_equipment)}")

                    # 儲存會議室頁面
                    room_file = f"ntnu_sce_{link['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    with open(room_file, 'w', encoding='utf-8') as f:
                        f.write(str(room_soup.prettify()))
                    print(f"  ✅ 頁面已儲存: {room_file}")

            except Exception as e:
                print(f"  ❌ 錯誤: {e}")

    # 儲存結果
    result = {
        'venue': '師大進修推廣學院',
        'venue_id': 1493,
        'base_url': base_url,
        'space_url': space_url,
        'room_links': room_links,
        'titles': titles,
        'page_text_length': len(page_text),
        'timestamp': datetime.now().isoformat()
    }

    result_file = f'ntnu_sce_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 結果已儲存: {result_file}")

except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'=' * 100}")
print("✅ 師大進修推廣學院爬取完成")
print("=" * 100)

# 顯示統計
print(f"\n統計:")
print(f"  會議室連結: {len(room_links)} 個")
print(f"  會議室標題: {len(titles)} 個")
