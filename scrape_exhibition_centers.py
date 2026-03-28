#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Scraping for Exhibition Centers + Retry Failed Venues
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
print("Complete Scraping: Exhibition Centers + Retry Failed Venues")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.exhibition_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Venues to process (5 new + 2 retry + 1505 漢來大飯店 try alternative)
venues_to_process = [
    (1532, '新北市工商展覽中心', 'http://www.tcwtc.com.tw/'),
    (1533, '臺中國際會展中心 (水湳)', 'https://www.ticec.com.tw/'),
    (1534, '臺中國際展覽館 (烏日)', 'https://www.tc-iec.com/'),
    (1535, '高雄展覽館 (KEC)', 'https://www.kecc.com.tw/'),
    (1536, '高雄國際會議中心 (ICCK)', 'https://www.icck.com.tw/'),
    (1505, '漢來大飯店', 'https://www.hilai.com.tw/'),  # Try alternative URL
    (1510, '新莊典華', 'https://www.denwell.com/service-xinzhuang-venue-introduction/'),  # Retry
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

processed = 0
success = 0

for vid, name, url in venues_to_process:
    venue = next((v for v in venues if v['id'] == vid), None)
    if not venue:
        print(f"Venue ID {vid} not found!")
        continue

    print(f"\n{'=' * 100}")
    print(f"[{processed + 1}] ID {vid}: {name}")
    print(f"URL: {url}")
    print("=" * 100)

    try:
        r = requests.get(url, timeout=30, verify=False, headers=headers, allow_redirects=True)
        print(f"HTTP: {r.status_code}")
        print(f"Final URL: {r.url}")

        if r.status_code != 200:
            print(f"Failed - HTTP {r.status_code}")
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = "V3_Failed"
            processed += 1
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Display preview
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 300]
        print(f"\nContent preview (first 50 lines):")
        for line in lines[:50]:
            print(f"  {line[:100]}")

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
            caps = [int(c) for c in capacities if 5 <= int(c) <= 5000][:25]
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
            print(f"  PDFs: {len(pdf_links)} found")
            for pdf_url in pdf_links[:3]:
                print(f"    {pdf_url}")

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
            if 'noreply' not in email_candidate.lower() and 'no-reply' not in email_candidate.lower():
                print(f"  Email: {email_candidate}")
                venue['contact']['email'] = email_candidate

        # Build room data
        rooms_data = []
        if capacities:
            caps_int = [int(c) for c in capacities if 5 <= int(c) <= 5000]
            if caps_int:
                max_cap = max(caps_int)
                min_cap = min(caps_int)

                rooms_data.append({
                    'name': 'Exhibition/Conference Hall',
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8),
                        'classroom': int(max_cap * 0.5)
                    },
                    'source': 'html_exhibition_20260327'
                })

        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # Update metadata
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Exhibition"
        venue['metadata']['pdfCount'] = len(pdf_links)

        # Calculate quality
        quality = 35
        if venue.get('contact', {}).get('phone'):
            quality += 10
        if venue.get('contact', {}).get('email'):
            quality += 10
        if venue.get('rooms'):
            quality += len(venue['rooms']) * 8
        if pdf_links:
            quality += 5

        venue['metadata']['qualityScore'] = min(quality, 100)
        venue['verified'] = False

        print(f"\nQuality Score: {venue['metadata']['qualityScore']}")
        print(f"SUCCESS!")
        success += 1

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        continue

    processed += 1

    # Save every 2 venues
    if processed % 2 == 0:
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)
        print(f"\n[Progress: {processed}/{len(venues_to_process)} saved]")

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("COMPLETE")
print("=" * 100)
print(f"Processed: {processed}")
print(f"Success: {success}")
print(f"Failed: {processed - success}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
