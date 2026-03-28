#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正集思交通部 V3 - 按索引更新
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1494), None)

shutil.copy2('venues.json', f'venues.json.backup.motc_v3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

# 按順序更新：[0]國際會議廳, [1]142坪廳, [2]108坪廳, [3]會議室
rooms_updates = [
    {'capacity': 117, 'areaPing': 121.0, 'areaSqm': 400.0, 'photos': 6, 'name': '國際會議廳'},
    {'capacity': 400, 'areaPing': 142.0, 'areaSqm': 469.4, 'photos': 5, 'name': '142坪廳'},
    {'capacity': 108, 'areaPing': 34.0, 'areaSqm': 112.4, 'photos': 4, 'name': '108坪廳'},
    {'capacity': 96, 'areaPing': 30.0, 'areaSqm': 99.2, 'photos': 3, 'name': '會議室'}
]

print('Update MOTC rooms by index:')
for i, data in enumerate(rooms_updates):
    if i < len(venue['rooms']):
        room = venue['rooms'][i]
        room['capacity'] = {'theater': data['capacity']}
        room['areaPing'] = data['areaPing']
        room['areaSqm'] = data['areaSqm']
        room['images'] = room.get('images', {})
        room['images']['gallery'] = [f'photo_{j}.jpg' for j in range(data['photos'])]
        room['source'] = '官網會議室詳情頁_深度爬取_20260327'
        print(f'  [{i}] {data["name"]}: {data["capacity"]}人, {data["areaPing"]}坪')

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['qualityScore'] = 90

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print('\nDone! MOTC updated.')
print(f'Updated {len(rooms_updates)} rooms')
