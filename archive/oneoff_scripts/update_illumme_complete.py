#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據官網資料更新茹曦酒店的場地資料
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

# 茹曦酒店完整資料
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
            "theater": 1200,
            "classroom": 800,
            "banquet": 1000
        },
        "equipment": ["投影設備", "音響系統", "舞台燈光"],
        "features": ["挑高無柱", "空間寬敞", "可分為A/B廳"],
        "images": [],
        "notes": "836平方公尺，挑高無柱、空間寬敞，可容納至多1,200人，可分為茹曦A廳(220平方公尺)和茹曦B廳"
    },
    {
        "id": "1090-02",
        "name": "斯賓諾莎宴會廳",
        "nameEn": "Spinoza Ballroom",
        "floor": "5F",
        "area": 134,  # 443平方公尺 ≈ 134坪
        "areaUnit": "坪",
        "sqm": 443,
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
            "theater": 400,
            "classroom": 250,
            "banquet": 300
        },
        "equipment": ["投影設備", "音響系統"],
        "features": ["挑高無柱", "獨立接待區", "陽光灑落"],
        "images": [],
        "notes": "443平方公尺，挑高、寬敞、方正且無柱，有著陽光灑落的獨立接待區，60~400人"
    },
    {
        "id": "1090-03",
        "name": "貴賓軒",
        "nameEn": "VIP Lounge",
        "floor": "2F",
        "area": 47,  # 最小 47平方公尺 ≈ 15坪
        "areaUnit": "坪",
        "sqm": 47,
        "ceiling": None,
        "dimensions": "長x寬x高m",
        "length": None,
        "width": None,
        "pillar": False,
        "pillarCount": 0,
        "hasWindow": True,
        "shape": "長方形",
        "capacity": {
            "theater": 220,
            "classroom": 100,
            "boardroom": 50
        },
        "equipment": ["投影設備", "白板", "無線網路"],
        "features": ["12個多功能空間", "靈活彈性"],
        "images": [],
        "notes": "47~271平方公尺，共有多達12個靈活彈性的多功能空間，包含狄德羅廳、康德廳、孔狄亞克廳、霍布斯廳、孟德斯鳩廳"
    },
    {
        "id": "1090-04",
        "name": "狄德羅廳",
        "nameEn": "Diderot Room",
        "floor": "2F",
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
            "theater": 80,
            "classroom": 40,
            "boardroom": 20
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": [],
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用"
    },
    {
        "id": "1090-05",
        "name": "康德廳",
        "nameEn": "Kant Room",
        "floor": "2F",
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
            "theater": 80,
            "classroom": 40,
            "boardroom": 20
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": [],
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用"
    },
    {
        "id": "1090-06",
        "name": "孔狄亞克廳",
        "nameEn": "Condillac Room",
        "floor": "2F",
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
            "theater": 80,
            "classroom": 40,
            "boardroom": 20
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": [],
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用"
    },
    {
        "id": "1090-07",
        "name": "霍布斯廳",
        "nameEn": "Hobbes Room",
        "floor": "2F",
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
            "theater": 60,
            "classroom": 30,
            "boardroom": 15
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "可合併"],
        "images": [],
        "notes": "貴賓軒多功能廳之一，可與其他廳合併使用"
    },
    {
        "id": "1090-08",
        "name": "孟德斯鳩廳",
        "nameEn": "Montesquieu Room",
        "floor": "2F",
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
            "theater": 60,
            "classroom": 30,
            "boardroom": 15
        },
        "equipment": ["會議設備", "投影設備", "白板"],
        "features": ["貴賓軒多功能廳", "獨立"],
        "images": [],
        "notes": "貴賓軒獨立多功能廳"
    },
    {
        "id": "1090-09",
        "name": "玉蘭軒",
        "nameEn": "Magnolia Lounge",
        "floor": "2F",
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
            "theater": 80,
            "classroom": 50,
            "banquet": 80
        },
        "equipment": ["餐飲設備", "音響設備"],
        "features": ["東方韻味", "私人用餐", "獨立包廂5間"],
        "images": [],
        "notes": "獨立包廂5間，充滿東方韻味、設計精美，適合私人用餐場合、特殊活動或夢想婚禮，10~80人"
    }
]

# 更新
for venue in venues:
    if venue['id'] == 1090:
        venue['rooms'] = illumme_rooms
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
backup_file = f'venues.json.backup.illumme_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_file)

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n📁 備份: {backup_file}")
print("\n✅ 完成！")
