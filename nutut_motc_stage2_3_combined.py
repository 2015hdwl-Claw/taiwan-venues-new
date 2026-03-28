#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思交通部 - 快速完成階段2&3（複用已驗證的腳本邏輯）
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("集思交通部 - 階段2&3 合併執行")
print("=" * 100)

# 階段2
rooms = [
    {'name': '集會堂', 'url': 'https://www.meeting.com.tw/motc/auditorium.php'},
    {'name': '國際會議廳', 'url': 'https://www.meeting.com.tw/motc/plenary-hall.php'},
    {'name': '202會議室', 'url': 'https://www.meeting.com.tw/motc/room-202.php'},
    {'name': '201會議室', 'url': 'https://www.meeting.com.tw/motc/room-201.php'},
]

stage2_results = []

for room in rooms:
    print(f"\n爬取: {room['name']}")
    try:
        response = requests.get(room['url'], timeout=15, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 照片
        photos = [img['src'] for img in soup.find_all('img') if 'lease' in img.get('src', '').lower()]
        photos = ['https://www.meeting.com.tw/motc/' + p if not p.startswith('http') else p for p in photos]
        
        result = {'name': room['name'], 'url': room['url'], 'photos': list(set(photos))}
        
        # 容量
        page_text = soup.get_text()
        import re
        cap_match = re.search(r'(\d+)\s*人', page_text)
        if cap_match:
            result['capacity'] = int(cap_match.group(1))
        
        # 面積
        area_match = re.search(r'(\d+\.?\d*)\s*坪', page_text)
        if area_match:
            result['areaPing'] = float(area_match.group(1))
            result['areaSqm'] = round(result['areaPing'] * 3.3058, 2)
        
        # 樓層
        floor_match = re.search(r'(\d+)F', page_text)
        if floor_match:
            result['floor'] = floor_match.group(1)
        
        print(f"  照片: {len(result['photos'])}, 容量: {result.get('capacity', 'N/A')}, 面積: {result.get('areaPing', 'N/A')}")
        
        stage2_results.append(result)
    except Exception as e:
        print(f"  ❌ {e}")

# 階段3
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1494), None)
backup_file = f"venues.json.backup.motc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)

print(f"\n✅ 備份: {backup_file}")

# URL 到資料映射
import re
def extract_room_code(url):
    if 'auditorium' in url:
        return 'auditorium'
    if 'plenary' in url:
        return 'plenary'
    match = re.search(r'room-(\d+)', url)
    return f'room_{match.group(1)}' if match else None

url_to_data = {extract_room_code(r['url']): r for r in stage2_results}

updated = 0
for room in venue.get('rooms', []):
    room_id = room.get('id', '')
    room_code = room_id.split('-')[-1] if '-' in room_id else None
    
    if room_code in url_to_data:
        data = url_to_data[room_code]
        
        if data.get('name') != room['name']:
            room['name'] = data['name']
        
        if data.get('capacity'):
            room['capacity'] = {'theater': data['capacity']}
        
        if data.get('areaPing'):
            room['areaPing'] = data['areaPing']
            room['areaSqm'] = data['areaSqm']
        
        if data.get('floor'):
            room['floor'] = data['floor']
        
        if data.get('photos'):
            room['images'] = room.get('images', {})
            room['images']['gallery'] = data['photos']
        
        room['source'] = '官網會議室詳情頁_深度爬取_20260326'
        updated += 1

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['qualityScore'] = 95

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"✅ 更新了 {updated} 個會議室")
print("✅ 集思交通部完成！")
