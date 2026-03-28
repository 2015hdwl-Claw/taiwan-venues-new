#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

print("飯店場地列表:")
print("=" * 80)

# 找出所有飯店
hotels = []
for v in venues:
    name = v.get('name', '')
    vtype = v.get('venueType', '')
    if '飯店' in name or 'Hotel' in name or 'HOTEL' in name or vtype == '飯店場地':
        hotels.append(v)

# 按 ID 排序
hotels.sort(key=lambda x: x.get('id', 0))

for h in hotels:
    vid = h.get('id')
    name = h.get('name')
    quality = h.get('metadata', {}).get('qualityScore', 'N/A')
    rooms = len(h.get('rooms', []))
    active = h.get('active', True)
    status = "" if active else " [停業/改建]"
    print(f"{vid}: {name}{status} - 品質: {quality}, 會議室: {rooms}")

print(f"\n總計: {len(hotels)} 個飯店")
