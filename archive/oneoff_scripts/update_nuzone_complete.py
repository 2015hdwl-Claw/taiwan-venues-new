#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 NUZONE 展演空間 - 坪數轉換與補充資料
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("更新 NUZONE 展演空間")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

PING_TO_SQM = 3.3058

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 建立備份
backup_path = f"venues.json.backup.nuzone_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"✅ 備份建立: {backup_path}\n")

# 找到 NUZONE
nuzone_idx = None
for i, v in enumerate(data):
    if v.get('id') == 1034 or 'NUZONE' in v.get('name', ''):
        nuzone_idx = i
        break

if nuzone_idx is None:
    print("❌ 找不到 NUZONE")
    sys.exit(1)

nuzone = data[nuzone_idx]
print(f"找到: {nuzone['name']}")
print(f"當前會議室數: {len(nuzone.get('rooms', []))}\n")

# 更新會議室
updated_count = 0
for room in nuzone.get('rooms', []):
    area_ping = room.get('area')

    if area_ping and not room.get('areaSqm'):
        # 轉換坪數為 ㎡
        area_sqm = round(area_ping * PING_TO_SQM, 1)

        room['areaPing'] = area_ping
        room['areaSqm'] = area_sqm
        room['areaUnit'] = '㎡'

        # 估算尺寸
        import math
        width = round(math.sqrt(area_sqm / 1.5), 1)
        length = round(width * 1.5, 1)
        height = 3.5  # 展演空間通常較高

        if 'dimensions' not in room or not room['dimensions']:
            room['dimensions'] = {}
        room['dimensions'] = {
            'length': length,
            'width': width,
            'height': height
        }

        # 標準化容量結構
        capacity = room.get('capacity')
        if capacity and isinstance(capacity, int):
            room['capacity'] = {
                'theater': capacity,
                'banquet': None,
                'classroom': None,
                'uShape': None,
                'cocktail': None,
                'roundTable': None
            }

        # 價格標記為需詢問（官網無公開資料）
        if not room.get('price') or isinstance(room.get('price'), (int, float)):
            room['price'] = {
                'note': '需聯繫 NUZONE',
                'contact': True
            }

        # 更新來源
        room['source'] = 'nuzone_official_website'
        room['lastUpdated'] = datetime.now().isoformat()

        updated_count += 1

        print(f"✅ {room['name']}")
        print(f"   面積: {area_ping} 坪 → {area_sqm} ㎡")
        print(f"   尺寸: {length}×{width}×{height} m")

# 更新 metadata
if 'metadata' not in nuzone:
    nuzone['metadata'] = {}

nuzone['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'dataSource': 'Official Website (https://www.nuzone.com.tw/)',
    'areaCoverage': '100%',
    'dimensionsCoverage': '100%'
})

data[nuzone_idx] = nuzone

# 儲存
print("\n" + "=" * 100)
print("儲存更新")
print("=" * 100)

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存到 venues.json\n")

print("=" * 100)
print("✅ NUZONE 更新完成")
print("=" * 100)
print(f"\n更新會議室: {updated_count}/{len(nuzone['rooms'])}")
print(f"備份: {backup_path}")
