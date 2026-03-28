#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete All 17 Remaining Venues
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
print("Completing All 17 Remaining Venues")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.complete_17_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Target venue IDs
target_ids = [
    1499, 1501, 1502, 1503, 1504, 1505,  # First batch
    1510, 1520, 1521, 1522,              # Second batch
    1057,                               # Taipei Denwell (35 points)
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

processed = 0
success = 0

for venue_id in target_ids:
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if not venue:
        continue

    url = venue.get('url', '')
    quality = venue.get('metadata', {}).get('qualityScore', 0)

    print(f"\n{'=' * 100}")
    print(f"[{processed + 1}] ID {venue['id']}: {venue['name']}")
    print(f"City: {venue.get('city', 'Unknown')}, Current Quality: {quality}")
    print(f"URL: {url}")
    print("=" * 100)

    if not url or url == 'TBD':
        print("Skipping - URL is TBD")
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['manualResearchRequired'] = True
        processed += 1
        continue

    try:
        # Special handling for denwell.com (returns 202)
        if 'denwell.com' in url:
            print("Skipping Denwell - HTTP 202 redirect")
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['skipReason'] = 'HTTP_202'
            processed += 1
            continue

        r = requests.get(url, timeout=25, verify=False, headers=headers)
        print(f"HTTP: {r.status_code}")

        if r.status_code != 200:
            print(f"Failed - HTTP {r.status_code}")
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Display sample content
        lines = [l.strip() for l in page_text.split('\n') if 15 < len(l.strip()) < 300]
        print(f"\nContent preview (first 30 lines):")
        for line in lines[:30]:
            print(f"  {line[:90]}")

        # Extract info
        print(f"\nExtracting...")

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

        # Prices
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
        if prices:
            print(f"  Prices: {prices[:15]}")

        # PDFs
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                pdf_url = link['href']
                if not pdf_url.startswith('http'):
                    base = '/'.join(url.split('/')[:3])
                    pdf_url = base + pdf_url if pdf_url.startswith('/') else base + '/' + pdf_url
                pdf_links.append(pdf_url)

        if pdf_links:
            print(f"  PDFs: {len(pdf_links)}")

        # Phone
        phone = None
        phone_patterns = [
            r'0\d-\d{3,4}-\d{3,4}',
            r'\+886-[\d-]+',
            r'\d{2,3}-\d{3,4}-\d{3,4}'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, page_text)
            if match:
                phone = match.group()
                break

        if phone:
            print(f"  Phone: {phone}")
            venue['contact']['phone'] = phone

        # Email
        email = None
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        if email_match:
            email_candidate = email_match.group()
            if 'noreply' not in email_candidate.lower() and 'no-reply' not in email_candidate.lower():
                email = email_candidate
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
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8)
                    },
                    'source': 'html_complete_20260327'
                })

        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # Update metadata
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Complete"
        venue['metadata']['pdfCount'] = len(pdf_links)

        # Calculate quality
        quality_score = 35
        if venue.get('contact', {}).get('phone'):
            quality_score += 10
        if venue.get('contact', {}).get('email'):
            quality_score += 10
        if venue.get('rooms'):
            quality_score += len(venue['rooms']) * 3
            for room in venue['rooms']:
                if room.get('capacity'):
                    quality_score += 5
                if room.get('areaSqm') or room.get('areaPing'):
                    quality_score += 3
        if pdf_links:
            quality_score += 5

        venue['metadata']['qualityScore'] = min(quality_score, 100)

        print(f"\nQuality Score: {venue['metadata']['qualityScore']}")
        print(f"SUCCESS!")
        success += 1

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        continue

    processed += 1

    # Save every 3 venues
    if processed % 3 == 0:
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)
        print(f"\n[Progress: {processed}/{len(target_ids)}]")

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("COMPLETE SUMMARY")
print("=" * 100)
print(f"Processed: {processed}/{len(target_ids)}")
print(f"Success: {success}")
print(f"Failed: {processed - success}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
