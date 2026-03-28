#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查所有台北市飯店場地的品質分數
"""

import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 找出所有台北市的飯店場地
hotels = [v for v in venues
          if v.get('venueType') == '飯店場地'
          and v.get('city') == '台北']

# 排序
hotels = sorted(hotels, key=lambda x: x['id'])

print('台北市所有飯店場地品質分數:')
print('=' * 100)

for hotel in hotels:
    quality = hotel.get('metadata', {}).get('qualityScore', 'N/A')
    print(f"ID {hotel['id']:4s}: {hotel['name']:40s} Quality: {str(quality):>3s}")

print(f'\n總計: {len(hotels)} 家飯店')
