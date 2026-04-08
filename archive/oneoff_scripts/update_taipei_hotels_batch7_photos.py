#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北市飯店照片 - 批次7
台北老爺大酒店：補充官網爬取的照片
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

# 台北老爺大酒店更新資料 (ID: 1097)
# 從官網爬取到更多照片
royal_inn_updates = {
    1097: {
        "images": {
            "main": "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/8f798454-fa7b-42f1-521a-3090032d1100/public",
            "gallery": [
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/8f798454-fa7b-42f1-521a-3090032d1100/public",
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/665d2e12-3499-4886-4236-7a6a13069a00/public",
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/ec171f60-ffea-4aaa-46bb-9a1cfbbcba00/public",
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/e02a5997-79c0-49f0-5b79-21021c084d00/public",
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/2c1ccdb4-92ab-421a-754a-b8c260065700/public",
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/f7beaee6-2e7f-4f8b-b5a3-362000ef8c00/public",
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/1936e1f8-40d6-4a50-0ece-bc8c33973e00/public",
                "https://imagedelivery.net/a6-OYZSpZSiOriMeuFHR3w/aa7bb9b4-bde2-43e0-99fb-fe2578309400/public",
                "https://www.hotelroyal.com.tw/Files/Images/Logo/20210830_group_logo.svg"
            ],
            "source": "https://www.hotelroyal.com.tw/zh-tw/taipei",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：老爺酒店集團，為城市商務及購物旅客提供舒適便捷的商務旅店",
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

    if venue_id in royal_inn_updates:
        update_data = royal_inn_updates[venue_id]

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
backup_name = f'venues.json.backup.batch7_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
