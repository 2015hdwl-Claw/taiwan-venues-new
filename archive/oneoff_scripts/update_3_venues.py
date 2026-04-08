#!/usr/bin/env python3
"""Update venues 1124, 1090, 1500 with proper meeting room data."""

import json
import sys
import copy
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

venue_map = {v['id']: v for v in venues}

# ============================================================
# 1. Venue 1124 — Copy rooms from venue 1100 (same hotel)
# ============================================================
print("=" * 60)
print("Venue 1124 (花園大酒店) — Copying from venue 1100")
print("=" * 60)

v1100 = venue_map.get(1100)
v1124 = venue_map.get(1124)

if not v1100 or not v1124:
    print("ERROR: venue 1100 or 1124 not found")
    sys.exit(1)

# Deep copy rooms from 1100, change ID prefix
new_rooms = []
for room in v1100.get('rooms', []):
    r = copy.deepcopy(room)
    # Change ID prefix: 1100-01 → 1124-01
    if 'id' in r:
        r['id'] = r['id'].replace('1100-', '1124-')
    new_rooms.append(r)

v1124['rooms'] = new_rooms

# Update venue-level fields
max_theater = max((r.get('capacity', {}).get('theater', 0) for r in new_rooms), default=0)
v1124['maxCapacityTheater'] = max_theater

min_half = min((r.get('price', {}).get('weekdayDaytime', 999999) for r in new_rooms), default=0)
v1124['priceHalfDay'] = min_half
v1124['priceFullDay'] = min_half * 2

# Update metadata
if 'metadata' not in v1124:
    v1124['metadata'] = {}
v1124['metadata']['totalRooms'] = len(new_rooms)
v1124['metadata']['scrapeConfidenceScore'] = 90
v1124['metadata']['lastScrapedAt'] = datetime.now().isoformat()
v1124['metadata']['scrapeVersion'] = 'Manual_PDF_Copy_1100'
v1124['metadata']['completeness'] = {
    'basicInfo': True, 'rooms': True, 'capacity': True,
    'area': True, 'price': True, 'images': True
}

print(f"  Copied {len(new_rooms)} rooms from venue 1100")
print(f"  Max theater: {max_theater}, Min half-day: {min_half}")

# ============================================================
# 2. Venue 1090 — Use archive script data (9 rooms)
# ============================================================
print("\n" + "=" * 60)
print("Venue 1090 (茹曦酒店 ILLUME TAIPEI) — 9 rooms")
print("=" * 60)

v1090 = venue_map.get(1090)
if not v1090:
    print("ERROR: venue 1090 not found")
    sys.exit(1)

illumme_rooms = [
    {
        "id": "1090-01",
        "name": "茹曦廳",
        "nameEn": "ILLUME Ballroom",
        "floor": "2F",
        "area": 253,
        "areaUnit": "坪",
        "areaSqm": 836,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "pillarInfo": "挑高無柱",
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 1200,
            "classroom": 800,
            "banquet": 1000
        },
        "equipment": ["投影設備", "音響系統", "舞台燈光"],
        "features": ["挑高無柱", "空間寬敞", "可分為A/B廳"],
        "images": {"main": "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/05_Events_2F_Grand_Ballroom_1-jpg.webp"},
        "notes": "836平方公尺，挑高無柱、空間寬敞，可容納至多1,200人，可分為茹曦A廳(220平方公尺)和茹曦B廳",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-02",
        "name": "斯賓諾莎宴會廳",
        "nameEn": "Spinoza Ballroom",
        "floor": "5F",
        "area": 134,
        "areaUnit": "坪",
        "areaSqm": 443,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "pillarInfo": "挑高無柱",
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 400,
            "classroom": 250,
            "banquet": 300
        },
        "equipment": ["投影設備", "音響系統"],
        "features": ["挑高無柱", "獨立接待區", "陽光灑落"],
        "images": {},
        "notes": "443平方公尺，挑高、寬敞、方正且無柱，有著陽光灑落的獨立接待區，60~400人",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-03",
        "name": "貴賓軒",
        "nameEn": "VIP Lounge",
        "floor": "2F",
        "area": 15,
        "areaUnit": "坪",
        "areaSqm": 47,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 220,
            "classroom": 100,
            "ushape": 50
        },
        "equipment": ["投影設備", "白板", "無線網路"],
        "features": ["12個多功能空間", "靈活彈性"],
        "images": {},
        "notes": "47~271平方公尺，共有多達12個靈活彈性的多功能空間",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-04",
        "name": "狄德羅廳",
        "nameEn": "Diderot Room",
        "floor": "2F",
        "area": None,
        "areaUnit": "坪",
        "areaSqm": None,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 80,
            "classroom": 40,
            "ushape": 20
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": {},
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-05",
        "name": "康德廳",
        "nameEn": "Kant Room",
        "floor": "2F",
        "area": None,
        "areaUnit": "坪",
        "areaSqm": None,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 80,
            "classroom": 40,
            "ushape": 20
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": {},
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-06",
        "name": "孔狄亞克廳",
        "nameEn": "Condillac Room",
        "floor": "2F",
        "area": None,
        "areaUnit": "坪",
        "areaSqm": None,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 80,
            "classroom": 40,
            "ushape": 20
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": {},
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-07",
        "name": "霍布斯廳",
        "nameEn": "Hobbes Room",
        "floor": "2F",
        "area": None,
        "areaUnit": "坪",
        "areaSqm": None,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 60,
            "classroom": 30,
            "ushape": 15
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": {},
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-08",
        "name": "孟德斯鳩廳",
        "nameEn": "Montesquieu Room",
        "floor": "2F",
        "area": None,
        "areaUnit": "坪",
        "areaSqm": None,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 60,
            "classroom": 30,
            "ushape": 15
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "獨立"],
        "images": {},
        "notes": "貴賓軒獨立多功能廳",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    },
    {
        "id": "1090-09",
        "name": "玉蘭軒",
        "nameEn": "Magnolia Lounge",
        "floor": "2F",
        "area": None,
        "areaUnit": "坪",
        "areaSqm": None,
        "height": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 80,
            "classroom": 50,
            "banquet": 80
        },
        "equipment": ["餐飲設備", "音響設備"],
        "features": ["東方韻味", "私人用餐", "獨立包廂5間"],
        "images": {},
        "notes": "獨立包廂5間，充滿東方韻味，適合私人用餐場合、特殊活動或夢想婚禮，10~80人",
        "source": "官網會議頁面_manual_20260331",
        "lastUpdated": "2026-03-31"
    }
]

v1090['rooms'] = illumme_rooms

# Update venue-level
max_theater_1090 = max((r.get('capacity', {}).get('theater', 0) for r in illumme_rooms if r.get('capacity', {}).get('theater')), default=0)
v1090['maxCapacityTheater'] = max_theater_1090
v1090['totalRooms'] = len(illumme_rooms)

if 'metadata' not in v1090:
    v1090['metadata'] = {}
v1090['metadata']['totalRooms'] = len(illumme_rooms)
v1090['metadata']['lastScrapedAt'] = datetime.now().isoformat()
v1090['metadata']['scrapeVersion'] = 'Manual_Website_20260331'
v1090['metadata']['scrapeConfidenceScore'] = 65
v1090['metadata']['completeness'] = {
    'basicInfo': True, 'rooms': True, 'capacity': True,
    'area': False, 'price': False, 'images': False, 'contact': True
}

print(f"  Updated {len(illumme_rooms)} rooms")
print(f"  Max theater: {max_theater_1090}")
for r in illumme_rooms:
    cap = r.get('capacity', {}).get('theater', '-')
    sqm = r.get('areaSqm', '-')
    print(f"    {r['id']} {r['name']}: {sqm}㎡, theater={cap}")

# ============================================================
# 3. Venue 1500 — Fix format compatibility
# ============================================================
print("\n" + "=" * 60)
print("Venue 1500 (南港展覽館) — Fix format")
print("=" * 60)

v1500 = venue_map.get(1500)
if not v1500:
    print("ERROR: venue 1500 not found")
    sys.exit(1)

fixed_count = 0
for room in v1500.get('rooms', []):
    # Fix 1: equipment string → array
    if isinstance(room.get('equipment'), str):
        # Use equipmentList if available, otherwise parse
        if room.get('equipmentList') and isinstance(room['equipmentList'], list):
            room['equipment'] = room['equipmentList']
        else:
            room['equipment'] = [item.strip() for item in room['equipment'].split('、') if item.strip()]
        fixed_count += 1

    # Fix 2: Add pricing field for room.js compatibility
    if room.get('price') and not room.get('pricing'):
        p = room['price']
        room['pricing'] = {
            'halfDay': p.get('weekday'),
            'fullDay': None,
            'overtime': None,
            'note': p.get('note', '')
        }

    # Fix 3: areaUnit ㎡ → standard
    if room.get('areaUnit') == '㎡':
        room['areaUnit'] = '平方公尺'

print(f"  Fixed {fixed_count} rooms (equipment string → array)")
print(f"  Added pricing field to all rooms")
print(f"  Fixed areaUnit ㎡ → 平方公尺")

# ============================================================
# Save
# ============================================================
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print("All 3 venues updated successfully!")
print("=" * 60)
print(f"  1124: {len(v1124['rooms'])} rooms")
print(f"  1090: {len(v1090['rooms'])} rooms")
print(f"  1500: {len(v1500['rooms'])} rooms (format fixed)")
