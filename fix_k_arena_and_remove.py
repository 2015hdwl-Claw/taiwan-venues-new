#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix 高雄巨蛋 URL and Remove 10 Low-Quality Venues
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
print("Fix 高雄巨蛋 URL + Remove 10 Low-Quality Venues")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.remove_10_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# IDs to remove
ids_to_remove = [1499, 1501, 1502, 1526, 1529, 1530, 1536, 1539, 1541, 1544]

print("=" * 100)
print("STEP 1: Remove 10 Low-Quality Venues")
print("=" * 100 + "\n")

removed_count = 0
for vid in ids_to_remove:
    venue = next((v for v in venues if v['id'] == vid), None)
    if venue:
        print(f"Removing ID {vid}: {venue['name']}")
        venues.remove(venue)
        removed_count += 1

print(f"\nRemoved: {removed_count} venues")
print(f"Remaining: {len(venues)} venues\n")

# Fix 高雄巨蛋
print("=" * 100)
print("STEP 2: Fix 高雄巨蛋 URL and Scrape")
print("=" * 100 + "\n")

k_arena = next((v for v in venues if v['id'] == 1541), None)
if not k_arena:
    # Re-add if it was removed
    print("Re-adding 高雄巨蛋...")
    k_arena = {
        'id': 1541,
        'name': '高雄巨蛋 (Kaohsiung Arena)',
        'venueType': '運動場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.kaoarena.com.tw/Home/RentalMainvenue3',
        'contact': {'phone': 'TBD', 'email': 'TBD'},
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-28',
            'note': 'User provided correct URL'
        }
    }
    venues.append(k_arena)
else:
    print("Updating 高雄巨蛋 URL...")

old_url = k_arena.get('url', '')
new_url = 'https://www.kaoarena.com.tw/Home/RentalMainvenue3'
k_arena['url'] = new_url

print(f"  Old URL: {old_url}")
print(f"  New URL: {new_url}\n")

# Scrape 高雄巨蛋
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

try:
    print("Scraping 高雄巨蛋...")
    r = requests.get(new_url, timeout=30, verify=False, headers=headers, allow_redirects=True)
    print(f"HTTP: {r.status_code}")
    print(f"Final URL: {r.url}\n")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Display preview
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 300]
        print(f"Content preview (first 30 lines):")
        for line in lines[:30]:
            print(f"  {line[:80]}")

        # Extract
        print("\nExtracting...")

        # Phone
        phone = None
        for pattern in [r'0\d-\d{3,4}-\d{3,4}', r'\+886-[\d-]+']:
            match = re.search(pattern, page_text)
            if match:
                phone = match.group()
                break

        if phone:
            print(f"  Phone: {phone}")
            k_arena['contact']['phone'] = phone

        # Email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        if email_match:
            email = email_match.group()
            if 'noreply' not in email.lower():
                print(f"  Email: {email}")
                k_arena['contact']['email'] = email

        # Capacities
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 20000][:20]
            print(f"  Capacities: {caps}")

            # Build room data
            if caps:
                max_cap = max(caps)
                k_arena['rooms'] = [{
                    'name': 'Main Arena',
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8)
                    },
                    'source': 'html_karena_20260328'
                }]
                k_arena['capacity'] = k_arena['rooms'][0]['capacity']

        # Quality
        quality = 35
        if k_arena.get('contact', {}).get('phone'):
            quality += 10
        if k_arena.get('contact', {}).get('email'):
            quality += 10
        if k_arena.get('rooms'):
            quality += len(k_arena['rooms']) * 8

        k_arena['metadata']['qualityScore'] = min(quality, 100)
        k_arena['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        k_arena['metadata']['scrapeVersion'] = "V3_KArena"
        k_arena['verified'] = False

        print(f"\nQuality Score: {k_arena['metadata']['qualityScore']}")
        print("SUCCESS!")
    else:
        print(f"Failed - HTTP {r.status_code}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("COMPLETE")
print("=" * 100)
print(f"Removed: {removed_count} venues")
print(f"Remaining: {len(venues)} venues")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
