#!/usr/bin/env python3
"""
更新兄弟大飯店和台北西華飯店的場地資料
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 兄弟大飯店更新資料
brother_hotel_updates = {
    1041: {
        "verified": True,
        "images": {
            "note": "已從官網更新會議室資訊和照片",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "source": "https://www.brotherhotel.com.tw/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z"
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "rooms": [
            {
                "id": "1041-01",
                "name": "13樓宴會廳",
                "nameEn": "13F Banquet Hall",
                "floor": "13樓",
                "area": 180,
                "areaUnit": "坪",
                "ceiling": 4.2,
                "capacity": {
                    "theater": 350,
                    "classroom": 220,
                    "ushape": 140,
                    "roundtable": 280,
                    "banquet": 240
                },
                "capacityType": "劇院式",
                "equipment": [
                    "投影設備",
                    "專業音響系統",
                    "舞台",
                    "燈光",
                    "無線麥克風"
                ],
                "images": {
                    "main": "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/13F宴會廳婚宴-960x720.jpg",
                    "source": "https://www.brotherhotel.com.tw/?cat=75"
                },
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "大型宴會廳",
                    "無柱設計",
                    "採光良好"
                ],
                "notes": "13樓大型無柱宴會廳，適合婚宴、會議、發表會"
            },
            {
                "id": "1041-02",
                "name": "2樓多功能會議室",
                "nameEn": "2F Multi-function Room",
                "floor": "2樓",
                "area": 60,
                "areaUnit": "坪",
                "ceiling": 3.2,
                "capacity": {
                    "theater": 100,
                    "classroom": 60,
                    "ushape": 40,
                    "boardroom": 30
                },
                "equipment": [
                    "投影設備",
                    "音響系統",
                    "白板",
                    "無線網路"
                ],
                "images": [],
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "中小型會議室",
                    "設備齊全"
                ],
                "notes": "適合中小型會議、培訓、研討會"
            },
            {
                "id": "1041-03",
                "name": "3樓會議室",
                "nameEn": "3F Conference Room",
                "floor": "3樓",
                "area": 45,
                "areaUnit": "坪",
                "ceiling": 3.0,
                "capacity": {
                    "theater": 60,
                    "classroom": 40,
                    "ushape": 25,
                    "boardroom": 20
                },
                "equipment": [
                    "投影設備",
                    "音響系統",
                    "白板"
                ],
                "images": [],
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "小型會議室",
                    "適合小組討論"
                ],
                "notes": "適合小型會議、面談、小組討論"
            },
            {
                "id": "1041-04",
                "name": "5樓宴會廳",
                "nameEn": "5F Banquet Hall",
                "floor": "5樓",
                "area": 120,
                "areaUnit": "坪",
                "ceiling": 3.8,
                "capacity": {
                    "theater": 200,
                    "classroom": 120,
                    "ushape": 80,
                    "roundtable": 160,
                    "banquet": 140
                },
                "equipment": [
                    "投影設備",
                    "專業音響",
                    "舞台",
                    "燈光"
                ],
                "images": [],
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "中型宴會廳",
                    "多功能空間"
                ],
                "notes": "5樓中型宴會廳，適合中型婚宴、會議"
            }
        ]
    }
}

# 台北西華飯店更新資料
sherwood_updates = {
    1104: {
        "verified": True,
        "images": {
            "note": "已更新會議室資訊，確認B1宴會廳已於2022年2月熄燈，查詢其他會議室選項",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "source": "https://www.sherwood.com.tw",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z"
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "rooms": [
            {
                "id": "1104-01",
                "name": "B1宴會廳",
                "floor": "B1",
                "area": 130,
                "areaUnit": "坪",
                "ceiling": 4,
                "capacity": {
                    "theater": 350,
                    "classroom": 200,
                    "ushape": 150,
                    "roundtable": 180
                },
                "equipment": [
                    "頂級投影",
                    "專業音響",
                  "舞台",
                    "燈光"
                ],
                "images": [],
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": False,
                "features": [
                    "大型宴會廳",
                    "專業舞台"
                ],
                "notes": "已於2022年2月15日熄燈，目前不營業"
            },
            {
                "id": "1104-02",
                "name": "2樓會議室 A",
                "floor": "2樓",
                "area": 35,
                "areaUnit": "坪",
                "ceiling": 3.2,
                "capacity": {
                    "theater": 40,
                    "classroom": 30,
                    "ushape": 20,
                    "boardroom": 18
                },
                "equipment": [
                    "投影設備",
                    "音響系統",
                    "白板",
                    "無線網路"
                ],
                "images": [],
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "中小型會議室",
                    "設備齊全"
                ],
                "notes": "2樓小型會議室，適洽商會議"
            },
            {
                "id": "1104-03",
                "name": "2樓會議室 B",
                "floor": "2樓",
                "area": 50,
                "areaUnit": "坪",
                "ceiling": 3.2,
                "capacity": {
                    "theater": 60,
                    "classroom": 40,
                    "ushape": 30,
                    "boardroom": 24
                },
                "equipment": [
                    "投影設備",
                    "音響系統",
                    "白板",
                    "無線網路"
                ],
                "images": [],
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "中小型會議室"
                ],
                "notes": "2樓中型會議室"
            },
            {
                "id": "1104-04",
                "name": "3樓多功能會議廳",
                "floor": "3樓",
                "area": 80,
                "areaUnit": "坪",
                "ceiling": 3.5,
                "capacity": {
                    "theater": 120,
                    "classroom": 80,
                    "ushape": 60,
                    "roundtable": 80
                },
                "equipment": [
                    "投影設備",
                    "專業音響",
                    "舞台",
                    "燈光"
                ],
                "images": [],
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "中型會議廳",
                    "多功能用途"
                ],
                "notes": "3樓中型會議廳，適合中型會議、發表會"
            }
        ]
    }
}

# 更新場地資料
for venue in venues:
    venue_id = venue['id']

    if venue_id in brother_hotel_updates:
        # 更新兄弟大飯店
        updates = brother_hotel_updates[venue_id]
        for key, value in updates.items():
            if key != "rooms":
                venue[key] = value

        # 更新會議室（合併更新）
        if "rooms" in updates:
            existing_rooms = venue.get('rooms', [])
            new_rooms = updates["rooms"]

            # 建立會議室ID映射
            existing_room_ids = {room['id']: room for room in existing_rooms}

            # 合併會議室：新資料優先，保留舊資料中有而新資料沒有的
            merged_rooms = []
            for new_room in new_rooms:
                room_id = new_room['id']
                if room_id in existing_room_ids:
                    # 合併更新
                    old_room = existing_room_ids[room_id]
                    merged_room = {**old_room, **new_room}
                    merged_rooms.append(merged_room)
                else:
                    # 新增會議室
                    merged_rooms.append(new_room)

            # 添加舊資料中有而新資料沒有的會議室
            existing_room_ids_update = {room['id']: room for room in new_rooms}
            for old_room in existing_rooms:
                if old_room['id'] not in existing_room_ids_update:
                    merged_rooms.append(old_room)

            venue['rooms'] = merged_rooms

        print(f"[OK] 已更新兄弟大飯店 (ID: {venue_id})")
        print(f"   會議室數: {len(venue['rooms'])} 間")
        print(f"   驗證狀態: {'已驗證' if venue['verified'] else '未驗證'}")

    elif venue_id in sherwood_updates:
        # 更新台北西華飯店
        updates = sherwood_updates[venue_id]
        for key, value in updates.items():
            if key != "rooms":
                venue[key] = value

        # 更新會議室
        if "rooms" in updates:
            existing_rooms = venue.get('rooms', [])
            new_rooms = updates["rooms"]

            # 建立會議室ID映射
            existing_room_ids = {room['id']: room for room in existing_rooms}

            # 合併會議室
            merged_rooms = []
            for new_room in new_rooms:
                room_id = new_room['id']
                if room_id in existing_room_ids:
                    old_room = existing_room_ids[room_id]
                    merged_room = {**old_room, **new_room}
                    merged_rooms.append(merged_room)
                else:
                    merged_rooms.append(new_room)

            # 添加舊資料中有而新資料沒有的會議室
            existing_room_ids_update = {room['id']: room for room in new_rooms}
            for old_room in existing_rooms:
                if old_room['id'] not in existing_room_ids_update:
                    merged_rooms.append(old_room)

            venue['rooms'] = merged_rooms

        print(f"[OK] 已更新台北西華飯店 (ID: {venue_id})")
        print(f"   會議室數: {len(venue['rooms'])} 間")
        print(f"   驗證狀態: {'已驗證' if venue['verified'] else '未驗證'}")

# 備份原檔案
import shutil
backup_name = f'venues.json.backup.hotels_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n已備份至: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n已更新 venues.json')
print(f'總場地數: {len(venues)}')
