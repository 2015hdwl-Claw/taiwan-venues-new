#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重複場地

保留每個重複場地中的第一個記錄，刪除其他重複的記錄
"""

import json
import shutil
from datetime import datetime
from collections import defaultdict

# 讀取資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 統計場地名稱
name_counts = defaultdict(list)
for venue in venues:
    name = venue.get('name', '')
    if name:
        name_counts[name].append(venue)

# 找出重複的場地
duplicates = {name: venue_list for name, venue_list in name_counts.items() if len(venue_list) > 1}

print(f"找到 {len(duplicates)} 個重複的場地名稱")
print(f"需要刪除 {sum(len(v) - 1 for v in duplicates.values())} 個重複記錄\n")

# 顯示將要刪除的記錄
ids_to_remove = []

for name, venue_list in duplicates.items():
    print(f"場地: {name}")
    print(f"  重複 {len(venue_list)} 次")
    print(f"  保留: ID {venue_list[0]['id']}")
    print(f"  刪除: {', '.join(str(v['id']) for v in venue_list[1:])}")

    # 記錄要刪除的 ID（保留第一個）
    ids_to_remove.extend([v['id'] for v in venue_list[1:]])
    print()

# 確認
print(f"總共將刪除 {len(ids_to_remove)} 個重複記錄")
print(f"刪除後將有 {len(venues) - len(ids_to_remove)} 個場地\n")

# 備份
backup = f'venues.json.backup.before_cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup)
print(f"已建立備份: {backup}\n")

# 過濾掉要刪除的記錄
cleaned_venues = [v for v in venues if v['id'] not in ids_to_remove]

# 儲存清理後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_venues, f, ensure_ascii=False, indent=2)

print(f"✅ 清理完成！")
print(f"   原始記錄: {len(venues)}")
print(f"   清理後: {len(cleaned_venues)}")
print(f"   刪除: {len(ids_to_remove)}")
print(f"   備份: {backup}")
