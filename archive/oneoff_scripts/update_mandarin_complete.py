#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據完整 PDF 更新文華東方酒店的場地資料
"""

import json
from datetime import datetime
import sys

# Windows UTF-8 相容
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 文華東方完整資料（從 PDF 第 8 頁容量表）
mandarin_rooms = [
    {
        "id": "1085-01",
        "name": "大宴會廳",
        "nameEn": "The Grand Ballroom",
        "floor": "B2",
        "area": 290,
        "areaUnit": "坪",
        "sqm": 960,
        "ceiling": 7.3,
        "length": 37,
        "width": 26,
        "dimensions": "37x26x7.3m",
        "shape": "長方形",
        "capacity": {
            "theater": 1170,
            "classroom": 624,
            "banquet": 780,
            "reception": 1200
        },
        "pillar": False,
        "pillarCount": 0,
        "pillarInfo": "全区无柱式的空间设计",
        "hasWindow": False,
        "equipment": ["先進影音設備", "投影設備", "音響系統"],
        "features": ["無柱設計", "挑高7.3米", "專屬車道"],
        "images": [],
        "notes": "290坪960平方公尺，全区无柱，挑高7.3米，劇院型可容納1,170位賓客"
    },
    {
        "id": "1085-02",
        "name": "大宴會廳 壹",
        "nameEn": "The Grand Ballroom I",
        "floor": "B2",
        "area": 175,
        "areaUnit": "坪",
        "sqm": 580,
        "ceiling": 7.3,
        "length": 22,
        "width": 26,
        "dimensions": "22x26x7.3m",
        "shape": "長方形",
        "capacity": {
            "theater": 608,
            "classroom": 351,
            "banquet": 384,
            "reception": 650
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["先進影音設備", "投影設備"],
        "features": ["大宴會廳分區"],
        "images": [],
        "notes": "大宴會廳第一分區"
    },
    {
        "id": "1085-03",
        "name": "大宴會廳 貳",
        "nameEn": "The Grand Ballroom II",
        "floor": "B2",
        "area": 115,
        "areaUnit": "坪",
        "sqm": 380,
        "ceiling": 7.3,
        "length": 14.5,
        "width": 26,
        "dimensions": "14.5x26x7.3m",
        "shape": "長方形",
        "capacity": {
            "theater": 399,
            "classroom": 234,
            "banquet": 240,
            "reception": 350
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["先進影音設備", "投影設備"],
        "features": ["大宴會廳分區"],
        "images": [],
        "notes": "大宴會廳第二分區"
    },
    {
        "id": "1085-04",
        "name": "迎賓區",
        "nameEn": "Pre-Function Area",
        "floor": "B2",
        "area": 180,
        "areaUnit": "坪",
        "sqm": 605,
        "ceiling": 0,
        "dimensions": "迎賓區",
        "shape": "長方形",
        "capacity": {
            "reception": 500
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": [],
        "features": ["接待區", "休息區"],
        "images": [],
        "notes": "宴會廳前迎賓區"
    },
    {
        "id": "1085-05",
        "name": "文華廳",
        "nameEn": "The Mandarin Ballroom",
        "floor": "B2",
        "area": 150,
        "areaUnit": "坪",
        "sqm": 500,
        "ceiling": 4,
        "length": 25,
        "width": 20,
        "dimensions": "25x20x4m",
        "shape": "長方形",
        "capacity": {
            "theater": 490,
            "classroom": 300,
            "banquet": 336,
            "reception": 320
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["先進影音設備", "投影設備"],
        "features": ["中型宴會廳"],
        "images": [],
        "notes": "150坪500平方公尺，劇院型490人"
    },
    {
        "id": "1085-06",
        "name": "文華廳 壹",
        "nameEn": "The Mandarin Ballroom I",
        "floor": "B2",
        "area": 80,
        "areaUnit": "坪",
        "sqm": 260,
        "ceiling": 4,
        "length": 12.8,
        "width": 20,
        "dimensions": "12.8x20x4m",
        "shape": "長方形",
        "capacity": {
            "theater": 308,
            "classroom": 150,
            "banquet": 144,
            "reception": 160
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["會議設備", "投影設備"],
        "features": ["文華廳分區"],
        "images": [],
        "notes": "文華廳第一分區"
    },
    {
        "id": "1085-07",
        "name": "文華廳 貳",
        "nameEn": "The Mandarin Ballroom II",
        "floor": "B2",
        "area": 70,
        "areaUnit": "坪",
        "sqm": 240,
        "ceiling": 4,
        "length": 11.8,
        "width": 20,
        "dimensions": "11.8x20x4m",
        "shape": "長方形",
        "capacity": {
            "theater": 280,
            "classroom": 150,
            "banquet": 144,
            "reception": 150
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["會議設備", "投影設備"],
        "features": ["文華廳分區"],
        "images": [],
        "notes": "文華廳第二分區"
    },
    {
        "id": "1085-08",
        "name": "東方廳 壹",
        "nameEn": "Oriental I",
        "floor": "B2",
        "area": 35,
        "areaUnit": "坪",
        "sqm": 120,
        "ceiling": 3.4,
        "length": 10.4,
        "width": 11.5,
        "dimensions": "10.4x11.5x3.4m",
        "shape": "長方形",
        "capacity": {
            "theater": 112,
            "classroom": 60,
            "banquet": 60,
            "reception": 100,
            "boardroom": 27
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["小型會議"],
        "images": [],
        "notes": "東方廳第一間"
    },
    {
        "id": "1085-09",
        "name": "東方廳 貳",
        "nameEn": "Oriental 2",
        "floor": "B2",
        "area": 15,
        "areaUnit": "坪",
        "sqm": 50,
        "ceiling": 3.4,
        "length": 6,
        "width": 8.5,
        "dimensions": "6x8.5x3.4m",
        "shape": "長方形",
        "capacity": {
            "theater": 36,
            "classroom": 18,
            "banquet": 12,
            "reception": 40,
            "boardroom": 12
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "白板"],
        "features": ["小型會議"],
        "images": [],
        "notes": "東方廳第二間"
    },
    {
        "id": "1085-10",
        "name": "東方廳 參",
        "nameEn": "Oriental 3",
        "floor": "B2",
        "area": 15,
        "areaUnit": "坪",
        "sqm": 50,
        "ceiling": 3.4,
        "length": 6,
        "width": 8.5,
        "dimensions": "6x8.5x3.4m",
        "shape": "長方形",
        "capacity": {
            "theater": 36,
            "classroom": 18,
            "banquet": 12,
            "reception": 40,
            "boardroom": 12
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "白板"],
        "features": ["小型會議"],
        "images": [],
        "notes": "東方廳第三間"
    },
    {
        "id": "1085-11",
        "name": "東方廳 貳&參",
        "nameEn": "Oriental 2 & 3",
        "floor": "B2",
        "area": 30,
        "areaUnit": "坪",
        "sqm": 100,
        "ceiling": 3.4,
        "length": 12,
        "width": 8.5,
        "dimensions": "12x8.5x3.4m",
        "shape": "長方形",
        "capacity": {
            "theater": 80,
            "classroom": 42,
            "banquet": 48,
            "reception": 80,
            "boardroom": 27
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "投影設備"],
        "features": ["合併場地"],
        "images": [],
        "notes": "東方廳2、3間合併"
    },
    {
        "id": "1085-12",
        "name": "東方廳 伍",
        "nameEn": "Oriental 5",
        "floor": "B2",
        "area": 20,
        "areaUnit": "坪",
        "sqm": 65,
        "ceiling": 3.4,
        "length": 8.6,
        "width": 7.5,
        "dimensions": "8.6x7.5x3.4m",
        "shape": "長方形",
        "capacity": {
            "theater": 60,
            "classroom": 27,
            "banquet": 36,
            "reception": 60,
            "boardroom": 24
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "白板"],
        "features": ["小型會議"],
        "images": [],
        "notes": "東方廳第五間"
    },
    {
        "id": "1085-13",
        "name": "東方廳 陸",
        "nameEn": "Oriental 6",
        "floor": "B2",
        "area": 20,
        "areaUnit": "坪",
        "sqm": 65,
        "ceiling": 3.4,
        "length": 8.6,
        "width": 7.5,
        "dimensions": "8.6x7.5x3.4m",
        "shape": "長方形",
        "capacity": {
            "theater": 60,
            "classroom": 27,
            "banquet": 36,
            "reception": 60,
            "boardroom": 24
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "白板"],
        "features": ["小型會議"],
        "images": [],
        "notes": "東方廳第六間"
    },
    {
        "id": "1085-14",
        "name": "文華閣",
        "nameEn": "The Grand Salon",
        "floor": "8F",
        "area": 55,
        "areaUnit": "坪",
        "sqm": 185,
        "ceiling": 7.3,
        "length": 8.2,
        "width": 22.7,
        "dimensions": "8.2x22.7x7.3m",
        "shape": "長方形",
        "capacity": {
            "theater": 120,
            "reception": 150
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "投影設備"],
        "features": ["高樓層", "挑高"],
        "images": [],
        "notes": "8樓場地，挑高7.3米"
    }
]

# 更新
for venue in venues:
    if venue['id'] == 1085:
        venue['rooms'] = mandarin_rooms
        venue['verified'] = True
        venue['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")

        print(f"✅ 更新 {venue['name']}")
        print(f"   場地數: {len(venue['rooms'])}")
        print("\n場地列表:")
        for room in venue['rooms']:
            sqm = room.get('sqm', 'N/A')
            theater = room.get('capacity', {}).get('theater', room.get('capacity', {}).get('reception', 'N/A'))
            print(f"   - {room['name']}: {sqm} 平方米, 容量 {theater} 人")
        break

# 備份
import shutil
backup_file = f'venues.json.backup.mo_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_file)

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n📁 備份: {backup_file}")
print("\n✅ 完成！")
