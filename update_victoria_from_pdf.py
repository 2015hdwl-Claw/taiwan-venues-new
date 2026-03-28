#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新維多麗亞酒店資料（從官方 PDF）
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*100)
print("更新維多麗亞酒店資料（從官方 PDF）")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.victoria_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# Find 維多麗亞酒店
victoria_idx = next((i for i, v in enumerate(data) if v.get('id') == 1122), None)
if not victoria_idx:
    print("❌ 找不到維多麗亞酒店")
    sys.exit(1)

victoria = data[victoria_idx]
print(f"找到: {victoria['name']}")
print(f"當前會議室數量: {len(victoria.get('rooms', []))} 間\n")

# PDF 中的會議室資料
pdf_rooms = [
    {
        'name': '大宴會廳',
        'nameEn': 'Grand Ballroom',
        'floor': '1F',
        'area': 516,
        'capacity': {
            'theater': 820,
            'cocktail': 450,
            'roundTable': 300,
            'uShape': 100,
            'classroom': 270
        },
        'price': {
            'morning': 100000,
            'afternoon': 100000,
            'evening': 300000,
            'fullDay': 360000,
            'overnightSetup': 100000
        }
    },
    {
        'name': '貴賓室',
        'nameEn': 'VIP Room',
        'floor': '1F',
        'area': 564,
        'capacity': {
            'theater': None,
            'cocktail': None,
            'roundTable': None
        },
        'price': {
            'morning': 40000,
            'afternoon': 40000,
            'evening': 120000,
            'fullDay': 140000,
            'overnightSetup': None
        }
    },
    {
        'name': '維多麗亞廳',
        'nameEn': 'Victoria Ballroom',
        'floor': '3F',
        'area': 564,
        'capacity': {
            'theater': 480,
            'cocktail': 270,
            'roundTable': 230,
            'uShape': 80,
            'classroom': 360
        },
        'price': {
            'morning': 80000,
            'afternoon': 80000,
            'evening': 240000,
            'fullDay': 280000,
            'overnightSetup': 80000
        }
    },
    {
        'name': '天璽廳',
        'nameEn': 'Noble Ballroom',
        'floor': '3F',
        'area': 171,
        'capacity': {
            'theater': 220,
            'cocktail': 120,
            'roundTable': 100,
            'uShape': 40,
            'classroom': 150
        },
        'price': {
            'morning': 60000,
            'afternoon': 60000,
            'evening': 180000,
            'fullDay': 240000,
            'overnightSetup': 60000
        }
    },
    {
        'name': '皇冠宴會廳',
        'nameEn': 'Crown Ballroom',
        'floor': '4F',
        'area': 220,
        'capacity': {
            'theater': 280,
            'cocktail': 180,
            'roundTable': 140,
            'uShape': 60,
            'classroom': 220
        },
        'price': {
            'morning': 60000,
            'afternoon': 60000,
            'evening': 180000,
            'fullDay': 240000,
            'overnightSetup': None
        }
    },
    {
        'name': '皇家宴會廳',
        'nameEn': 'Royal Ballroom',
        'floor': '4F',
        'area': 154,
        'capacity': {
            'theater': 220,
            'cocktail': 140,
            'roundTable': 120,
            'uShape': 50,
            'classroom': 150
        },
        'price': {
            'morning': 60000,
            'afternoon': 60000,
            'evening': 180000,
            'fullDay': 240000,
            'overnightSetup': None
        }
    },
    {
        'name': '維多麗亞戶外庭園',
        'nameEn': 'Victoria Garden',
        'floor': '戶外',
        'area': 231,
        'capacity': {
            'theater': None,
            'cocktail': 120
        },
        'price': None
    }
]

# 更新會議室資料
print("更新會議室資料:\n")
updated_count = 0

# 清空並重新添加會議室
victoria['rooms'] = []

for pdf_room in pdf_rooms:
    room = {
        'name': pdf_room['name'],
        'nameEn': pdf_room['nameEn'],
        'floor': pdf_room['floor'],
        'area': f"{pdf_room['area']} sqm",
        'capacity': pdf_room['capacity']
    }

    if pdf_room['price']:
        room['price'] = pdf_room['price']

    victoria['rooms'].append(room)
    updated_count += 1

    print(f"✅ {room['name']} ({room['nameEn']})")
    print(f"   樓層: {room['floor']}")
    print(f"   面積: {room['area']}")
    print(f"   容量: 劇院 {room['capacity'].get('theater', 'N/A')} 人")
    if room.get('price'):
        print(f"   價格: 全日 NT${room['price']['fullDay']:,}")
    print()

# 更新 metadata
if 'metadata' not in victoria:
    victoria['metadata'] = {}

victoria['metadata']['capacitySource'] = 'https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf'
victoria['metadata']['capacityUpdatedAt'] = datetime.now().isoformat()
victoria['metadata']['dataSource'] = 'Official PDF 2022'

data[victoria_idx] = victoria

# 儲存
print("="*100)
print("儲存更新")
print("="*100)

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存更新到 venues.json\n")

print("="*100)
print("✅ 維多麗亞酒店資料更新完成")
print("="*100)
print()
print(f"總共更新: {updated_count} 間會議室")
print(f"包含完整容量和價格資料")
print()
print(f"備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
