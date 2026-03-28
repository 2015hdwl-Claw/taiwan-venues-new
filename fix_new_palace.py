#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix 新天地餐飲集團 URL and Scrape
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
print("Fix 新天地餐飲集團 URL and Scrape")
print("=" * 100)

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.newpalace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Find venue 1538
venue = next((v for v in venues if v['id'] == 1538), None)
if venue:
    old_url = venue.get('url', '')
    new_url = 'https://www.newpalace.com.tw/'
    venue['url'] = new_url
    print(f"Updated ID 1538: 新天地餐飲集團")
    print(f"  Old URL: {old_url}")
    print(f"  New URL: {new_url}\n")

    # Scrape
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    try:
        r = requests.get(new_url, timeout=30, verify=False, headers=headers, allow_redirects=True)
        print(f"HTTP: {r.status_code}")
        print(f"Final URL: {r.url}\n")

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text()

            # Preview (limited to avoid encoding errors)
            lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 300]
            print(f"Content preview: {len(lines)} lines found")

            # Extract
            print("\nExtracting...")

            # Rooms
            rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
            if rooms:
                unique_rooms = list(set(rooms))[:15]
                print(f"  Rooms: {unique_rooms}")

            # Capacities
            capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
            if capacities:
                caps = [int(c) for c in capacities if 5 <= int(c) <= 2000][:20]
                print(f"  Capacities: {caps}")

            # Areas
            areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
            if areas:
                print(f"  Areas: {areas[:15]}")

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
                        'name': 'Banquet Hall',
                        'capacity': {
                            'theater': max_cap,
                            'banquet': int(max_cap * 0.8),
                            'classroom': int(max_cap * 0.5)
                        },
                        'source': 'html_newpalace_20260327'
                    })

            if rooms_data:
                venue['rooms'] = rooms_data
                venue['capacity'] = rooms_data[0]['capacity']

            # Update metadata
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = "V3_NewPalace"

            # Calculate quality
            quality = 35
            if venue.get('contact', {}).get('phone'):
                quality += 10
            if venue.get('contact', {}).get('email'):
                quality += 10
            if venue.get('rooms'):
                quality += len(venue['rooms']) * 8

            venue['metadata']['qualityScore'] = min(quality, 100)
            venue['verified'] = False

            print(f"\nQuality Score: {venue['metadata']['qualityScore']}")
            print("SUCCESS!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Save
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

else:
    print("Venue 1538 not found!")

print(f"\n{'=' * 100}")
print("COMPLETE")
print("=" * 100)
print(f"\nBackup: {backup_file}")
print("\nDONE!")
