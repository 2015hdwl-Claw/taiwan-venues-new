#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

taipei_venues = [v for v in venues if '台北' in v.get('city', '')]

print(f"Total Taipei venues: {len(taipei_venues)}\n")

print("ID | Name | Venue Type | Quality Score | Rooms")
print("-" * 100)

for venue in taipei_venues:
    vid = venue.get('id', 'N/A')
    name = venue.get('name', 'N/A')[:30]
    vtype = venue.get('venueType', 'N/A')
    quality = venue.get('metadata', {}).get('qualityScore', 'N/A')
    rooms = len(venue.get('rooms', []))
    print(f"{vid} | {name} | {vtype} | {quality} | {rooms}")
