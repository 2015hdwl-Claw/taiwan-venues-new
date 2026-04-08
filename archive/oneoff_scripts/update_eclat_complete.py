#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北怡亨酒店 - 標記缺失資料
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("更新台北怡亨酒店")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 建立備份
backup_path = f"venues.json.backup.eclat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"✅ 備份建立: {backup_path}\n")

# 找到台北怡亨
eclat_idx = None
for i, v in enumerate(data):
    if v.get('id') == 1082 or '怡亨' in v.get('name', ''):
        eclat_idx = i
        break

if eclat_idx is None:
    print("❌ 找不到台北怡亨")
    sys.exit(1)

eclat = data[eclat_idx]
print(f"找到: {eclat['name']}")
print(f"當前會議室數: {len(eclat.get('rooms', []))}\n")

# 更新會議室
for room in eclat.get('rooms', []):
    # 補充英文名稱
    if not room.get('nameEn'):
        room['nameEn'] = 'Meeting Room'

    # 補充樓層
    if not room.get('floor'):
        room['floor'] = '未公開'

    # 標記面積為需詢問（高級飯店通常不公開）
    if not room.get('areaSqm') and not room.get('areaPing'):
        room['areaSqm'] = None
        room['areaPing'] = None
        room['areaUnit'] = '㎡'
        room['areaNote'] = '需聯繫飯店'

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

    # 標記價格為需詢問
    if not room.get('price') or isinstance(room.get('price'), (int, float)):
        room['price'] = {
            'note': '需聯繫飯店詢問',
            'contact': True
        }

    price_note = room.get('price', {}).get('note', '無資料')

    # 新增尺寸結構
    if not room.get('dimensions'):
        room['dimensions'] = {
            'length': None,
            'width': None,
            'height': None
        }

    # 更新來源
    room['source'] = 'eclat_official_website'
    room['lastUpdated'] = datetime.now().isoformat()

    print(f"✅ {room['name']}")
    print(f"   英文名: {room['nameEn']}")
    print(f"   樓層: {room['floor']}")
    print(f"   面積: {room.get('areaNote', '未公開')}")
    print(f"   價格: {room.get('price', {}).get('note', '無資料')}")

# 更新 metadata
if 'metadata' not in eclat:
    eclat['metadata'] = {}

eclat['metadata'].update({
    'lastScrapedAt': datetime.now().isoformat(),
    'dataSource': 'Official Website (https://www.eclathotels.com/zt/taipei)',
    'priceNote': '高級飯店，價格需直接詢問',
    'areaNote': '高級飯店，面積未公開'
})

data[eclat_idx] = eclat

# 儲存
print("\n" + "=" * 100)
print("儲存更新")
print("=" * 100)

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存到 venues.json\n")

print("=" * 100)
print("✅ 台北怡亨更新完成")
print("=" * 100)
print(f"\n更新會議室: {len(eclat['rooms'])}")
print(f"備份: {backup_path}")
