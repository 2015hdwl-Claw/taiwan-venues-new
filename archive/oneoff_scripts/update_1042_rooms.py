#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update venue 1042 (公務人力發展學院) rooms - 23 spaces from hrd.gov.tw."""

import json, shutil, datetime

# Backup first
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy('venues.json', f'venues.json.backup.{ts}')
print(f'Backup: venues.json.backup.{ts}')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

venue = [v for v in data if v.get('id') == 1042][0]

# Standard equipment
standard_equipment = ['投影設備', '音響系統', '無線麥克風', 'WiFi', '空調', '白板', '講台', '飲用水']

# Image base
img_base = 'https://www.hrd.gov.tw/media'

# 23 spaces from https://www.hrd.gov.tw/1122/2141/3157/NPmeetingVenue
rooms_data = [
    # === 1F (2 spaces) ===
    {
        'id': '1042-01',
        'name': '1F 前瞻廳',
        'nameEn': '1F Vision Hall',
        'floor': '1樓',
        'capacity': {'theater': 220},
        'height': None,
        'pillar': False,
        'equipment': standard_equipment + ['電動螢幕'],
        'images': {'main': f'{img_base}/1015/1f.jpg'},
        'notes': '階梯教室型，無白板提供',
        'source': 'website_20260330',
    },
    {
        'id': '1042-02',
        'name': '1F 101階梯教室',
        'nameEn': '1F Room 101',
        'floor': '1樓',
        'capacity': {'theater': 41},
        'pillar': False,
        'equipment': standard_equipment + ['電動螢幕'],
        'images': {'main': f'{img_base}/1019/101.jpg'},
        'notes': '階梯教室型',
        'source': 'website_20260330',
    },
    # === 1F continued ===
    {
        'id': '1042-03',
        'name': '1F 103階梯教室',
        'nameEn': '1F Room 103',
        'floor': '1樓',
        'capacity': {'theater': 78},
        'pillar': False,
        'equipment': standard_equipment + ['電動螢幕'],
        'images': {'main': f'{img_base}/1020/103.jpg'},
        'notes': '階梯戲院型',
        'source': 'website_20260330',
    },
    # === 2F (5 spaces) ===
    {
        'id': '1042-04',
        'name': '2F 卓越堂下層',
        'nameEn': '2F Excellence Hall (Lower)',
        'floor': '2樓',
        'capacity': {'theater': 455},
        'pillar': False,
        'equipment': standard_equipment + ['電動螢幕', '基本場燈', '音響'],
        'images': {'main': f'{img_base}/1016/2f_down.jpg'},
        'notes': '階梯戲院型，無白板。特殊燈光音響需自備，舞台大型布置需自備地毯',
        'source': 'website_20260330',
    },
    {
        'id': '1042-05',
        'name': '2F 卓越堂全場',
        'nameEn': '2F Excellence Hall (Full)',
        'floor': '2樓',
        'capacity': {'theater': 712},
        'pillar': False,
        'equipment': standard_equipment + ['電動螢幕', '基本場燈', '音響'],
        'images': {'main': f'{img_base}/1017/img_8605s.jpg'},
        'notes': '階梯戲院型，全場最大容量。無白板。特殊燈光音響需自備',
        'source': 'website_20260330',
    },
    {
        'id': '1042-06',
        'name': '2F 201教室',
        'nameEn': '2F Room 201',
        'floor': '2樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1021/201_1.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    {
        'id': '1042-07',
        'name': '2F 202教室',
        'nameEn': '2F Room 202',
        'floor': '2樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1022/202.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    {
        'id': '1042-08',
        'name': '2F 203教室',
        'nameEn': '2F Room 203',
        'floor': '2樓',
        'capacity': {'classroom': 48, 'ushape': 48},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1023/203.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    # === 2F continued ===
    {
        'id': '1042-09',
        'name': '2F 204教室',
        'nameEn': '2F Room 204',
        'floor': '2樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1024/204.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    {
        'id': '1042-10',
        'name': '2F 205教室',
        'nameEn': '2F Room 205',
        'floor': '2樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1024/204.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    # === 3F (3 spaces) ===
    {
        'id': '1042-11',
        'name': '3F 303研討室',
        'nameEn': '3F Room 303',
        'floor': '3樓',
        'capacity': {'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1025/303s.jpg'},
        'notes': 'U型',
        'source': 'website_20260330',
    },
    {
        'id': '1042-12',
        'name': '3F 304教室',
        'nameEn': '3F Room 304',
        'floor': '3樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1026/n2011321113539s.jpg'},
        'notes': '教室型/U型/分組型。3F平日8:00-18:00由學院保留',
        'source': 'website_20260330',
    },
    {
        'id': '1042-13',
        'name': '3F 305教室',
        'nameEn': '3F Room 305',
        'floor': '3樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1028/n2011321113539s.jpg'},
        'notes': '教室型/U型/分組型。3F平日8:00-18:00由學院保留',
        'source': 'website_20260330',
    },
    # === 4F (4 spaces) ===
    {
        'id': '1042-14',
        'name': '4F 401教室',
        'nameEn': '4F Room 401',
        'floor': '4樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1029/n2011318143112s.jpg'},
        'notes': '教室型/U型/分組型。4F平日8:00-18:00由學院保留',
        'source': 'website_20260330',
    },
    {
        'id': '1042-15',
        'name': '4F 402教室',
        'nameEn': '4F Room 402',
        'floor': '4樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1029/n2011318143112s.jpg'},
        'notes': '教室型/U型/分組型。4F平日8:00-18:00由學院保留',
        'source': 'website_20260330',
    },
    {
        'id': '1042-16',
        'name': '4F 403數位科技教室',
        'nameEn': '4F Digital Tech Room 403',
        'floor': '4樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment + ['短焦投影機', '液晶電視'],
        'images': {'main': f'{img_base}/7857/會議場地-4f-403數位科技教室.png'},
        'notes': '數位科技教室，提供短焦投影機及液晶電視。4F平日保留',
        'source': 'website_20260330',
    },
    {
        'id': '1042-17',
        'name': '4F 404數位互動教室',
        'nameEn': '4F Digital Interactive Room 404',
        'floor': '4樓',
        'capacity': {'classroom': 60, 'ushape': 60},
        'pillar': False,
        'equipment': standard_equipment + ['互動顯示設備'],
        'images': {'main': f'{img_base}/10534/附檔2_404數位互動教室-11205修.jpg'},
        'notes': '數位互動教室，容量較大(60位)。4F平日保留',
        'source': 'website_20260330',
    },
    # === 5F (2 spaces) ===
    {
        'id': '1042-18',
        'name': '5F 501教室',
        'nameEn': '5F Room 501',
        'floor': '5樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/4311/img_1072s.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    {
        'id': '1042-19',
        'name': '5F 502教室',
        'nameEn': '5F Room 502',
        'floor': '5樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1035/n2011318143328s.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    # === 6F (2 spaces) ===
    {
        'id': '1042-20',
        'name': '6F 601教室',
        'nameEn': '6F Room 601',
        'floor': '6樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1036/601s.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    {
        'id': '1042-21',
        'name': '6F 602教室',
        'nameEn': '6F Room 602',
        'floor': '6樓',
        'capacity': {'classroom': 30, 'ushape': 30},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1037/601s.jpg'},
        'notes': '教室型/U型/分組型',
        'source': 'website_20260330',
    },
    # === 14F (2 spaces - same room, different layouts) ===
    {
        'id': '1042-22',
        'name': '14F 貴賓廳',
        'nameEn': '14F VIP Hall',
        'floor': '14樓',
        'capacity': {'theater': 100, 'classroom': 100},
        'pillar': False,
        'equipment': standard_equipment,
        'images': {'main': f'{img_base}/1018/14fs.jpg'},
        'notes': '教室型100位/分組型81位',
        'source': 'website_20260330',
    },
]

# Build rooms list
venue['rooms'] = []

for rd in rooms_data:
    room = {
        'id': rd['id'],
        'name': rd['name'],
        'nameEn': rd.get('nameEn', ''),
        'floor': rd.get('floor', ''),
        'capacity': rd.get('capacity', {}),
        'pillar': rd.get('pillar', True),
        'equipment': rd.get('equipment', standard_equipment),
        'images': rd.get('images', {}),
        'notes': rd.get('notes', ''),
        'source': rd.get('source', ''),
    }

    # Calculate quality score
    score = 0
    if room.get('name'):
        score += 10
    cap = room.get('capacity', {})
    if cap.get('theater') or cap.get('classroom') or cap.get('ushape'):
        score += 15
    if room.get('area') or room.get('areaSqm'):
        score += 15
    price = room.get('price', {})
    if any(v for v in price.values() if v):
        score += 20
    imgs = room.get('images', {})
    if imgs.get('main'):
        score += 20
    if room.get('equipment') and len(room.get('equipment', [])) > 0:
        score += 10
    if room.get('floor'):
        score += 5
    if room.get('length') or room.get('width'):
        score += 5

    room['qualityScore'] = score
    room['qualityLevel'] = 'high' if score >= 70 else ('medium' if score >= 40 else 'low')

    venue['rooms'].append(room)
    cap_str = f"theater={cap.get('theater','-')}, classroom={cap.get('classroom','-')}, ushape={cap.get('ushape','-')}"
    print(f'{rd["id"]} {rd["name"]}: score={score}, cap=[{cap_str}], '
          f'imgs={"yes" if imgs.get("main") else "no"}')

# Update venue-level metadata
venue['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = 'Manual_Website_20260330'
venue['metadata']['totalRooms'] = len(venue['rooms'])
venue['metadata']['skipReason'] = None

# Update main venue image (use 前瞻廳 as the best representative image)
venue['images']['main'] = f'{img_base}/1015/1f.jpg'
venue['images']['gallery'] = [
    f'{img_base}/1015/1f.jpg',
    f'{img_base}/1017/img_8605s.jpg',
    f'{img_base}/1016/2f_down.jpg',
    f'{img_base}/1018/14fs.jpg',
    f'{img_base}/7857/會議場地-4f-403數位科技教室.png',
]

# Update max capacity
max_theater = max((r.get('capacity', {}).get('theater', 0) for r in venue['rooms']), default=0)
venue['maxCapacityTheater'] = max_theater
venue['capacity'] = {'theater': max_theater}

# Update contact info
venue['contactEmail'] = 'sales-ih@howard-hotels.com.tw'

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone! Added {len(venue["rooms"])} rooms for venue 1042 (公務人力發展學院)')
print(f'Max theater capacity: {max_theater}')
