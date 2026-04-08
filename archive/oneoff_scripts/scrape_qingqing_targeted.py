#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Targeted scraper for 青青婚宴會館 (ID: 1129)"""

import sys
import io
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def scrape_qingqing_halls():
    """Scrape all halls from 青青婚宴會館"""

    base_url = 'https://www.77-67.com/'
    venue_id = 1129
    venue_name = '青青婚宴會館'

    print('=' * 80)
    print(f'Scraping: {venue_name} (ID: {venue_id})')
    print('=' * 80)

    # Hall pages discovered
    hall_urls = [
        ('凱薩廳', '/sacred-wood-courtyard'),
        ('香榭廳', '/champs-hall'),
        ('法頌廳', '/Fasong-Hall'),
        ('維也納廳', '/vienna-hall'),
        ('巴洛克廳', '/baroque-hall'),
        ('普羅旺斯廳', '/provence-hall'),
        ('凱特廳', '/kate-hall'),
        ('凱旋廳', '/triumph-hall'),
        ('愛麗絲廳', '/alice-hall'),
        ('富城廳', '/prosperity-hall'),
    ]

    rooms = []

    for i, (hall_name, path) in enumerate(hall_urls, 1):
        url = urljoin(base_url, path)
        print(f'\n[{i}/{len(hall_urls)}] {hall_name}')
        print(f'URL: {url}')

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract JSON-LD first
            json_ld = soup.find('script', type='application/ld+json')
            json_ld_data = None
            if json_ld:
                try:
                    json_ld_data = json.loads(json_ld.string)
                except:
                    pass

            # Extract room data
            room = {
                'id': f'{venue_id}-{i:02d}',
                'name': hall_name,
                'url': url
            }

            # Extract capacity
            page_text = soup.get_text()
            capacity_patterns = [
                r'容量[：:]\s*(\d+)',
                r'(\d+)\s*桌',
                r'(\d+)\s*人',
            ]
            for pattern in capacity_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room['capacity'] = int(match.group(1))
                        break
                    except:
                        pass

            # Extract area (坪)
            area_pattern = r'(\d+\.?\d*)\s*坪'
            match = re.search(area_pattern, page_text)
            if match:
                room['area'] = float(match.group(1))
                room['areaUnit'] = '坪'

            # Extract price
            price_patterns = [
                r'NT\$?\s*([\d,]+)',
                r'([\d,]+)\s*元',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room['price'] = int(match.group(1).replace(',', ''))
                        break
                    except:
                        pass

            # Extract description
            # Look for meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                room['description'] = meta_desc.get('content', '')[:200]

            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                if any(kw in src.lower() for kw in ['hall', 'banquet', 'wedding', '廳']):
                    full_url = urljoin(base_url, src)
                    if full_url not in images:
                        images.append(full_url)
                        if len(images) >= 3:
                            break
            if images:
                room['images'] = images

            # Print summary
            cap = room.get('capacity', 'N/A')
            area = room.get('area', 'N/A')
            price = room.get('price', 'N/A')
            print(f'  Result: {cap} people / {area} ping / NT${price}')

            rooms.append(room)

        except Exception as e:
            print(f'  Error: {e}')

    return rooms


def update_venues_json(rooms):
    """Update venues.json with scraped data"""

    print('\n' + '=' * 80)
    print('Updating venues.json...')
    print('=' * 80)

    # Load venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # Find venue
    venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1129), None)
    if venue_idx is None:
        print("Venue ID 1129 not found!")
        return

    venue = venues[venue_idx]

    # Update rooms
    venue['rooms'] = rooms

    # Update max capacity
    if rooms:
        capacities = [r.get('capacity', 0) for r in rooms if r.get('capacity')]
        if capacities:
            venue['maxCapacityTheater'] = max(capacities)

    # Update metadata
    if 'metadata' not in venue:
        venue['metadata'] = {}
    venue['metadata'].update({
        'lastScrapedAt': datetime.now().isoformat(),
        'scrapeVersion': 'Targeted_Deep_Scrape_V1',
        'totalRooms': len(rooms),
        'roomCoverage': f'{len(rooms)} halls'
    })

    # Create backup
    backup_path = f"venues.json.backup.qingqing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'Backup created: {backup_path}')

    # Save
    venues[venue_idx] = venue
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f'Updated {len(rooms)} rooms for venue ID 1129')

    # Calculate coverage
    with_capacity = sum(1 for r in rooms if r.get('capacity'))
    with_area = sum(1 for r in rooms if r.get('area'))
    with_price = sum(1 for r in rooms if r.get('price'))

    print(f'\nCoverage:')
    print(f'  Capacity: {with_capacity}/{len(rooms)} ({with_capacity*100//len(rooms)}%)')
    print(f'  Area: {with_area}/{len(rooms)} ({with_area*100//len(rooms)}%)')
    print(f'  Price: {with_price}/{len(rooms)} ({with_price*100//len(rooms)}%)')


def main():
    print('=' * 80)
    print('Targeted Scraper - 青青婚宴會館 (ID: 1129)')
    print('=' * 80)

    # Scrape all halls
    rooms = scrape_qingqing_halls()

    if rooms:
        print('\n' + '=' * 80)
        print(f'Successfully scraped {len(rooms)} halls')
        print('=' * 80)

        # Update venues.json
        update_venues_json(rooms)
    else:
        print('\nNo rooms scraped')


if __name__ == '__main__':
    main()
