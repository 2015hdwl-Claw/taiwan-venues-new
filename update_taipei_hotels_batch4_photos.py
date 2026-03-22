#!/usr/bin/env python3
"""
更新照片不足的台北市飯店 - 圓山大飯店
13間會議室僅4張照片，補充各會議廳照片
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 圓山大飯店更新資料 (ID: 1072) - 13間會議室僅4張照片
# 從各會議廳照片中選取代表性照片加入主畫廊
grand_hotel_updates = {
    1072: {
        "images": {
            "main": "https://www.grand-hotel.org/fileupload/Banner_File/1_Ballroom.jpg",
            "gallery": [
                "https://www.grand-hotel.org/fileupload/Banner_File/1_Ballroom.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/2_wasfumdpas.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/7_jtjubqyqlw.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/3_blsvdmouas.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/4_fjomorlyda.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/5_fgzmrzgbxc.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/6_kqzlzokmyf.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/8_omzicfhukb.jpg",
                "https://www.grand-hotel.org/fileupload/Ballroom_File/9_fcfsecebue.jpg",
                "https://www.grand-hotel.org/TW/images/layout/logo/logo.svg"
            ],
            "floorPlan": "https://www.grand-hotel.org/fileupload/Ballroom_File/1.pdf",
            "source": "https://www.grand-hotel.org/TW/official/ballroom.aspx?gh=TP",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：13個宴會會議廳，最大容納2000人，挑高11米無柱空間",
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

    if venue_id in grand_hotel_updates:
        update_data = grand_hotel_updates[venue_id]

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
backup_name = f'venues.json.backup.batch4_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
