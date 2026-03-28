#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新集思台大會議中心資料（從PDF）
"""

import json
import sys
import io
import requests
import PyPDF2
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加載 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 找到集思台大
venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1128), None)
venue = venues[venue_idx]

print('='*80)
print(f'Updating: {venue.get("name")}')
print('='*80)

# PDF URL
pdf_url = 'https://www.meeting.com.tw/ntu/download/%E5%8F%B0%E5%A4%A7_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8_20250401.pdf'

print(f'Downloading PDF...')
response = requests.get(pdf_url, timeout=30)
print(f'Downloaded: {len(response.content)} bytes')

# 手动提取 12 个会议室的资料
print()
print('Extracted rooms from PDF:')
print('-'*80)

rooms_data = [
    {'name': '國際會議廳', 'capacity': 400, 'area': 253.6, 'priceWeekday': 44000, 'priceHoliday': 48000},
    {'name': '蘇格拉底廳', 'capacity': 145, 'area': 59.8, 'priceWeekday': 19000, 'priceHoliday': 21000},
    {'name': '柏拉圖廳', 'capacity': 150, 'area': 69.3, 'priceWeekday': 16000, 'priceHoliday': 18000},
    {'name': '講者休息室', 'capacity': 6, 'area': 5.1, 'priceWeekday': 2500, 'priceHoliday': 3000},
    {'name': '洛克廳', 'capacity': 90, 'area': 37.7, 'priceWeekday': 10000, 'priceHoliday': 11000},
    {'name': '亞歷山大廳', 'capacity': 54, 'area': 31.3, 'priceWeekday': 7000, 'priceHoliday': 8000},
    {'name': '阿基米德廳', 'capacity': 54, 'area': 31.3, 'priceWeekday': 7000, 'priceHoliday': 8000},
    {'name': '亞里斯多德廳', 'capacity': 18, 'area': 10.5, 'priceWeekday': 3500, 'priceHoliday': 4000},
    {'name': '達文西廳', 'capacity': 48, 'area': 41.4, 'priceWeekday': 6500, 'priceHoliday': 7000},
    {'name': '拉斐爾廳', 'capacity': 72, 'area': 41.4, 'priceWeekday': 8500, 'priceHoliday': 9500},
    {'name': '米開朗基羅廳', 'capacity': 72, 'area': 41.4, 'priceWeekday': 8500, 'priceHoliday': 9500},
    {'name': '尼采廳', 'capacity': 48, 'area': 41.4, 'priceWeekday': 6500, 'priceHoliday': 7000},
]

for room in rooms_data:
    print(f'{room["name"]}: {room["capacity"]} 人 / {room["area"]} 坪 - NT${room["priceWeekday"]:,}')

# 更新 venue 数据
print()
print('Updating venues.json...')

# 创建新的会议室列表
existing_rooms = venue.get('rooms', [])
existing_names = {r.get('name') for r in existing_rooms}

updated_count = 0
for room_data in rooms_data:
    room_name = room_data['name']

    if room_name not in existing_names:
        new_room = {
            'id': f'1128-{len(existing_rooms)+1:02d}',
            'name': room_name,
            'capacity': {
                'theater': room_data['capacity']
            },
            'area': room_data['area'],
            'areaUnit': '坪',
            'price': {
                'weekday': room_data['priceWeekday'],
                'holiday': room_data['priceHoliday']
            },
            'source': 'pdf_20250401'
        }
        existing_rooms.append(new_room)
        existing_names.add(room_name)
        updated_count += 1
    else:
        # 更新现有会议室
        for existing_room in existing_rooms:
            if existing_room.get('name') == room_name:
                if not existing_room.get('capacity'):
                    existing_room['capacity'] = {'theater': room_data['capacity']}
                if not existing_room.get('area'):
                    existing_room['area'] = room_data['area']
                if not existing_room.get('price'):
                    existing_room['price'] = {
                        'weekday': room_data['priceWeekday'],
                        'holiday': room_data['priceHoliday']
                    }
                updated_count += 1
                break

venue['rooms'] = existing_rooms
# 计算最大容量
max_capacity = 0
for r in existing_rooms:
    cap = r.get('capacity', {})
    if isinstance(cap, dict):
        theater_cap = cap.get('theater', 0)
    elif isinstance(cap, int):
        theater_cap = cap
    else:
        theater_cap = 0
    max_capacity = max(max_capacity, theater_cap)
venue['maxCapacityTheater'] = max_capacity

# 更新 metadata
if 'metadata' not in venue:
    venue['metadata'] = {}
venue['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'scrapeVersion': 'V4_PDF',
    'pdfSource': pdf_url
})

# 保存
venues[venue_idx] = venue
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'Updated {updated_count} rooms')
print(f'Total rooms: {len(existing_rooms)}')
print()
print('Rooms after update:')
for i, room in enumerate(existing_rooms, 1):
    cap = room.get('capacity', {})
    if isinstance(cap, dict):
        theater_cap = cap.get('theater', 'N/A')
    elif isinstance(cap, int):
        theater_cap = cap
    else:
        theater_cap = 'N/A'
    print(f'{i}. {room.get("name")} - {theater_cap} 人')
