#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復寒舍艾美酒店樓層格式不一致問題
統一為 XF 格式 (2F, 3F, 5F)
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*100)
print("修復寒舍艾美酒店樓層格式")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.lemeridien_floors2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# Find 寒舍艾美
lemeridien_idx = next((i for i, v in enumerate(data) if v.get('id') == 1076), None)
if lemeridien_idx is None:
    print("❌ 找不到寒舍艾美酒店")
    sys.exit(1)

lemeridien = data[lemeridien_idx]

print(f"找到寒舍艾美酒店: {lemeridien['name']}")
print(f"會議室數量: {len(lemeridien.get('rooms', []))}\n")

# 樓層對照表（根據官網確認）
floor_mapping = {
    # 2樓會議室
    '軒轅廳': '2F',
    'Leo': '2F',
    '室宿廳': '2F',
    'Pegasus': '2F',
    '角宿廳': '2F',
    'Virgo': '2F',
    '河鼓廳': '2F',
    'Aquila': '2F',
    '北河廳': '2F',
    'Gemini': '2F',
    '畢宿廳': '2F',
    'Taurus': '2F',
    '室宿畢宿廳': '2F',
    'Pegasus-Taurus': '2F',

    # 3樓貴賓室
    '貴賓室I': '3F',
    'VIP Room I': '3F',
    '貴賓室II': '3F',
    'VIP Room II': '3F',

    # 5樓會議室
    'QUUBE': '5F',
    '艾美廳': '5F',
    'Le Grand Ballroom': '5F',
    '翡翠廳': '5F',
    'Jadeite': '5F',
    '珍珠廳': '5F',
    'Pearl': '5F',
    '琥珀廳': '5F',
    'Amber': '5F'
}

# Fix floor formats
corrections = []
for room in lemeridien.get('rooms', []):
    name = room.get('name', '')
    name_en = room.get('nameEn', '')
    old_floor = room.get('floor', '')

    # Determine correct floor
    correct_floor = None
    if name in floor_mapping:
        correct_floor = floor_mapping[name]
    elif name_en in floor_mapping:
        correct_floor = floor_mapping[name_en]

    # Fix if needed
    if correct_floor and old_floor != correct_floor:
        room['floor'] = correct_floor
        corrections.append({
            'room': name,
            'old': old_floor,
            'new': correct_floor
        })

print(f"完成修正: {len(corrections)}\n")
for correction in corrections:
    print(f"  ✅ {correction['room']}: {correction['old']} → {correction['new']}")

# Update venue
data[lemeridien_idx] = lemeridien

# Add metadata
if 'metadata' not in lemeridien:
    lemeridien['metadata'] = {}

lemeridien['metadata']['floorsVerified'] = True
lemeridien['metadata']['floorsVerifiedAt'] = datetime.now().isoformat()
lemeridien['metadata']['floorSource'] = 'https://www.lemeridien-taipei.com/websev?lang=zh-tw&ref=pages&id=60'

# Save
print(f"\n{'='*100}")
print("更新 venues.json")
print(f"{'='*100}")

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存\n")

# Show corrected floors
print(f"{'='*100}")
print("寒舍艾美酒店 - 修正後的樓層配置")
print(f"{'='*100}\n")

# Group by floor
floor_groups = {}
for room in lemeridien.get('rooms', []):
    floor = room.get('floor', 'Unknown')
    if floor not in floor_groups:
        floor_groups[floor] = []
    floor_groups[floor].append(room)

for floor in sorted(floor_groups.keys()):
    rooms = floor_groups[floor]
    print(f"{floor} ({len(rooms)} 間):")
    for room in rooms:
        name = room.get('name', '')
        name_en = room.get('nameEn', '')
        area = room.get('area', '')
        capacity = room.get('capacity', {})
        theater = capacity.get('theater', 'N/A') if capacity else 'N/A'

        print(f"  • {name} ({name_en}) - {area} sqm - {theater} 人")
    print()

print(f"{'='*100}")
print("✅ 寒舍艾美酒店樓層格式已全部修正")
print(f"{'='*100}")
print(f"\n備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
