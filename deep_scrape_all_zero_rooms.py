#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Scraping for All Venues with 0 Rooms
Multi-page discovery and complete data extraction
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import re
import sys
from urllib.parse import urljoin, urlparse
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("Deep Scraping: All Venues with 0 Rooms")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.deep_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Find venues with 0 rooms
targets = []
for v in venues:
    if not v.get('rooms') or len(v.get('rooms', [])) == 0:
        if v.get('url') and v.get('url') != 'TBD':
            targets.append({
                'id': v['id'],
                'name': v['name'],
                'url': v['url'],
                'type': v.get('venueType', 'Unknown')
            })

print(f"Found {len(targets)} venues with 0 rooms (excluding TBD URLs)\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

processed = 0
success = 0

def extract_all_meeting_data(base_url, soup, page_text, venue):
    """Extract complete meeting room data from page"""
    rooms_data = []

    # Pattern 1: Explicit room cards/tables
    # Look for common patterns in Taiwanese hotel websites

    # Find room names with patterns like "宴會廳", "會議室", "Function Room"
    room_patterns = [
        r'([^\s]{2,8}[廳室樓層])(?:\s|[,，、\n])',
        r'([A-Z][a-z]+\s+(?:Room|Hall|Ballroom|Center))',
        r'(\d+[F樓]\s*[^\s]{2,6}[廳室])',
    ]

    room_names = set()
    for pattern in room_patterns:
        matches = re.findall(pattern, page_text)
        room_names.update(matches)

    # Clean up room names
    room_names = [name for name in room_names if len(name) >= 2 and len(name) <= 10]
    room_names = list(room_names)[:30]  # Limit to 30 rooms

    if room_names:
        print(f"  Found {len(room_names)} potential rooms")

    # Extract capacities
    capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
    caps_int = [int(c) for c in capacities if 5 <= int(c) <= 20000]

    # Extract areas
    areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)

    # Extract prices
    prices = re.findall(r'(\d+,?\d*)\s*元', page_text)

    # Extract dimensions
    dimensions = re.findall(r'(\d+\.?\d*)\s*[x×*]\s*(\d+\.?\d*)\s*[x×*]\s*(\d+\.?\d*)\s*[米m]', page_text)

    # Build room data
    if room_names:
        for i, room_name in enumerate(room_names):
            room_data = {
                'name': room_name,
                'capacity': {},
                'source': f'deep_scrape_{datetime.now().strftime("%Y%m%d")}'
            }

            # Assign capacity if available
            if caps_int:
                if i < len(caps_int):
                    cap = caps_int[i]
                else:
                    cap = max(caps_int) if caps_int else 100

                room_data['capacity'] = {
                    'theater': cap,
                    'banquet': int(cap * 0.8),
                    'classroom': int(cap * 0.5)
                }

            # Assign area if available
            if areas and i < len(areas):
                area_value, area_unit = areas[i]
                if area_unit in ['坪', '平方公尺', '㎡', '㎡²']:
                    if area_unit == '坪':
                        room_data['areaPing'] = float(area_value)
                        room_data['areaSqm'] = float(area_value) * 3.3058
                    else:
                        room_data['areaSqm'] = float(area_value)
                        room_data['areaPing'] = float(area_value) / 3.3058

            # Assign price if available
            if prices and i < len(prices):
                try:
                    room_data['price'] = int(prices[i].replace(',', ''))
                except:
                    pass

            rooms_data.append(room_data)

    # If no room names found but have capacities, create generic room
    elif caps_int:
        max_cap = max(caps_int)
        rooms_data.append({
            'name': '會議廳',
            'capacity': {
                'theater': max_cap,
                'banquet': int(max_cap * 0.8),
                'classroom': int(max_cap * 0.5)
            },
            'source': f'deep_scrape_{datetime.now().strftime("%Y%m%d")}'
        })

    return rooms_data

def discover_and_scrape_pages(base_url, venue):
    """Discover all relevant pages and scrape data"""
    all_room_data = []
    visited_urls = set()

    try:
        # Page 1: Main page
        print(f"\n[Page 1] Main page: {base_url}")
        r = requests.get(base_url, timeout=25, verify=False, headers=headers, allow_redirects=True)
        if r.status_code != 200:
            print(f"  Failed: HTTP {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()
        visited_urls.add(r.url)

        # Extract from main page
        main_rooms = extract_all_meeting_data(base_url, soup, page_text, venue)
        all_room_data.extend(main_rooms)
        print(f"  Extracted: {len(main_rooms)} rooms")

        # Page 2: Find meeting/banquet links
        print(f"\n[Page 2] Discovering meeting/conference pages...")

        meeting_links = []

        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True).lower()
            href_lower = href.lower()

            # Check for meeting/banquet keywords
            keywords = ['meeting', 'conference', 'banquet', 'mice', 'wedding',
                       '會議', '宴會', '婚宴', '活動', '會展', '場地']

            if any(kw in href_lower or kw in text for kw in keywords):
                # Convert to absolute URL
                if not href.startswith('http'):
                    absolute_url = urljoin(base_url, href)
                else:
                    absolute_url = href

                # Only follow links from same domain
                if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                    if absolute_url not in visited_urls:
                        meeting_links.append(absolute_url)

        # Deduplicate and limit
        meeting_links = list(dict.fromkeys(meeting_links))[:5]

        if meeting_links:
            print(f"  Found {len(meeting_links)} meeting-related links")

            for i, link_url in enumerate(meeting_links[:3], 1):  # Limit to 3 sub-pages
                print(f"\n[Page 2.{i}] {link_url}")
                try:
                    r2 = requests.get(link_url, timeout=20, verify=False, headers=headers)
                    if r2.status_code == 200:
                        soup2 = BeautifulSoup(r2.text, 'html.parser')
                        page_text2 = soup2.get_text()
                        visited_urls.add(r2.url)

                        sub_rooms = extract_all_meeting_data(link_url, soup2, page_text2, venue)
                        if sub_rooms:
                            all_room_data.extend(sub_rooms)
                            print(f"  Extracted: {len(sub_rooms)} additional rooms")
                except Exception as e:
                    print(f"  Error: {e}")
                    continue
        else:
            print(f"  No additional meeting pages found")

        # Page 3: Try common meeting page paths
        print(f"\n[Page 3] Trying common paths...")
        common_paths = [
            '/meeting',
            '/banquet',
            '/mice',
            '/conference',
            '/wedding',
            '/facility',
            '/space',
            '/zh-TW/meeting',
            '/zh-TW/banquet',
            '/tw/meeting',
        ]

        for path in common_paths[:3]:  # Try 3 paths
            try:
                test_url = urljoin(base_url, path)
                if test_url not in visited_urls:
                    print(f"  Trying: {test_url}")
                    r3 = requests.get(test_url, timeout=15, verify=False, headers=headers)
                    if r3.status_code == 200:
                        soup3 = BeautifulSoup(r3.text, 'html.parser')
                        page_text3 = soup3.get_text()

                        # Check if this page has room data
                        if '廳' in page_text3 or '室' in page_text3:
                            path_rooms = extract_all_meeting_data(test_url, soup3, page_text3, venue)
                            if path_rooms:
                                all_room_data.extend(path_rooms)
                                print(f"    Found: {len(path_rooms)} rooms")
            except:
                continue

        return all_room_data

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

# Process each venue
for target in targets:
    vid = target['id']
    venue = next((v for v in venues if v['id'] == vid), None)

    if not venue:
        continue

    print(f"\n{'=' * 100}")
    print(f"[{processed + 1}/{len(targets)}] ID {vid}: {target['name']}")
    print(f"Type: {target['type']}")
    print(f"URL: {target['url']}")
    print("=" * 100)

    try:
        # Deep scrape
        all_rooms = discover_and_scrape_pages(target['url'], venue)

        if all_rooms:
            # Deduplicate rooms by name
            unique_rooms = {}
            for room in all_rooms:
                room_name = room['name']
                if room_name not in unique_rooms:
                    unique_rooms[room_name] = room
                else:
                    # Merge data if room exists
                    existing = unique_rooms[room_name]
                    if not existing.get('capacity') and room.get('capacity'):
                        existing['capacity'] = room['capacity']

            rooms_list = list(unique_rooms.values())

            print(f"\n✓ Total unique rooms found: {len(rooms_list)}")

            # Update venue
            venue['rooms'] = rooms_list

            # Update overall capacity (use max)
            if rooms_list:
                max_cap = 0
                for room in rooms_list:
                    if room.get('capacity', {}).get('theater', 0) > max_cap:
                        max_cap = room['capacity']['theater']

                venue['capacity'] = {
                    'theater': max_cap,
                    'banquet': int(max_cap * 0.8),
                    'classroom': int(max_cap * 0.5)
                }

            # Update quality score
            quality = 35
            if venue.get('contact', {}).get('phone'):
                quality += 10
            if venue.get('contact', {}).get('email'):
                quality += 10
            if venue.get('rooms'):
                quality += len(venue['rooms']) * 5  # 5 points per room

            venue['metadata']['qualityScore'] = min(quality, 100)
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = "V4_DeepScrape"
            venue['metadata']['roomCount'] = len(rooms_list)
            venue['verified'] = False

            print(f"Quality Score: {venue['metadata']['qualityScore']}")
            print("SUCCESS!")
            success += 1
        else:
            print("\n✗ No rooms found")
            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = "V4_DeepScrape_NoRooms"

    except Exception as e:
        print(f"ERROR: {e}")
        continue

    processed += 1

    # Save every 5 venues
    if processed % 5 == 0:
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)
        print(f"\n[Progress: {processed}/{len(targets)} saved]")

# Final save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("DEEP SCRAPING COMPLETE")
print("=" * 100)
print(f"Processed: {processed}")
print(f"Success: {success}")
print(f"Failed: {processed - success}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
