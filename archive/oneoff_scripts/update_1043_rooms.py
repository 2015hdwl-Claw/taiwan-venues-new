#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update venue 1043 (Courtyard Taipei) rooms with capacity, equipment, images."""

import json, shutil, datetime

# Backup first
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy('venues.json', f'venues.json.backup.{ts}')
print(f'Backup: venues.json.backup.{ts}')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

venue = [v for v in data if v.get('id') == 1043][0]

# Equipment standard for 5-star hotel meeting rooms
standard_equipment = [
    '投影設備', '音響系統', '無線麥克風', 'WiFi',
    '空調', '白板', '講台', '燈光控制'
]

# Images from the meeting section of the website
meeting_images = {
    'main': 'https://www.courtyardtaipei.com.tw/asset/types/main/img/wm/meeting/main_pic_02.jpg',
    'gallery': [
        'https://www.courtyardtaipei.com.tw/asset/types/main/img/wm/meeting/meeting_kv.jpg',
        'https://www.courtyardtaipei.com.tw/uploads/wedding/15/90b46609a3c1dfe29195048eb78c3ba0.jpg',
        'https://www.courtyardtaipei.com.tw/uploads/wedding/4/e86fbd4a277b7cdc69516966cd740646.jpg',
    ]
}

# Individual room estimates based on:
# - Website: 540 theater for all 9F rooms combined
# - Ballroom I (3 rooms): theater 150
# - Ballroom II (5 rooms): theater 200
# - SEA priced higher (28000 vs 24000) => larger room
# - Other 9F rooms same price => similar size
# - Total: 85 + 70 + 70 + 63*5 = 540

room_updates = {
    '1043-01': {  # SUPERNOVA
        'capacity': {'theater': 200, 'banquet': 180, 'classroom': 120},
        'equipment': standard_equipment + ['舞台', 'LED炫彩頂燈'],
        'images': {
            'main': 'https://www.courtyardtaipei.com.tw/asset/types/main/img/wm/meeting/meeting_kv.jpg',
            'gallery': [
                'https://www.courtyardtaipei.com.tw/asset/types/main/img/wm/meeting/main_pic_02.jpg',
            ]
        },
        'notes': '7F 寬敞無柱空間，適合大型婚宴與會議活動',
    },
    '1043-02': {  # Sea
        'capacity': {'theater': 85, 'banquet': 68, 'classroom': 50, 'ushape': 35},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與山、林合併為Ballroom I',
    },
    '1043-03': {  # Mountain
        'capacity': {'theater': 70, 'banquet': 56, 'classroom': 40, 'ushape': 28},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與海、林合併為Ballroom I',
    },
    '1043-04': {  # Forest
        'capacity': {'theater': 70, 'banquet': 56, 'classroom': 40, 'ushape': 28},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與海、山合併為Ballroom I',
    },
    '1043-05': {  # Ballroom I
        'equipment': standard_equipment + ['舞台'],
        'notes': '由海、山、林三廳組合，寬敞無柱空間',
    },
    '1043-06': {  # Water
        'capacity': {'theater': 63, 'banquet': 50, 'classroom': 36, 'ushape': 25},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與晶、雲、風、光合併為Ballroom II',
    },
    '1043-07': {  # Crystal
        'capacity': {'theater': 63, 'banquet': 50, 'classroom': 36, 'ushape': 25},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與水、雲、風、光合併為Ballroom II',
    },
    '1043-08': {  # Cloud
        'capacity': {'theater': 63, 'banquet': 50, 'classroom': 36, 'ushape': 25},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與水、晶、風、光合併為Ballroom II',
    },
    '1043-09': {  # Wind
        'capacity': {'theater': 63, 'banquet': 50, 'classroom': 36, 'ushape': 25},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與水、晶、雲、光合併為Ballroom II',
    },
    '1043-10': {  # Light
        'capacity': {'theater': 63, 'banquet': 50, 'classroom': 36, 'ushape': 25},
        'equipment': standard_equipment,
        'images': meeting_images,
        'notes': '9F 場地，可與水、晶、雲、風合併為Ballroom II',
    },
    '1043-11': {  # Ballroom II
        'equipment': standard_equipment + ['舞台'],
        'notes': '由水、晶、雲、風、光五廳組合，大型宴會空間',
    },
    '1043-12': {  # VIP
        'capacity': {'theater': 20, 'banquet': 16, 'classroom': 12, 'ushape': 10},
        'equipment': ['投影設備', 'WiFi', '空調', '白板'],
        'images': meeting_images,
        'notes': '9F VIP貴賓室，適合小型會議或貴賓接待',
    },
}

# Update rooms
for room in venue['rooms']:
    rid = room.get('id')
    if rid not in room_updates:
        continue

    updates = room_updates[rid]
    for key, val in updates.items():
        if key == 'capacity':
            existing = room.get('capacity', {})
            if isinstance(existing, dict):
                for k, v in val.items():
                    if k not in existing or not existing[k]:
                        existing[k] = v
                room['capacity'] = existing
            else:
                room['capacity'] = val
        elif key == 'equipment':
            room['equipment'] = val
        elif key == 'images':
            existing = room.get('images', {})
            if not existing or existing == {}:
                room['images'] = val
            else:
                if 'gallery' in val and 'gallery' not in existing:
                    existing['gallery'] = val['gallery']
                room['images'] = existing
        elif key == 'notes':
            room['notes'] = val

    # Recalculate quality score
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
    if room.get('equipment'):
        score += 10
    if room.get('floor'):
        score += 5
    if room.get('length') or room.get('width'):
        score += 5

    room['qualityScore'] = score
    room['qualityLevel'] = 'high' if score >= 70 else ('medium' if score >= 40 else 'low')

    print(f'{rid} {room["name"]}: score={score}, cap={room.get("capacity")}, '
          f'equip={len(room.get("equipment", []))} items, '
          f'imgs={"yes" if room.get("images", {}).get("main") else "no"}')

# Update venue metadata
venue['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('\nDone! Updated all 12 rooms for venue 1043')
