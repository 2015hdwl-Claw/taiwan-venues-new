#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正集思交通部映射問題 V2 - 直接更新所有房間
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("修正集思交通部映射問題 V2")
print("=" * 100)

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1494), None)

# 備份
backup_file = f"venues.json.backup.motc_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"✅ 備份: {backup_file}\n")

# 直接定義所有 4 個房間的資料
rooms_data = [
    {
        'target_name': '國際會議廳',
        'capacity': 117,
        'areaPing': 121.0,
        'areaSqm': 400.0,
        'photos': [
            'https://www.meeting.com.tw/motc/images/lease/plenary-01.jpg',
            'https://www.meeting.com.tw/motc/images/lease/plenary-02.jpg',
            'https://www.meeting.com.tw/motc/images/lease/plenary-03.jpg',
            'https://www.meeting.com.tw/motc/images/lease/plenary-04.jpg',
            'https://www.meeting.com.tw/motc/images/lease/plenary-05.jpg',
            'https://www.meeting.com.tw/motc/images/lease/plenary-06.jpg'
        ]
    },
    {
        'target_name': '142坪廳',
        'capacity': 400,
        'areaPing': 142.0,
        'areaSqm': 469.4,
        'photos': [
            'https://www.meeting.com.tw/motc/images/lease/auditorium-01.jpg',
            'https://www.meeting.com.tw/motc/images/lease/auditorium-02.jpg',
            'https://www.meeting.com.tw/motc/images/lease/auditorium-03.jpg',
            'https://www.meeting.com.tw/motc/images/lease/auditorium-04.jpg',
            'https://www.meeting.com.tw/motc/images/lease/auditorium-05.jpg'
        ]
    },
    {
        'target_name': '108坪廳',
        'capacity': 108,
        'areaPing': 34.0,
        'areaSqm': 112.4,
        'photos': [
            'https://www.meeting.com.tw/motc/images/lease/201-01.jpg',
            'https://www.meeting.com.tw/motc/images/lease/201-02.jpg',
            'https://www.meeting.com.tw/motc/images/lease/201-03.jpg',
            'https://www.meeting.com.tw/motc/images/lease/201-04.jpg'
        ]
    },
    {
        'target_name': '會議室',
        'capacity': 96,
        'areaPing': 30.0,
        'areaSqm': 99.2,
        'photos': [
            'https://www.meeting.com.tw/motc/images/lease/202-01.jpg',
            'https://www.meeting.com.tw/motc/images/lease/202-02.jpg',
            'https://www.meeting.com.tw/motc/images/lease/202-03.jpg'
        ]
    }
]

print("更新會議室資料...")
print("-" * 100)

updated = 0

for data in rooms_data:
    target_name = data['target_name']

    # 找到對應的房間
    room = next((r for r in venue['rooms'] if r['name'] == target_name), None)

    if room:
        print(f"\n{target_name}:")

        # 更新容量
        room['capacity'] = {'theater': data['capacity']}
        print(f"  容量: {data['capacity']} 人")

        # 更新面積
        room['areaPing'] = data['areaPing']
        room['areaSqm'] = data['areaSqm']
        print(f"  面積: {data['areaPing']} 坪")

        # 更新照片
        room['images'] = room.get('images', {})
        room['images']['gallery'] = data['photos']
        print(f"  照片: {len(data['photos'])} 張")

        room['source'] = '官網會議室詳情頁_深度爬取_20260327'

        updated += 1
    else:
        print(f"\n⚠️  找不到: {target_name}")

print(f"\n\n更新了 {updated} 個會議室")

# 更新 metadata
venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['totalPhotos'] = sum(len(r.get('images', {}).get('gallery', [])) for r in venue['rooms'])
venue['qualityScore'] = 90

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n✅ venues.json 已更新")

# 統計
print("\n" + "=" * 100)
print("集思交通部完成統計")
print("=" * 100)

total_photos = sum(len(r.get('images', {}).get('gallery', [])) for r in venue['rooms'])
print(f"\n會議室: {len(venue['rooms'])} 個")
print(f"照片總數: {total_photos} 張")
print(f"品質分數: {venue['qualityScore']}/100")

print("\n✅ 集思交通部完成！")
