#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
處理所有剩餘場地 - 最終完整爬取
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
print("Processing All Remaining Venues - Final Complete Scraping")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.final_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Get all venues that need processing (quality <= 65 or TBD URLs)
target_venues = []
for venue in venues:
    quality = venue.get('metadata', {}).get('qualityScore', 0)
    url = venue.get('url', '')

    # Include if:
    # 1. Quality <= 65 (needs improvement)
    # 2. URL is TBD or missing
    # 3. Has URL but quality is low
    if quality <= 65 or url == 'TBD' or not url:
        target_venues.append({
            'id': venue['id'],
            'name': venue['name'],
            'city': venue.get('city', 'Unknown'),
            'url': url,
            'quality': quality
        })

# Sort by quality (lowest first)
target_venues.sort(key=lambda x: x['quality'])

print(f"Found {len(target_venues)} venues to process\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

processed_count = 0
success_count = 0

for i, target in enumerate(target_venues, 1):
    venue = next((v for v in venues if v['id'] == target['id']), None)
    if not venue:
        continue

    print(f"\n{'=' * 100}")
    print(f"[{i}/{len(target_venues)}] ID {target['id']}: {target['name']}")
    print(f"City: {target['city']}, Current Quality: {target['quality']}")
    print(f"URL: {target['url']}")
    print("=" * 100)

    url = target['url']

    # Skip if URL is TBD
    if url == 'TBD' or not url:
        print("Skipping - URL is TBD or empty")
        # Update metadata
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Manual_Required"
        venue['metadata']['manualResearchRequired'] = True
        continue

    try:
        # Fetch website
        print(f"Fetching {url}...")
        r = requests.get(url, timeout=20, verify=False, headers=headers)
        print(f"HTTP Status: {r.status_code}")

        if r.status_code != 200:
            print(f"Failed - HTTP {r.status_code}")
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Extract key information
        print(f"Extracting information...")

        # Meeting rooms
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            unique_rooms = list(set(rooms))[:15]
            print(f"  Rooms: {unique_rooms}")

        # Capacity
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 2000][:20]
            print(f"  Capacities: {caps}")

        # Area
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        if areas:
            print(f"  Areas: {areas[:20]}")

        # Prices
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
        if prices:
            print(f"  Prices: {prices[:20]}")

        # PDF links
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                pdf_url = link['href']
                if not pdf_url.startswith('http'):
                    base = '/'.join(url.split('/')[:3])
                    pdf_url = base + pdf_url if pdf_url.startswith('/') else base + '/' + pdf_url
                pdf_links.append(pdf_url)

        if pdf_links:
            print(f"  PDFs: {len(pdf_links)} found")

        # Contact info
        phone = None
        phone_patterns = [
            r'0\d-\d{3,4}-\d{3,4}',
            r'\+886-\d[\d-]{7,9}',
            r'\+886\s?\d[\d\s-]{7,9}',
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
                    'source': 'html_final_20260327'
                })

        # Update venue
        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # Metadata
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Final"
        venue['metadata']['pdfCount'] = len(pdf_links)

        # Calculate quality score
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

        print(f"Quality Score: {venue['metadata']['qualityScore']}")
        print(f"SUCCESS: Updated venue {target['id']}")
        success_count += 1

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        continue

    processed_count += 1

    # Save progress every 5 venues
    if i % 5 == 0:
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)
        print(f"\n[Progress saved: {i}/{len(target_venues)}]")

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("FINAL SUMMARY")
print("=" * 100)
print(f"Total processed: {processed_count}/{len(target_venues)}")
print(f"Successful: {success_count}")
print(f"Failed: {processed_count - success_count}")
print(f"\nBackup: {backup_file}")
print(f"\nDONE!")
