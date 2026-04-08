#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update URLs and Retry HTTP 202 Venues
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
print("Update URLs and Retry HTTP 202 Venues")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.url_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Update URLs provided by user
url_updates = {
    1523: ('好運來洲際宴展中心', 'http://www.lilo-park.com.tw/edcontent.php?lang=tw&tb=8'),
    1524: ('林皇宮花園', 'https://www.linweddinggarden.com/download.php'),
}

for vid, (name, url) in url_updates.items():
    venue = next((v for v in venues if v['id'] == vid), None)
    if venue:
        print(f"Updating ID {vid}: {name}")
        print(f"  Old URL: {venue.get('url', 'N/A')}")
        print(f"  New URL: {url}")
        venue['url'] = url
        print(f"  Updated!\n")

# Venues to retry (HTTP 202 or DNS fail)
retry_venues = [
    (1501, '安順文旅', 'https://www.amforahotel.com.tw/ambanew/'),
    (1502, '台灣晶豐酒店', 'https://www.chinapalace.com.tw/'),
    (1503, '裕珍花園酒店', 'https://www.yuzenhotel.com.tw/'),
    (1504, '高雄國際會議中心', 'https://www.kicc.com.tw/'),
    (1505, '漢來大飯店', 'https://www.hanlai-hotel.com.tw/'),
    (1510, '新莊典華', 'https://www.denwell.com/'),
    (1057, '台北典華', 'https://www.denwell.com/'),
    (1520, '寶麗金婚宴會館 市政店', 'https://www.weddings.tw/'),
    (1521, '寶麗金婚宴會館 崇德店', 'https://www.weddings.tw/'),
    (1522, '天圓地方婚宴會館', 'https://xycuisinetw.com/'),
    (1523, '好運來洲際宴展中心', 'http://www.lilo-park.com.tw/edcontent.php?lang=tw&tb=8'),
    (1524, '林皇宮花園', 'https://www.linweddinggarden.com/download.php'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'http://www.google.com'
}

processed = 0
success = 0

for vid, name, url in retry_venues:
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

        if r.status_code not in [200, 202]:
            print(f"Failed - HTTP {r.status_code}")
            continue

        # Even if 202, try to parse content
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Display preview
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 300]
        print(f"\nContent preview (first 40 lines):")
        for line in lines[:40]:
            print(f"  {line[:90]}")

        # Extract key info
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
            caps_int = [int(c) for c in capacities if 5 <= int(c) <= 2000]
            if caps_int:
                max_cap = max(caps_int)
                rooms_data.append({
                    'name': 'Meeting Room',
                    'capacity': {
                        'theater': max_cap,
                        'banquet': int(max_cap * 0.8)
                    },
                    'source': 'html_retry_20260327'
                })

        if rooms_data:
            venue['rooms'] = rooms_data
            venue['capacity'] = rooms_data[0]['capacity']

        # Update metadata
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = "V3_Retry"
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
        print(f"\n[Progress: {processed}/{len(retry_venues)} saved]")

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("RETRY COMPLETE")
print("=" * 100)
print(f"Processed: {processed}")
print(f"Success: {success}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
