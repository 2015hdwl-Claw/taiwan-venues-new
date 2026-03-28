#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 從 SVG 地圖提取場地資料
"""

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
print("華山1914 - 從 SVG 地圖提取場地資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取保存的 HTML
html_file = "huashan1914_venue_list_20260326_205406.html"

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 尋找所有 path, polygon, circle 等 SVG 元素
print("從 SVG 元素提取場地資料...")

venues = []

# 尋找所有有 data-name 的元素
for element in soup.find_all(['path', 'polygon', 'circle', 'rect', 'ellipse']):
    data_name = element.get('data-name')
    data_url = element.get('data-url')

    if data_name:
        # 解析名稱（可能有多個場地用逗號分隔）
        names = data_name.split(',')

        # 解析 URL（可能有多個）
        urls = data_url.split(',') if data_url else []

        for i, name in enumerate(names):
            name = name.strip()

            # 過濾掉空的或只有 "戶外空間" 的
            if not name or name == '戶外空間':
                continue

            venue = {
                'name': name,
                'url': urls[i] if i < len(urls) else None,
                'full_url': None
            }

            if venue['url']:
                # 建構完整 URL
                venue['full_url'] = urljoin('https://www.huashan1914.com/w/huashan1914/', venue['url'])

            venues.append(venue)

# 尋找坪數資訊（在文字中）
page_text = soup.get_text()

# 尋找所有坪數
area_pattern = r'(約\s*)?(\d+\.?\d*)\s*坪'
areas = re.findall(area_pattern, page_text)

# 統計場地類型
print(f"從 SVG 找到場地: {len(venues)} 個\n")

# 顯示場地列表
for i, venue in enumerate(venues, 1):
    print(f"{i}. {venue['name']}")
    if venue['full_url']:
        print(f"   詳情頁: {venue['full_url']}")
    print()

# 尋找樓層資訊
floor_pattern = r'(\d+[F樓層])|([B\d]+|[地下]\d*[層樓])'
floors = re.findall(floor_pattern, page_text)

if floors:
    unique_floors = list(set([f[0] if f[0] else f[1] for f in floors]))
    print(f"找到樓層: {', '.join(unique_floors[:10])}\n")

# 尋找價格
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

# 儲存結果
result = {
    'venue': '華山1914文化創意產業園區',
    'venue_id': 1125,
    'url': 'https://www.huashan1914.com/w/huashan1914/AppPlaceList',
    'total_venues': len(venues),
    'venues': venues,
    'areas_found': len(areas),
    'floors': list(set([f[0] if f[0] else f[1] for f in floors])) if floors else [],
    'prices': valid_prices if 'valid_prices' in locals() else [],
    'timestamp': datetime.now().isoformat()
}

result_file = f'huashan1914_svg_venues_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 場地資料已儲存: {result_file}")

print("\n" + "=" * 100)
print("下一步建議")
print("=" * 100)

# 檢查有多少場地有詳情頁
venues_with_detail = [v for v in venues if v['full_url']]
print(f"有詳情頁的場地: {len(venues_with_detail)} 個")

if venues_with_detail:
    print("\n建議：逐一訪問這些場地的詳情頁，獲取完整資料")
    print("前 5 個場地詳情頁:")
    for venue in venues_with_detail[:5]:
        print(f"  - {venue['name']}")
        print(f"    {venue['full_url']}")

print("\n" + "=" * 100)
print("✅ 華山1914 SVG 場地資料提取完成")
print("=" * 100)
