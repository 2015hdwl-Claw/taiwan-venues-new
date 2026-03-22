#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北市飯店照片 - 批次10
茹曦酒店 ILLUME TAIPEI：補充官網爬取的照片
"""

import json
import sys
import io
from datetime import datetime

# 設置 UTF-8 編碼輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 茹曦酒店 ILLUME TAIPEI 更新資料 (ID: 1090)
# 從官網爬取到更多照片
illume_updates = {
    1090: {
        "images": {
            "main": "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/01_PublicArea_Atrium_Light_3-jpg.webp",
            "gallery": [
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/01_PublicArea_Atrium_Light_3-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/01_PublicArea_Entrance-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/02_Rooms_1_Premier_King_1-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/02_Rooms_4_Premier_Suite_1_Living_Room-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/05_Events_2F_Grand_Ballroom_1-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/05_Events_2F_VIP_Courts_Classroom-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/Illume_Taipei_01_s-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/03_Facilities_1_Gym_1_Equipments-jpg.webp",
                "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/03_Facilities_2_Outdoor_Swimming_Pool_1-jpg.webp"
            ],
            "source": "https://www.theillumehotel.com/zh/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：結合光影藝術與人文關懷的台北飯店，鄰近台北小巨蛋與大巨蛋，現代美學與溫暖服務",
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

    if venue_id in illume_updates:
        update_data = illume_updates[venue_id]

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
backup_name = f'venues.json.backup.batch10_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
