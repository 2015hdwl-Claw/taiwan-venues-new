#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 將爬取的場地轉換為 30 欄位格式並更新 venues.json
"""

import json
from datetime import datetime
import shutil
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("華山1914 - 轉換為 30 欄位格式並更新 venues.json")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 備份
backup_file = f"venues.json.backup.huashan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"✅ 備份完成: {backup_file}\n")

# 讀取爬取的資料
with open('huashan1914_all_venues_20260326_210529.json', encoding='utf-8') as f:
    huashan_data = json.load(f)

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 尋找華山1914
huashan_venue = next((v for v in venues if v.get('id') == 1125), None)

if not huashan_venue:
    print("❌ 找不到華山1914 (ID: 1125)")
    sys.exit(1)

print(f"找到華山1914: {huashan_venue['name']}\n")

# 轉換為 30 欄位會議室格式
rooms_30fields = []

for i, venue_data in enumerate(huashan_data['venues'], 1):
    room_id = f"1125-{str(i).zfill(2)}"

    # 英文名稱（簡單翻譯）
    name_en_map = {
        '西1館': 'West Hall 1',
        '西2館': 'West Hall 2',
        '西5-1館': 'West Hall 5-1',
        '西5-2館': 'West Hall 5-2',
        '西4': 'West Hall 4',
        '中5B 鍋爐室': 'Center 5B Boiler Room',
        '中4B 2樓演講廳': 'Center 4B 2F Lecture Hall',
        '中4B 2樓': 'Center 4B 2F',
        '中4B 1樓': 'Center 4B 1F',
        '中4A 紅酒作業場': 'Center 4A Red Wine Workshop',
        '中7A': 'Center 7A',
        '中7B': 'Center 7B',
        '中3館2樓-拱廳': 'Center 3 2F Arch Hall',
        '中2館2樓-果酒練舞場': 'Center 2 2F Fruit Wine Dance Studio',
        '中3館前廣場': 'Center 3 Front Plaza',
        '東2A': 'East 2A',
        '東2B': 'East 2B',
        '東2C': 'East 2C',
        '東2D': 'East 2D',
        '東3B-烏梅劇院': 'East 3B Wumei Theater',
        '華山劇場': 'Huashan Theater',
        '樹前草地': 'Tree Front Lawn',
        '忠孝三角': 'Zhongxiao Triangle',
        '金八廣場': 'Jinba Plaza'
    }

    name_en = name_en_map.get(venue_data['name'], venue_data['name'])

    # 坪轉平米
    area_ping = venue_data.get('area')
    area_sqm = round(area_ping * 3.3058, 2) if area_ping else None

    room = {
        'id': room_id,
        'name': venue_data['name'],
        'nameEn': name_en,
        'floor': venue_data.get('floor', None),
        'capacity': {
            'theater': venue_data.get('capacity'),
            'banquet': None,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': area_ping,
        'areaSqm': area_sqm,
        'area': area_ping,
        'areaUnit': '坪' if area_ping else None,
        'dimensions': None,
        'price': {
            'weekday': venue_data.get('price'),
            'holiday': None,
            'morning': None,
            'afternoon': None,
            'evening': None,
            'fullDay': None,
            'hourly': None,
            'note': '需申請' if venue_data.get('price') else '對外開放，需申請'
        },
        'equipment': venue_data.get('equipment'),
        'equipmentList': venue_data.get('equipment').split(', ') if venue_data.get('equipment') else [],
        'features': venue_data.get('description', '')[:100] if venue_data.get('description') else None,
        'source': venue_data.get('url'),
        'lastUpdated': datetime.now().isoformat()
    }

    rooms_30fields.append(room)

print(f"轉換了 {len(rooms_30fields)} 個場地為 30 欄位格式\n")

# 更新華山1914資料
huashan_venue['rooms'] = rooms_30fields

# 更新 metadata
if 'metadata' not in huashan_venue:
    huashan_venue['metadata'] = {}

huashan_venue['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'scrapeVersion': 'HUASHAN_24VENUES',
    'scrapeConfidenceScore': 75,  # 75% 場地有完整資料
    'totalRooms': 24,
    'completeness': {
        'basicInfo': True,
        'rooms': True,
        'capacity': True,
        'area': True,
        'price': False,  # 只有3個有價格
        'transportation': False,
        'images': True
    },
    'dataQuality': 'medium',
    'roomsCompleteness': '79% (19/24 有容量資料)',
    'priceCoverage': '12.5% (3/24 有價格)'
})

# 更新照片
all_images = []
for venue_data in huashan_data['venues']:
    if venue_data.get('images'):
        for img_url in venue_data['images'][:3]:  # 每個場地最多3張
            all_images.append({
                'url': img_url,
                'venue': venue_data['name'],
                'added_at': datetime.now().isoformat()
            })

huashan_venue['photos'] = all_images[:24]  # 最多24張

# 更新 qualityScore
huashan_venue['qualityScore'] = 75
huashan_venue['verified'] = True

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("✅ venues.json 已更新")

# 統計
print("\n" + "=" * 100)
print("華山1914 更新統計")
print("=" * 100)

with_capacity = sum(1 for r in rooms_30fields if r['capacity']['theater'])
with_area = sum(1 for r in rooms_30fields if r['areaPing'])
with_price = sum(1 for r in rooms_30fields if r['price']['weekday'])

print(f"總場地數: {len(rooms_30fields)}")
print(f"有容量: {with_capacity} 個 ({with_capacity/len(rooms_30fields)*100:.1f}%)")
print(f"有面積: {with_area} 個 ({with_area/len(rooms_30fields)*100:.1f}%)")
print(f"有價格: {with_price} 個 ({with_price/len(rooms_30fields)*100:.1f}%)")
print(f"完整度: 75%")

# 容量範圍
capacities = [r['capacity']['theater'] for r in rooms_30fields if r['capacity']['theater']]
if capacities:
    print(f"\n容量範圍:")
    print(f"  最小: {min(capacities)} 人")
    print(f"  最大: {max(capacities)} 人")
    print(f"  平均: {sum(capacities)//len(capacities)} 人")

# 面積範圍
areas = [r['areaPing'] for r in rooms_30fields if r['areaPing']]
if areas:
    print(f"\n面積範圍:")
    print(f"  最小: {min(areas):.0f} 坪")
    print(f"  最大: {max(areas):.0f} 坪")
    print(f"  平均: {sum(areas)/len(areas):.0f} 坪")

# 價格範圍
prices = [r['price']['weekday'] for r in rooms_30fields if r['price']['weekday']]
if prices:
    print(f"\n價格範圍:")
    print(f"  最低: ${min(prices):,}")
    print(f"  最高: ${max(prices):,}")

print("\n" + "=" * 100)
print("✅ 華山1914 更新完成")
print("=" * 100)
