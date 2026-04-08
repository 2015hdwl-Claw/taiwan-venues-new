#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update venue 1049 (台北世貿中心 TWTC) rooms - fix wrong capacity values and add images."""

import json, shutil, datetime

# Backup first
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy('venues.json', f'venues.json.backup.{ts}')
print(f'Backup: venues.json.backup.{ts}')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

venue = [v for v in data if v.get('id') == 1049][0]

# Standard equipment
standard_equipment = ['投影設備', '音響系統', '無線麥克風', 'WiFi', '空調', '白板', '講台', '飲用水']

# Image base from TWTC website
img_base = 'https://www.twtc.com.tw/img/meeting'

# Fixed room data - correcting wrong capacity values (original scraper lost a digit)
# Source: https://www.twtc.com.tw/meeting
rooms_data = [
    {
        'id': '1049-01',
        'name': '第一會議室',
        'nameEn': 'Room 1',
        'floor': '1樓',
        'capacity': {'theater': 250, 'classroom': 84, 'ushape': 144},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/第1會議室.jpg'},
        'notes': '標準型144位',
        'source': 'website_20260330',
    },
    {
        'id': '1049-02',
        'name': 'A+會議室',
        'nameEn': 'A+ Room',
        'floor': '1樓',
        'capacity': {'theater': 108, 'classroom': 48, 'ushape': 72},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/A會議室.jpg'},
        'notes': '標準型72位',
        'source': 'website_20260330',
    },
    {
        'id': '1049-03',
        'name': '第二會議室',
        'nameEn': 'Room 2',
        'floor': '1樓',
        'capacity': {'theater': 160, 'classroom': 60, 'ushape': 100},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/第2會議室.jpg'},
        'notes': '標準型100位',
        'source': 'website_20260330',
    },
    {
        'id': '1049-04',
        'name': '第三會議室',
        'nameEn': 'Room 3',
        'floor': '1樓',
        'capacity': {'theater': 200, 'classroom': 70, 'ushape': 120},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/第3會議室.jpg'},
        'notes': '標準型120位',
        'source': 'website_20260330',
    },
    {
        'id': '1049-05',
        'name': '第四會議室',
        'nameEn': 'Room 4',
        'floor': '1樓',
        'capacity': {'theater': 108, 'classroom': 48, 'ushape': 72},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/第4會議室.jpg'},
        'notes': '標準型72位',
        'source': 'website_20260330',
    },
    {
        'id': '1049-06',
        'name': '第五會議室',
        'nameEn': 'Room 5',
        'floor': '1樓',
        'capacity': {'theater': 250, 'classroom': 84, 'ushape': 144},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/第5會議室.jpg'},
        'notes': '標準型144位，與第一會議室規格相同',
        'source': 'website_20260330',
    },
    {
        'id': '1049-07',
        'name': '第三四五會議室(打通)',
        'nameEn': 'Rooms 3+4+5 Combined',
        'floor': '1樓',
        'capacity': {'theater': 500},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/345會議室.jpg'},
        'notes': '由第三、四、五會議室打通，大型活動空間',
        'source': 'website_20260330',
    },
    {
        'id': '1049-08',
        'name': '一樓貴賓室',
        'nameEn': '1F VIP Room',
        'floor': '1樓',
        'capacity': {},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/一樓貴賓室1.jpg'},
        'notes': '一樓貴賓接待室',
        'source': 'website_20260330',
    },
    {
        'id': '1049-09',
        'name': '第一五會議室間廊廳',
        'nameEn': 'Corridor between Room 1 & 5',
        'floor': '1樓',
        'capacity': {},
        'pillar': False,
        'equipment': [],
        'images': {'main': f'{img_base}/第一、五會議室間廊廳1.jpg'},
        'notes': '第一與第五會議室間之廊廳空間',
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
        'capacity': rd.get('capacity', {}),
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
    if cap.get('theater') or cap.get('classroom') or cap.get('ushape'):
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
    cap_str = f"theater={cap.get('theater','-')}, classroom={cap.get('classroom','-')}, ushape={cap.get('ushape','-')}"
    print(f'{rd["id"]} {rd["name"]}: score={score}, cap=[{cap_str}], '
          f'imgs={"yes" if imgs.get("main") else "no"}')

# Update venue-level metadata
venue['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = 'Manual_Website_20260330'
venue['metadata']['totalRooms'] = len(venue['rooms'])
venue['metadata']['skipReason'] = None

# Update main venue image
venue['images']['main'] = f'{img_base}/345會議室.jpg'
venue['images']['gallery'] = [
    f'{img_base}/345會議室.jpg',
    f'{img_base}/第1會議室.jpg',
    f'{img_base}/第2會議室.jpg',
    f'{img_base}/第3會議室.jpg',
    f'{img_base}/A會議室.jpg',
]

# Update max capacity
max_theater = max((r.get('capacity', {}).get('theater', 0) for r in venue['rooms']), default=0)
venue['maxCapacityTheater'] = max_theater
venue['capacity'] = {'theater': max_theater}

# Update URL (fix if needed)
if 'twtc.com.tw' not in venue.get('url', ''):
    venue['url'] = 'https://www.twtc.com.tw/meeting'

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone! Added {len(venue["rooms"])} rooms for venue 1049 (台北世貿中心)')
print(f'Max theater capacity: {max_theater}')
