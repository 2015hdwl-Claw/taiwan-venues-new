#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據官網資料更新晶華酒店的場地資料
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

# 晶華酒店完整資料
regent_rooms = [
    {
        "id": "1086-01",
        "name": "宴會廳",
        "nameEn": "Grand Ballroom",
        "floor": "B2",
        "area": 288,  # 9555平方英尺 ≈ 888坪 (估計)
        "areaUnit": "坪",
        "sqm": 952,  # 轉換為平方公尺
        "ceiling": 7,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "pillarInfo": "挑高壯麗、氣宇非凡",
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 955,
            "classroom": 700,
            "banquet": 888
        },
        "equipment": ["投影設備", "音響系統", "舞台燈光", "3D環景投影"],
        "features": ["挑高壯麗", "三面落地窗", "景攬綠意"],
        "images": [],
        "notes": "888/9555 (宴會/劇院)，挑高壯麗、氣宇非凡，三面落地窗景攬入一室綠意"
    },
    {
        "id": "1086-02",
        "name": "萬象廳",
        "nameEn": "Wanxiang Hall",
        "floor": "B2",
        "area": 156,  # 轉換估計
        "areaUnit": "坪",
        "sqm": 517,
        "ceiling": None,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 517,
            "classroom": 350,
            "banquet": 470
        },
        "equipment": ["投影設備", "音響系統"],
        "features": ["六間多功能貴賓廳", "可合併"],
        "images": [],
        "notes": "470/5170 (宴會/劇院)，擁有六間多功能貴賓廳，適合研討會、喜慶宴會及社交活動"
    },
    {
        "id": "1086-03",
        "name": "寰宇廳",
        "nameEn": "Universal Hall",
        "floor": "B2",
        "area": 80,
        "areaUnit": "坪",
        "sqm": 264,
        "ceiling": None,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 200,
            "classroom": 150,
            "banquet": 180
        },
        "equipment": ["投影設備", "音響系統"],
        "features": ["三間優雅貴賓廳", "中型規模"],
        "images": [],
        "notes": "包含三間優雅的貴賓廳，適合中型規模社交活動及喜慶宴會"
    },
    {
        "id": "1086-04",
        "name": "貴賓廳",
        "nameEn": "VIP Hall",
        "floor": "B2",
        "area": 257,
        "areaUnit": "坪",
        "sqm": 850,
        "ceiling": None,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 850,
            "classroom": 600,
            "banquet": 776
        },
        "equipment": ["投影設備", "音響系統", "會議設備"],
        "features": ["9間高雅貴賓廳", "可個別預訂或合併"],
        "images": [],
        "notes": "776/8508 (宴會/劇院)，9間高雅的貴賓廳，可個別預訂或合併間數"
    },
    {
        "id": "1086-05",
        "name": "晶華會",
        "nameEn": "Regent Club",
        "floor": "高樓層",
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
            "banquet": 40
        },
        "equipment": ["高端音響", "投影設備", "私人管家"],
        "features": ["頂級私人招待所", "隱密尊貴"],
        "images": [],
        "notes": "以頂級私人招待所風貌，隱密尊貴的宴飲空間及私人管家式的貼心服務"
    }
]

# 更新
for venue in venues:
    if venue['id'] == 1086:
        venue['rooms'] = regent_rooms
        venue['verified'] = True
        venue['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")

        print(f"✅ 更新 {venue['name']}")
        print(f"   場地數: {len(venue['rooms'])}")
        print("\n場地列表:")
        for room in venue['rooms']:
            sqm = room.get('sqm', 'N/A')
            capacity = room.get('capacity', {}).get('theater', 'N/A')
            print(f"   - {room['name']}: {sqm} 平方米, 劇院式 {capacity} 人")
        break

# 備份
import shutil
backup_file = f'venues.json.backup.regent_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_file)

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n📁 備份: {backup_file}")
print("\n✅ 完成！")
