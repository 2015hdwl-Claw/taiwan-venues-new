#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Remaining Venues - Stable Version
One venue at a time
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import re
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("Stable Venue Completion - One by One")
print("=" * 100)

# Read venues
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.stable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Venues to process (with URLs)
venues_to_process = [
    (1501, '安順文旅', 'https://www.amforahotel.com.tw/ambanew/'),
    (1502, '台灣晶豐酒店', 'https://www.chinapalace.com.tw/'),
    (1503, '裕珍花園酒店', 'https://www.yuzenhotel.com.tw/'),
    (1504, '高雄國際會議中心', 'https://www.kicc.com.tw/'),
    (1505, '漢來大飯店', 'https://www.hanlai-hotel.com.tw/'),
    (1520, '寶麗金婚宴會館 市政店', 'https://www.weddings.tw/'),
    (1521, '寶麗金婚宴會館 崇德店', 'https://www.weddings.tw/'),
    (1522, '天圓地方婚宴會館', 'https://xycuisinetw.com/'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

for i, (vid, name, url) in enumerate(venues_to_process, 1):
    print(f"\n{'=' * 100}")
    print(f"[{i}/{len(venues_to_process)}] ID {vid}: {name}")
    print(f"URL: {url}")
    print("=" * 100)

    venue = next((v for v in venues if v['id'] == vid), None)
    if not venue:
        print("Venue not found!")
        continue

    try:
        r = requests.get(url, timeout=25, verify=False, headers=headers)
        print(f"HTTP: {r.status_code}")

        if r.status_code != 200:
            print(f"Failed - HTTP {r.status_code}")
            # Update metadata
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = "V3_Failed"
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Extract key info
        print("Extracting...")

        # Rooms
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            print(f"  Rooms: {list(set(rooms))[:10]}")

        # Capacities
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 2000][:15]
            print(f"  Capacities: {caps}")

        # Phone
        phone = None
        for pattern in [r'0\d-\d{3,4}-\d{3,4}', r'\+886-[\d-]+', r'\d{2,3}-\d{3,4}-\d{3,4}']:
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
            email_candidate = email_match.group()
            if 'noreply' not in email_candidate.lower():
                print(f"  Email: {email_candidate}")
                venue['contact']['email'] = email_candidate

        # Build room data
        rooms_data = []
        if capacities:
            caps_int = [int(c) for c in capacities if 5 <= int(c) <= 2000]
            if caps_int:
                max_cap = max(caps_int)
                rooms_data.append({
                    'name': 'Meeting Room',
                    'capacity': {'theater': max_cap, 'banquet': int(max_cap * 0.8)},
                    'source': 'html_stable_20260327'
                })

        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # Quality score
        quality = 35
        if venue.get('contact', {}).get('phone'):
            quality += 10
        if venue.get('contact', {}).get('email'):
            quality += 10
        if venue.get('rooms'):
            quality += len(venue['rooms']) * 8

        venue['metadata']['qualityScore'] = min(quality, 100)
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Stable"

        print(f"Quality: {venue['metadata']['qualityScore']}")
        print("SUCCESS!")

        # Save after each venue
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"ERROR: {e}")
        continue

print(f"\n{'=' * 100}")
print("Complete!")
print(f"Backup: {backup_file}")
