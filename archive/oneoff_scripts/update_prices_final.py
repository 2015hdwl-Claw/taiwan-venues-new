#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正確提取的價格更新 venues.json
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("使用正確提取的價格更新 venues.json")
print("=" * 100)

# 讀取正確的價格
with open('prices_v2_extracted.json', encoding='utf-8') as f:
    correct_prices = json.load(f)

# 備份
backup_file = f"venues.json.backup.correct_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"✅ 備份: {backup_file}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 更新竹科
print("=== 集思竹科會議中心 ===\n")
hcph = next((v for v in venues if v['id'] == 1496), None)
if hcph:
    updated = 0
    for room in hcph.get('rooms', []):
        room_name = room.get('name')
        if room_name in correct_prices['hcph']:
            old_price = room.get('price', {})
            new_price = correct_prices['hcph'][room_name]

            room['price'] = new_price

            if old_price != new_price:
                print(f"{room_name}:")
                print(f"  舊: 平日 {old_price.get('weekday', 'N/A'):,} / 假日 {old_price.get('holiday', 'N/A'):,}")
                print(f"  新: 平日 {new_price['weekday']:,} / 假日 {new_price['holiday']:,}")
                updated += 1

    print(f"\n✅ 竹科更新了 {updated} 個會議室")
    hcph['metadata']['lastScrapedAt'] = datetime.now().isoformat()

# 更新新烏日
print("\n\n=== 集思台中新烏日會議中心 ===\n")
wuri = next((v for v in venues if v['id'] == 1498), None)
if wuri:
    updated = 0
    for room in wuri.get('rooms', []):
        room_name = room.get('name')
        if room_name in correct_prices['wuri']:
            old_price = room.get('price', {})
            new_price = correct_prices['wuri'][room_name]

            room['price'] = new_price

            if old_price != new_price:
                print(f"{room_name}:")
                print(f"  舊: 平日 {old_price.get('weekday', 'N/A'):,} / 假日 {old_price.get('holiday', 'N/A'):,}")
                print(f"  新: 平日 {new_price['weekday']:,} / 假日 {new_price['holiday']:,}")
                updated += 1

    print(f"\n✅ 新烏日更新了 {updated} 個會議室")
    wuri['metadata']['lastScrapedAt'] = datetime.now().isoformat()

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n\n✅ venues.json 已更新")

# 最終驗證
print("\n" + "=" * 100)
print("最終驗證")
print("=" * 100)

for venue_name, venue_id, prices_key in [("集思竹科會議中心", 1496, 'hcph'),
                                          ("集思台中新烏日會議中心", 1498, 'wuri')]:
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if venue:
        print(f"\n{venue_name}:")
        print("-" * 100)

        for room in venue.get('rooms', []):
            room_name = room.get('name')
            price = room.get('price', {})
            if price.get('weekday'):
                print(f"  {room_name:12s}: 平日 {price['weekday']:6,} 元 / 假日 {price.get('holiday', 0):6,} 元")

print("\n" + "=" * 100)
print("✅ 價格更新完成！")
print("=" * 100)
