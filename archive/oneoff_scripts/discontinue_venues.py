#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下架場地處理
- 台北兄弟大飯店 (ID: 1053)
- 青青婚宴會館 (ID: 1129)
- 師大進修推廣學院 (ID: 1493)
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("下架場地處理")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 建立備份
backup_path = f"venues.json.backup.discontinue_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"✅ 備份建立: {backup_path}\n")

# 下架的場地 ID
discontinue_ids = [1053, 1129, 1493]  # 台北兄弟、青青婚宴、師大進修
discontinued = []

for venue_id in discontinue_ids:
    # 尋找場地
    venue_idx = next((i for i, v in enumerate(data) if v.get('id') == venue_id), None)

    if venue_idx is not None:
        venue = data[venue_idx]
        print(f"下架: {venue['name']} (ID: {venue_id})")

        # 標記為下架
        venue['active'] = False
        venue['discontinuedAt'] = datetime.now().isoformat()
        venue['discontinuedReason'] = '用戶要求下架'

        discontinued.append(venue['name'])
        data[venue_idx] = venue

if discontinued:
    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已下架 {len(discontinued)} 個場地:")
    for name in discontinued:
        print(f"   - {name}")
else:
    print("沒有找到需要下架的場地")

print(f"\n備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
