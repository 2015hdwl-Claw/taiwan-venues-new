#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update venue 1057 (台北典華 Denwell Taipei) rooms - 16 spaces extracted from website."""

import json, shutil, datetime

# Backup first
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy('venues.json', f'venues.json.backup.{ts}')
print(f'Backup: venues.json.backup.{ts}')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

venue = [v for v in data if v.get('id') == 1057][0]

# Standard equipment for premium banquet venue
standard_equipment = [
    '投影設備', '音響系統', '無線麥克風', 'WiFi',
    '空調', '白板', '講台', '燈光控制'
]

# Image CDN base
img_base = 'https://img.denwell.com/denwell/wp-content/uploads'

# 16 spaces data extracted from https://www.denwell.com/service-dazhi-venue-introduction/
# Each space has: name, nameEn, floor, area (坪), areaSqm, capacity (6 configs), dimensions
rooms_data = [
    # === 3F 樓層 (6 spaces) ===
    {
        'id': '1057-01',
        'name': '3F 大地',
        'nameEn': '3F Terra',
        'floor': '3樓',
        'area': 84,
        'areaUnit': '坪',
        'areaSqm': 278,
        'capacity': {
            'theater': 480,
            'classroom': 280,
            'ushape': 140,
            'roundtable': 310,
            'banquet': 440,
        },
        'length': 21.5,
        'width': 13,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈'],
        'images': {
            'main': f'{img_base}/2024111307194564-scaled.jpg',
            'gallery': [f'{img_base}/202411130711577.jpg'],
        },
        'notes': '3F 無柱空間，可與光影、湖泊合併使用',
        'source': 'website_20260330',
    },
    {
        'id': '1057-02',
        'name': '3F 光影',
        'nameEn': '3F Luma',
        'floor': '3樓',
        'area': 64,
        'areaUnit': '坪',
        'areaSqm': 212,
        'capacity': {
            'theater': 370,
            'classroom': 200,
            'ushape': 100,
            'roundtable': 230,
            'banquet': 330,
        },
        'length': 16.6,
        'width': 12.8,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈'],
        'images': {
            'main': f'{img_base}/2024111306562866.jpg',
        },
        'notes': '3F 無柱空間，可與大地合併使用',
        'source': 'website_20260330',
    },
    {
        'id': '1057-03',
        'name': '3F 湖泊',
        'nameEn': '3F Lake',
        'floor': '3樓',
        'area': 40,
        'areaUnit': '坪',
        'areaSqm': 132,
        'capacity': {
            'theater': 230,
            'classroom': 130,
            'ushape': 65,
            'roundtable': 150,
            'banquet': 200,
        },
        'length': 12.4,
        'width': 10.6,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {
            'main': f'{img_base}/202411130749229-scaled.jpg',
        },
        'notes': '3F 無柱空間，可與大地、光影合併使用',
        'source': 'website_20260330',
    },
    {
        'id': '1057-04',
        'name': '3F 閣樓',
        'nameEn': '3F Loft',
        'floor': '3樓',
        'area': 33,
        'areaUnit': '坪',
        'areaSqm': 109,
        'capacity': {
            'theater': 190,
            'classroom': 110,
            'ushape': 55,
            'roundtable': 120,
            'banquet': 170,
        },
        'length': 11,
        'width': 9.9,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {
            'main': f'{img_base}/2024/07/2024111504011310-scaled.jpg',
        },
        'notes': '3F 無柱空間，適合中型宴會',
        'source': 'website_20260330',
    },
    {
        'id': '1057-05',
        'name': '3F 法室',
        'nameEn': '3F Salotto',
        'floor': '3樓',
        'area': 19,
        'areaUnit': '坪',
        'areaSqm': 63,
        'capacity': {
            'theater': 110,
            'classroom': 60,
            'ushape': 30,
            'roundtable': 70,
            'banquet': 100,
        },
        'length': 7.7,
        'width': 8.2,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 無柱空間，適合小型聚會',
        'source': 'website_20260330',
    },
    {
        'id': '1057-06',
        'name': '3F 藝廊',
        'nameEn': '3F Gallery',
        'floor': '3樓',
        'area': 18,
        'areaUnit': '坪',
        'areaSqm': 60,
        'capacity': {
            'theater': 100,
            'classroom': 60,
            'ushape': 30,
            'roundtable': 60,
            'banquet': 90,
        },
        'length': 7.7,
        'width': 7.7,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 無柱空間，適合小型聚會',
        'source': 'website_20260330',
    },
    # === S級 圓頂 (2 spaces) ===
    {
        'id': '1057-07',
        'name': '飛蝶圓頂',
        'nameEn': 'Crystal Hall',
        'floor': 'B1',
        'area': 68,
        'areaUnit': '坪',
        'areaSqm': 225,
        'capacity': {
            'theater': 400,
            'classroom': 220,
            'ushape': 110,
            'roundtable': 250,
            'banquet': 360,
        },
        'length': 17.6,
        'width': 12.8,
        'height': 5.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈', '圓頂投影'],
        'images': {
            'main': f'{img_base}/2020/12/2021092006512044.jpg',
        },
        'notes': 'S級圓頂空間，5.5米挑高，飛蝶造型頂燈',
        'source': 'website_20260330',
    },
    {
        'id': '1057-08',
        'name': '圓心',
        'nameEn': 'Dome Hall',
        'floor': 'B1',
        'area': 68,
        'areaUnit': '坪',
        'areaSqm': 225,
        'capacity': {
            'theater': 400,
            'classroom': 220,
            'ushape': 110,
            'roundtable': 250,
            'banquet': 360,
        },
        'length': 17.6,
        'width': 12.8,
        'height': 5.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈', '圓頂投影'],
        'images': {
            'main': f'{img_base}/2024100808341399-scaled.jpg',
        },
        'notes': 'S級圓頂空間，5.5米挑高',
        'source': 'website_20260330',
    },
    # === 5F 樓層 (5 spaces) ===
    {
        'id': '1057-09',
        'name': '5F 日出',
        'nameEn': '5F Sunrise',
        'floor': '5樓',
        'area': 40,
        'areaUnit': '坪',
        'areaSqm': 132,
        'capacity': {
            'theater': 230,
            'classroom': 130,
            'ushape': 65,
            'roundtable': 150,
            'banquet': 200,
        },
        'length': 12.4,
        'width': 10.6,
        'height': 3.4,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {
            'main': f'{img_base}/2024/07/2024122605375269.jpg',
        },
        'notes': '5F 無柱空間，可與紫境合併',
        'source': 'website_20260330',
    },
    {
        'id': '1057-10',
        'name': '5F 紫境',
        'nameEn': '5F Venue526',
        'floor': '5樓',
        'area': 54,
        'areaUnit': '坪',
        'areaSqm': 178,
        'capacity': {
            'theater': 310,
            'classroom': 170,
            'ushape': 85,
            'roundtable': 200,
            'banquet': 280,
        },
        'length': 16.6,
        'width': 10.7,
        'height': 3.4,
        'pillar': False,
        'equipment': standard_equipment,
        'images': {},
        'notes': '5F 無柱空間，可與日出合併',
        'source': 'website_20260330',
    },
    {
        'id': '1057-11',
        'name': '5F 繁華',
        'nameEn': '5F Splendor',
        'floor': '5樓',
        'area': 65,
        'areaUnit': '坪',
        'areaSqm': 215,
        'capacity': {
            'theater': 380,
            'classroom': 210,
            'ushape': 105,
            'roundtable': 240,
            'banquet': 340,
        },
        'length': 16.5,
        'width': 13,
        'height': 3.4,
        'pillar': False,
        'equipment': standard_equipment + ['舞台'],
        'images': {},
        'notes': '5F 無柱空間，可與似錦合併為繁華似錦',
        'source': 'website_20260330',
    },
    {
        'id': '1057-12',
        'name': '5F 似錦',
        'nameEn': '5F Glory',
        'floor': '5樓',
        'area': 65,
        'areaUnit': '坪',
        'areaSqm': 215,
        'capacity': {
            'theater': 380,
            'classroom': 210,
            'ushape': 105,
            'roundtable': 240,
            'banquet': 340,
        },
        'length': 16.5,
        'width': 13,
        'height': 3.4,
        'pillar': False,
        'equipment': standard_equipment + ['舞台'],
        'images': {},
        'notes': '5F 無柱空間，可與繁華合併為繁華似錦',
        'source': 'website_20260330',
    },
    {
        'id': '1057-13',
        'name': '5F 繁華似錦',
        'nameEn': '5F Opulence',
        'floor': '5樓',
        'area': 130,
        'areaUnit': '坪',
        'areaSqm': 430,
        'capacity': {
            'theater': 760,
            'classroom': 420,
            'ushape': 210,
            'roundtable': 480,
            'banquet': 680,
        },
        'length': 33,
        'width': 13,
        'height': 3.4,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈'],
        'images': {
            'main': f'{img_base}/2020/12/21.09.03大直典華空拍-116.jpg',
        },
        'notes': '5F 由繁華+似錦合併的超大無柱空間',
        'source': 'website_20260330',
    },
    # === 6F 樓層 (3 spaces) ===
    {
        'id': '1057-14',
        'name': '6F 花田好事',
        'nameEn': '6F Grand Ballroom II',
        'floor': '6樓',
        'area': 68,
        'areaUnit': '坪',
        'areaSqm': 225,
        'capacity': {
            'theater': 400,
            'classroom': 220,
            'ushape': 110,
            'roundtable': 250,
            'banquet': 360,
        },
        'length': 17.6,
        'width': 12.8,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈'],
        'images': {},
        'notes': '6F 無柱空間，可與花田盛事合併為大花田盛事',
        'source': 'website_20260330',
    },
    {
        'id': '1057-15',
        'name': '6F 花田盛事',
        'nameEn': '6F Grand Ballroom I',
        'floor': '6樓',
        'area': 115,
        'areaUnit': '坪',
        'areaSqm': 380,
        'capacity': {
            'theater': 660,
            'classroom': 360,
            'ushape': 180,
            'roundtable': 420,
            'banquet': 580,
        },
        'length': 29,
        'width': 13.1,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈'],
        'images': {},
        'notes': '6F 超大無柱空間',
        'source': 'website_20260330',
    },
    {
        'id': '1057-16',
        'name': '6F 大花田盛事',
        'nameEn': '6F Grand Ballroom III',
        'floor': '6樓',
        'area': 183,
        'areaUnit': '坪',
        'areaSqm': 605,
        'capacity': {
            'theater': 1060,
            'classroom': 580,
            'ushape': 290,
            'roundtable': 670,
            'banquet': 940,
        },
        'length': 46.6,
        'width': 13,
        'height': 4.5,
        'pillar': False,
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈'],
        'images': {},
        'notes': '6F 由花田好事+花田盛事合併，全館最大無柱空間',
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
    print(f'{rd["id"]} {rd["name"]}: score={score}, area={rd.get("area")}坪, '
          f'theater={cap.get("theater","-")}, '
          f'imgs={"yes" if imgs.get("main") else "no"}')

# Update venue-level metadata
venue['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = 'Manual_Website_20260330'
venue['metadata']['totalRooms'] = len(venue['rooms'])
venue['metadata']['skipReason'] = None  # Clear old skip reason

# Calculate max capacity from rooms
max_theater = max((r.get('capacity', {}).get('theater', 0) for r in venue['rooms']), default=0)
venue['maxCapacityTheater'] = max_theater
venue['capacity'] = {'theater': max_theater}

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone! Added {len(venue["rooms"])} rooms for venue 1057 (台北典華)')
print(f'Max theater capacity: {max_theater}')
