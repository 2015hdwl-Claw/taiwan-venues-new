#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update venue 1051 (亞都麗緻 The Landis Taipei) rooms - 3 meeting spaces with complete data."""

import json, shutil, datetime

# Backup first
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy('venues.json', f'venues.json.backup.{ts}')
print(f'Backup: venues.json.backup.{ts}')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

venue = [v for v in data if v.get('id') == 1051][0]

# Standard equipment for 5-star hotel
standard_equipment = [
    '投影設備', '音響系統', '無線麥克風', 'WiFi',
    '空調', '白板', '講台', '燈光控制'
]

# Image base from Landis website
img_base = 'https://taipei.landishotelsresorts.com/manage/upload/meetroom'

# 3 meeting spaces from https://taipei.landishotelsresorts.com/meeting-list.php
rooms_data = [
    {
        'id': '1051-01',
        'name': 'B1 宴會廳 Banquet Hall',
        'nameEn': 'B1 Banquet Hall',
        'floor': 'B1',
        'area': 97,
        'areaUnit': '坪',
        'areaSqm': 314,
        'capacity': {
            'theater': 160,
            'classroom': 120,
            'ushape': 63,
            'banquet': 300,
        },
        'length': 21,
        'width': 14,
        'height': 2.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台'],
        'images': {
            'main': f'{img_base}/1730557395_12909.jpg',
            'gallery': [
                f'{img_base}/1730557395_20477.jpg',
                f'{img_base}/1730557395_29897.jpg',
                f'{img_base}/1761043325_42599.jpg',
            ],
        },
        'notes': 'B1 最大宴會空間，21×14m，挑高2.5m',
        'source': 'website_20260330',
    },
    {
        'id': '1051-02',
        'name': '2F Le Salon',
        'nameEn': '2F Le Salon',
        'floor': '2樓',
        'area': 33,
        'areaUnit': '坪',
        'areaSqm': 109,
        'capacity': {
            'theater': 62,
            'classroom': 60,
            'ushape': 38,
            'banquet': 96,
        },
        'length': 14,
        'width': 4.4,
        'height': 2.5,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {
            'main': f'{img_base}/1730057351_39587.jpg',
        },
        'notes': '2F 長型會議空間，14×4.4m',
        'source': 'website_20260330',
    },
    {
        'id': '1051-03',
        'name': '2F Matisse',
        'nameEn': '2F Matisse',
        'floor': '2樓',
        'area': 20,
        'areaUnit': '坪',
        'areaSqm': 66,
        'capacity': {
            'theater': 40,
            'classroom': 30,
            'ushape': 15,
            'banquet': 36,
        },
        'length': 8,
        'width': 6,
        'height': 2.5,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {
            'main': f'{img_base}/1730558037_77374.jpg',
        },
        'notes': '2F 小型會議空間，8×6m',
        'source': 'website_20260330',
    },
]

# Build rooms list
venue['rooms'] = []

for rd in rooms_data:
    room = {
        'id': rd['id'],
        'name': rd['name'],
        'nameEn': rd.get('nameEn', ''),
        'floor': rd.get('floor', ''),
        'area': rd.get('area'),
        'areaUnit': rd.get('areaUnit', '坪'),
        'areaSqm': rd.get('areaSqm'),
        'capacity': rd.get('capacity', {}),
        'length': rd.get('length'),
        'width': rd.get('width'),
        'height': rd.get('height'),
        'pillar': rd.get('pillar', True),
        'equipment': rd.get('equipment', standard_equipment),
        'images': rd.get('images', {}),
        'notes': rd.get('notes', ''),
        'source': rd.get('source', ''),
    }

    # Calculate quality score
    score = 0
    if room.get('name'):
        score += 10
    cap = room.get('capacity', {})
    if cap.get('theater'):
        score += 15
    if room.get('area') or room.get('areaSqm'):
        score += 15
    price = room.get('price', {})
    if any(v for v in price.values() if v):
        score += 20
    imgs = room.get('images', {})
    if imgs.get('main'):
        score += 20
    if room.get('equipment') and len(room.get('equipment', [])) > 0:
        score += 10
    if room.get('floor'):
        score += 5
    if room.get('length') or room.get('width'):
        score += 5

    room['qualityScore'] = score
    room['qualityLevel'] = 'high' if score >= 70 else ('medium' if score >= 40 else 'low')

    venue['rooms'].append(room)
    cap_str = f"theater={cap.get('theater','-')}, classroom={cap.get('classroom','-')}, banquet={cap.get('banquet','-')}"
    print(f'{rd["id"]} {rd["name"]}: score={score}, area={rd.get("area")}坪, '
          f'cap=[{cap_str}], '
          f'imgs={"yes" if imgs.get("main") else "no"}')

# Update venue-level metadata
venue['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = 'Manual_Website_20260330'
venue['metadata']['totalRooms'] = len(venue['rooms'])
venue['metadata']['skipReason'] = None

# Update main venue image and gallery
venue['images']['main'] = f'{img_base}/1730557395_12909.jpg'
venue['images']['gallery'] = [
    f'{img_base}/1730557395_12909.jpg',
    f'{img_base}/1730557395_20477.jpg',
    f'{img_base}/1730057351_39587.jpg',
    f'{img_base}/1730558037_77374.jpg',
]

# Update max capacity
max_theater = max((r.get('capacity', {}).get('theater', 0) for r in venue['rooms']), default=0)
venue['maxCapacityTheater'] = max_theater
venue['capacity'] = {'theater': max_theater}

# Fix URL to correct meeting page
venue['url'] = 'https://taipei.landishotelsresorts.com/meeting-list.php'

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone! Added {len(venue["rooms"])} rooms for venue 1051 (亞都麗緻)')
print(f'Max theater capacity: {max_theater}')
