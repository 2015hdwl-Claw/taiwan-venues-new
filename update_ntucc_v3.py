#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update NTUCC (ID: 1128) with PDF data"""

import json
import sys
import io
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding
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
print(f'Updating: {venue.get("name")}')
print('=' * 80)

# PDF data (manually extracted from PDF)
rooms_data = [
    {
        'name': 'International Conference Hall',
        'nameEn': 'International Conference Hall',
        'nameZh': 'International Conference Hall',
        'capacity': 400,
        'area': 253.6,
        'priceWeekday': 44000,
        'priceHoliday': 48000,
        'facilities': 'Wireless mic x3, table mic, VIP lounge x1, registration table x3'
    },
    {
        'name': 'Socrates Hall',
        'nameEn': 'Socrates Hall',
        'nameZh': 'Socrates Hall',
        'capacity': 145,
        'area': 59.8,
        'priceWeekday': 19000,
        'priceHoliday': 21000,
        'facilities': 'Wireless mic x3, backroom x1, registration table x2'
    },
    {
        'name': 'Plato Hall',
        'nameEn': 'Plato Hall',
        'nameZh': 'Plato Hall',
        'capacity': 150,
        'area': 69.3,
        'priceWeekday': 16000,
        'priceHoliday': 18000,
        'facilities': 'Wireless mic x3, registration table x2'
    },
    {
        'name': 'Speaker Lounge',
        'nameEn': 'Speaker Lounge',
        'nameZh': 'Speaker Lounge',
        'capacity': 6,
        'area': 5.1,
        'priceWeekday': 2500,
        'priceHoliday': 3000,
        'facilities': 'Speaker rest area for 6 people (only with Plato Hall)'
    },
    {
        'name': 'Locke Hall',
        'nameEn': 'Locke Hall',
        'nameZh': 'Locke Hall',
        'capacity': 90,
        'area': 37.7,
        'priceWeekday': 10000,
        'priceHoliday': 11000,
        'facilities': 'Wireless mic x2, registration table x2'
    },
    {
        'name': 'Alexander Hall',
        'nameEn': 'Alexander Hall',
        'nameZh': 'Alexander Hall',
        'capacity': 54,
        'area': 31.3,
        'priceWeekday': 7000,
        'priceHoliday': 8000,
        'facilities': 'Wireless mic x2, registration table x1'
    },
    {
        'name': 'Archimedes Hall',
        'nameEn': 'Archimedes Hall',
        'nameZh': 'Archimedes Hall',
        'capacity': 54,
        'area': 31.3,
        'priceWeekday': 7000,
        'priceHoliday': 8000,
        'facilities': 'Wireless mic x2, registration table x1'
    },
    {
        'name': 'Aristotle Hall',
        'nameEn': 'Aristotle Hall',
        'nameZh': 'Aristotle Hall',
        'capacity': 18,
        'area': 10.5,
        'priceWeekday': 3500,
        'priceHoliday': 4000,
        'facilities': 'Registration table x1'
    },
    {
        'name': 'Da Vinci Hall',
        'nameEn': 'Da Vinci Hall',
        'nameZh': 'Da Vinci Hall',
        'capacity': 48,
        'area': 41.4,
        'priceWeekday': 6500,
        'priceHoliday': 7000,
        'facilities': 'Wireless mic x2, registration table x1'
    },
    {
        'name': 'Raphael Hall',
        'nameEn': 'Raphael Hall',
        'nameZh': 'Raphael Hall',
        'capacity': 72,
        'area': 41.4,
        'priceWeekday': 8500,
        'priceHoliday': 9500,
        'facilities': 'Wireless mic x2, registration table x1'
    },
    {
        'name': 'Michelangelo Hall',
        'nameEn': 'Michelangelo Hall',
        'nameZh': 'Michelangelo Hall',
        'capacity': 72,
        'area': 41.4,
        'priceWeekday': 8500,
        'priceHoliday': 9500,
        'facilities': 'Wireless mic x2, registration table x1'
    },
    {
        'name': 'Nietzsche Hall',
        'nameEn': 'Nietzsche Hall',
        'nameZh': 'Nietzsche Hall',
        'capacity': 48,
        'area': 41.4,
        'priceWeekday': 6500,
        'priceHoliday': 7000,
        'facilities': 'Wireless mic x2, registration table x1'
    },
]

print(f'\nExtracted {len(rooms_data)} rooms from PDF')
print('-' * 80)

# Create complete room list (replace existing)
new_rooms = []
for i, room_data in enumerate(rooms_data, 1):
    room = {
        'id': f'1128-{i:02d}',
        'name': room_data['nameEn'],
        'nameEn': room_data.get('nameEn', ''),
        'capacity': {
            'theater': room_data['capacity']
        },
        'area': room_data['area'],
        'areaUnit': 'ping',
        'price': {
            'weekday': room_data['priceWeekday'],
            'holiday': room_data['priceHoliday']
        },
        'equipment': room_data.get('facilities', ''),
        'source': 'pdf_20250401'
    }
    new_rooms.append(room)
    print(f'{i}. {room["name"]}: {room_data["capacity"]} people / {room_data["area"]} ping / NT${room_data["priceWeekday"]:,} weekday')

# Update venue
venue['rooms'] = new_rooms
venue['maxCapacityTheater'] = 400  # International Conference Hall
venue['maxCapacityClassroom'] = 150  # Plato Hall

# Update metadata
if 'metadata' not in venue:
    venue['metadata'] = {}
venue['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'scrapeVersion': 'V4_PDF_Enhanced',
    'pdfSource': 'https://www.meeting.com.tw/ntu/download/...',
    'totalRooms': len(new_rooms),
    'pdfExtractDate': '2025-04-01',
    'priceCoverage': '100%',
    'equipmentCoverage': '100%'
})

# Save
print('\nSaving to venues.json...')
venues[venue_idx] = venue

# Create backup
backup_path = f"venues.json.backup.ntucc_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)
print(f'Backup created: {backup_path}')

# Save main file
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\nSuccess! Updated {len(new_rooms)} rooms in venues.json')
print(f'Total rooms: {len(new_rooms)}')
print(f'Max capacity: {venue["maxCapacityTheater"]} people')
print(f'Data source: PDF 2025-04-01')
print(f'Price coverage: 100%')
print(f'Equipment coverage: 100%')
