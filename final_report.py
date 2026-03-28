#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新TBD場地狀態並生成最終報告
"""

import json
from datetime import datetime

print("=" * 100)
print("最終進度報告")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 統計各城市場地
cities = {}
for venue in venues:
    city = venue.get('city', '未知')
    if city not in cities:
        cities[city] = {
            'total': 0,
            'completed': 0,
            'in_progress': 0,
            'not_started': 0,
            'venues': []
        }

    cities[city]['total'] += 1
    cities[city]['venues'].append({
        'id': venue['id'],
        'name': venue['name'],
        'quality': venue.get('metadata', {}).get('qualityScore', 0),
        'url': venue.get('url', 'N/A')
    })

    # 根據品質分數分類
    quality = venue.get('metadata', {}).get('qualityScore', 0)
    if quality >= 70:
        cities[city]['completed'] += 1
    elif quality > 35:
        cities[city]['in_progress'] += 1
    else:
        cities[city]['not_started'] += 1

# 顯示統計
print("Gevenue Statistics:\n")

for city, data in sorted(cities.items()):
    print(f"{city}:")
    print(f"  Total: {data['total']}")
    print(f"  Completed (>=70): {data['completed']}")
    print(f"  In Progress (36-69): {data['in_progress']}")
    print(f"  Not Started (<=35): {data['not_started']}")

    # 顯示場地列表
    print(f"\n  Venues:")
    for v in sorted(data['venues'], key=lambda x: x['quality'], reverse=True):
        status_icon = "[V]" if v['quality'] >= 70 else "[~]" if v['quality'] > 35 else "[X]"
        url_short = v['url'][:50] + "..." if len(v['url']) > 50 else v['url']
        print(f"    {status_icon} ID {v['id']}: {v['name']:40s} Q:{v['quality']:3d} URL:{url_short}")
    print()

# 全場統計
all_venues = len(venues)
high_quality = sum(1 for v in venues if v.get('metadata', {}).get('qualityScore', 0) >= 70)
medium_quality = sum(1 for v in venues if 36 <= v.get('metadata', {}).get('qualityScore', 0) < 70)
low_quality = sum(1 for v in venues if v.get('metadata', {}).get('qualityScore', 0) <= 35)

print("=" * 100)
print("Overall Statistics")
print("=" * 100)
print(f"Total Venues: {all_venues}")
print(f"  High Quality (>=70): {high_quality} ({high_quality/all_venues*100:.1f}%)")
print(f"  Medium Quality (36-69): {medium_quality} ({medium_quality/all_venues*100:.1f}%)")
print(f"  Low Quality (<=35): {low_quality} ({low_quality/all_venues*100:.1f}%)")

# 品質分數分布
quality_scores = [v.get('metadata', {}).get('qualityScore', 0) for v in venues]
avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

print(f"\n平均品質分數: {avg_quality:.1f}")

# 找出Top 10場地
print("\n" + "=" * 100)
print("Top 10 場地（按品質分數）")
print("=" * 100)

top_venues = sorted(venues, key=lambda v: v.get('metadata', {}).get('qualityScore', 0), reverse=True)[:10]

for i, venue in enumerate(top_venues, 1):
    quality = venue.get('metadata', {}).get('qualityScore', 0)
    rooms = venue.get('rooms', [])
    room_count = len(rooms)
    room_info = f"{room_count} 會議室" if room_count > 0 else "無會議室資料"

    print(f"{i}. {venue['name']}")
    print(f"   ID: {venue['id']}, 城市: {venue.get('city', 'N/A')}")
    print(f"   品質分數: {quality}, {room_info}")

print("\n" + "=" * 100)
print("下一步建議")
print("=" * 100)
print("""
1. 優先處理低品質（≤35分）場地：
   - 搜尋這些場地的正確URL
   - 手動查找聯絡資訊
   - 訪問並提取完整資料

2. 提升中品質（36-69分）場地：
   - 補充缺失的會議室資料
   - 添加價格資訊
   - 提取照片和設備清單

3. 需要特別處理的TBD URL場地：
   - 寶麗金婚宴會館 (1520, 1521)
   - 好運來洲際宴展中心 (1523)
   - 林皇宮花園 (1524)
   - 蓮潭國際會館 (1526)
   - 義大世界會議中心 (1527)
   - 福客來南北樓 (1529)
   - 富苑喜宴會館 (1530)
""")

print(f"\n報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
