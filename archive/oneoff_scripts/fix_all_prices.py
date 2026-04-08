#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正竹科與新烏日所有會議室的價格
根據 Stage 1 技術檢測的結果
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("修正竹科與新烏日價格資料")
print("=" * 100)

# 備份
backup_file = f"venues.json.backup.price_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"✅ 備份: {backup_file}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 竹科正確價格（根據 Stage 1 檢測）
hcph_prices = {
    '巴哈廳': {'weekday': 7000, 'holiday': 7500},
    '羅西尼廳': {'weekday': 8500, 'holiday': 9000},  # weekday 錯誤：500 → 8500
    '鄧肯廳': {'weekday': 5000, 'holiday': 5000},
    '愛因斯坦廳': {'weekday': 11000, 'holiday': 12000},
    '愛迪生廳': {'weekday': 7500, 'holiday': 7500}
}

# 新烏日正確價格（根據 Stage 1 檢測與手動確認）
wuri_prices = {
    '瓦特廳': {'weekday': 22000, 'holiday': 24000},
    '巴本廳': {'weekday': 8000, 'holiday': 9000},  # 已在 update_baban_price.py 修正
    '富蘭克林廳': {'weekday': 9000, 'holiday': 10000},
    '史蒂文生廳': {'weekday': 2500, 'holiday': 2800}
}

# 修正竹科
print("\n=== 集思竹科會議中心 ===")
hcph = next((v for v in venues if v['id'] == 1496), None)
if hcph:
    for room in hcph.get('rooms', []):
        room_name = room.get('name')
        if room_name in hcph_prices:
            old_price = room.get('price', {})
            correct_price = hcph_prices[room_name]

            room['price'] = correct_price

            print(f"\n{room_name}:")
            print(f"  舊價格: weekday={old_price.get('weekday')}, holiday={old_price.get('holiday')}")
            print(f"  新價格: weekday={correct_price['weekday']}, holiday={correct_price['holiday']}")

    hcph['metadata']['lastScrapedAt'] = datetime.now().isoformat()

# 修正新烏日
print("\n\n=== 集思台中新烏日會議中心 ===")
wuri = next((v for v in venues if v['id'] == 1498), None)
if wuri:
    for room in wuri.get('rooms', []):
        room_name = room.get('name')
        if room_name in wuri_prices:
            old_price = room.get('price', {})
            correct_price = wuri_prices[room_name]

            room['price'] = correct_price

            print(f"\n{room_name}:")
            print(f"  舊價格: weekday={old_price.get('weekday')}, holiday={old_price.get('holiday')}")
            print(f"  新價格: weekday={correct_price['weekday']}, holiday={correct_price['holiday']}")

    wuri['metadata']['lastScrapedAt'] = datetime.now().isoformat()

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n\n✅ venues.json 已更新")

# 驗證報告
print("\n" + "=" * 100)
print("驗證報告")
print("=" * 100)

for venue_name, venue_id, correct_prices in [("集思竹科會議中心", 1496, hcph_prices),
                                              ("集思台中新烏日會議中心", 1498, wuri_prices)]:
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if venue:
        print(f"\n{venue_name}:")

        with_price = sum(1 for r in venue['rooms'] if r.get('price', {}).get('weekday'))
        print(f"  有價格: {with_price}/{len(venue['rooms'])}")

        prices = [r['price']['weekday'] for r in venue['rooms'] if r.get('price', {}).get('weekday')]
        if prices:
            print(f"  價格範圍: {min(prices):,} - {max(prices):,} 元/時段")

        # 列出所有價格
        for room in venue['rooms']:
            p = room.get('price', {})
            if p.get('weekday'):
                print(f"    {room['name']}: 平日 {p['weekday']:,} / 假日 {p.get('holiday', 0):,}")

print("\n" + "=" * 100)
print("✅ 價格修正完成")
print("=" * 100)
