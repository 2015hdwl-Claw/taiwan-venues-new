#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北市飯店照片 - 批次6
台北怡亨酒店：補充官網爬取的照片
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

# 台北怡亨酒店更新資料 (ID: 1082)
# 從官網首頁爬取到更多照片
eclat_updates = {
    1082: {
        "images": {
            "main": "https://image-tc.galaxy.tf/wijpeg-49sf1014yy958cxn2fb6alobj/deluxe1_standard.jpg?crop=118%2C0%2C1365%2C1024",
            "gallery": [
                "https://image-tc.galaxy.tf/wijpeg-49sf1014yy958cxn2fb6alobj/deluxe1_standard.jpg?crop=118%2C0%2C1365%2C1024",
                "https://image-tc.galaxy.tf/wijpeg-if05do23cuz4u6gycg6qvubc/grand-deluxe1_standard.jpg?crop=118%2C0%2C1365%2C1024",
                "https://image-tc.galaxy.tf/wijpeg-6ro07xpyjte7obg1g2ov5qfr/premier1_standard.jpg?crop=118%2C0%2C1365%2C1024",
                "https://image-tc.galaxy.tf/wijpeg-a65yg2fc9830obqqn8itdawks/hero-eclat1-wide_standard.jpg?crop=143%2C0%2C855%2C641",
                "https://image-tc.galaxy.tf/wijpeg-9461v37sm1ay8zed222hwf875/a-c-e-20-100_standard.jpg?crop=0%2C0%2C1140%2C855",
                "https://image-tc.galaxy.tf/wijpeg-aquig4z12oa2p9wj161ik6p07/a-c-e-20-100_standard.jpg?crop=1%2C0%2C1140%2C855",
                "https://image-tc.galaxy.tf/wijpeg-ca1zih7ki22eub0n193fod84t/a-a-a-c-a-c-e-19_standard.jpg?crop=0%2C0%2C1140%2C855",
                "https://image-tc.galaxy.tf/wijpeg-cdp6exljvvomuslfv2nm5u2j9/thomas-tucker-au3cybd7vcu-unsplash_standard.jpg?crop=268%2C0%2C1384%2C1038"
            ],
            "source": "https://www.eclathotels.com/zt/taipei",
            "verified": True,
            "verifiedAt": datetime.now().isoformat() + "Z",
            "note": "從官網爬取：60間極盡奢華客房，多元化會議室，價值連城的藝術真跡",
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

    if venue_id in eclat_updates:
        update_data = eclat_updates[venue_id]

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
backup_name = f'venues.json.backup.batch6_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'\n[OK] venues.json updated')
print(f'[OK] Total venues: {len(venues)}')
print(f'[OK] Updated: {updated_count} venues')
