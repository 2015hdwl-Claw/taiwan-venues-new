#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下架台北中山運動中心
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("下架台北中山運動中心")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 備份
backup_file = f"venues.json.backup.zhongshan_discontinue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"✅ 備份完成: {backup_file}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 下架中山運動中心
venue_id = 1334
venue = next((v for v in venues if v.get('id') == venue_id), None)

if venue:
    venue_name = venue.get('name', 'Unknown')
    venue['active'] = False
    venue['discontinuedAt'] = datetime.now().isoformat()
    venue['discontinueReason'] = '官網無場地資料，使用外部預約系統'

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f"✅ 已下架: {venue_name} (ID: {venue_id})")
    print(f"   原因: {venue['discontinueReason']}")
    print(f"   下架時間: {venue['discontinuedAt']}")
else:
    print(f"❌ 找不到場地 (ID: {venue_id})")

print("\n" + "=" * 100)
print("✅ 下架完成")
print("=" * 100)
