#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry Failed Venues with Corrected URLs
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
print("Retry Failed Venues with Corrected URLs")
print("=" * 100)

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.retry_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Corrected URLs
url_fixes = [
    {
        'id': 1541,
        'name': '高雄巨蛋',
        'old_url': 'http://www.k-arena.com.tw/',
        'new_url': 'https://kaohsiungarena.com.tw/'  # Try without www
    },
    {
        'id': 1542,
        'name': '高雄萬豪酒店',
        'old_url': 'https://www.khm.com.tw/zh-TW/banquet',
        'new_url': 'https://www.khm.com.tw/'  # Main page
    },
    {
        'id': 1545,
        'name': '承億酒店',
        'old_url': 'https://www.taiurbanresort.com.tw/meeting-banquet/',
        'new_url': 'https://www.taiurbanresort.com.tw/'  # Main page
    },
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

success = 0

for fix in url_fixes:
    venue = next((v for v in venues if v['id'] == fix['id']), None)
    if not venue:
        continue

    print(f"\n{'=' * 100}")
    print(f"ID {fix['id']}: {fix['name']}")
    print(f"Old URL: {fix['old_url']}")
    print(f"New URL: {fix['new_url']}")
    print("=" * 100)

    # Update URL
    venue['url'] = fix['new_url']

    try:
        r = requests.get(fix['new_url'], timeout=30, verify=False, headers=headers, allow_redirects=True)
        print(f"HTTP: {r.status_code}")
        print(f"Final URL: {r.url}")

        if r.status_code != 200:
            print(f"Failed - HTTP {r.status_code}")
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Extract
        print("\nExtracting...")

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
                    'source': 'html_retry_20260328'
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
        venue['metadata']['scrapeVersion'] = "V3_RetryURL"
        venue['verified'] = False

        print(f"\nQuality Score: {venue['metadata']['qualityScore']}")
        print("SUCCESS!")
        success += 1

    except Exception as e:
        print(f"ERROR: {e}")
        continue

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("COMPLETE")
print("=" * 100)
print(f"Success: {success}/{len(url_fixes)}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
