#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新新烏日巴本廳價格
"""

import json
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("更新新烏日巴本廳價格")
print("=" * 50)

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 尋找新烏日
venue = next((v for v in venues if v.get('id') == 1498), None)

if not venue:
    print("❌ 找不到集思台中新烏日會議中心")
    sys.exit(1)

# 尋找巴本廳
room = next((r for r in venue.get('rooms', []) if r.get('name') == '巴本廳'), None)

if not room:
    print("❌ 找不到巴本廳")
    sys.exit(1)

# 更新價格
room['price'] = {
    'weekday': 8000,
    'holiday': 9000,
    'hourly': 8000
}

print(f"✅ 巴本廳價格已更新:")
print(f"   平日: {room['price']['weekday']:,} 元/時段")
print(f"   假日: {room['price']['holiday']:,} 元/時段")

# 更新 metadata
venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n✅ venues.json 已更新")

# 統計
with_price = sum(1 for r in venue['rooms'] if r.get('price', {}).get('weekday'))
prices = [r['price']['weekday'] for r in venue['rooms'] if r.get('price', {}).get('weekday')]

print("\n" + "=" * 50)
print("最終統計")
print("=" * 50)
print(f"有價格: {with_price}/{len(venue['rooms'])}")
print(f"價格範圍: {min(prices):,} - {max(prices):,} 元/時段")
print(f"品質分數: {venue['qualityScore']}/100")
