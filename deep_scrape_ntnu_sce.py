#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
師大進修推廣學院 - 深度爬蟲（第 3 層詳細資料）

提取頁面中 room_data JavaScript 變數的完整資料
"""

import sys
import io
import json
import re
import requests
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def extract_room_data_from_js():
    """從頁面的 JavaScript 變數中提取完整會議室資料"""

    url = "https://www.sce.ntnu.edu.tw/home/space/"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        html_content = response.text

        # 尋找 room_data 變數
        # 模式：var room_data = [{...}];
        pattern = r'var room_data = (\[.*?\]);'
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            print('  ❌ 找不到 room_data 變數')
            return None

        # 提取 JSON 字串
        json_str = match.group(1)

        # 解析 JSON
        room_data = json.loads(json_str)

        print(f'  ✅ 成功提取 {len(room_data)} 個會議室的完整資料')

        return room_data

    except Exception as e:
        print(f'  ❌ 錯誤: {e}')
        return None


def convert_room_data(room_data):
    """轉換 room_data 為標準格式"""

    converted_rooms = []

    for room in room_data:
        # 提取注意事項中的尺寸資訊
        notice = room.get('notice', '')
        dimensions = None

        # 尋找尺寸模式：長寬15*8公尺
        dimension_match = re.search(r'長寬(\d+)\*(\d+)公尺', notice)
        if dimension_match:
            length = int(dimension_match.group(1))
            width = int(dimension_match.group(2))
            dimensions = {
                'length': length,
                'width': width,
                'area': length * width  # 平方公尺
            }

        # 構建標準格式
        converted_room = {
            'id': f"1493-{room['id']}",
            'name': room['name'],
            'nameEn': None,
            'floor': None,  # 可以從名稱或照片推斷
            'type': room['type'],
            'location': room['location'],
            'capacity': {
                'seats': room['seats'],
                'theater': None,
                'classroom': None,
                'banquet': None
            },
            'area': dimensions,
            'price': {
                'amount': int(room['price']) if room['price'].isdigit() else None,
                'unit': room['unit'],
                'weekday': None,
                'holiday': None
            },
            'equipment': {
                'hardware': room['hardware'],
                'software': room['software'],
                'network': room['network']
            },
            'description': {
                'suitable_for': room['activitys'],
                'notice': room['notice'],
                'counts': room['counts']
            },
            'images': {
                'photo_count': room['photo_counts'],
                'photos': room['photos']
            },
            'source': 'room_data_js_variable',
            'scraped_at': datetime.now().isoformat()
        }

        converted_rooms.append(converted_room)

    return converted_rooms


def update_venues_json(venue_id, rooms):
    """更新 venues.json"""

    # 載入
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到場地
    for venue in venues:
        if venue['id'] == venue_id:
            # 更新會議室
            venue['rooms'] = rooms

            # 更新 metadata
            if 'metadata' not in venue:
                venue['metadata'] = {}

            venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            venue['metadata']['scrapeVersion'] = 'Deep_Scrape_V3_JS_Variable'
            venue['metadata']['scrapeDepth'] = 'Layer 3 (room_data variable)'
            venue['metadata']['scrapeMethod'] = 'JavaScript variable extraction'

            # 統計
            total_rooms = len(rooms)
            rooms_with_capacity = sum(1 for r in rooms if r['capacity']['seats'])
            rooms_with_price = sum(1 for r in rooms if r['price']['amount'])
            rooms_with_area = sum(1 for r in rooms if r['area'])
            rooms_with_equipment = sum(1 for r in rooms if r['equipment']['hardware'])
            rooms_with_photos = sum(1 for r in rooms if r['images']['photo_count'] > 0)

            venue['metadata']['stats'] = {
                'total_rooms': total_rooms,
                'rooms_with_capacity': rooms_with_capacity,
                'rooms_with_price': rooms_with_price,
                'rooms_with_area': rooms_with_area,
                'rooms_with_equipment': rooms_with_equipment,
                'rooms_with_photos': rooms_with_photos
            }

            print(f'  ✅ 更新場地: {venue["name"]}')
            print(f'     總會議室: {total_rooms}')
            print(f'     有容量: {rooms_with_capacity} ({rooms_with_capacity/total_rooms*100:.1f}%)')
            print(f'     有價格: {rooms_with_price} ({rooms_with_price/total_rooms*100:.1f}%)')
            print(f'     有面積: {rooms_with_area} ({rooms_with_area/total_rooms*100:.1f}%)')
            print(f'     有設備: {rooms_with_equipment} ({rooms_with_equipment/total_rooms*100:.1f}%)')
            print(f'     有照片: {rooms_with_photos} ({rooms_with_photos/total_rooms*100:.1f}%)')

            break

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)


def main():
    print('=' * 80)
    print('師大進修推廣學院 - 深度爬蟲（第 3 層）')
    print('=' * 80)
    print()

    print('[1/3] 提取 JavaScript room_data 變數...')
    room_data = extract_room_data_from_js()

    if not room_data:
        print('❌ 無法提取資料')
        return

    print()
    print('[2/3] 轉換為標準格式...')
    converted_rooms = convert_room_data(room_data)

    print()
    print('會議室列表（前 3 個）:')
    for i, room in enumerate(converted_rooms[:3], 1):
        print(f'{i}. {room["name"]}')
        print(f'   容量: {room["capacity"]["seats"]} 人')
        print(f'   價格: NT${room["price"]["amount"]} / {room["price"]["unit"]}')
        print(f'   面積: {room["area"]["area"] if room["area"] else "無"} 平方公尺')
        print(f'   照片: {room["images"]["photo_count"]} 張')
        print()

    print(f'... 還有 {len(converted_rooms) - 3} 個會議室')
    print()

    print('[3/3] 更新 venues.json...')
    update_venues_json(1493, converted_rooms)

    print()
    print('=' * 80)
    print('深度爬蟲完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
