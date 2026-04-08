#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove unreachable hotel venues from database"""
import json
from datetime import datetime
import shutil

# Hotels to remove
HOTELS_TO_REMOVE = [1048, 1059, 1073, 1080, 1084, 1092]

HOTEL_NAMES = {
    1048: "Old Hotel (老爺大酒店)",
    1059: "Youchun Hotel (友春大飯店)",
    1073: "Zibei Hotel (子皮大飯店)",
    1080: "Kanghua Hotel (康華大飯店)",
    1084: "Ching Tai Hotel (寒舍大飯店)",
    1092: "First Hotel (第一飯店)",
}

print("="*80)
print("Remove Unreachable Hotel Venues")
print("="*80)
print()

# Backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_name = f"venues.json.backup.removed_hotels_{timestamp}"
shutil.copy('venues.json', backup_name)
print(f"Backup: {backup_name}")
print()

# Load
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

print(f"Total venues before removal: {len(venues)}")

# Remove venues
removed_venues = []
remaining_venues = []

for venue in venues:
    if venue.get('id') in HOTELS_TO_REMOVE:
        removed_venues.append(venue)
    else:
        remaining_venues.append(venue)

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(remaining_venues, f, ensure_ascii=False, indent=2)

print(f"Total venues after removal: {len(remaining_venues)}")
print(f"Removed: {len(removed_venues)} venues")
print()

print("Removed venues:")
for venue in removed_venues:
    vid = venue.get('id')
    name = venue.get('name')
    reason = venue.get('metadata', {}).get('scrapeError', 'Unknown')
    print(f"  - ID {vid}: {name}")
    print(f"    Reason: {reason}")

# Save removed venues to separate file
removed_file = f"removed_hotels_{timestamp}.json"
with open(removed_file, 'w', encoding='utf-8') as f:
    json.dump(removed_venues, f, ensure_ascii=False, indent=2)

print()
print(f"Removed venues saved to: {removed_file}")
print()
print("="*80)
print("Summary")
print("="*80)
print()
print(f"Original count: {len(venues)}")
print(f"Removed count: {len(removed_venues)}")
print(f"New count: {len(remaining_venues)}")
print()
print("These venues have been removed due to:")
print("  - Website inaccessible (DNS resolution failed)")
print("  - No public data available")
print("  - Unable to verify current status")
