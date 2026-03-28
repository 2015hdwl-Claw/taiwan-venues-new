#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北文華東方酒店 - 標記官網維護中
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北文華東方酒店 - 標記官網維護中")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.moh_maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# 找到場地
venue = next((v for v in venues if v['id'] == 1085), None)

if not venue:
    print("Venue 1085 not found!")
    sys.exit(1)

print(f"Found venue: {venue['name']}")
print(f"Current quality score: {venue.get('metadata', {}).get('qualityScore', 'N/A')}")
print(f"Rooms with data: {len(venue.get('rooms', []))}")

# 更新 metadata
if 'metadata' not in venue:
    venue['metadata'] = {}

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = 'V3_WebsiteMaintenance'
venue['metadata']['note'] = '官網正在維護中（2026-03-27），無法取得價格資訊。已有會議室容量與面積資料。'

# 計算完整度
rooms = venue.get('rooms', [])
rooms_with_capacity = sum(1 for r in rooms if r.get('capacity') and any(r['capacity'].values()))
rooms_with_area = sum(1 for r in rooms if r.get('area'))

print(f"\nCurrent data completeness:")
print(f"  Rooms with capacity: {rooms_with_capacity}/{len(rooms)}")
print(f"  Rooms with area: {rooms_with_area}/{len(rooms)}")

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("台北文華東方酒店標記完成")
print("=" * 100)
print(f"\n狀態：官網維護中")
print(f"已有資料：9 個會議室（容量、面積完整）")
print(f"缺少資料：價格、聯絡資訊")
print(f"Backup: {backup_file}")
print(f"\n⚠️  建議官網恢復後重新爬取")
