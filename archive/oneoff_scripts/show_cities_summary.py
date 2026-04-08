#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顯示所有城市場地分佈
"""

import json
import sys
from collections import Counter

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

print("=" * 100)
print("資料庫中的所有城市場地分佈")
print("=" * 100)

# 統計城市
cities = Counter(v.get('city', 'Unknown') for v in venues)

for city, count in cities.most_common():
    city_venues = [v for v in venues if v.get('city') == city]
    high_quality = sum(1 for v in city_venues if v.get('metadata', {}).get('qualityScore', 0) >= 75)

    print(f"\n{city}: {count} 個場地 (高品質: {high_quality})")

    # 列出所有場地
    for v in sorted(city_venues, key=lambda x: x['id']):
        quality = v.get('metadata', {}).get('qualityScore', 'N/A')
        print(f"  ID {v['id']}: {v['name']} - Quality: {quality}")

print(f"\n{'=' * 100}")
print(f"總場地數: {len(venues)}")
