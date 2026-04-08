#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北市飯店照片 - 批次9
台北美福大飯店：補充官網爬取的照片
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

# 台北美福大飯店更新資料 (ID: 1095)
# 從官網首頁爬取到更多照片
mayfull_updates = {
    1095: {
        "images": {
            "main": "https://www.grandmayfull.com/uploads/indexD/20160202_123636_462.jpeg",
            "gallery": [
                "https://www.grandmayfull.com/uploads/indexD/20160202_123636_462.jpeg",
                "https://www.grandmayfull.com/uploads/indexD/20160202_123646_549.jpeg",
                "https://www.grandmayfull.com/uploads/indexD/20161222_171520_993.jpeg",
                "https://www.grandmayfull.com/uploads/indexD/20161222_173332_937.jpeg",
                "https://www.grandmayfull.com/uploads/indexD/20201029_165821_201.jpeg",
                "https://www.grandmayfull.com/uploads/indexD/20201029_165902_386.jpeg",
                "https://www.grandmayfull.com/img/2023 World Luxury Awards.png",
                "https://www.grandmayfull.com/img/2024-Michelin Logo.png",
                "https://www.grandmayfull.com/img/footer_contact.jpg"
            ],
            "source": "https://www.grandmayfull.com/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：2023世界豪華酒店大獎得主，米其林推薦餐廳，146間豪華客房，挑高7米無柱宴會廳",
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

    if venue_id in mayfull_updates:
        update_data = mayfull_updates[venue_id]

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
backup_name = f'venues.json.backup.batch9_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
