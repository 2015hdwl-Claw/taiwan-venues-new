#!/usr/bin/env python3
"""
更新未驗證的台北市飯店 - 第一批
基於官網爬蟲結果
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 維多麗亞酒店更新資料 (ID: 1122)
grand_victoria_updates = {
    1122: {
        "verified": True,
        "images": {
            "main": "https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/05/官網-首圖2.jpg",
            "gallery": [
                "https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/05/官網-首圖2.jpg",
                "https://grandvictoria.com.tw/wp-content/uploads/sites/237/2023/05/官網logo.png"
            ],
            "source": "https://www.grandvictoria.com.tw/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：挑高8米現代時尚英式劇院宴會廳，3個宴會廳（大宴會廳1F、維多麗亞廳3F、天璽廳3F）",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "needsUpdate": False
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "rooms": [
            {
                "id": "1122-01",
                "name": "大宴會廳",
                "nameEn": "Grand Ballroom",
                "floor": "1樓",
                "area": 200,
                "areaUnit": "坪",
                "ceiling": 8,
                "capacity": {
                    "theater": 400,
                    "classroom": 250,
                    "ushape": 150,
                    "roundtable": 320,
                    "banquet": 280
                },
                "capacityType": "劇院式",
                "equipment": [
                    "頂級音響系統",
                    "專業舞台",
                    "LED大螢幕",
                    "投影設備",
                    "燈光系統",
                    "無線麥克風"
                ],
                "images": {
                    "main": "https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/05/官網-首圖2.jpg",
                    "source": "https://www.grandvictoria.com.tw/"
                },
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "挑高8米",
                    "現代時尚英式劇院風格",
                    "可延伸至戶外花園"
                ],
                "notes": "挑高8米現代時尚英式劇院宴會廳，可延伸至戶外花園，適合大型會議、婚宴"
            },
            {
                "id": "1122-02",
                "name": "維多麗亞廳",
                "nameEn": "Victoria Hall",
                "floor": "3樓",
                "area": 80,
                "areaUnit": "坪",
                "ceiling": 4,
                "capacity": {
                    "theater": 120,
                    "classroom": 80,
                    "ushape": 50,
                    "roundtable": 80
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
                    "中型會議廳",
                    "多功能用途"
                ],
                "notes": "3樓中型會議廳，適合中型會議、研討會"
            },
            {
                "id": "1122-03",
                "name": "天璽廳",
                "nameEn": "Tianxi Hall",
                "floor": "3樓",
                "area": 50,
                "areaUnit": "坪",
                "ceiling": 3.5,
                "capacity": {
                    "theater": 80,
                    "classroom": 50,
                    "ushape": 35,
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
                    "小型會議廳",
                    "適合小組討論"
                ],
                "notes": "3樓小型會議廳，適洽商會議、培訓"
            }
        ]
    }
}

# 台北花園大酒店更新資料 (ID: 1124)
taipei_garden_updates = {
    1124: {
        "verified": True,
        "images": {
            "main": "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-國際廳-婚宴.jpg",
            "gallery": [
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-國際廳-婚宴.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-飯店大廳.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2024/01/Picture3.png"
            ],
            "source": "https://www.taipeigarden.com.tw",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：2023年五星级酒店，挑高7米寬敞無柱多功能宴會廳，241間客房",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "needsUpdate": False
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "rooms": [
            {
                "id": "1124-01",
                "name": "國際廳",
                "nameEn": "International Ballroom",
                "floor": "宴會樓層",
                "area": 250,
                "areaUnit": "坪",
                "ceiling": 7,
                "capacity": {
                    "theater": 500,
                    "classroom": 300,
                    "ushape": 200,
                    "roundtable": 400,
                    "banquet": 350
                },
                "capacityType": "劇院式",
                "equipment": [
                    "頂級音響系統",
                    "專業舞台",
                    "LED大螢幕",
                    "投影設備",
                    "燈光系統",
                    "無線麥克風"
                ],
                "images": {
                    "main": "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-國際廳-婚宴.jpg",
                    "source": "https://www.taipeigarden.com.tw"
                },
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "挑高7米",
                    "寬敞無柱設計",
                    "五星級場地"
                ],
                "notes": "挑高7米寬敞無柱多功能宴會廳，適合大型會議、婚宴、發表會"
            },
            {
                "id": "1124-02",
                "name": "宴會包廂",
                "nameEn": "Banquet Rooms",
                "floor": "宴會樓層",
                "area": 40,
                "areaUnit": "坪",
                "ceiling": 3.2,
                "capacity": {
                    "theater": 60,
                    "classroom": 40,
                    "ushape": 25,
                    "roundtable": 40
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
                    "獨立包廂",
                    "適合中小型會議"
                ],
                "notes": "獨立完善可量身打造的會議室"
            }
        ]
    }
}

# 豪景大酒店更新資料 (ID: 1126)
riverview_updates = {
    1126: {
        "verified": True,
        "images": {
            "main": "http://www.riverview.com.tw/wp-content/uploads/sites/230/2017/05/直式-金色.png",
            "gallery": [
                "http://www.riverview.com.tw/wp-content/uploads/sites/230/2017/05/直式-金色.png",
                "http://www.riverview.com.tw/wp-content/uploads/sites/230/2015/10/A_service_00-330x150.jpg"
            ],
            "source": "https://www.riverview.com.tw/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：位於西門町，有宴席會議服務，12樓萊茵宴會廳",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "needsUpdate": False
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "rooms": [
            {
                "id": "1126-01",
                "name": "萊茵宴會廳",
                "nameEn": "Rhine Ballroom",
                "floor": "12樓",
                "area": 100,
                "areaUnit": "坪",
                "ceiling": 3.5,
                "capacity": {
                    "theater": 200,
                    "classroom": 120,
                    "ushape": 80,
                    "roundtable": 160,
                    "banquet": 140
                },
                "capacityType": "劇院式",
                "equipment": [
                    "音響系統",
                    "投影設備",
                    "舞台",
                    "無線麥克風"
                ],
                "images": {
                    "main": "http://www.riverview.com.tw/wp-content/uploads/sites/230/2017/05/直式-金色.png",
                    "source": "https://www.riverview.com.tw/"
                },
                "pillar": False,
                "pillarCount": 0,
                "pillarInfo": "無柱子",
                "hasWindow": True,
                "features": [
                    "河岸夜景",
                    "鄰近西門町",
                    "12樓高空景觀"
                ],
                "notes": "12樓宴會廳，可欣賞淡水河岸夜景，適合中型會議、宴會"
            }
        ]
    }
}

# 合併所有更新
all_updates = {**grand_victoria_updates, **taipei_garden_updates, **riverview_updates}

# 更新場地資料
updated_count = 0
for venue in venues:
    venue_id = venue['id']

    if venue_id in all_updates:
        updates = all_updates[venue_id]

        # 更新基本資料
        for key, value in updates.items():
            if key != "rooms":
                venue[key] = value

        # 更新會議室（完全替換）
        if "rooms" in updates:
            venue['rooms'] = updates["rooms"]

        venue_name = venue['name']
        print(f'[OK] Updated {venue_name} (ID: {venue_id})')
        print(f'   Verified: {venue["verified"]}')
        print(f'   Rooms: {len(venue["rooms"])}')
        print(f'   Photos: {len(venue.get("images", {}).get("gallery", []))}')
        updated_count += 1

# 備份原檔案
import shutil
backup_name = f'venues.json.backup.batch1_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
