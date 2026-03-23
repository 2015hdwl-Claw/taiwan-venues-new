#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找重複場地

找出資料庫中重複的場地名稱
"""

import json
from collections import defaultdict

# 讀取資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 統計場地名稱
name_counts = defaultdict(list)
for venue in venues:
    name = venue.get('name', '')
    if name:
        name_counts[name].append(venue['id'])

# 找出重複的場地
duplicates = {name: ids for name, ids in name_counts.items() if len(ids) > 1}

print(f"找到 {len(duplicates)} 個重複的場地名稱：\n")

# 按重複次數排序
sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)

for name, ids in sorted_duplicates:
    print(f"* {name}")
    print(f"   出現次數: {len(ids)}")
    print(f"   ID 列表: {', '.join(map(str, ids))}")
    print()

# 統計
total_venues = len(venues)
unique_names = len(name_counts)
duplicate_count = sum(len(ids) - 1 for ids in duplicates.values())

print(f"統計：")
print(f"  總場地數: {total_venues}")
print(f"  唯一名稱數: {unique_names}")
print(f"  重複記錄數: {duplicate_count}")
print(f"  重複場地數: {len(duplicates)}")
