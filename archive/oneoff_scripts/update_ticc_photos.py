#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 TICC 照片到 venues.json
（使用已提取的照片 URL）
"""
import json
import shutil
from datetime import datetime

print("="*80)
print("更新 TICC 照片")
print("="*80)
print()

# TICC 照片 URL（從 Playwright 提取）
ticc_photos = [
    {"src": "https://www.ticc.com.tw/xslgip/style1/images/ticc/VENUE-1.png", "alt": ""},
    {"src": "https://www.ticc.com.tw/xslgip/style1/images/ticc/VENUE-2.png", "alt": ""},
    {"src": "https://www.ticc.com.tw/xslgip/style1/images/ticc/VENUE-3.png", "alt": ""},
    {"src": "https://www.ticc.com.tw/xslgip/style1/images/ticc/img-hero.jpg", "alt": ""},
]

# 備份
backup = f'venues.json.backup.ticc_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup)
print(f"備份: {backup}")
print()

# 載入
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 更新 TICC
for venue in venues:
    if venue['id'] == 1448:
        # 添加照片資訊
        if 'photos' not in venue:
            venue['photos'] = []

        for photo in ticc_photos:
            venue['photos'].append({
                'url': photo['src'],
                'alt': photo.get('alt', ''),
                'added_at': datetime.now().isoformat()
            })

        if 'metadata' not in venue:
            venue['metadata'] = {}

        venue['metadata']['total_photos'] = len(venue['photos'])
        venue['metadata']['photos_updated_at'] = datetime.now().isoformat()
        venue['metadata']['photos_source'] = 'playwright_extraction'

        print(f"[OK] TICC (ID 1448)")
        print(f"   添加 {len(venue['photos'])} 張照片")
        print()
        print("   照片列表:")
        for i, photo in enumerate(venue['photos'], 1):
            print(f"   {i}. {photo['url']}")
        break

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print()
print("[OK] venues.json 已更新")
