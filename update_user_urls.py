#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update User-Provided URLs and Complete Scraping
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
print("Update User URLs and Complete Scraping")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.user_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# User-provided URL updates
url_updates = {
    1528: ('漢來國際宴會廳', 'https://www.grand-hilai.com/space/conference/'),
    1504: ('高雄國際會議中心', 'https://khhplaza.com.tw/conferenence-area/'),
    1527: ('義大世界會議中心', 'https://www.edaroyal.com.tw/halls/'),  # Updated from 義大皇家酒店
    1510: ('新莊典華', 'https://www.denwell.com/service-xinzhuang-venue-introduction/'),
    1522: ('天圓地方婚宴會館', 'https://www.tianyuan.com.tw/paper/other_select_index.php?title_id=7925&group_id=378'),
    1525: ('潮港城宴會廳 南屯店', 'https://www.ckcchao.com/rental'),  # Already has this
    1530: ('富苑喜宴會館', 'TBD'),  # No URL provided yet
    1526: ('蓮潭國際會館', 'TBD'),  # No URL provided yet
    1529: ('福客來南北樓', 'TBD'),  # No URL provided yet
}

# Also update ID 1505 if needed
url_updates[1505] = ('漢來大飯店', 'https://www.hanlai-hotel.com.tw/')  # Try this

# New venue - 御元花園酒店
new_venue = {
    'id': 1531,
    'name': '御元花園酒店',
    'venueType': '飯店場地',
    'city': '高雄市',
    'address': '高雄市',
    'url': 'https://www.windsortaiwan.com/tw/project',
    'contact': {'phone': 'TBD', 'email': 'TBD'},
    'verified': False,
    'metadata': {
        'addedAt': '2026-03-27',
        'note': 'User provided URL'
    }
}

# Add new venue
venues.append(new_venue)
print(f"Added new venue: ID 1531 - 御元花園酒店\n")

# Update URLs
for vid, (name, url) in url_updates.items():
    if url == 'TBD':
        continue

    venue = next((v for v in venues if v['id'] == vid), None)
    if venue:
        print(f"Updating ID {vid}: {name}")
        print(f"  New URL: {url}")
        venue['url'] = url
        print(f"  Updated!\n")

# Venues to process
venues_to_process = [
    (1504, '高雄國際會議中心', 'https://khhplaza.com.tw/conferenence-area/'),
    (1505, '漢來大飯店', 'https://www.hanlai-hotel.com.tw/'),
    (1510, '新莊典華', 'https://www.denwell.com/service-xinzhuang-venue-introduction/'),
    (1522, '天圓地方婚宴會館', 'https://www.tianyuan.com.tw/paper/other_select_index.php?title_id=7925&group_id=378'),
    (1527, '義大世界會議中心', 'https://www.edaroyal.com.tw/halls/'),
    (1528, '漢來國際宴會廳', 'https://www.grand-hilai.com/space/conference/'),
    (1531, '御元花園酒店', 'https://www.windsortaiwan.com/tw/project'),
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
                    'name': 'Conference Room',
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8),
                        'classroom': int(max_cap * 0.5)
                    },
                    'source': 'html_user_urls_20260327'
                })

        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # Update metadata
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_UserURLs"
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
print(f"Added 1 new venue: 御元花園酒店")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
