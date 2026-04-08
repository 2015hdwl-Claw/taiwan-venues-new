#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify GIS venues update"""
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Count GIS venues with data
gis_venues = [v for v in venues if v.get('name', '').startswith('集思')]
completed = [v for v in gis_venues if v.get('rooms')]
total_rooms = sum(len(v.get('rooms', [])) for v in completed)

print(f"GIS Venues Completed: {len(completed)}/{len(gis_venues)}")
print(f"Total Rooms: {total_rooms}")
print()

# Show details for newly updated venues
for vid in [1498, 1496]:
    for v in venues:
        if v.get('id') == vid:
            print(f"{v.get('name')} (ID: {vid})")
            print(f"  Rooms: {len(v.get('rooms', []))}")
            print(f"  Max Capacity: {v.get('capacity', {}).get('standard')}")
            print(f"  Source: {v.get('metadata', {}).get('source')}")
            print()
            break
