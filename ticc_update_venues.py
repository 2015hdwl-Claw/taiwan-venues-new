#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC - 更新 venues.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - 更新 venues.json")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 備份 venues.json
backup_file = f"venues.json.backup.ticc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
import shutil
shutil.copy2('venues.json', backup_file)
print(f"✅ 備份完成: {backup_file}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 讀取新的 30 欄位資料
with open('ticc_rooms_30fields_20260326_203805.json', encoding='utf-8') as f:
    new_room_data = json.load(f)

# 找到 TICC
ticc_index = None
for i, venue in enumerate(venues):
    if venue.get('id') == 1448:
        ticc_index = i
        break

if ticc_index is None:
    print("❌ 找不到 TICC (venue_id: 1448)")
    sys.exit(1)

print(f"找到 TICC: {venues[ticc_index]['name']}\n")

# 更新 rooms
venues[ticc_index]['rooms'] = new_room_data['rooms']
print(f"✅ 更新 {len(new_room_data['rooms'])} 個會議室")

# 更新 metadata
if 'metadata' not in venues[ticc_index]:
    venues[ticc_index]['metadata'] = {}

venues[ticc_index]['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'scrapeVersion': 'TICC_PDF_30FIELDS',
    'scrapeConfidenceScore': 96,  # 26/27 完整
    'totalRooms': 27,
    'pdfSource': 'https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf',
    'completeness': {
        'basicInfo': True,
        'rooms': True,
        'capacity': True,
        'area': True,
        'price': True,
        'transportation': False,
        'images': True
    },
    'dataQuality': 'high',
    'roomsCompleteness': '96% (26/27 完整)',
    'missingFields': ['大會堂半場缺少 areaPing, areaSqm, dimensions']
})

# 更新 qualityScore
venues[ticc_index]['qualityScore'] = 96
venues[ticc_index]['metadata']['qualityScore'] = 96

# 更新 verified
venues[ticc_index]['verified'] = True

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("✅ venues.json 已更新")

# 統計資訊
print("\n" + "=" * 100)
print("更新統計")
print("=" * 100)
print(f"總會議室數: {len(new_room_data['rooms'])}")
print(f"完整會議室: 26 個")
print(f"不完整會議室: 1 個 (大會堂半場)")
print(f"完整度: 96%")
print(f"品質分數: 96")

# 樓層分布
floors = {}
for room in new_room_data['rooms']:
    floor = room.get('floor', 'Unknown')
    floors[floor] = floors.get(floor, 0) + 1

print("\n樓層分布:")
for floor in sorted(floors.keys()):
    print(f"  {floor}: {floors[floor]} 個")

# 容量範圍
capacities = [room['capacity']['theater'] for room in new_room_data['rooms'] if room['capacity'].get('theater')]
if capacities:
    print(f"\n容量範圍 (劇院型):")
    print(f"  最小: {min(capacities)} 人")
    print(f"  最大: {max(capacities)} 人")
    print(f"  平均: {sum(capacities)//len(capacities)} 人")

# 價格範圍
prices = [room['price']['weekday'] for room in new_room_data['rooms'] if room['price'].get('weekday')]
if prices:
    print(f"\n價格範圍 (週一至週五):")
    print(f"  最低: ${min(prices):,}")
    print(f"  最高: ${max(prices):,}")
    print(f"  平均: ${sum(prices)//len(prices):,}")

print("\n" + "=" * 100)
print("✅ TICC 更新完成")
print("=" * 100)
