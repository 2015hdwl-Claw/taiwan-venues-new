#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新集思台大會議中心資料（從PDF）- V2"""

import json
import sys
import io
import requests
import PyPDF2
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加載 venues.json
print("Loading venues.json...")
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 找到集思台大
venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1128), None)
venue = venues[venue_idx]

print('='*80)
print(f'Updating: {venue.get("name")}')
print('='*80)

# PDF 資料（從 PDF 手動提取）
rooms_data = [
    {
        'name': '國際會議廳',
        'nameEn': 'International Conference Hall',
        'capacity': 400,
        'area': 253.6,
        'priceWeekday': 44000,
        'priceHoliday': 48000,
        'facilities': '無線麥克風 3支、桌上型提問麥克風、貴賓休息室 1 間、報到桌 3 張'
    },
    {
        'name': '蘇格拉底廳',
        'nameEn': 'Socrates Hall',
        'capacity': 145,
        'area': 59.8,
        'priceWeekday': 19000,
        'priceHoliday': 21000,
        'facilities': '無線麥克風 3支、後台準備室 1 間、報到桌 2 張'
    },
    {
        'name': '柏拉圖廳',
        'nameEn': 'Plato Hall',
        'capacity': 150,
        'area': 69.3,
        'priceWeekday': 16000,
        'priceHoliday': 18000,
        'facilities': '無線麥克風 3支、報到桌 2 張'
    },
    {
        'name': '講者休息室',
        'nameEn': 'Speaker Lounge',
        'capacity': 6,
        'area': 5.1,
        'priceWeekday': 2500,
        'priceHoliday': 3000,
        'facilities': '講師休息桌椅 6 人（僅柏拉圖廳搭配租借）'
    },
    {
        'name': '洛克廳',
        'nameEn': 'Locke Hall',
        'capacity': 90,
        'area': 37.7,
        'priceWeekday': 10000,
        'priceHoliday': 11000,
        'facilities': '無線麥克風 2支、報到桌 2 張'
    },
    {
        'name': '亞歷山大廳',
        'nameEn': 'Alexander Hall',
        'capacity': 54,
        'area': 31.3,
        'priceWeekday': 7000,
        'priceHoliday': 8000,
        'facilities': '無線麥克風 2支、報到桌 1 張'
    },
    {
        'name': '阿基米德廳',
        'nameEn': 'Archimedes Hall',
        'capacity': 54,
        'area': 31.3,
        'priceWeekday': 7000,
        'priceHoliday': 8000,
        'facilities': '無線麥克風 2支、報到桌 1 張'
    },
    {
        'name': '亞里斯多德廳',
        'nameEn': 'Aristotle Hall',
        'capacity': 18,
        'area': 10.5,
        'priceWeekday': 3500,
        'priceHoliday': 4000,
        'facilities': '報到桌 1 張'
    },
    {
        'name': '達文西廳',
        'nameEn': 'Da Vinci Hall',
        'capacity': 48,
        'area': 41.4,
        'priceWeekday': 6500,
        'priceHoliday': 7000,
        'facilities': '無線麥克風 2支、報到桌 1 張'
    },
    {
        'name': '拉斐爾廳',
        'nameEn': 'Raphael Hall',
        'capacity': 72,
        'area': 41.4,
        'priceWeekday': 8500,
        'priceHoliday': 9500,
        'facilities': '無線麥克風 2支、報到桌 1 張'
    },
    {
        'name': '米開朗基羅廳',
        'nameEn': 'Michelangelo Hall',
        'capacity': 72,
        'area': 41.4,
        'priceWeekday': 8500,
        'priceHoliday': 9500,
        'facilities': '無線麥克風 2支、報到桌 1 張'
    },
    {
        'name': '尼采廳',
        'nameEn': 'Nietzsche Hall',
        'capacity': 48,
        'area': 41.4,
        'priceWeekday': 6500,
        'priceHoliday': 7000,
        'facilities': '無線麥克風 2支、報到桌 1 張'
    },
]

print(f'\nExtracted {len(rooms_data)} rooms from PDF')
print('-'*80)

# 创建完整的会议室列表（替换现有的）
new_rooms = []
for i, room_data in enumerate(rooms_data, 1):
    room = {
        'id': f'1128-{i:02d}',
        'name': room_data['name'],
        'nameEn': room_data.get('nameEn', ''),
        'capacity': {
            'theater': room_data['capacity']
        },
        'area': room_data['area'],
        'areaUnit': '坪',
        'price': {
            'weekday': room_data['priceWeekday'],
            'holiday': room_data['priceHoliday']
        },
        'facilities': room_data.get('facilities', ''),
        'source': 'pdf_20250401'
    }
    new_rooms.append(room)
    print(f'{i}. {room[\"name\"]}: {room_data[\"capacity\"]} 人 / {room_data[\"area\"]} 坪 - NT${room_data[\"priceWeekday\"]:,}')

# 更新 venue
venue['rooms'] = new_rooms
venue['maxCapacityTheater'] = 400  # 國際會議廳
venue['maxCapacityClassroom'] = 150  # 柏拉圖廳

# 更新 metadata
if 'metadata' not in venue:
    venue['metadata'] = {}
venue['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'scrapeVersion': 'V4_PDF_Enhanced',
    'pdfSource': 'https://www.meeting.com.tw/ntu/download/...',
    'totalRooms': len(new_rooms),
    'pdfExtractDate': '2025-04-01'
})

# 保存
print('\nSaving to venues.json...')
venues[venue_idx] = venue

# 创建备份
backup_path = f"venues.json.backup.ntucc_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)
print(f'Backup created: {backup_path}')

# 保存主文件
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'Saved {len(new_rooms)} rooms to venues.json')
print(f'\nUpdated venue:')
print(f'- Total rooms: {len(new_rooms)}')
print(f'- Max capacity: {venue[\"maxCapacityTheater\"]} people')
print(f'- Data source: PDF 2025-04-01')
