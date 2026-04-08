#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新師大進修推廣學院會議室資料

從官網場地頁面提取容量資料並更新到 venues.json
"""

import sys
import io
import json
import re
import requests
from html import unescape

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def extract_rooms_from_page():
    """從場地頁面提取會議室資料"""

    url = "https://www.sce.ntnu.edu.tw/home/space/"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        html_content = response.text

        # Find all room entries
        pattern = r'<p><b>([^<]+)</b></p>'
        matches = re.findall(pattern, html_content)

        # Remove HTML entities and decode
        rooms = []
        for match in matches:
            room_name = unescape(match)
            rooms.append(room_name)

        # Deduplicate
        unique_rooms = sorted(set(rooms))

        # Parse each room
        parsed_rooms = []
        for room in unique_rooms:
            # Extract capacity from room name
            capacity_match = re.search(r'（(\d+)人）', room)
            capacity2_match = re.search(r'\((\d+)人\)', room)

            capacity = None
            if capacity_match:
                capacity = int(capacity_match.group(1))
            elif capacity2_match:
                capacity = int(capacity2_match.group(1))

            # Handle range like "35-40人"
            range_match = re.search(r'(\d+)-(\d+)人', room)
            if range_match:
                capacity = int(range_match.group(2))  # Use max capacity

            # Clean up room name
            clean_name = re.sub(r'（\d+人）', '', room)
            clean_name = re.sub(r'\(\d+人\)', '', clean_name)
            clean_name = re.sub(r'\(\d+-\d+人\)', '', clean_name)
            clean_name = clean_name.strip()

            parsed_rooms.append({
                'name': clean_name,
                'capacity': capacity,
                'floor': None,
                'area': None,
                'equipment': None,
                'price': None,
                'images': None
            })

        return parsed_rooms

    except Exception as e:
        print(f'錯誤: {e}')
        return []


def update_venues_json(venue_id, rooms):
    """更新 venues.json"""

    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # Find the venue
    for venue in venues:
        if venue['id'] == venue_id:
            # Update rooms
            venue['rooms'] = rooms

            # Update metadata
            if 'metadata' not in venue:
                venue['metadata'] = {}

            venue['metadata']['lastScrapedAt'] = '2026-03-26T10:30:00'
            venue['metadata']['scrapeVersion'] = 'Manual_Update_V1'
            venue['metadata']['scrapeSource'] = 'Official Website (Space Page)'

            # Count rooms with capacity
            rooms_with_capacity = sum(1 for r in rooms if r.get('capacity'))

            venue['metadata']['roomsWithCapacity'] = rooms_with_capacity
            venue['metadata']['totalRooms'] = len(rooms)

            print(f'✅ 已更新場地: {venue["name"]}')
            print(f'   總會議室: {len(rooms)}')
            print(f'   有容量資料: {rooms_with_capacity}')
            print(f'   覆蓋率: {rooms_with_capacity/len(rooms)*100:.1f}%')

            break

    # Write back
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)


def main():
    print('=' * 80)
    print('更新師大進修推廣學院會議室資料')
    print('=' * 80)
    print()

    # Extract rooms
    print('[1/2] 從官網提取會議室資料...')
    rooms = extract_rooms_from_page()

    if not rooms:
        print('❌ 無法提取會議室資料')
        return

    print(f'✅ 成功提取 {len(rooms)} 個會議室')
    print()

    # Show sample
    print('會議室列表（前 5 個）:')
    for room in rooms[:5]:
        cap_str = f'{room["capacity"]} 人' if room['capacity'] else '未知'
        print(f'  {room["name"]:30} 容量: {cap_str:>6}')

    if len(rooms) > 5:
        print(f'  ... 還有 {len(rooms) - 5} 個會議室')

    print()
    print('[2/2] 更新 venues.json...')

    # Update
    update_venues_json(1493, rooms)

    print()
    print('=' * 80)
    print('更新完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
