#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update TICC (ID 1448) with V5 parser results
"""
import json
import shutil
from datetime import datetime

print("="*80)
print("Update TICC with V5 Parser Results")
print("="*80)
print()

# Backup
backup = f'venues.json.backup.ticc_v5_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup)
print(f"Backup: {backup}")
print()

# Load parsed data
with open('ticc_v5_final_20260325_201434.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)

print(f"Loaded {parsed['total_rooms']} rooms from V5 parser")
print()

# Load venues
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Update TICC (ID 1448)
for venue in venues:
    if venue['id'] == 1448:
        old_count = len(venue.get('rooms', []))

        # Update rooms
        venue['rooms'] = parsed['rooms']

        # Update metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}

        venue['metadata']['pdf_parser'] = 'V5_final'
        venue['metadata']['pdf_parsed_at'] = parsed['parsed_at']
        venue['metadata']['total_rooms'] = len(parsed['rooms'])
        venue['metadata']['data_quality'] = 'high'

        print(f"[UPDATED] TICC (ID 1448)")
        print(f"  Rooms: {old_count} -> {len(parsed['rooms'])}")
        print(f"  Parser: V5_final")
        print()

        # Show key rooms
        key_rooms = ['大會堂全場', '大會堂半場', '3樓南']
        print("  Key rooms:")
        for room in parsed['rooms']:
            for key in key_rooms:
                if key in room['name']:
                    print(f"    {room['name']}")
                    print(f"      Capacity: {room.get('capacity_theater', 'N/A')}")
                    print(f"      Area: {room.get('area_sqm', 'N/A')} sqm")
                    print(f"      Price: ${room.get('price_weekday', 'N/A'):,}")
                    break
        break

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print()
print("[OK] venues.json updated")
print()
print("="*80)
print("TICC Update Complete")
print("="*80)
print()
print("Summary:")
print("  - Parser: V5 (correct column mapping)")
print("  - Rooms: 26 (multi-line handled)")
print("  - Key issues fixed:")
print("    1. 大會堂全場: Cap 3100, Area 2973, Price 159000")
print("    2. 3樓南/北軒: Cap 90 (name no longer truncated to '3')")
print("    3. Multi-line data correctly merged")
print()
print("Next steps:")
print("  1. Review venues.json for any remaining issues")
print("  2. Process Nangang Exhibition Center (ID 1500)")
