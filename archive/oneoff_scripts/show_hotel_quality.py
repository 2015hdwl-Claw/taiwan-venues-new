#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顯示所有台北飯店品質分數
"""

import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 找出所有台北市的飯店
taipei_hotels = []
for v in venues:
    name = v.get('name', '')
    if '台北' in v.get('city', '') and ('飯店' in name or '酒店' in name):
        quality = v.get('metadata', {}).get('qualityScore', 0)
        taipei_hotels.append({
            'id': v['id'],
            'name': name,
            'quality': quality
        })

# 排序
taipei_hotels = sorted(taipei_hotels, key=lambda x: x['id'])

print('台北市所有飯店場地品質分數:')
print('=' * 100)

for hotel in taipei_hotels:
    quality = hotel['quality'] if hotel['quality'] > 0 else 'N/A'
    status = '✅' if isinstance(quality, int) and quality >= 60 else '⚠️'
    print(f"{status} ID {hotel['id']:4d}: {hotel['name']:45s} Quality: {str(quality):>3s}")

# 統計
completed = sum(1 for h in taipei_hotels if isinstance(h['quality'], int) and h['quality'] >= 60)
need_work = sum(1 for h in taipei_hotels if isinstance(h['quality'], int) and h['quality'] < 60)
no_quality = sum(1 for h in taipei_hotels if h['quality'] == 0 or h['quality'] == 'N/A')

print(f'\n統計:')
print(f'  ✅ 已完成 (>=60): {completed}')
print(f'  ⚠️ 需改進 (<60): {need_work}')
print(f'  ❓ 無分數: {no_quality}')
print(f'  總計: {len(taipei_hotels)}')
