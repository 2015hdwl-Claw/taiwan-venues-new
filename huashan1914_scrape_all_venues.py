#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 批次爬取 24 個場地詳情頁
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import re
import time
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("華山1914 - 批次爬取 24 個場地詳情頁")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取場地列表
with open('huashan1914_svg_venues_20260326_205431.json', encoding='utf-8') as f:
    venue_list = json.load(f)

venues = venue_list['venues']
print(f"總場地數: {len(venues)} 個\n")

# 開始爬取
all_venues_detailed = []

for i, venue in enumerate(venues, 1):
    print(f"{'=' * 100}")
    print(f"場地 {i}/{len(venues)}: {venue['name']}")
    print(f"URL: {venue['full_url']}")
    print(f"{'=' * 100}\n")

    if not venue['full_url']:
        print("⚠️  無詳情頁 URL，跳過\n")
        continue

    try:
        response = requests.get(venue['full_url'], timeout=15, verify=False)
        print(f"HTTP 狀態: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ 頁面訪問失敗\n")
            time.sleep(2)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取場地詳細資料
        venue_detail = {
            'name': venue['name'],
            'url': venue['full_url'],
            'capacity': None,
            'area': None,
            'floor': None,
            'description': None,
            'equipment': None,
            'price': None,
            'images': []
        }

        # 尋找容量
        page_text = soup.get_text()
        capacity_match = re.search(r'(\d+)\s*[人名]', page_text)
        if capacity_match:
            venue_detail['capacity'] = int(capacity_match.group(1))
            print(f"容量: {venue_detail['capacity']} 人")

        # 尋找坪數
        area_match = re.search(r'(約\s*)?(\d+\.?\d*)\s*坪', page_text)
        if area_match:
            venue_detail['area'] = float(area_match.group(2))
            print(f"面積: {venue_detail['area']} 坪")

        # 尋找樓層
        floor_match = re.search(r'(\d+[F樓層])', page_text)
        if floor_match:
            venue_detail['floor'] = floor_match.group(1)
            print(f"樓層: {venue_detail['floor']}")

        # 尋找描述
        # 通常在 p 或 div 中
        for p in soup.find_all(['p', 'div'], class_=True):
            text = p.get_text(strip=True)
            if len(text) > 50 and len(text) < 500:
                # 避免重複
                if not venue_detail['description'] or len(text) > len(venue_detail['description']):
                    venue_detail['description'] = text

        if venue_detail['description']:
            print(f"描述: {venue_detail['description'][:80]}...")

        # 尋找設備
        equipment_keywords = ['投影', '音響', '麥克風', '燈光', '空調', '冷氣', '網路', 'WiFi']
        equipment_found = []
        for keyword in equipment_keywords:
            if keyword in page_text:
                equipment_found.append(keyword)

        if equipment_found:
            venue_detail['equipment'] = ', '.join(equipment_found)
            print(f"設備: {venue_detail['equipment']}")

        # 尋找圖片
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and not any(skip in src.lower() for skip in ['icon', 'logo', 'btn']):
                # 轉換為完整 URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://www.huashan1914.com' + src

                venue_detail['images'].append(src)

        if venue_detail['images']:
            print(f"照片: {len(venue_detail['images'])} 張")

        # 尋找價格
        price_match = re.search(r'(\d{2,6}[,.]?\d{0,3})\s*元', page_text)
        if price_match:
            try:
                price = int(price_match.group(1).replace(',', ''))
                if 1000 <= price <= 500000:
                    venue_detail['price'] = price
                    print(f"價格: ${price:,}")
            except:
                pass

        all_venues_detailed.append(venue_detail)
        print(f"✅ 資料提取完成\n")

        # 延遲避免被封
        time.sleep(2)

    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        time.sleep(2)
        continue

# 儲存結果
result = {
    'venue': '華山1914文化創意產業園區',
    'venue_id': 1125,
    'total_venues': len(all_venues_detailed),
    'venues': all_venues_detailed,
    'timestamp': datetime.now().isoformat()
}

result_file = f'huashan1914_all_venues_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 所有場地資料已儲存: {result_file}")

# 統計
print("\n" + "=" * 100)
print("統計資訊")
print("=" * 100)

with_capacity = [v for v in all_venues_detailed if v['capacity']]
with_area = [v for v in all_venues_detailed if v['area']]
with_price = [v for v in all_venues_detailed if v['price']]
with_images = [v for v in all_venues_detailed if v['images']]

print(f"成功爬取: {len(all_venues_detailed)} 個場地")
print(f"有容量資料: {len(with_capacity)} 個")
print(f"有面積資料: {len(with_area)} 個")
print(f"有價格資料: {len(with_price)} 個")
print(f"有照片資料: {len(with_images)} 個")

if with_capacity:
    capacities = [v['capacity'] for v in with_capacity]
    print(f"\n容量範圍: {min(capacities)} - {max(capacities)} 人")

if with_area:
    areas = [v['area'] for v in with_area]
    print(f"面積範圍: {min(areas):.0f} - {max(areas):.0f} 坪")

print("\n" + "=" * 100)
print("✅ 華山1914 場地爬取完成")
print("=" * 100)
