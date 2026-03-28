#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mark unreachable hotel venues"""
import json
from datetime import datetime
import shutil

# Unreachable hotel IDs
UNREACHABLE_HOTELS = [1048, 1059, 1073, 1080, 1084, 1092]

print("="*80)
print("Mark Unreachable Hotel Venues")
print("="*80)
print()

# Backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_name = f"venues.json.backup.hotels_unreachable_{timestamp}"
shutil.copy('venues.json', backup_name)
print(f"Backup: {backup_name}")
print()

# Load
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Update metadata
updated_count = 0
for venue in venues:
    if venue.get('id') in UNREACHABLE_HOTELS:
        venue['metadata'] = venue.get('metadata', {})
        venue['metadata'].update({
            'lastScrapedAt': datetime.now().isoformat(),
            'scrapeStatus': 'website_unreachable',
            'scrapeError': 'DNS resolution failed or SSL/connection error',
            'notes': 'Official website inaccessible, no public data available via web search',
            'recommendation': 'Requires manual verification. Consider removing if confirmed out of business.',
        })
        updated_count += 1
        print(f"Marked: ID {venue['id']} - {venue['name']}")

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print()
print(f"Updated: {updated_count} venues")
print(f"Backup: {backup_name}")
print()
print("="*80)
print("Summary")
print("="*80)
print()
print(f"Marked {updated_count} hotels as unreachable")
print("These venues will be rechecked in 3 months (2026-06-25)")
print()
print("Hotels marked:")
for hid in UNREACHABLE_HOTELS:
    for v in venues:
        if v.get('id') == hid:
            print(f"  - {v['name']} (ID: {hid})")
            break
