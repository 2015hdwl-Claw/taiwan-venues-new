#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import shutil

# Backup
backup = f'venues.json.backup.ticc_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup)

# Load venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Load TICC parsed data
with open('ticc_rooms_parsed_v2.json', 'r', encoding='utf-8') as f:
    ticc_data = json.load(f)

# Find TICC
for venue in venues:
    if venue['id'] == 1448:
        # Convert rooms format
        rooms = []
        for room in ticc_data['rooms']:
            cleaned_room = {
                'name': room['name'],
                'capacity': str(room['capacity_theater']) if room.get('capacity_theater') else None,
                'area': f"{room.get('area_sqm')}m2" if room.get('area_sqm') else None
            }
            rooms.append(cleaned_room)

        # Update
        venue['rooms'] = rooms
        venue['metadata']['pdf_source'] = 'ticc_pdf_parsed_v2'
        venue['metadata']['total_rooms_from_pdf'] = len(rooms)
        venue['metadata']['pdf_updated_at'] = datetime.now().isoformat()
        break

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'TICC updated with {len(rooms)} rooms from PDF')
print(f'Backup: {backup}')
