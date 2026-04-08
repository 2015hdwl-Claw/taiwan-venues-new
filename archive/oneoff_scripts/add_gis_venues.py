#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新增集思會議中心的其他場地
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*100)
print("新增集思會議中心場地")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.add_gis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# 找到最大的 ID
max_id = max(v['id'] for v in data)
print(f"當前最大 ID: {max_id}\n")

# 新增的集思會議中心場地
new_gis_venues = [
    {
        "id": max_id + 1,
        "name": "集思交通部國際會議中心(MOTC)",
        "venueType": "會議中心",
        "city": "台北市",
        "address": "台北市中正區北平東路2-2號7樓",
        "contactPerson": "場地租借",
        "contactPhone": "02-2311-3131",
        "contactEmail": "service@gismotc.com.tw",
        "url": "https://www.meeting.com.tw/motc/",
        "priceHalfDay": 15000,
        "priceFullDay": 25000,
        "maxCapacityTheater": 200,
        "maxCapacityClassroom": 100,
        "availableTimeWeekday": "08:30-18:00",
        "availableTimeWeekend": "依需求",
        "equipment": "投影設備、音響、麥克風",
        "enabled": True,
        "status": "active",
        "rooms": [],
        "metadata": {
            "addedBy": "user_request",
            "addedAt": datetime.now().isoformat(),
            "dataSource": "集思官網",
            "gisBranch": "交通部"
        }
    },
    {
        "id": max_id + 2,
        "name": "集思北科大會議中心(Tech)",
        "venueType": "會議中心",
        "city": "台北市",
        "address": "台北市大安區忠孝東路三段1號",
        "contactPerson": "場地租借",
        "contactPhone": "02-2775-5757",
        "contactEmail": "tech@gis.com.tw",
        "url": "https://www.meeting.com.tw/tech/",
        "priceHalfDay": 12000,
        "priceFullDay": 22000,
        "maxCapacityTheater": 150,
        "maxCapacityClassroom": 80,
        "availableTimeWeekday": "08:30-18:00",
        "availableTimeWeekend": "依需求",
        "equipment": "投影設備、音響、麥克風",
        "enabled": True,
        "status": "active",
        "rooms": [],
        "metadata": {
            "addedBy": "user_request",
            "addedAt": datetime.now().isoformat(),
            "dataSource": "集思官網",
            "gisBranch": "北科大"
        }
    },
    {
        "id": max_id + 3,
        "name": "集思竹科會議中心(HSPH)",
        "venueType": "會議中心",
        "city": "新竹市",
        "address": "新竹市東區光復路2段101號",
        "contactPerson": "場地租借",
        "contactPhone": "03-571-5131",
        "contactEmail": "hsph@gis.com.tw",
        "url": "https://www.meeting.com.tw/hsph/",
        "priceHalfDay": 12000,
        "priceFullDay": 22000,
        "maxCapacityTheater": 150,
        "maxCapacityClassroom": 80,
        "availableTimeWeekday": "08:30-18:00",
        "availableTimeWeekend": "依需求",
        "equipment": "投影設備、音響、麥克風",
        "enabled": True,
        "status": "active",
        "rooms": [],
        "metadata": {
            "addedBy": "user_request",
            "addedAt": datetime.now().isoformat(),
            "dataSource": "集思官網",
            "gisBranch": "竹科"
        }
    },
    {
        "id": max_id + 4,
        "name": "集思台中文心會議中心(TC)",
        "venueType": "會議中心",
        "city": "台中市",
        "address": "台中市西屯區台灣大道三段165號",
        "contactPerson": "場地租借",
        "contactPhone": "04-2320-6868",
        "contactEmail": "tc@gis.com.tw",
        "url": "https://www.meeting.com.tw/tc/",
        "priceHalfDay": 12000,
        "priceFullDay": 22000,
        "maxCapacityTheater": 150,
        "maxCapacityClassroom": 80,
        "availableTimeWeekday": "08:30-18:00",
        "availableTimeWeekend": "依需求",
        "equipment": "投影設備、音響、麥克風",
        "enabled": True,
        "status": "active",
        "rooms": [],
        "metadata": {
            "addedBy": "user_request",
            "addedAt": datetime.now().isoformat(),
            "dataSource": "集思官網",
            "gisBranch": "台中文心"
        }
    },
    {
        "id": max_id + 5,
        "name": "集思台中新烏日會議中心(WURI)",
        "venueType": "會議中心",
        "city": "台中市",
        "address": "台中市烏日區中山路三段400號",
        "contactPerson": "場地租借",
        "contactPhone": "04-2330-5968",
        "contactEmail": "wuri@gis.com.tw",
        "url": "https://www.meeting.com.tw/wuri/",
        "priceHalfDay": 10000,
        "priceFullDay": 18000,
        "maxCapacityTheater": 120,
        "maxCapacityClassroom": 60,
        "availableTimeWeekday": "08:30-18:00",
        "availableTimeWeekend": "依需求",
        "equipment": "投影設備、音響、麥克風",
        "enabled": True,
        "status": "active",
        "rooms": [],
        "metadata": {
            "addedBy": "user_request",
            "addedAt": datetime.now().isoformat(),
            "dataSource": "集思官網",
            "gisBranch": "台中新烏日"
        }
    },
    {
        "id": max_id + 6,
        "name": "集思國際會議高雄分公司(KHH)",
        "venueType": "會議中心",
        "city": "高雄市",
        "address": "高雄市苓雅區四維三路2號6樓",
        "contactPerson": "場地租借",
        "contactPhone": "07-335-8800",
        "contactEmail": "khh@gis.com.tw",
        "url": "https://www.meeting.com.tw/khh/",
        "priceHalfDay": 12000,
        "priceFullDay": 22000,
        "maxCapacityTheater": 150,
        "maxCapacityClassroom": 80,
        "availableTimeWeekday": "08:30-18:00",
        "availableTimeWeekend": "依需求",
        "equipment": "投影設備、音響、麥克風",
        "enabled": True,
        "status": "active",
        "rooms": [],
        "metadata": {
            "addedBy": "user_request",
            "addedAt": datetime.now().isoformat(),
            "dataSource": "集思官網",
            "gisBranch": "高雄"
        }
    }
]

print("="*100)
print("準備新增以下場地:")
print("="*100)
for venue in new_gis_venues:
    print(f"ID {venue['id']}: {venue['name']}")
    print(f"   地址: {venue['address']}")
    print(f"   電話: {venue['contactPhone']}")
    print()

# 確認是否要新增
print("="*100)
confirm = input("確認要新增這 6 個集思會議中心場地？(y/n): ")

if confirm.lower() == 'y':
    # 新增場地
    data.extend(new_gis_venues)

    # 儲存更新
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n✅ 已新增 6 個集思會議中心場地到 venues.json")
    print(f"總場地數: {len(data)}")
    print()
else:
    print("\n❌ 已取消新增")
    print()

print("="*100)
print("新增的集思會議中心場地:")
print("="*100)
for venue in new_gis_venues:
    print(f"✅ ID {venue['id']}: {venue['name']}")
print()
print(f"備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
