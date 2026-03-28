#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选台北市飯店和婚宴场地
"""
import json
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 筛选台北市的飯店和婚宴场地
taipei_venues = []
for v in venues:
    if v.get('city') == '台北市' and v.get('status') != 'discontinued':
        venue_type = v.get('venueType', '')
        # 飯店類型
        if any(kw in venue_type for kw in ['飯店', '酒店', 'Hotel']):
            taipei_venues.append({'venue': v, 'category': '飯店'})
        # 婚宴類型
        elif any(kw in venue_type for kw in ['婚宴', '宴會', '餐廳']):
            taipei_venues.append({'venue': v, 'category': '婚宴'})

print(f'找到 {len(taipei_venues)} 個台北市飯店+婚宴場地')
print()

# 分类统计
hotels = [v for v in taipei_venues if v['category'] == '飯店']
banquets = [v for v in taipei_venues if v['category'] == '婚宴']

print(f'飯店: {len(hotels)} 個')
print(f'婚宴: {len(banquets)} 個')
print()

# 列出場地
print('='*70)
print('場地清單')
print('='*70)

for item in taipei_venues:
    v = item['venue']
    cat = item['category']
    venue_id = v.get('id')
    name = v.get('name', 'Unknown')
    quality = v.get('qualityScore', 'N/A')
    print(f'[{venue_id:4d}] {cat} - {name[:40]:40} (品質: {quality})')

# 儲存清單
target_ids = [item['venue']['id'] for item in taipei_venues]
print()
print('='*70)
print(f'目標場地ID: {target_ids}')
print('='*70)
