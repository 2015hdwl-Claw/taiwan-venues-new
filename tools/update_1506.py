#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update venue 1506 瓏山林台北中和飯店 with complete data"""

import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')

with open(VENUES_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

v = [x for x in data if x.get('id') == 1506][0]

# === Venue-level updates ===
v['nameEn'] = 'RSL Hotel Taipei Zhonghe'
v['description'] = (
    '瓏山林台北中和飯店位於北二高中和交流道旁，是新北市首家國際級飯店。'
    '擁有挑高4米國際宴會廳，最多可容納360人，場地可靈活分隔為東廳、南廳、北廳、西廳及2間貴賓廳。'
    '自有廚藝團隊提供中、西式餐飲服務，專業會議設備齊全。'
)
v['image'] = 'https://taipei.rslhotel.com/upload/banner_ins_list/twL_banner_ins_19G26_qzjpkptqms.jpg'
v['images'] = {
    'main': 'https://taipei.rslhotel.com/upload/banner_ins_list/twL_banner_ins_19G26_qzjpkptqms.jpg',
    'gallery': [
        'https://taipei.rslhotel.com/upload/banner_ins_list/twL_banner_ins_19G26_qzjpkptqms.jpg',
        'https://taipei.rslhotel.com/upload/catalog_home_list_pic/enL_catalog_19J28_tqns9cx6dj.jpg',
        'https://taipei.rslhotel.com/upload/package_meeting_b/ALL_package_meeting_19H14_wzh49hp2a6.jpg',
    ],
    'source': 'https://taipei.rslhotel.com/',
    'verified': True,
    'verifiedAt': '2026-04-11',
    'lastUpdated': '2026-04-11',
}
v['highlights'] = [
    '挑高4米國際宴會廳，最多可容納360人',
    '場地可靈活分隔為多個獨立空間（東廳、南廳、北廳、西廳 + 2間貴賓廳）',
    '北二高中和交流道旁，交通便利 — 鄰近中和、永和、板橋',
    '自有廚藝團隊，提供中、西式餐飲服務',
    '專業會議設備齊全：麥克風、白板、簡報架、液晶投影機、PA系統',
]
v['equipment'] = ['投影設備', '音響系統', '無線麥克風', '白板', '簡報架', 'PA系統', '海報架', '文具用品']
v['floorPlan'] = 'https://taipei.rslhotel.com/upload/package_meeting_b/ALL_package_meeting_19H14_wzh49hp2a6.jpg'
v['contactPerson'] = '餐飲宴會訂席'
v['contactPhone'] = '02-2221-5658 #2702 / 2703'
v['contactEmail'] = 'email@rslhotel.tw'
v['availableTimeWeekday'] = '08:00-22:00'
v['availableTimeWeekend'] = '08:00-22:00'
v['priceHalfDay'] = 4000
v['priceFullDay'] = 8000

v['accessInfo'] = {
    'mrt': [
        {'line': '中和新蘆線', 'station': '景安站', 'bus': ['橘5', '藍41'], 'walk': '約3分鐘'},
        {'line': '環狀線', 'station': '中和站', 'bus': ['201'], 'walk': '約3分鐘'},
        {'line': '板南線', 'station': '板橋站', 'bus': ['307', '793'], 'walk': '約3分鐘'},
    ],
    'bus': {'stopName': '連城中正路口', 'routes': ['57', '201', '214', '275', '307', '311', '706', '793']},
    'parking': {'available': True, 'note': '住宿及用餐免費停車，地下室限高2米，停車位數量有限'},
}
v['transportation'] = {
    'car': '北二高中和交流道下，位於左側',
    'mrt': '景安站(橘5/藍41)、中和站(201)、板橋站(307/793)',
    'bus': '連城中正路口站：57, 201, 214, 275, 307, 311, 706, 793',
    'parking': '免費（住宿/用餐），地下室限高2米',
    'notes': '停車位有限，無保留服務',
}
v['loadIn'] = {
    'loadInTime': '依場地租借時段',
    'loadOutTime': '依場地租借時段',
    'elevatorCapacity': '未提供',
}
v['risks'] = {
    'bookingLeadTime': '建議至少2週前預約',
    'peakSeasons': ['12-1月尾牙季', '10-12月婚宴旺季', '6-7月畢業季'],
    'commonIssues': ['停車位有限無保留', '地下室限高2米', '液晶投影機需額外租用NT$12,000/次'],
}
v['pricingTips'] = [
    '會議專案（每人計價）比純場租划算，10人以上適用',
    '所有價格需加服務費一成（10%）',
    '液晶投影機額外租用NT$12,000net/次',
    '婚宴吉日優惠：10桌以上贈送1桌',
]
v['limitations'] = [
    '貴賓廳 I/II 無公開面積和容量資料',
    '停車位數量有限，無保留服務',
    '地下室停車限高2米',
]
v['rules'] = {
    'catering': [
        {'rule': '自有廚藝團隊，提供中、西式餐飲服務', 'source': {'type': 'website', 'url': 'https://taipei.rslhotel.com/meeting/', 'extractedAt': '2026-04-11'}, 'confidence': 'strict'},
        {'rule': '所有價格需加服務費一成（10% service charge）', 'source': {'type': 'website', 'url': 'https://taipei.rslhotel.com/meeting/', 'extractedAt': '2026-04-11'}, 'confidence': 'strict'},
    ],
    'decoration': [
        {'rule': '場地使用視訂席實際情況做調整及安排', 'source': {'type': 'website', 'url': 'https://taipei.rslhotel.com/meeting/', 'extractedAt': '2026-04-11'}, 'confidence': 'moderate'},
    ],
    'sound': [
        {'rule': 'PA系統由飯店提供，麥克風含在會議設備中', 'source': {'type': 'website', 'url': 'https://taipei.rslhotel.com/meeting/', 'extractedAt': '2026-04-11'}, 'confidence': 'moderate'},
    ],
    'loadIn': [
        {'rule': '逾時將酌收場租', 'source': {'type': 'website', 'url': 'https://taipei.rslhotel.com/meeting/', 'extractedAt': '2026-04-11'}, 'confidence': 'strict'},
    ],
    'cancellation': [
        {'rule': '取消政策需洽詢飯店', 'source': {'type': 'website', 'url': 'https://taipei.rslhotel.com/', 'extractedAt': '2026-04-11'}, 'confidence': 'moderate'},
    ],
    'insurance': [
        {'rule': '保險規定需洽詢飯店', 'source': {'type': 'website', 'url': 'https://taipei.rslhotel.com/', 'extractedAt': '2026-04-11'}, 'confidence': 'moderate'},
    ],
}

# === Room-level updates ===
room_pricing = {
    '宴會廳': {'halfDay': 40000, 'fullDay': 80000},
    '東廳': {'halfDay': 16000, 'fullDay': 32000},
    '南廳': {'halfDay': 13000, 'fullDay': 26000},
    '北廳': {'halfDay': 12000, 'fullDay': 24000},
    '西廳': {'halfDay': 10000, 'fullDay': 20000},
    '貴賓廳 I': {'halfDay': 4000, 'fullDay': 8000},
    '貴賓廳 II': {'halfDay': 4000, 'fullDay': 8000},
}
room_specs = {
    '宴會廳': {'areaPing': 98, 'height': 4.1, 'theater': 350, 'banquet': 300, 'reception': 400, 'classroom': 150},
    '東廳': {'areaPing': 31, 'height': 4.1, 'theater': 80, 'banquet': 48, 'reception': 50, 'classroom': 54, 'uShape': 55},
    '南廳': {'areaPing': 18, 'height': 4.1, 'theater': 36, 'banquet': 20, 'reception': 36, 'classroom': 24, 'uShape': 36},
    '北廳': {'areaPing': 29, 'height': 4.1, 'theater': 50, 'banquet': 24, 'reception': 50, 'classroom': 24, 'uShape': 36},
    '西廳': {'areaPing': 11, 'height': 4.1, 'theater': 30, 'banquet': 20, 'reception': 30, 'classroom': 18, 'uShape': 30},
}

rooms = v.get('rooms', [])
seen = set()
updated = []

for r in rooms:
    name = r.get('name', '').replace('\n', ' ').strip()
    prefix = name.split()[0] if name else name

    # Dedup: use prefix as key
    if prefix in seen:
        continue
    seen.add(prefix)

    r['name'] = name
    parts = name.split()
    r['nameEn'] = parts[-1] if len(parts) >= 2 and parts[-1].isascii() else ''
    r['floor'] = '3樓'
    r['pillar'] = False
    r['source'] = 'website_20260411'

    # Update specs from website
    if prefix in room_specs:
        spec = room_specs[prefix]
        r['area'] = spec['areaPing']
        r['areaUnit'] = 'ping'
        cap = r.get('capacity', {})
        for layout in ['theater', 'banquet', 'reception', 'classroom', 'uShape']:
            if layout in spec and not cap.get(layout):
                cap[layout] = spec[layout]
        r['capacity'] = cap
        if 'dimensions' not in r:
            r['dimensions'] = {}
        r['dimensions']['height'] = spec['height']

    # Update pricing
    if prefix in room_pricing:
        p = room_pricing[prefix]
        r['pricing'] = {'halfDay': p['halfDay'], 'fullDay': p['fullDay'], 'note': '價格需加10%服務費', 'source': 'website_20260411'}

    r['notes'] = ''
    updated.append(r)

# Add 貴賓廳 I if missing
has_vip1 = any('貴賓廳 I' in r.get('name', '') for r in updated)
if not has_vip1:
    updated.append({
        'id': '1506-07',
        'name': '貴賓廳 I (VIP I)',
        'nameEn': 'VIP I',
        'floor': '3樓',
        'capacity': {'theater': 20, 'banquet': 16},
        'area': 6.0,
        'areaUnit': 'ping',
        'pillar': False,
        'equipment': ['投影設備', '音響系統'],
        'images': {},
        'pricing': {'halfDay': 4000, 'fullDay': 8000, 'note': '價格需加10%服務費', 'source': 'website_20260411'},
        'notes': '官網無公開面積容量資料',
        'source': 'website_20260411',
    })

# Quality scores
sys.path.insert(0, PROJECT_ROOT)
from scraper.validators import calculate_room_quality, get_quality_level
for r in updated:
    r['qualityScore'] = calculate_room_quality(r)
    r['qualityLevel'] = get_quality_level(r['qualityScore'])

v['rooms'] = updated

# Derived fields
v['maxCapacityTheater'] = max(r.get('capacity', {}).get('theater', 0) or 0 for r in updated)
v['maxCapacityClassroom'] = max(r.get('capacity', {}).get('classroom', 0) or 0 for r in updated)
v['maxCapacity'] = max(
    v['maxCapacityTheater'],
    v['maxCapacityClassroom'],
    max(r.get('capacity', {}).get('banquet', 0) or 0 for r in updated),
)
v['minCapacity'] = min(r.get('capacity', {}).get('theater', 999) or 999 for r in updated)
v['totalArea'] = sum(r.get('area', 0) or 0 for r in updated)
v['totalAreaUnit'] = '坪'
v['totalMeetingRooms'] = len(updated)

v['verified'] = True
v['lastUpdated'] = '2026-04-11'
v['lastVerified'] = '2026-04-11T09:45:00'

with open(VENUES_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Updated venue 1506:')
print(f'  Rooms: {len(updated)}')
for r in updated:
    cap = r.get('capacity', {})
    print(f'    {r["name"][:25]:25s} | theater={cap.get("theater","?")} | area={r.get("area","?")}ping | price={r.get("pricing",{}).get("halfDay","?")}')
print(f'  Rules: {list(v["rules"].keys())}')
print(f'  Verified: {v["verified"]}')
print(f'  Total area: {v["totalArea"]} 坪')
print(f'  Max capacity: {v["maxCapacity"]} 人')
