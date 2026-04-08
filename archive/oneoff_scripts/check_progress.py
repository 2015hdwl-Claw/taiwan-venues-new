#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查台北市飯店照片進度
"""
import json
import sys
import io

# 設置 UTF-8 編碼輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

taipei_hotels = [v for v in venues if v.get('city') == '台北市']
low_photo_venues = [(v['id'], v['name'], len(v.get('images', {}).get('gallery', []))) for v in taipei_hotels if len(v.get('images', {}).get('gallery', [])) <= 3]
low_photo_venues.sort(key=lambda x: x[2])

print('=== 台北市場地照片進度統計 ===')
print(f'場地總數: {len(taipei_hotels)}')
print(f'照片 ≤3 張的場地: {len(low_photo_venues)}')
print()

for vid, name, count in low_photo_venues:
    print(f'ID {vid}: {name} - {count} 張照片')

print()
print('=== 照片數量分佈 ===')
from collections import Counter
dist = Counter([count for _, _, count in low_photo_venues])
for count in sorted(dist.keys()):
    print(f'{count} 張照片: {dist[count]} 家場地')
