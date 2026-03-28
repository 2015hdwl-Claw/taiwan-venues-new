#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 深度爬取場地資料
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
print("華山1914 - 深度爬取場地資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.huashan1914.com"
venue_list_url = "https://www.huashan1914.com/AppPlaceList"

all_venues = []

# 訪問場地列表頁面
print(f"訪問場地列表頁面...")
print(f"URL: {venue_list_url}\n")

try:
    response = requests.get(venue_list_url, timeout=30, verify=False)
    print(f"HTTP 狀態: {response.status_code}")

    if response.status_code != 200:
        print("❌ 頁面訪問失敗")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 儲存頁面內容
    page_file = f"huashan1914_venue_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    print(f"✅ 頁面已儲存: {page_file}\n")

    # 尋找場地卡片或列表
    print("尋找場地資訊...\n")

    # 方法 1: 尋找場地卡片（常見的 class 名稱）
    venue_cards = []
    possible_classes = [
        'venue-card', 'place-card', 'location-card',
        'card', 'item', 'list-item',
        'place', 'venue', 'location'
    ]

    for class_name in possible_classes:
        elements = soup.find_all(class_=class_name)
        if elements:
            print(f"找到 class='{class_name}': {len(elements)} 個")

    # 方法 2: 尋找所有場地連結
    print("\n尋找場地連結...")
    venue_links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        # 尋找可能的場地連結
        if len(text) > 2 and len(text) < 100:
            # 場地名稱通常包含特定關鍵字
            if any(kw in text for kw in ['館', '廳', '場', '室', '區', '空間', '劇場']):
                full_url = urljoin(base_url, href)
                venue_links.append({
                    'name': text,
                    'url': full_url
                })

    print(f"找到 {len(venue_links)} 個可能的場地連結:")
    for link in venue_links[:15]:
        print(f"  - {link['name']}")
        print(f"    {link['url']}")

    # 方法 3: 尋找標題
    print("\n尋找場地標題...")
    titles = []

    for tag in ['h1', 'h2', 'h3', 'h4']:
        for element in soup.find_all(tag):
            text = element.get_text(strip=True)
            if len(text) > 2 and len(text) < 100:
                if any(kw in text for kw in ['館', '廳', '場', '室', '區', '空間', '劇場']):
                    titles.append({
                        'tag': tag,
                        'text': text
                    })

    if titles:
        print(f"找到 {len(titles)} 個標題:")
        for title in titles[:15]:
            print(f"  {title['tag']}: {title['text']}")

    # 方法 4: 尋找圖片（通常場地有圖片）
    print("\n尋找場地圖片...")
    images = []

    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')

        if alt and len(alt) > 2:
            if any(kw in alt for kw in ['館', '廳', '場', '室', '區', '空間']):
                full_src = urljoin(base_url, src)
                images.append({
                    'alt': alt,
                    'src': full_src
                })

    if images:
        print(f"找到 {len(images)} 個場地圖片:")
        for img in images[:10]:
            print(f"  - {img['alt']}")
            print(f"    {img['src']}")

    # 方法 5: 解析頁面文字
    print("\n解析頁面文字...")
    page_text = soup.get_text()

    # 尋找容量
    capacity_pattern = r'(\d+)\s*[人名]'
    capacities = re.findall(capacity_pattern, page_text)
    if capacities:
        print(f"找到容量資訊: {len(capacities)} 處")
        unique_caps = list(set(capacities))
        print(f"容量範圍: {min(int(c) for c in capacities)} - {max(int(c) for c in capacities)} 人")

    # 尋找坪數
    area_pattern = r'(\d+\.?\d*)\s*[坪平米]'
    areas = re.findall(area_pattern, page_text)
    if areas:
        print(f"找到面積資訊: {len(areas)} 處")
        print(f"面積範圍: {min(float(a) for a in areas)} - {max(float(a) for a in areas)} 坪")

    # 儲存結果
    result = {
        'venue': '華山1914',
        'venue_id': 1125,
        'base_url': base_url,
        'venue_list_url': venue_list_url,
        'venue_links': venue_links,
        'titles': titles,
        'images': images,
        'page_text_length': len(page_text),
        'timestamp': datetime.now().isoformat()
    }

    result_file = f'huashan1914_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 結果已儲存: {result_file}")

    # 如果找到場地連結，深度爬取前幾個
    if venue_links:
        print(f"\n{'=' * 100}")
        print("深度爬取前 5 個場地詳情")
        print("=" * 100)

        for i, link in enumerate(venue_links[:5], 1):
            print(f"\n場地 {i}: {link['name']}")
            print(f"URL: {link['url']}")

            try:
                time.sleep(1)  # 避免請求過快
                response = requests.get(link['url'], timeout=15, verify=False)
                print(f"  HTTP 狀態: {response.status_code}")

                if response.status_code == 200:
                    venue_soup = BeautifulSoup(response.text, 'html.parser')

                    # 尋找詳細資訊
                    venue_text = venue_soup.get_text()

                    # 容量
                    caps = re.findall(capacity_pattern, venue_text)
                    if caps:
                        print(f"  容量: {caps}")

                    # 面積
                    ars = re.findall(area_pattern, venue_text)
                    if ars:
                        print(f"  面積: {ars}")

                    # 價格
                    price_pattern = r'(\d+[,.]?\d*)\s*元'
                    prices = re.findall(price_pattern, venue_text)
                    if prices:
                        print(f"  價格: {prices[:5]}")

            except Exception as e:
                print(f"  ❌ 錯誤: {e}")

except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'=' * 100}")
print("✅ 華山1914 深度爬取完成")
print("=" * 100)

# 顯示統計
print(f"\n統計:")
print(f"  場地連結: {len(venue_links)} 個")
print(f"  場地標題: {len(titles)} 個")
print(f"  場地圖片: {len(images)} 個")
