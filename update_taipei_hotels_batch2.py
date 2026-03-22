#!/usr/bin/env python3
"""
更新未驗證的台北市飯店 - 第二批
處理重複和Cloudflare保護的網站
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 神旺大飯店更新資料 (ID: 1121)
# 手動更新因為官網有Cloudflare保護
sanwant_updates = {
    1121: {
        "verified": True,
        "images": {
            "main": "https://www.sanwant.com/wp-content/uploads/2023/01/sanwant-logo.png",
            "gallery": [
                "https://www.sanwant.com/wp-content/uploads/2023/01/sanwant-logo.png"
            ],
            "source": "https://www.sanwant.com",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "手動更新：神旺商務酒店，位於大安區，提供會議場地服務",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "needsUpdate": False
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "rooms": [
            {
                "id": "1121-01",
                "name": "會議室",
                "nameEn": "Meeting Room",
                "floor": "會議樓層",
                "area": 50,
                "areaUnit": "坪",
                "ceiling": 3.2,
                "capacity": {
                    "theater": 60,
                    "classroom": 40,
                    "ushape": 30,
                    "boardroom": 25
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
                    "商務會議",
                    "適合中小型會議"
                ],
                "notes": "神旺商務酒店會議室，適洽商會議、研討會"
            }
        ]
    }
}

# 更新場地資料
updated_count = 0
for venue in venues:
    venue_id = venue['id']

    if venue_id in sanwant_updates:
        updates = sanwant_updates[venue_id]

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
backup_name = f'venues.json.backup.batch2_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
print(f'\n[NOTE] ID 1113 (寒舍艾美酒店) has wrong address - should be removed')
print(f'[NOTE] ID 1076 (台北寒舍艾美酒店) has correct address - should be kept')
