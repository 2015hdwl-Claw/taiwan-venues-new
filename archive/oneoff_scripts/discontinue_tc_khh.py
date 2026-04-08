#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將集思台中文心和集思高雄標記為停業
網站已關閉 (404)
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("標記集思台中文心和集思高雄為停業")
print("=" * 100)

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.discontinue_tc_khh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# 處理兩個場地
venues_to_discontinue = [
    {"id": 1497, "name": "集思台中文心會議中心", "reason": "網站已關閉 (HTTP 404)"},
    {"id": 1499, "name": "集思高雄分公司", "reason": "網站已關閉 (HTTP 404)"}
]

discontinued = []

for info in venues_to_discontinue:
    venue = next((v for v in venues if v['id'] == info['id']), None)

    if venue:
        print(f"{venue.get('name')} (ID: {venue['id']}):")

        # 標記為停業
        venue['active'] = False
        venue['discontinuedAt'] = datetime.now().isoformat()
        venue['discontinueReason'] = info['reason']

        print(f"  Active: True → False")
        print(f"  Reason: {info['reason']}")
        print(f"  Discontinued at: {venue['discontinuedAt']}")

        discontinued.append(venue['id'])

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print(f"Discontinued {len(discontinued)} venues")
print("=" * 100)

print("\nDetails:")
for vid in discontinued:
    venue = next((v for v in venues if v['id'] == vid), None)
    print(f"  - {venue.get('name')} (ID: {vid})")

print("\nVenues.json updated.")
