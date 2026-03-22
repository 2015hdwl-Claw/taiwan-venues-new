#!/usr/bin/env python3
"""
基於官網最新內容更新飯店資料
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 更新兄弟大飯店（基於官網資訊）
brother_updates = {
    1041: {
        "verified": True,
        "venueType": "婚宴場地",
        "images": {
            "main": "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/飯店外觀.jpg",
            "gallery": [
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/飯店外觀.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/13F宴會廳婚宴-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/婚宴場地-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/DSC_9665-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/櫃台_fix-1.jpg"
            ],
            "source": "https://www.brotherhotel.com.tw/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：提供婚宴場地（13F宴會廳），餐飲專案豐富",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "needsUpdate": False
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
                    "gallery": [
                        "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/13F宴會廳婚宴-960x720.jpg"
                    ],
                    "source": "https://www.brotherhotel.com.tw/"
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
            }
        ]
    }
}

# 更新台北西華飯店 - 標記為已停業
sherwood_updates = {
    1104: {
        "verified": True,
        "status": "已停業",
        "closedDate": "2022-02-15",
        "images": {
            "note": "已於2022年2月15日熄燈停業。官網現為紀念性網站，展示西華歷史與NFT",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "source": "https://www.sherwood.com.tw",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z"
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "rooms": [
            {
                "id": "1104-01",
                "name": "B1宴會廳（已停業）",
                "floor": "B1",
                "status": "已停業",
                "notes": "隨飯店於2022年2月15日一同停業"
            }
        ]
    }
}

# 更新場地資料
updated_count = 0
for venue in venues:
    venue_id = venue['id']

    if venue_id in brother_updates:
        # 更新兄弟大飯店
        updates = brother_updates[venue_id]
        for key, value in updates.items():
            if key != "rooms":
                venue[key] = value

        # 更新會議室
        if "rooms" in updates:
            venue['rooms'] = updates["rooms"]

        print(f"[OK] 已更新兄弟大飯店 (ID: {venue_id})")
        print(f"   場地類型: {venue['venueType']}")
        print(f"   會議室數: {len(venue['rooms'])} 間")
        print(f"   驗證狀態: 已驗證")
        updated_count += 1

    elif venue_id in sherwood_updates:
        # 更新台北西華飯店 - 標記停業
        updates = sherwood_updates[venue_id]
        for key, value in updates.items():
            if key != "rooms":
                venue[key] = value

        # 更新會議室
        if "rooms" in updates:
            venue['rooms'] = updates["rooms"]

        print(f"[WARN] 已標記台北西華飯店為停業 (ID: {venue_id})")
        print(f"   狀態: 已停業")
        print(f"   停業日期: 2022-02-15")
        updated_count += 1

# 備份原檔案
import shutil
backup_name = f'venues.json.backup.official_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n已備份至: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n已更新 venues.json')
print(f'總場地數: {len(venues)}')
print(f'更新數: {updated_count}')
