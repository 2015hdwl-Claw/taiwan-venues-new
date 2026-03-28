#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新剩餘 3 家飯店的場地資料
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

# 1069 台北國賓大飯店
ambassador_rooms = [
    {
        "id": "1069-01",
        "name": "國賓宴會廳",
        "nameEn": "Ambassador Ballroom",
        "floor": "2F",
        "area": 100,
        "areaUnit": "坪",
        "sqm": 330,
        "ceiling": 6,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 500,
            "classroom": 300,
            "banquet": 360
        },
        "equipment": ["投影設備", "音響系統", "舞台燈光"],
        "features": ["五星級", "婚宴專案"],
        "images": [],
        "notes": "提供2026國賓璀璨婚宴專案、尾牙春酒歡樂饗宴"
    }
]

# 1086 台北晶華酒店
regent_rooms = [
    {
        "id": "1086-01",
        "name": "晶華大宴會廳",
        "nameEn": "Regent Grand Ballroom",
        "floor": "B2",
        "area": 150,
        "areaUnit": "坪",
        "sqm": 495,
        "ceiling": 7,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": False,
        "shape": "長方形",
        "capacity": {
            "theater": 800,
            "classroom": 500,
            "banquet": 600
        },
        "equipment": ["投影設備", "音響系統", "舞台燈光", "3D環景投影"],
        "features": ["16間場地", "3D建模", "環景投影"],
        "images": [],
        "notes": "16間兼具各種功能的宴會、會議場地，結合最先進的設施"
    }
]

# 1090 茹曦酒店 (基於抓取的資料)
illumme_rooms = [
    {
        "id": "1090-01",
        "name": "茹曦廳",
        "nameEn": "ILLUME Ballroom",
        "floor": "2F",
        "area": 253,  # 836平方公尺 ≈ 253坪
        "areaUnit": "坪",
        "sqm": 836,
        "ceiling": None,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "pillarInfo": "挑高無柱",
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 1000,
            "classroom": 600,
            "banquet": 700
        },
        "equipment": ["投影設備", "音響系統", "舞台燈光"],
        "features": ["挑高無柱", "空間寬敞", "最大活動空間"],
        "images": [],
        "notes": "836平方公尺，挑高無柱、空間寬敞，多達1,000人的盛大晚宴"
    },
    {
        "id": "1090-02",
        "name": "斯賓諾莎宴會廳",
        "nameEn": "Spinoza Ballroom",
        "floor": "5F",
        "area": 121,  # 估計 400平方公尺
        "areaUnit": "坪",
        "sqm": 400,
        "ceiling": None,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "pillarInfo": "挑高無柱",
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 300,
            "classroom": 200,
            "banquet": 240
        },
        "equipment": ["投影設備", "音響系統"],
        "features": ["挑高無柱", "獨立接待區", "陽光灑落"],
        "images": [],
        "notes": "5F，兼具時尚大方與美麗優雅，有著陽光灑落的獨立接待區"
    },
    {
        "id": "1090-03",
        "name": "貴賓軒多功能廳",
        "nameEn": "VIP Lounge",
        "floor": "會議樓層",
        "area": None,
        "areaUnit": "坪",
        "sqm": None,
        "ceiling": None,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 50,
            "classroom": 30,
            "boardroom": 20
        },
        "equipment": ["投影設備", "白板", "無線網路"],
        "features": ["彈性運用", "小型會議"],
        "images": [],
        "notes": "11個彈性運用的多功能廳，適合中小型會議"
    }
]

# 更新飯店資料
updates = {
    1069: ambassador_rooms,
    1086: regent_rooms,
    1090: illumme_rooms
}

updated_count = 0

for venue in venues:
    venue_id = venue['id']
    if venue_id in updates:
        venue['rooms'] = updates[venue_id]
        venue['verified'] = True
        venue['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")

        print(f"✅ 更新 {venue['name']} (ID: {venue_id})")
        print(f"   場地數: {len(venue['rooms'])}")
        for room in venue['rooms']:
            print(f"   - {room['name']}: {room.get('sqm', 'N/A')} 平方米, {room['capacity']['theater']} 人")

        updated_count += 1

# 備份
import shutil
backup_file = f'venues.json.backup.remaining3_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_file)

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n📁 備份: {backup_file}")
print(f"\n✅ 完成！更新了 {updated_count} 個飯店")
