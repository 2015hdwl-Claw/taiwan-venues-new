#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北市婚宴場地照片 - 批次11
青青婚宴會館：補充官網爬取的照片
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

# 青青婚宴會館更新資料 (ID: 1129)
# 從官網爬取到更多照片
chinchin_updates = {
    1129: {
        "images": {
            "main": "https://www.77-67.com/wp-content/uploads/2024/10/青青食尚花園會館-cdn.jpg",
            "gallery": [
                "https://www.77-67.com/wp-content/uploads/2024/10/青青食尚花園會館-cdn.jpg",
                "https://www.77-67.com/wp-content/uploads/2024/10/青青格麗絲莊園＿icn.jpg",
                "https://www.77-67.com/wp-content/uploads/2024/10/青青風車莊園.jpg",
                "https://www.77-67.com/wp-content/uploads/2024/10/青青南港星光wedding.jpg",
                "https://www.77-67.com/wp-content/uploads/2023/12/青青戶外婚禮06-1.jpg",
                "https://www.77-67.com/wp-content/uploads/2024/08/460651929_1042045757923961_4932139221916449438_n.jpg",
                "https://www.77-67.com/wp-content/uploads/2025/04/20250321-0099-1.jpg",
                "https://www.77-67.com/wp-content/uploads/2023/10/img-section-5_01_v2.jpg",
                "https://www.77-67.com/wp-content/uploads/2023/12/青青食尚花園會館戶外婚禮場景04.jpg",
                "https://www.77-67.com/wp-content/uploads/2023/12/青青星光Wedding場景02.jpg"
            ],
            "source": "https://www.77-67.com/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：青青國際婚宴餐飲集團，自家人辦婚禮的心，台北青青食尚花園會館，多樣獨特的婚禮服務，花園婚禮、教堂婚禮、戶外場景",
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

    if venue_id in chinchin_updates:
        update_data = chinchin_updates[venue_id]

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
backup_name = f'venues.json.backup.batch11_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
