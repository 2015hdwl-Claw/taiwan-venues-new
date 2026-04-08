#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北市飯店照片 - 批次8
台北兄弟大飯店：補充官網爬取的照片
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

# 台北兄弟大飯店更新資料 (ID: 1053)
# 從官網首頁爬取到更多照片
brother_hotel_updates = {
    1053: {
        "images": {
            "main": "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/飯店外觀.jpg",
            "gallery": [
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/飯店外觀.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/櫃台_fix-1.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/13F宴會廳婚宴-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/婚宴場地-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/11/DSC_9665-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/food-gaf10f4051_1920-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2021/03/梅花廳-6-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/蘭花4-960x720.jpg",
                "https://www.brotherhotel.com.tw/wp-content/uploads/2022/09/footer_logo.png"
            ],
            "source": "https://www.brotherhotel.com.tw/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：兄弟大飯店，我們接待客人有如照顧兄弟，健康、榮譽、協和、誠實、謙虛經營理念",
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

    if venue_id in brother_hotel_updates:
        update_data = brother_hotel_updates[venue_id]

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
backup_name = f'venues.json.backup.batch8_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
