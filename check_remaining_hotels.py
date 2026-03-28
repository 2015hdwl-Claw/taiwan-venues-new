#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查剩餘的重要飯店場地
"""

import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 找出台北市的重要飯店場地（品質分數 < 60）
hotels = [v for v in venues
          if v.get('venueType') == '飯店場地'
          and v.get('city') == '台北'
          and v.get('metadata', {}).get('qualityScore', 0) < 60]

# 排序
hotels = sorted(hotels, key=lambda x: x['id'])

print(f"剩餘的重要飯店場地（品質分數 < 60）: {len(hotels)}\n")
print("=" * 100)

for hotel in hotels:
    quality = hotel.get('metadata', {}).get('qualityScore', 'N/A')
    url = hotel.get('url', 'N/A')
    print(f"ID {hotel['id']}: {hotel['name']}")
    print(f"  品質分數: {quality}")
    print(f"  URL: {url}")
    print()
