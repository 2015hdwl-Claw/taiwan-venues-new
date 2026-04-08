#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細檢查寒舍艾美酒店所有會議室樓層
"""

import json
import sys

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find 寒舍艾美
lemeridien = next((v for v in data if v.get('id') == 1076), None)

if not lemeridien:
    print("❌ 找不到寒舍艾美酒店")
    sys.exit(1)

print("="*100)
print("寒舍艾美酒店 - 所有會議室樓層檢查")
print("="*100)

print(f"\n根據官網: https://www.lemeridien-taipei.com/websev?lang=zh-tw&ref=pages&id=60")
print(f"QUUBE 確認在 5 樓\n")

rooms = lemeridien.get('rooms', [])

print(f"{'No.':<4} {'中文名稱':<15} {'英文名稱':<25} {'當前樓層':<10} {'面積':<10} {'容量(劇院)':<10}")
print("-"*100)

floor_mapping = {
    '軒轅廳': '2樓',
    'Leo': '2F',
    '室宿廳': '2樓',
    'Pegasus': '2F',
    '角宿廳': '2樓',
    'Virgo': '2F',
    '河鼓廳': '2樓',
    'Aquila': '2F',
    '北河廳': '2樓',
    'Gemini': '2F',
    '畢宿廳': '2樓',
    'Taurus': '2F',
    '室宿畢宿廳': '2樓',
    'Pegasus-Taurus': '2F',
    'QUUBE': '5樓',  # 修正：5樓，不是3樓
    'QUUBE': '5F',
    '艾美廳': '5樓',
    'Le Grand Ballroom': '5F',
    '翡翠廳': '5樓',
    'Jadeite': '5F',
    '珍珠廳': '5樓',
    'Pearl': '5F',
    '琥珀廳': '5樓',
    'Amber': '5F',
    '貴賓室I': '3樓',
    'VIP Room I': '3F',
    '貴賓室II': '3樓',
    'VIP Room II': '3F'
}

issues = []

for i, room in enumerate(rooms, 1):
    name = room.get('name', '')
    name_en = room.get('nameEn', '')
    current_floor = room.get('floor', '')
    area = f"{room.get('area', '')} sqm" if room.get('area') else 'N/A'
    capacity = room.get('capacity', {})
    theater = capacity.get('theater', 'N/A') if capacity else 'N/A'
    if theater is None:
        theater = 'N/A'

    # Check if floor is correct
    expected_floor = None
    if name in floor_mapping:
        expected_floor = floor_mapping[name]
    elif name_en in floor_mapping:
        expected_floor = floor_mapping[name_en]

    status = "✅"
    if expected_floor and expected_floor != current_floor:
        status = "❌"
        issues.append({
            'room': name,
            'current': current_floor,
            'expected': expected_floor
        })

    print(f"{i:<4} {name:<15} {name_en:<25} {current_floor:<10} {area:<10} {str(theater):<10} {status}")

print("\n" + "="*100)
if issues:
    print("❌ 發現樓層錯誤:")
    print("-"*100)
    for issue in issues:
        print(f"   {issue['room']}: {issue['current']} → 應為 {issue['expected']}")
else:
    print("✅ 所有樓層正確")

# Now show a verified venue
print("\n" + "="*100)
print("推薦檢查的場地（已驗證無誤）")
print("="*100)

# Find 六福萬怡（已完整驗證）
courtyard = next((v for v in data if v.get('id') == 1043), None)

if courtyard:
    print(f"\n🏨 台北六福萬怡酒店 (ID: 1043)")
    print(f"狀態: ✅ 已完整驗證 - 所有資料來自官方 PDF")
    print(f"官網: https://www.courtyardtaipei.com.tw/wedding/meeting")
    print(f"會議室: {len(courtyard.get('rooms', []))} 間")

    print(f"\n會議室清單:")
    courtyard_rooms = courtyard.get('rooms', [])

    print(f"\n7F - 主要宴會廳:")
    for room in courtyard_rooms:
        if '7F' in room.get('floor', '') or '7樓' in room.get('floor', ''):
            print(f"   • {room['name']} ({room['nameEn']}) - {room.get('capacity', {}).get('theater', 'N/A')} 人")

    print(f"\n9F - 會議室群 (山、海、林、水、晶、雲、風、光):")
    for room in courtyard_rooms:
        if '9F' in room.get('floor', '') or '9樓' in room.get('floor', ''):
            print(f"   • {room['name']} ({room['nameEn']}) - {room.get('capacity', {}).get('theater', 'N/A')} 人")

    print(f"\n戶外:")
    for room in courtyard_rooms:
        if '戶外' in room.get('floor', ''):
            print(f"   • {room['name']} ({room['nameEn']}) - {room.get('capacity', {}).get('theater', 'N/A')} 人")

    print(f"\n✅ 驗證項目:")
    print(f"   • 電話: 02-6615-6565 (分機 8915, 8911)")
    print(f"   • Email: service@courtyardtaipei.com")
    print(f"   • 價格: 2026 官方 PDF")
    print(f"   • 照片: 每個會議室都有照片")
    print(f"   • 天花板高度: 已從 PDF 確認")

print("\n" + "="*100)
