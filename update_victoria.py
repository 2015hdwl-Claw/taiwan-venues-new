#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新維多麗亞酒店的場地資料（從 PDF 提取）
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

# 維多麗亞酒店資料（從 PDF 提取）
victoria_rooms = [
    {
        "id": "1122-01",
        "name": "大宴會廳 全區",
        "nameEn": "Grand Ballroom Full Area",
        "floor": "1F",
        "area": 156,
        "areaUnit": "坪",
        "sqm": 516,
        "ceiling": 8,
        "length": 29,
        "width": 18,
        "dimensions": "29x18x8m",
        "shape": "長方形",
        "capacity": {
            "theater": 300,
            "classroom": 270,
            "banquet": 46,
            "cocktail": 450,
            "ushape": 216
        },
        "pillar": False,
        "pillarCount": 0,
        "pillarInfo": "挑高八米無樑柱",
        "hasWindow": False,
        "equipment": ["音響設備", "投影設備", "舞台燈光", "LED燈光"],
        "features": ["挑高8米", "無樑柱", "英式劇院氛圍", "水晶吊燈"],
        "images": [],
        "notes": "156坪516平方公尺，挑高八米無樑柱的婚宴空間設計"
    },
    {
        "id": "1122-02",
        "name": "大宴會廳 A區",
        "nameEn": "Grand Ballroom Area A",
        "floor": "1F",
        "area": 37,
        "areaUnit": "坪",
        "sqm": 123,
        "ceiling": 8,
        "length": 7,
        "width": 18,
        "dimensions": "7x18x8m",
        "shape": "長方形",
        "capacity": {
            "theater": 100,
            "classroom": 45,
            "banquet": 5,
            "cocktail": 30,
            "ushape": 24
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["音響設備", "投影設備"],
        "features": ["彈性空間"],
        "images": [],
        "notes": "可獨立使用或與其他區域合併"
    },
    {
        "id": "1122-03",
        "name": "大宴會廳 B區",
        "nameEn": "Grand Ballroom Area B",
        "floor": "1F",
        "area": 44,
        "areaUnit": "坪",
        "sqm": 147,
        "ceiling": 8,
        "length": 8,
        "width": 18,
        "dimensions": "8x18x8m",
        "shape": "長方形",
        "capacity": {
            "theater": 100,
            "classroom": 54,
            "banquet": 6,
            "cocktail": 33,
            "ushape": 27
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["音響設備", "投影設備"],
        "features": ["彈性空間"],
        "images": [],
        "notes": "可獨立使用或與其他區域合併"
    },
    {
        "id": "1122-04",
        "name": "大宴會廳 C區",
        "nameEn": "Grand Ballroom Area C",
        "floor": "1F",
        "area": 74,
        "areaUnit": "坪",
        "sqm": 246,
        "ceiling": 8,
        "length": 14,
        "width": 18,
        "dimensions": "14x18x8m",
        "shape": "長方形",
        "capacity": {
            "theater": 230,
            "classroom": 126,
            "banquet": 15,
            "cocktail": 74,
            "ushape": 29
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["音響設備", "投影設備"],
        "features": ["最大分區"],
        "images": [],
        "notes": "最大的分區，適合中型活動"
    },
    {
        "id": "1122-05",
        "name": "維多麗亞戶外庭園",
        "nameEn": "Victoria Garden",
        "floor": "1F",
        "area": 70,
        "areaUnit": "坪",
        "sqm": 231,
        "ceiling": 0,
        "length": 28,
        "width": 16,
        "dimensions": "28x16m",
        "shape": "戶外空間",
        "capacity": {
            "theater": 270,
            "cocktail": 408
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["戶外音響"],
        "features": ["英式戶外花園", "證婚場地"],
        "images": [],
        "notes": "台北最大英式戶外花園，適合證婚儀式、雞尾酒會"
    },
    {
        "id": "1122-06",
        "name": "維多麗亞廳 全區",
        "nameEn": "Victoria Ballroom Full Area",
        "floor": "3F",
        "area": 171,
        "areaUnit": "坪",
        "sqm": 564,
        "ceiling": 4,
        "length": 32,
        "width": 18,
        "dimensions": "32x18x4m",
        "shape": "長方形",
        "capacity": {
            "theater": 270,
            "classroom": 248,
            "banquet": 36,
            "cocktail": 450,
            "ushape": 216
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["音響設備", "投影設備"],
        "features": ["可分為 A/B/C 區"],
        "images": [],
        "notes": "3樓大型宴會廳，可彈性分區使用"
    },
    {
        "id": "1122-07",
        "name": "天璽廳 全區",
        "nameEn": "Noble Ballroom Full Area",
        "floor": "3F",
        "area": 52,
        "areaUnit": "坪",
        "sqm": 171,
        "ceiling": 4,
        "length": 23,
        "width": 8,
        "dimensions": "23x8x4m",
        "shape": "長方形",
        "capacity": {
            "theater": 130,
            "classroom": 72,
            "banquet": 12,
            "cocktail": 220,
            "ushape": 104
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "equipment": ["音響設備", "投影設備"],
        "features": ["可分為 N1/N2/N3"],
        "images": [],
        "notes": "3樓中型宴會廳，可分為3間獨立包廂"
    },
    {
        "id": "1122-08",
        "name": "天璽廳 N1",
        "nameEn": "Noble Ballroom 1",
        "floor": "3F",
        "area": 17,
        "areaUnit": "坪",
        "sqm": 57,
        "ceiling": 4,
        "length": 8,
        "width": 8,
        "dimensions": "8x8x4m",
        "shape": "正方形",
        "capacity": {
            "theater": 40,
            "classroom": 27,
            "banquet": 3,
            "cocktail": 18,
            "ushape": 15
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "投影設備"],
        "features": ["小型包廂"],
        "images": [],
        "notes": "16-20人的包廂服務"
    },
    {
        "id": "1122-09",
        "name": "天璽廳 N2",
        "nameEn": "Noble Ballroom 2",
        "floor": "3F",
        "area": 17,
        "areaUnit": "坪",
        "sqm": 57,
        "ceiling": 4,
        "length": 8,
        "width": 8,
        "dimensions": "8x8x4m",
        "shape": "正方形",
        "capacity": {
            "theater": 40,
            "classroom": 27,
            "banquet": 3,
            "cocktail": 18,
            "ushape": 15
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "投影設備"],
        "features": ["小型包廂"],
        "images": [],
        "notes": "16-20人的包廂服務"
    },
    {
        "id": "1122-10",
        "name": "天璽廳 N3",
        "nameEn": "Noble Ballroom 3",
        "floor": "3F",
        "area": 17,
        "areaUnit": "坪",
        "sqm": 57,
        "ceiling": 4,
        "length": 8,
        "width": 8,
        "dimensions": "8x8x4m",
        "shape": "正方形",
        "capacity": {
            "theater": 40,
            "classroom": 27,
            "banquet": 3,
            "cocktail": 18,
            "ushape": 15
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["會議設備", "投影設備"],
        "features": ["小型包廂"],
        "images": [],
        "notes": "16-20人的包廂服務"
    },
    {
        "id": "1122-11",
        "name": "戶外花園",
        "nameEn": "Garden",
        "floor": "4F",
        "area": 70,
        "areaUnit": "坪",
        "sqm": 231,
        "ceiling": 0,
        "length": 13,
        "width": 18,
        "dimensions": "13x18m",
        "shape": "戶外空間",
        "capacity": {
            "theater": 220,
            "cocktail": 220
        },
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "equipment": ["戶外音響"],
        "features": ["4樓戶外花園"],
        "images": [],
        "notes": "4樓戶外花園，適合小型活動"
    }
]

# 更新
for venue in venues:
    if venue['id'] == 1122:
        venue['rooms'] = victoria_rooms
        venue['verified'] = True
        venue['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")
        print(f"✅ 更新 {venue['name']}")
        print(f"   場地數: {len(venue['rooms'])}")
        print("\n場地列表:")
        for room in venue['rooms']:
            print(f"   - {room['name']}: {room.get('sqm', 0)} 平方米, 劇院式 {room['capacity']['theater']} 人")
        break

# 備份
import shutil
backup_file = f'venues.json.backup.victoria_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_file)

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n📁 備份: {backup_file}")
print("✅ 完成！")
