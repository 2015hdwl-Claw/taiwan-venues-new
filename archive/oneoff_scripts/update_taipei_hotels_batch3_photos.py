#!/usr/bin/env python3
"""
更新照片不足的台北市飯店 - 第一批（高優先級）
優先處理會議室多但照片少的場地
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 台北萬豪酒店更新資料 (ID: 1103) - 26間會議室僅1張照片
marriott_updates = {
    1103: {
        "images": {
            "main": "https://www.taipeimarriott.com.tw/files/page_176900693814vqap059_m.jpg",
            "gallery": [
                "https://www.taipeimarriott.com.tw/files/page_176900693814vqap059_m.jpg",
                "https://www.taipeimarriott.com.tw/files/page_1516614885xcuqj084_m.jpg",
                "https://www.taipeimarriott.com.tw/files/page_1516614716xcuqe177_m.jpg",
                "https://www.taipeimarriott.com.tw/files/page_1505323692x4fh3369_m.jpg",
                "https://www.taipeimarriott.com.tw/files/page_1516616234xcuron76_m.jpg",
                "https://www.taipeimarriott.com.tw/files/page_1462471087w6d7cc98_m.jpg",
                "https://www.taipeimarriott.com.tw/files/page_1462469869w6d6ai04_m.jpg",
                "https://www.taipeimarriott.com.tw/files/page_1516615054xcuqnx61_m.jpg",
                "https://www.taipeimarriott.com.tw/images/logo_02.png"
            ],
            "source": "https://www.taipeimarriott.com.tw/websev?cat=page&id=39",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：26個多功能活動場地，4,569平方米宴會會議空間，挑高9.9米無樑柱空間",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "needsUpdate": False
        },
        "lastUpdated": datetime.now().strftime("%Y-%m-%d")
    }
}

# 更新場地資料
updated_count = 0
for venue in venues:
    venue_id = venue['id']

    if venue_id in marriott_updates:
        update_data = marriott_updates[venue_id]

        # 更新照片資料
        for key, value in update_data.items():
            venue[key] = value

        venue_name = venue['name']
        photo_count = len(venue.get("images", {}).get("gallery", []))
        print(f'[OK] Updated {venue_name} (ID: {venue_id})')
        print(f'   Photos: {photo_count}')
        print(f'   Source: {venue["images"]["source"]}')
        updated_count += 1

# 備份原檔案
import shutil
backup_name = f'venues.json.backup.batch3_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
