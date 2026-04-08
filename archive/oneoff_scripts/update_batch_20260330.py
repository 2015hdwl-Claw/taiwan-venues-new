#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch update: 1051 images, 1100 rooms (14 from PDF), delete 1121."""

import json, shutil, datetime, sys

sys.stdout.reconfigure(encoding='utf-8')

# Backup
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy('venues.json', f'venues.json.backup.{ts}')
print(f'Backup: venues.json.backup.{ts}')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ============================================================
# 1. ID 1051 (亞都麗緻) - Update broken image URLs
# ============================================================
print('\n=== ID 1051 亞都麗緻 ===')
v1051 = [v for v in data if v['id'] == 1051][0]

img_base = 'https://taipei.landishotelsresorts.com/manage/upload/meetroom'
# New working URLs (verified 200 as of 2026-03-30)
new_images = {
    'banquet_hall': f'{img_base}/1773940339_47730.jpg',
    'banquet_gallery_1': f'{img_base}/1773940339_20713.jpg',
    'banquet_gallery_2': f'{img_base}/1773940339_71745.jpg',
    'banquet_gallery_3': f'{img_base}/1773940339_48479.jpg',
    'matisse': f'{img_base}/1773940189_93854.jpg',
    'matisse_gallery': f'{img_base}/1773940189_48772.jpg',
    'le_salon': f'{img_base}/1773940120_95031.jpg',
    'le_salon_gallery': f'{img_base}/1773940120_10547.jpg',
}

# Update venue main image and gallery
v1051['images']['main'] = new_images['banquet_hall']
v1051['images']['gallery'] = [
    new_images['banquet_hall'],
    new_images['matisse'],
    new_images['le_salon'],
    new_images['banquet_gallery_1'],
]

# Update room images
for room in v1051.get('rooms', []):
    if 'Banquet' in room.get('name', ''):
        room['images'] = {
            'main': new_images['banquet_hall'],
            'gallery': [
                new_images['banquet_gallery_1'],
                new_images['banquet_gallery_2'],
                new_images['banquet_gallery_3'],
            ],
        }
        print(f'  {room["id"]}: Updated Banquet Hall images')
    elif 'Le Salon' in room.get('name', ''):
        room['images'] = {
            'main': new_images['le_salon'],
            'gallery': [new_images['le_salon_gallery']],
        }
        print(f'  {room["id"]}: Updated Le Salon images')
    elif 'Matisse' in room.get('name', ''):
        room['images'] = {
            'main': new_images['matisse'],
            'gallery': [new_images['matisse_gallery']],
        }
        print(f'  {room["id"]}: Updated Matisse images')

v1051['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()
print('ID 1051 done: images updated')

# ============================================================
# 2. ID 1100 (台北花園大酒店) - 14 rooms from PDF
# ============================================================
print('\n=== ID 1100 台北花園大酒店 ===')
v1100 = [v for v in data if v['id'] == 1100][0]

standard_equipment = ['投影設備', '音響系統', '無線麥克風', 'WiFi', '空調', '白板', '講台', '飲用水']

# Image base from website
img_base_1100 = 'https://www.taipeigarden.com.tw/wp-content/uploads/sites/278'

# Data extracted from PDF: 2025-台北花園大酒店-宴會廳容納及場租表.pdf
rooms_data = [
    # === 2F (3 spaces) ===
    {
        'id': '1100-01',
        'name': '2F 百合廳',
        'nameEn': '2F Lily Room',
        'floor': '2樓',
        'area': 71,
        'areaUnit': '坪',
        'areaSqm': 236,
        'height': 6.5,
        'pillar': False,
        'capacity': {'banquet': 150, 'cocktail': 200, 'theater': 220, 'classroom': 140, 'hollowSquare': 54, 'ushape': 48},
        'price': {'weekdayDaytime': 48000, 'weekdayNighttime': 100000, 'weekendDaytime': 50000, 'weekendNighttime': 110000, 'fullDay': 150000, 'overtime': 20000},
        'equipment': standard_equipment + ['舞台', '音響'],
        'images': {'main': f'{img_base_1100}/2024/05/IMG_6811-HDR-2200x1200.jpg'},
        'notes': '2F 大型宴會廳，71坪，挑高6.5米，可與薔薇廳合併為國際廳',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-02',
        'name': '2F 薔薇廳',
        'nameEn': '2F Rosa Room',
        'floor': '2樓',
        'area': 71,
        'areaUnit': '坪',
        'areaSqm': 236,
        'height': 6.5,
        'pillar': False,
        'capacity': {'banquet': 150, 'cocktail': 200, 'theater': 220, 'classroom': 140, 'hollowSquare': 54, 'ushape': 48},
        'price': {'weekdayDaytime': 48000, 'weekdayNighttime': 100000, 'weekendDaytime': 50000, 'weekendNighttime': 110000, 'fullDay': 150000, 'overtime': 20000},
        'equipment': standard_equipment + ['舞台', '音響'],
        'images': {'main': f'{img_base_1100}/2023/07/IMG_6839-HDR.jpg'},
        'notes': '2F 大型宴會廳，71坪，挑高6.5米，與百合廳規格相同',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-03',
        'name': '2F 國際廳',
        'nameEn': '2F International Hall',
        'floor': '2樓',
        'area': 142,
        'areaUnit': '坪',
        'areaSqm': 495,
        'height': 6.5,
        'pillar': False,
        'capacity': {'banquet': 500, 'cocktail': 500, 'theater': 460, 'classroom': 300},
        'price': {'weekdayDaytime': 96000, 'weekdayNighttime': 200000, 'weekendDaytime': 100000, 'weekendNighttime': 220000, 'fullDay': 300000, 'overtime': 35000},
        'equipment': standard_equipment + ['大型舞台', '專業音響', '燈光'],
        'images': {'main': f'{img_base_1100}/2023/05/台北花園大酒店-國際廳-婚宴.jpg'},
        'notes': '百合+薔薇合併，142坪，挑高6.5米，最大宴會空間',
        'source': 'pdf_20260330',
    },
    # === 3F (10 spaces) ===
    {
        'id': '1100-04',
        'name': '3F 海芋廳',
        'nameEn': '3F Calla Room',
        'floor': '3樓',
        'area': 12,
        'areaUnit': '坪',
        'areaSqm': 40,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 30, 'cocktail': 30, 'theater': 30, 'classroom': 21, 'hollowSquare': 16, 'ushape': 12},
        'price': {'weekdayDaytime': 12000, 'weekdayNighttime': 30000, 'weekendDaytime': 15000, 'weekendNighttime': 35000, 'fullDay': 50000, 'overtime': 10000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 小型會議室，12坪，可與水仙廳合併為玫瑰廳',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-05',
        'name': '3F 水仙廳',
        'nameEn': '3F Daffodil Room',
        'floor': '3樓',
        'area': 12,
        'areaUnit': '坪',
        'areaSqm': 39,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 30, 'cocktail': 30, 'theater': 30, 'classroom': 21, 'hollowSquare': 16, 'ushape': 12},
        'price': {'weekdayDaytime': 12000, 'weekdayNighttime': 30000, 'weekendDaytime': 15000, 'weekendNighttime': 35000, 'fullDay': 50000, 'overtime': 10000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 小型會議室，12坪',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-06',
        'name': '3F 玫瑰廳',
        'nameEn': '3F Rose Room',
        'floor': '3樓',
        'area': 27,
        'areaUnit': '坪',
        'areaSqm': 89,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 50, 'cocktail': 60, 'theater': 76, 'classroom': 30},
        'price': {'weekdayDaytime': 24000, 'weekdayNighttime': 60000, 'weekendDaytime': 30000, 'weekendNighttime': 70000, 'fullDay': 100000, 'overtime': 15000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '海芋+水仙合併，27坪中型會議室',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-07',
        'name': '3F 火鶴廳',
        'nameEn': '3F Tail Flower Room',
        'floor': '3樓',
        'area': 18,
        'areaUnit': '坪',
        'areaSqm': 59,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 40, 'cocktail': 50, 'theater': 50, 'classroom': 27, 'hollowSquare': 20, 'ushape': 16},
        'price': {'weekdayDaytime': 15000, 'weekdayNighttime': 40000, 'weekendDaytime': 20000, 'weekendNighttime': 45000, 'fullDay': 64000, 'overtime': 10000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 中型會議室，18坪，可與茉莉廳合併為山茶廳',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-08',
        'name': '3F 茉莉廳',
        'nameEn': '3F Jasmine Room',
        'floor': '3樓',
        'area': 18,
        'areaUnit': '坪',
        'areaSqm': 60,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 40, 'cocktail': 50, 'theater': 50, 'classroom': 30, 'hollowSquare': 20, 'ushape': 16},
        'price': {'weekdayDaytime': 15000, 'weekdayNighttime': 40000, 'weekendDaytime': 20000, 'weekendNighttime': 45000, 'fullDay': 64000, 'overtime': 10000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 中型會議室，18坪',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-09',
        'name': '3F 山茶廳',
        'nameEn': '3F Camellia Room',
        'floor': '3樓',
        'area': 38,
        'areaUnit': '坪',
        'areaSqm': 126,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 100, 'cocktail': 100, 'theater': 130, 'classroom': 51},
        'price': {'weekdayDaytime': 30000, 'weekdayNighttime': 80000, 'weekendDaytime': 40000, 'weekendNighttime': 90000, 'fullDay': 128000, 'overtime': 15000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '火鶴+茉莉合併，38坪大型會議室',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-10',
        'name': '3F 牡丹廳',
        'nameEn': '3F Peony Room',
        'floor': '3樓',
        'area': 75,
        'areaUnit': '坪',
        'areaSqm': 247,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 250, 'cocktail': 180, 'theater': 160, 'classroom': 100},
        'price': {'weekdayDaytime': 50000, 'weekdayNighttime': 120000, 'weekendDaytime': 60000, 'weekendNighttime': 140000, 'fullDay': 220000, 'overtime': 30000},
        'equipment': standard_equipment + ['舞台', '音響'],
        'images': {},
        'notes': '火鶴+茉莉+海芋+水仙合併，75坪，3F最大空間',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-11',
        'name': '3F 月桂廳',
        'nameEn': '3F Bay Room',
        'floor': '3樓',
        'area': 7,
        'areaUnit': '坪',
        'areaSqm': 23,
        'height': 2.5,
        'pillar': False,
        'capacity': {'ushape': 10},
        'price': {'weekdayDaytime': 10000, 'weekdayNighttime': 11000, 'weekendDaytime': 12000, 'weekendNighttime': 13000, 'fullDay': 20000, 'overtime': 2000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 最小會議室，7坪，僅10人U型配置',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-12',
        'name': '3F 櫻花廳',
        'nameEn': '3F Cherry Blossoms Room',
        'floor': '3樓',
        'area': 25,
        'areaUnit': '坪',
        'areaSqm': 81,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 60, 'cocktail': 75, 'theater': 70, 'classroom': 42, 'hollowSquare': 31, 'ushape': 20},
        'price': {'weekdayDaytime': 35000, 'weekdayNighttime': 75000, 'weekendDaytime': 40000, 'weekendNighttime': 80000, 'fullDay': 120000, 'overtime': 15000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 中型會議室，25坪',
        'source': 'pdf_20260330',
    },
    {
        'id': '1100-13',
        'name': '3F 百花廳',
        'nameEn': '3F Flora Room',
        'floor': '3樓',
        'area': 35,
        'areaUnit': '坪',
        'areaSqm': 204,
        'height': 2.5,
        'pillar': False,
        'capacity': {'banquet': 50, 'cocktail': 60, 'theater': 60, 'classroom': 24, 'hollowSquare': 18, 'ushape': 21},
        'price': {'weekdayDaytime': 40000, 'weekdayNighttime': 100000, 'weekendDaytime': 45000, 'weekendNighttime': 120000, 'fullDay': 180000, 'overtime': 20000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '3F 大型會議室，35坪',
        'source': 'pdf_20260330',
    },
    # === 1F (1 space) ===
    {
        'id': '1100-14',
        'name': '1F 貴賓廳',
        'nameEn': '1F VIP Room',
        'floor': '1樓',
        'area': 34.5,
        'areaUnit': '坪',
        'areaSqm': 114,
        'height': 3.3,
        'pillar': False,
        'capacity': {'banquet': 70, 'cocktail': 100, 'theater': 100, 'classroom': 51, 'hollowSquare': 36, 'ushape': 30},
        'price': {'weekdayDaytime': 30000, 'weekdayNighttime': 75000, 'weekendDaytime': 30000, 'weekendNighttime': 80000, 'fullDay': 120000, 'overtime': 15000},
        'equipment': standard_equipment,
        'images': {},
        'notes': '1F 貴賓接待室，34.5坪，挑高3.3米',
        'source': 'pdf_20260330',
    },
]

# Build rooms list
v1100['rooms'] = []

for rd in rooms_data:
    room = {
        'id': rd['id'],
        'name': rd['name'],
        'nameEn': rd.get('nameEn', ''),
        'floor': rd.get('floor', ''),
        'area': rd.get('area'),
        'areaUnit': rd.get('areaUnit', '坪'),
        'areaSqm': rd.get('areaSqm'),
        'height': rd.get('height'),
        'pillar': rd.get('pillar', True),
        'capacity': rd.get('capacity', {}),
        'price': rd.get('price', {}),
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
    if room.get('height'):
        score += 5

    room['qualityScore'] = score
    room['qualityLevel'] = 'high' if score >= 70 else ('medium' if score >= 40 else 'low')

    v1100['rooms'].append(room)
    cap_str = f"theater={cap.get('theater','-')}, classroom={cap.get('classroom','-')}, banquet={cap.get('banquet','-')}"
    print(f'  {rd["id"]} {rd["name"]}: score={score}, area={rd.get("area")}坪, '
          f'cap=[{cap_str}], price=weekday_day={price.get("weekdayDaytime","-")}')

# Update venue-level metadata
v1100['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()
v1100['metadata']['scrapeVersion'] = 'Manual_PDF_20260330'
v1100['metadata']['totalRooms'] = len(v1100['rooms'])
v1100['metadata']['skipReason'] = None
v1100['metadata']['completeness']['rooms'] = True
v1100['metadata']['completeness']['capacity'] = True
v1100['metadata']['completeness']['price'] = True

# Update main venue image and gallery
v1100['images']['main'] = f'{img_base_1100}/2024/05/IMG_6811-HDR-2200x1200.jpg'
v1100['images']['gallery'] = [
    f'{img_base_1100}/2024/05/IMG_6811-HDR-2200x1200.jpg',
    f'{img_base_1100}/2023/07/IMG_6811-HDR.jpg',
    f'{img_base_1100}/2023/07/IMG_6839-HDR.jpg',
    f'{img_base_1100}/2023/05/台北花園大酒店-宴會會議-02.jpg',
    f'{img_base_1100}/2023/05/台北花園大酒店-宴會會議-04.jpg',
]

# Update max capacity
max_theater = max((r.get('capacity', {}).get('theater', 0) for r in v1100['rooms']), default=0)
v1100['maxCapacityTheater'] = max_theater
v1100['capacity'] = {'theater': max_theater}

# Update price range
min_half = min((r.get('price', {}).get('weekdayDaytime', 999999) for r in v1100['rooms']), default=0)
v1100['priceHalfDay'] = min_half
v1100['priceFullDay'] = min_half * 2

# Fix contact info
v1100['contactPhone'] = '02-2314-3300'
v1100['contactPerson'] = '宴會部'

# Fix URL
v1100['url'] = 'https://www.taipeigarden.com.tw/banquets-conferences/banquet-conference/'

print(f'\nID 1100 done: {len(v1100["rooms"])} rooms, max theater capacity: {max_theater}')

# ============================================================
# 3. ID 1121 (三德大酒店) - Delete
# ============================================================
print('\n=== ID 1121 三德大酒店 ===')
before = len(data)
data = [v for v in data if v['id'] != 1121]
after = len(data)
print(f'Deleted ID 1121: {before} → {after} venues')

# ============================================================
# Save
# ============================================================
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('\n=== All done! ===')
print(f'ID 1051: Images updated')
print(f'ID 1100: {len(v1100["rooms"])} rooms added from PDF')
print(f'ID 1121: Deleted')
print(f'Total venues: {len(data)}')
