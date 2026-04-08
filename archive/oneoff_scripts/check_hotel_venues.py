#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check hotel venues status"""
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Find hotel venues
hotel_venues = []
for v in venues:
    vtype = v.get('venueType', '').lower()
    name = v.get('name', '').lower()
    if 'hotel' in vtype or '飯店' in v.get('name', '') or 'hotel' in name:
        hotel_venues.append(v)

# Sort by ID
hotel_venues.sort(key=lambda x: x.get('id', 0))

print('Hotel Venues Analysis')
print('='*80)
print()

missing_rooms = []
with_rooms = []

for v in hotel_venues:
    vid = v.get('id')
    name = v.get('name')
    vtype = v.get('venueType', '')
    rooms = v.get('rooms', [])
    room_count = len(rooms) if rooms else 0
    url = v.get('url', '')

    if room_count == 0:
        missing_rooms.append(v)
    else:
        with_rooms.append(v)

print(f'Total Hotel Venues: {len(hotel_venues)}')
print(f'With Room Data: {len(with_rooms)}')
print(f'Missing Room Data: {len(missing_rooms)}')
print()

if missing_rooms:
    print('Hotels WITHOUT room data (need processing):')
    print('-'*80)
    for v in missing_rooms:
        vid = v.get('id')
        name = v.get('name')
        url = v.get('url', '')
        print(f'ID: {vid}')
        print(f'Name: {name}')
        print(f'URL: {url}')
        print()

print('='*80)
print('Summary:')
print(f'- Need to process: {len(missing_rooms)} hotels')
print(f'- Already complete: {len(with_rooms)} hotels')
