#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug venue types
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

# 統計 venueType
venue_types = Counter(v.get('venueType', 'Unknown') for v in venues)
print("Venue Type 統計:")
for vt, count in venue_types.most_common():
    print(f"  {vt}: {count}")

# 統計 city
cities = Counter(v.get('city', 'Unknown') for v in venues)
print("\nCity 統計:")
for city, count in cities.most_common():
    print(f"  {city}: {count}")

# 找出台北的飯店
print("\n搜尋 '飯店' 或 '酒店' 在名稱中的場地:")
taipei_venues = [v for v in venues if '台北' in v.get('city', '')]
for v in taipei_venues[:20]:
    name = v.get('name', '')
    if '飯店' in name or '酒店' in name:
        quality = v.get('metadata', {}).get('qualityScore', 'N/A')
        print(f"  ID {v['id']}: {name} - Quality: {quality}")
