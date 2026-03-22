#!/usr/bin/env python3
"""
更新台北市飯店照片 - 批次5
台北花園大酒店：補充官方網站爬取的照片
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 台北花園大酒店更新資料 (ID: 1100)
# 從官網首頁爬取到更多照片
garden_hotel_updates = {
    1100: {
        "images": {
            "main": "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-國際廳-婚宴.jpg",
            "gallery": [
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-國際廳-婚宴.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-飯店大廳.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2024/01/Picture3.png",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-PRIME-ONE-牛排館-包廂.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-雅緻客房-一大床.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/05/台北花園大酒店-雅緻客房-兩小床.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/07/台北花園大酒店-PRIME-ONE-牛排館-形象.jpg",
                "https://www.taipeigarden.com.tw/wp-content/uploads/sites/278/2023/03/01天成集團指示標誌-16-e1683518085598.png"
            ],
            "source": "https://www.taipeigarden.com.tw/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：2023年五星级酒店，挑高7米寬敞無柱多功能宴會廳，241間客房",
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

    if venue_id in garden_hotel_updates:
        update_data = garden_hotel_updates[venue_id]

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
backup_name = f'venues.json.backup.batch5_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
