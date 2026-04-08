#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修復集思台大會議中心 - 添加中英文會議室名稱"""

import json
import sys
import io
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load venues.json
print("Loading venues.json...")
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Find NTUCC
venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1128), None)
if venue_idx is None:
    print("Venue ID 1128 not found!")
    sys.exit(1)

venue = venues[venue_idx]

print('=' * 80)
print(f'Fixing: {venue.get("name")}')
print('=' * 80)

# Correct room names with both Chinese and English
rooms_correction = [
    {
        'id': '1128-01',
        'name': '國際會議廳',
        'nameEn': 'International Conference Hall',
        'capacity': {'theater': 400},
        'area': 253.6,
        'areaUnit': 'ping',
        'price': {'weekday': 44000, 'holiday': 48000},
        'equipment': 'Wireless mic x3, table mic, VIP lounge x1, registration table x3',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-02',
        'name': '蘇格拉底廳',
        'nameEn': 'Socrates Hall',
        'capacity': {'theater': 145},
        'area': 59.8,
        'areaUnit': 'ping',
        'price': {'weekday': 19000, 'holiday': 21000},
        'equipment': 'Wireless mic x3, backroom x1, registration table x2',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-03',
        'name': '柏拉圖廳',
        'nameEn': 'Plato Hall',
        'capacity': {'theater': 150},
        'area': 69.3,
        'areaUnit': 'ping',
        'price': {'weekday': 16000, 'holiday': 18000},
        'equipment': 'Wireless mic x3, registration table x2',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-04',
        'name': '講者休息室',
        'nameEn': 'Speaker Lounge',
        'capacity': {'theater': 6},
        'area': 5.1,
        'areaUnit': 'ping',
        'price': {'weekday': 2500, 'holiday': 3000},
        'equipment': 'Speaker rest area for 6 people (only with Plato Hall)',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-05',
        'name': '洛克廳',
        'nameEn': 'Locke Hall',
        'capacity': {'theater': 90},
        'area': 37.7,
        'areaUnit': 'ping',
        'price': {'weekday': 10000, 'holiday': 11000},
        'equipment': 'Wireless mic x2, registration table x2',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-06',
        'name': '亞歷山大廳',
        'nameEn': 'Alexander Hall',
        'capacity': {'theater': 54},
        'area': 31.3,
        'areaUnit': 'ping',
        'price': {'weekday': 7000, 'holiday': 8000},
        'equipment': 'Wireless mic x2, registration table x1',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-07',
        'name': '阿基米德廳',
        'nameEn': 'Archimedes Hall',
        'capacity': {'theater': 54},
        'area': 31.3,
        'areaUnit': 'ping',
        'price': {'weekday': 7000, 'holiday': 8000},
        'equipment': 'Wireless mic x2, registration table x1',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-08',
        'name': '亞里斯多德廳',
        'nameEn': 'Aristotle Hall',
        'capacity': {'theater': 18},
        'area': 10.5,
        'areaUnit': 'ping',
        'price': {'weekday': 3500, 'holiday': 4000},
        'equipment': 'Registration table x1',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-09',
        'name': '達文西廳',
        'nameEn': 'Da Vinci Hall',
        'capacity': {'theater': 48},
        'area': 41.4,
        'areaUnit': 'ping',
        'price': {'weekday': 6500, 'holiday': 7000},
        'equipment': 'Wireless mic x2, registration table x1',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-10',
        'name': '拉斐爾廳',
        'nameEn': 'Raphael Hall',
        'capacity': {'theater': 72},
        'area': 41.4,
        'areaUnit': 'ping',
        'price': {'weekday': 8500, 'holiday': 9500},
        'equipment': 'Wireless mic x2, registration table x1',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-11',
        'name': '米開朗基羅廳',
        'nameEn': 'Michelangelo Hall',
        'capacity': {'theater': 72},
        'area': 41.4,
        'areaUnit': 'ping',
        'price': {'weekday': 8500, 'holiday': 9500},
        'equipment': 'Wireless mic x2, registration table x1',
        'source': 'pdf_20250401'
    },
    {
        'id': '1128-12',
        'name': '尼采廳',
        'nameEn': 'Nietzsche Hall',
        'capacity': {'theater': 48},
        'area': 41.4,
        'areaUnit': 'ping',
        'price': {'weekday': 6500, 'holiday': 7000},
        'equipment': 'Wireless mic x2, registration table x1',
        'source': 'pdf_20250401'
    },
]

print(f'\nUpdating {len(rooms_correction)} rooms with Chinese + English names...')
print('-' * 80)

for room in rooms_correction:
    name_zh = room['name']
    name_en = room['nameEn']
    cap = room['capacity']['theater']
    price_weekday = room['price']['weekday']
    print(f'{name_zh:15s} / {name_en:30s}: {cap:3} people, NT${price_weekday:,}/day')

# Update venue
venue['rooms'] = rooms_correction

# Update metadata
if 'metadata' not in venue:
    venue['metadata'] = {}
venue['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'scrapeVersion': 'V4_PDF_Enhanced_ChineseNames',
    'totalRooms': len(rooms_correction),
    'pdfExtractDate': '2025-04-01',
    'priceCoverage': '100%',
    'equipmentCoverage': '100%',
    'nameFormat': 'Chinese + English'
})

# Save
print('\nSaving to venues.json...')
venues[venue_idx] = venue

# Create backup
backup_path = f"venues.json.backup.ntucc_chinese_names_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)
print(f'Backup created: {backup_path}')

# Save main file
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n✅ Success! Updated {len(rooms_correction)} rooms with Chinese + English names')
print(f'Name format: 中文（主要） + 英文（nameEn 欄位）')
