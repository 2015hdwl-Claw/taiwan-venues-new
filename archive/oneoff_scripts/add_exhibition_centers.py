#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add 5 New Exhibition and Conference Centers
"""

import json
import shutil
from datetime import datetime

print("=" * 100)
print("Add 5 New Exhibition and Conference Centers")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.exhibition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# New venues
new_venues = [
    {
        'id': 1532,
        'name': '新北市工商展覽中心',
        'venueType': '展覽中心',
        'city': '新北市',
        'address': '新北市',
        'url': 'http://www.tcwtc.com.tw/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL - Exhibition center'
        }
    },
    {
        'id': 1533,
        'name': '臺中國際會展中心 (水湳)',
        'venueType': '會展中心',
        'city': '台中市',
        'address': '台中市',
        'url': 'https://www.ticec.com.tw/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL - International convention center'
        }
    },
    {
        'id': 1534,
        'name': '臺中國際展覽館 (烏日)',
        'venueType': '展覽館',
        'city': '台中市',
        'address': '台中市',
        'url': 'https://www.tc-iec.com/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL - International exhibition center'
        }
    },
    {
        'id': 1535,
        'name': '高雄展覽館 (KEC)',
        'venueType': '展覽館',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.kecc.com.tw/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL - Kaohsiung exhibition center'
        }
    },
    {
        'id': 1536,
        'name': '高雄國際會議中心 (ICCK)',
        'venueType': '會議中心',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.icck.com.tw/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL - International convention center'
        }
    },
]

# Add all new venues
for venue in new_venues:
    venues.append(venue)
    print(f"Added: ID {venue['id']} - {venue['name']}")

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("COMPLETE")
print("=" * 100)
print(f"Total venues: {len(venues)}")
print(f"Added: {len(new_venues)} venues")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
