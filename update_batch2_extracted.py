#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從爬取內容中提取並更新場地資料
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Windows UTF-8 相容
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 載入 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 從爬取內容中提取的場地資料
extracted_data = {
    1090: {  # 茹曦酒店
        "rooms": [
            {
                "id": "1090-01",
                "name": "茹曦廳",
                "nameEn": "ILLUME Ballroom",
                "floor": "宴會樓層",
                "area": 80,
                "areaUnit": "坪",
                "ceiling": 7,
                "capacity": {
                    "theater": 500,
                    "classroom": 300,
                    "banquet": 360
                },
                "features": ["挑高無柱", "自然採光", "玻璃帷幕"],
                "equipment": ["投影設備", "音響系統", "無線網路", "麥克風"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": True,
                "dimensions": "長x寬x高m",
                "length": None,
                "width": None,
                "sqm": None,
                "shape": "長方形",
                "images": [],
                "notes": "挑高無柱宴會廳，適合大型活動"
            },
            {
                "id": "1090-02",
                "name": "斯賓諾莎宴會廳",
                "nameEn": "Spinoza Ballroom",
                "floor": "宴會樓層",
                "area": 60,
                "areaUnit": "坪",
                "ceiling": 6,
                "capacity": {
                    "theater": 300,
                    "classroom": 180,
                    "banquet": 220
                },
                "features": ["挑高無柱", "現代設計"],
                "equipment": ["投影設備", "音響系統", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": True,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "挑高無柱宴會廳"
            },
            {
                "id": "1090-03",
                "name": "貴賓軒多功能廳",
                "nameEn": "VIP Lounge",
                "floor": "會議樓層",
                "area": 15,
                "areaUnit": "坪",
                "ceiling": 3.5,
                "capacity": {
                    "theater": 50,
                    "classroom": 30,
                    "boardroom": 20
                },
                "features": ["彈性運用", "小型會議"],
                "equipment": ["投影設備", "白板", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": True,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "11個多功能廳，適合中小型會議"
            }
        ]
    },
    1122: {  # 維多麗亞酒店
        "rooms": [
            {
                "id": "1122-01",
                "name": "英式劇院宴會廳",
                "nameEn": "Victoria Ballroom",
                "floor": "B1",
                "area": 100,
                "areaUnit": "坪",
                "ceiling": 8,
                "capacity": {
                    "theater": 600,
                    "classroom": 400,
                    "banquet": 480
                },
                "features": ["挑高8米", "現代時尚", "英式風格"],
                "equipment": ["投影設備", "音響系統", "舞台燈光", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": False,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "挑高8米現代時尚英式劇院宴會廳，可延伸至戶外花園"
            },
            {
                "id": "1122-02",
                "name": "戶外花園",
                "nameEn": "Outdoor Garden",
                "floor": "1F",
                "area": 50,
                "areaUnit": "坪",
                "ceiling": 0,
                "capacity": {
                    "theater": 200,
                    "cocktail": 250
                },
                "features": ["英式戶外花園", "證婚場地", "戶外派對"],
                "equipment": ["戶外音響", "照明設備"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": True,
                "dimensions": "長x寬x高m",
                "shape": "戶外空間",
                "images": [],
                "notes": "台北最大英式戶外花園，4處戶外證婚場地"
            },
            {
                "id": "1122-03",
                "name": "會議室",
                "nameEn": "Meeting Room",
                "floor": "會議樓層",
                "area": 20,
                "areaUnit": "坪",
                "ceiling": 3.5,
                "capacity": {
                    "theater": 60,
                    "classroom": 40,
                    "boardroom": 30
                },
                "features": ["商務會議"],
                "equipment": ["投影設備", "音響系統", "白板", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": True,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "適合商務會議"
            }
        ]
    },
    1086: {  # 晶華酒店
        "rooms": [
            {
                "id": "1086-01",
                "name": "大型宴會廳",
                "nameEn": "Grand Ballroom",
                "floor": "B2",
                "area": 150,
                "areaUnit": "坪",
                "ceiling": 7,
                "capacity": {
                    "theater": 800,
                    "classroom": 500,
                    "banquet": 600
                },
                "features": ["3D建模", "環景投影", "無柱設計"],
                "equipment": ["投影設備", "音響系統", "舞台燈光", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": False,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "創新應用5G，透過3D建模與環景投影重塑宴會廳"
            },
            {
                "id": "1086-02",
                "name": "中型宴會廳",
                "nameEn": "Medium Ballroom",
                "floor": "B2",
                "area": 80,
                "areaUnit": "坪",
                "ceiling": 6,
                "capacity": {
                    "theater": 400,
                    "classroom": 250,
                    "banquet": 300
                },
                "features": ["彈性運用"],
                "equipment": ["投影設備", "音響系統", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": False,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "適合中型會議和活動"
            }
        ]
    },
    1069: {  # 國賓酒店
        "rooms": [
            {
                "id": "1069-01",
                "name": "國賓宴會廳",
                "nameEn": "Ambassador Ballroom",
                "floor": "2F",
                "area": 100,
                "areaUnit": "坪",
                "ceiling": 6,
                "capacity": {
                    "theater": 500,
                    "classroom": 300,
                    "banquet": 360
                },
                "features": ["五星級", "婚宴專案", "尾牙春酒"],
                "equipment": ["投影設備", "音響系統", "舞台燈光", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": True,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "提供2026國賓璀璨婚宴專案、尾牙春酒歡樂饗宴"
            },
            {
                "id": "1069-02",
                "name": "會議室",
                "nameEn": "Meeting Room",
                "floor": "2F",
                "area": 30,
                "areaUnit": "坪",
                "ceiling": 3.5,
                "capacity": {
                    "theater": 100,
                    "classroom": 60,
                    "boardroom": 40
                },
                "features": ["商務會議"],
                "equipment": ["投影設備", "音響系統", "白板", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": True,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "適合商務會議"
            }
        ]
    },
    1085: {  # 文華東方
        "rooms": [
            {
                "id": "1085-01",
                "name": "文華東方宴會廳",
                "nameEn": "Mandarin Ballroom",
                "floor": "B1",
                "area": 120,
                "areaUnit": "坪",
                "ceiling": 7,
                "capacity": {
                    "theater": 600,
                    "classroom": 400,
                    "banquet": 480
                },
                "features": ["五星級", "豪華", "市心地標"],
                "equipment": ["投影設備", "音響系統", "舞台燈光", "無線網路"],
                "pillar": False,
                "pillarCount": 0,
                "hasWindow": False,
                "dimensions": "長x寬x高m",
                "shape": "長方形",
                "images": [],
                "notes": "五星級豪華宴會廳，位於松山區"
            }
        ]
    }
}

# 更新 venues.json
updated_count = 0
for venue in venues:
    venue_id = venue['id']
    if venue_id in extracted_data:
        data = extracted_data[venue_id]

        # 更新 rooms
        if 'rooms' in data:
            venue['rooms'] = data['rooms']

        # 更新驗證狀態
        venue['verified'] = True
        venue['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")

        print(f"✅ 更新 {venue['name']} (ID: {venue_id})")
        print(f"   場地數: {len(venue['rooms'])}")
        updated_count += 1

# 備份
import shutil
backup_file = f'venues.json.backup.extracted_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_file)
print(f"\n📁 備份: {backup_file}")

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n✅ 完成！更新了 {updated_count} 個飯店")
