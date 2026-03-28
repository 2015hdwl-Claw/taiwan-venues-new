#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Existing Venues + Add 6 New Kaohsiung Venues
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("Fix Existing Venues + Add 6 New Kaohsiung Venues")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.fix_add_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Fix existing venues
fixes = [
    {
        'id': 1503,
        'old_name': '裕珍花園酒店',
        'new_name': '裕元花園酒店',
        'old_url': 'https://www.yuzenhotel.com.tw/',
        'new_url': 'https://www.windsortaiwan.com/'
    },
    {
        'id': 1505,
        'old_name': '漢來大飯店',
        'new_name': '漢來大飯店',
        'old_url': 'https://www.hanlai-hotel.com.tw/',
        'new_url': 'https://www.grand-hilai.com/'
    },
    {
        'id': 1539,
        'old_name': '震大金鬱金香酒店 (Zenda Gold Tulip)',
        'new_name': '震大金鬱金香酒店 (Zenda Gold Tulip)',
        'old_url': 'https://www.goldentulip-zendahotel.com/',
        'new_url': 'https://www.goldentulip-zendahotel.com/'
    },
]

print("=" * 100)
print("STEP 1: Fix Existing Venues")
print("=" * 100 + "\n")

for fix in fixes:
    venue = next((v for v in venues if v['id'] == fix['id']), None)
    if venue:
        print(f"ID {fix['id']}: {venue['name']}")
        print(f"  Old URL: {venue.get('url', 'N/A')}")

        if fix['old_name'] != fix['new_name']:
            venue['name'] = fix['new_name']
            print(f"  Name: {fix['old_name']} → {fix['new_name']}")

        venue['url'] = fix['new_url']
        print(f"  New URL: {fix['new_url']}")
        print()

# Add new venues
new_venues_data = [
    {
        'id': 1540,
        'name': '高雄展覽館 (KEC)',
        'venueType': '展覽館',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.kecc.com.tw/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-28',
            'note': 'User provided URL - Exhibition center (already exists as 1535, skip if duplicate)'
        }
    },
    {
        'id': 1541,
        'name': '高雄巨蛋 (Kaohsiung Arena)',
        'venueType': '運動場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'http://www.k-arena.com.tw/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-28',
            'note': 'User provided URL'
        }
    },
    {
        'id': 1542,
        'name': '高雄萬豪酒店 (Kaohsiung Marriott)',
        'venueType': '飯店場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.khm.com.tw/zh-TW/banquet',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-28',
            'note': 'User provided URL'
        }
    },
    {
        'id': 1543,
        'name': '衛武營國家藝術文化中心',
        'venueType': '展演場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.npac-weiwuying.org/space',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-28',
            'note': 'User provided URL - Venue rental'
        }
    },
    {
        'id': 1544,
        'name': '高雄流行音樂中心',
        'venueType': '展演場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://khmc.org.tw/rental/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-28',
            'note': 'User provided URL - Venue rental'
        }
    },
    {
        'id': 1545,
        'name': '承億酒店 (TAI Urban Resort)',
        'venueType': '飯店場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.taiurbanresort.com.tw/meeting-banquet/',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-28',
            'note': 'User provided URL'
        }
    },
]

print("=" * 100)
print("STEP 2: Add New Venues")
print("=" * 100 + "\n")

# Check if KEC already exists
kec_exists = any(v['id'] == 1535 for v in venues)
if kec_exists:
    print("KEC (ID 1535) already exists, skipping duplicate...")
    new_venues_data = [v for v in new_venues_data if v['id'] != 1540]

for venue_data in new_venues_data:
    venues.append(venue_data)
    print(f"Added: ID {venue_data['id']} - {venue_data['name']}")

# Save after fixes and additions
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\nTotal venues: {len(venues)}")

# Now scrape fixed and new venues
print("\n" + "=" * 100)
print("STEP 3: Scrape Fixed + New Venues")
print("=" * 100 + "\n")

venues_to_scrape = [
    (1503, '裕元花園酒店', 'https://www.windsortaiwan.com/'),
    (1505, '漢來大飯店', 'https://www.grand-hilai.com/'),
    (1539, '震大金鬱金香酒店', 'https://www.goldentulip-zendahotel.com/'),
    (1541, '高雄巨蛋', 'http://www.k-arena.com.tw/'),
    (1542, '高雄萬豪酒店', 'https://www.khm.com.tw/zh-TW/banquet'),
    (1543, '衛武營國家藝術文化中心', 'https://www.npac-weiwuying.org/space'),
    (1544, '高雄流行音樂中心', 'https://khmc.org.tw/rental/'),
    (1545, '承億酒店', 'https://www.taiurbanresort.com.tw/meeting-banquet/'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

processed = 0
success = 0

for vid, name, url in venues_to_scrape:
    venue = next((v for v in venues if v['id'] == vid), None)
    if not venue:
        print(f"Venue ID {vid} not found!")
        continue

    print(f"\n[{processed + 1}/{len(venues_to_scrape)}] ID {vid}: {name}")
    print(f"URL: {url}")

    try:
        r = requests.get(url, timeout=30, verify=False, headers=headers, allow_redirects=True)
        print(f"HTTP: {r.status_code}")

        if r.status_code != 200:
            print(f"Failed - HTTP {r.status_code}")
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = "V3_Failed"
            processed += 1
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Extract
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            unique_rooms = list(set(rooms))[:15]
            print(f"  Rooms: {unique_rooms}")

        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 5000][:20]
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
            caps_int = [int(c) for c in capacities if 5 <= int(c) <= 5000]
            if caps_int:
                max_cap = max(caps_int)
                rooms_data.append({
                    'name': 'Meeting Room',
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8),
                        'classroom': int(max_cap * 0.5)
                    },
                    'source': 'html_fix_20260328'
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
        venue['metadata']['scrapeVersion'] = "V3_Fixed"
        venue['verified'] = False

        print(f"  Quality: {venue['metadata']['qualityScore']}")
        print("  SUCCESS!")
        success += 1

    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    processed += 1

    # Save every 3 venues
    if processed % 3 == 0:
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)
        print(f"\n[Progress: {processed}/{len(venues_to_scrape)} saved]")

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("COMPLETE")
print("=" * 100)
print(f"Processed: {processed}")
print(f"Success: {success}")
print(f"Total venues: {len(venues)}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
