#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add 3 New Taichung Venues + Check TCIEC
"""

import json
import shutil
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("Add 3 New Taichung Venues + Check TCIEC")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.taichung3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Check if TCIEC exists
tciec = next((v for v in venues if v['id'] == 1534), None)
if tciec:
    print(f"TCIEC exists: ID {tciec['id']} - Quality: {tciec.get('metadata', {}).get('qualityScore', 0)}")
else:
    print("TCIEC not found!")

# New venues
new_venues = [
    {
        'id': 1537,
        'name': '台中港酒店',
        'venueType': '飯店場地',
        'city': '台中市',
        'address': '台中市',
        'url': 'https://www.tchhotel.com/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL'
        }
    },
    {
        'id': 1538,
        'name': '新天地餐飲集團 (梧棲創始店)',
        'venueType': '婚宴場地',
        'city': '台中市',
        'address': '台中市',
        'url': 'https://www.new-palace.com.tw/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL'
        }
    },
    {
        'id': 1539,
        'name': '震大金鬱金香酒店 (Zenda Gold Tulip)',
        'venueType': '飯店場地',
        'city': '台中市',
        'address': '台中市',
        'url': 'https://www.goldentulip-zendahotel.com/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'User provided URL'
        }
    },
]

# Add new venues
for venue in new_venues:
    venues.append(venue)
    print(f"Added: ID {venue['id']} - {venue['name']}")

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\nTotal venues: {len(venues)}")

# Now scrape these 3 venues
print("\n" + "=" * 100)
print("Scraping 3 New Venues")
print("=" * 100)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

venues_to_scrape = [
    (1537, '台中港酒店', 'https://www.tchhotel.com/'),
    (1538, '新天地餐飲集團', 'https://www.new-palace.com.tw/'),
    (1539, '震大金鬱金香酒店', 'https://www.goldentulip-zendahotel.com/'),
]

success = 0

for vid, name, url in venues_to_scrape:
    venue = next((v for v in venues if v['id'] == vid), None)
    if not venue:
        continue

    print(f"\n[{venues_to_scrape.index((vid, name, url)) + 1}] ID {vid}: {name}")
    print(f"URL: {url}")

    try:
        r = requests.get(url, timeout=30, verify=False, headers=headers, allow_redirects=True)
        print(f"HTTP: {r.status_code}")

        if r.status_code != 200:
            print(f"Failed - HTTP {r.status_code}")
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = "V3_Failed"
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Extract
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            unique_rooms = list(set(rooms))[:10]
            print(f"  Rooms: {unique_rooms}")

        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 2000][:15]
            print(f"  Capacities: {caps}")

        # Phone
        phone = None
        for pattern in [r'0\d-\d{3,4}-\d{3,4}', r'\+886-[\d-]+']:
            match = re.search(pattern, page_text)
            if match:
                phone = match.group()
                break

        if phone:
            print(f"  Phone: {phone}")
            venue['contact']['phone'] = phone

        # Email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        if email_match:
            email = email_match.group()
            if 'noreply' not in email.lower():
                print(f"  Email: {email}")
                venue['contact']['email'] = email

        # Build room data
        rooms_data = []
        if capacities:
            caps_int = [int(c) for c in capacities if 5 <= int(c) <= 2000]
            if caps_int:
                max_cap = max(caps_int)
                rooms_data.append({
                    'name': 'Meeting Room',
                    'capacity': {'theater': max_cap, 'banquet': int(max_cap * 0.8)},
                    'source': 'html_taichung_20260327'
                })

        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # Quality
        quality = 35
        if venue.get('contact', {}).get('phone'):
            quality += 10
        if venue.get('contact', {}).get('email'):
            quality += 10
        if venue.get('rooms'):
            quality += len(venue['rooms']) * 8

        venue['metadata']['qualityScore'] = min(quality, 100)
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Taichung"
        venue['verified'] = False

        print(f"  Quality: {venue['metadata']['qualityScore']}")
        print("  SUCCESS!")
        success += 1

    except Exception as e:
        print(f"  ERROR: {e}")
        continue

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("COMPLETE")
print("=" * 100)
print(f"Processed: 3")
print(f"Success: {success}")
print(f"Total venues: {len(venues)}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
