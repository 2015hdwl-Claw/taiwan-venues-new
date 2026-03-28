#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Targeted scraper for 台北世貿中心 (ID: 1049)"""

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


def scrape_twtc_meeting_rooms():
    """Scrape all meeting rooms from 台北世貿中心"""

    base_url = 'https://www.twtc.com.tw/'
    venue_id = 1049
    venue_name = '台北世貿中心'

    print('=' * 80)
    print(f'Scraping: {venue_name} (ID: {venue_id})')
    print('=' * 80)

    # Meeting room pages discovered
    meeting_rooms = [
        ('第一會議室', './meeting1'),
        ('A+會議室', './meeting11'),
        ('第二會議室', './meeting2'),
        ('第三會議室', './meeting3'),
        ('第四會議室', './meeting4'),
        ('第五會議室', './meeting5'),
        ('第三四五會議室(打通)', './meeting345'),
    ]

    rooms = []

    for i, (room_name, path) in enumerate(meeting_rooms, 1):
        url = urljoin(base_url, path)
        print(f'\n[{i}/{len(meeting_rooms)}] {room_name}')
        print(f'URL: {url}')

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract room data
            room = {
                'id': f'{venue_id}-{i:02d}',
                'name': room_name,
                'url': url
            }

            # Look for content sections
            page_text = soup.get_text()

            # Extract capacity (人數)
            capacity_patterns = [
                r'人數[：:]\s*(\d+)',
                r'容量[：:]\s*(\d+)',
                r'(\d+)\s*人',
                r'(\d+)\s*位',
            ]
            for pattern in capacity_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room['capacity'] = int(match.group(1))
                        break
                    except:
                        pass

            # Extract area (坪/平方米)
            area_patterns = [
                r'面積[：:]\s*(\d+\.?\d*)\s*(坪|平方米|㎡)',
                r'(\d+\.?\d*)\s*坪',
                r'(\d+\.?\d*)\s*平方米',
            ]
            for pattern in area_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room['area'] = float(match.group(1))
                        room['areaUnit'] = '坪'
                        break
                    except:
                        pass

            # Extract price
            price_patterns = [
                r'NT\$?\s*([\d,]+)',
                r'([\d,]+)\s*元',
                r'價格[：:]\s*NT\$?\s*([\d,]+)',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        room['price'] = int(match.group(1).replace(',', ''))
                        break
                    except:
                        pass

            # Extract equipment/facilities
            # Look for common equipment keywords
            equipment_keywords = {
                '投影機': 'projector',
                '投影': 'projector',
                '麥克風': 'microphone',
                '音響': 'audio',
                '網路': 'internet',
                'WiFi': 'wifi',
                '白板': 'whiteboard',
                '螢幕': 'screen',
            }

            found_equipment = []
            for keyword, en_name in equipment_keywords.items():
                if keyword in page_text:
                    found_equipment.append(keyword)

            if found_equipment:
                room['equipment'] = ', '.join(found_equipment)

            # Print summary
            cap = room.get('capacity', 'N/A')
            area = room.get('area', 'N/A')
            price = room.get('price', 'N/A')
            equip = room.get('equipment', 'N/A')
            print(f'  Result: {cap} people / {area} ping / NT${price}')
            if equip != 'N/A':
                print(f'  Equipment: {equip}')

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
    venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1049), None)
    if venue_idx is None:
        print("Venue ID 1049 not found!")
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
        'roomCoverage': f'{len(rooms)} meeting rooms'
    })

    # Create backup
    backup_path = f"venues.json.backup.twtc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'Backup created: {backup_path}')

    # Save
    venues[venue_idx] = venue
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f'Updated {len(rooms)} rooms for venue ID 1049')

    # Calculate coverage
    with_capacity = sum(1 for r in rooms if r.get('capacity'))
    with_area = sum(1 for r in rooms if r.get('area'))
    with_price = sum(1 for r in rooms if r.get('price'))
    with_equipment = sum(1 for r in rooms if r.get('equipment'))

    print(f'\nCoverage:')
    print(f'  Capacity: {with_capacity}/{len(rooms)} ({with_capacity*100//len(rooms)}%)')
    print(f'  Area: {with_area}/{len(rooms)} ({with_area*100//len(rooms)}%)')
    print(f'  Price: {with_price}/{len(rooms)} ({with_price*100//len(rooms)}%)')
    print(f'  Equipment: {with_equipment}/{len(rooms)} ({with_equipment*100//len(rooms)}%)')


def main():
    print('=' * 80)
    print('Targeted Scraper - 台北世貿中心 (ID: 1049)')
    print('=' * 80)

    # Scrape all meeting rooms
    rooms = scrape_twtc_meeting_rooms()

    if rooms:
        print('\n' + '=' * 80)
        print(f'Successfully scraped {len(rooms)} meeting rooms')
        print('=' * 80)

        # Update venues.json
        update_venues_json(rooms)
    else:
        print('\nNo rooms scraped')


if __name__ == '__main__':
    main()
