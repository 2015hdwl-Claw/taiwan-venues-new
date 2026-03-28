#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete fix for TICC room names + Nangang Exhibition Center update
"""
import json
import shutil
from datetime import datetime

print("="*80)
print("FINAL FIX: TICC Room Names + Nangang Exhibition Center")
print("="*80)
print()

# Backup
backup = f'venues.json.backup.final_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup)
print(f"Backup: {backup}")
print()

# Load V8 parsed data
with open('ticc_v8_final_20260325_202328.json', 'r', encoding='utf-8') as f:
    ticc_parsed = json.load(f)

print(f"TICC: {len(ticc_parsed['rooms'])} rooms loaded from V8 parser")

# Add missing rooms manually based on PDF
missing_rooms = [
    {
        'name': '大會堂半場',
        'capacity_theater': 1208,
        'capacity_classroom': None,
        'capacity_u': None,
        'capacity_negotiate': None,
        'area_sqm': None,
        'area_ping': None,
        'dimensions': None,
        'price_weekday': 112000,
        'price_weekend': 123000,
        'price_exhibition': None
    },
    {
        'name': '3樓南 /北軒',
        'capacity_theater': 90,
        'capacity_classroom': 70,
        'capacity_u': 40,
        'capacity_negotiate': 52,
        'area_sqm': 152,
        'area_ping': 46,
        'dimensions': '18×7.5×3.7',
        'price_weekday': 18500,
        'price_weekend': 21500,
        'price_exhibition': 23500
    },
    {
        'name': '4樓雅 /悅軒',
        'capacity_theater': 90,
        'capacity_classroom': 70,
        'capacity_u': 40,
        'capacity_negotiate': 52,
        'area_sqm': 152,
        'area_ping': 46,
        'dimensions': '18×7.5×3.7',
        'price_weekday': 18500,
        'price_weekend': 21500,
        'price_exhibition': 23500
    },
    {
        'name': '201 全室',
        'capacity_theater': 800,
        'capacity_classroom': 544,
        'capacity_u': 108,
        'capacity_negotiate': 288,
        'area_sqm': 729,
        'area_ping': 220,
        'dimensions': '25.8×28.8×5.6',
        'price_weekday': 67000,
        'price_weekend': 80000,
        'price_exhibition': 87500
    }
]

# Add missing rooms
all_rooms = ticc_parsed['rooms'] + missing_rooms

# Update venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Update TICC (ID 1448)
for venue in venues:
    if venue['id'] == 1448:
        venue['rooms'] = all_rooms

        if 'metadata' not in venue:
            venue['metadata'] = {}

        venue['metadata']['pdf_parser'] = 'V8_final_manual_fix'
        venue['metadata']['pdf_parsed_at'] = datetime.now().isoformat()
        venue['metadata']['total_rooms'] = len(all_rooms)

        print(f"\n[UPDATED] TICC (ID 1448)")
        print(f"  Rooms: {len(all_rooms)}")
        print(f"  Parser: V8 + Manual fixes")

        # Show critical rooms
        print("\n  Critical rooms:")
        critical = ['大會堂全場', '大會堂半場', '102', '103', '3樓南 /北軒']
        for room in all_rooms:
            for name in critical:
                if name == room['name']:
                    print(f"    {room['name']}")
                    print(f"      Cap: {room.get('capacity_theater')}, Area: {room.get('area_sqm')}")
                    break
        break

# Update Nangang (ID 1500) - Correct URL
for venue in venues:
    if venue['id'] == 1500:
        old_url = venue['url']
        venue['url'] = 'https://www.tainex.com.tw/venue/room-info/1/3'

        print(f"\n[UPDATED] Nangang Exhibition Center (ID 1500)")
        print(f"  Old URL: {old_url}")
        print(f"  New URL: {venue['url']}")

        # Add metadata about the correct URLs
        if 'metadata' not in venue:
            venue['metadata'] = {}

        venue['metadata']['alternative_urls'] = [
            'https://www.tainex.com.tw/venue/room-info/1/3',
            'https://www.tainex.com.tw/venue/app-room'
        ]
        venue['metadata']['url_updated_at'] = datetime.now().isoformat()

        break

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print()
print("[OK] venues.json updated")
print()

print("="*80)
print("SUMMARY")
print("="*80)
print()
print("TICC (ID 1448):")
print(f"  - Fixed room names (102, 103, etc. no longer contain numbers)")
print(f"  - Added missing rooms: 大會堂半場, 3樓南 /北軒, 4樓雅 /悅軒, 201 全室")
print(f"  - Total: {len(all_rooms)} rooms")
print()
print("Nangang Exhibition Center (ID 1500):")
print(f"  - Updated URL: https://www.tainex.com.tw/venue/room-info/1/3")
print(f"  - Added alternative URLs to metadata")
print()
print("Next steps:")
print("  1. Scrape Nangang from new URL")
print("  2. Extract TICC room photos from: https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueSearch.jsp&ctNode=322&CtUnit=99&BaseDSD=7&mp=1")
