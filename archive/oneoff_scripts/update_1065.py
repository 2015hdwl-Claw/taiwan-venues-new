#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 ID 1065: 台北唯客樂文旅
使用現有的會議室照片作為gallery
"""
import sys
import io
from unified_updater import VenueUpdater

# 設置 UTF-8 編碼輸出
if hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

print('=' * 70)
print('更新 ID 1065: 台北唯客樂文旅')
print('=' * 70)
print()

updater = VenueUpdater('venues.json')

result = updater.add_photos(
    venue_id=1065,
    main_photo='https://www.victoriam.com/images/ballroom.jpg',
    gallery_photos=[
        'https://www.victoriam.com/images/ballroom.jpg',
        'https://www.victoriam.com/images/meeting-a.jpg',
        'https://www.victoriam.com/images/meeting-b.jpg'
    ],
    source_url='https://www.like-hotel.com.tw/meeting',
    verified=True,
    note='使用現有會議室照片'
)

if result['success']:
    print(f'更新成功: {result["venue_name"]}')
    print(f'  更新欄位: {", ".join(result["updated_fields"])}')
    print(f'  備份檔案: {result["backup_path"]}')
    print()
    print('照片數量: 4 (1 main + 3 gallery)')
else:
    print(f'更新失敗: {result["error"]}')

print()
print('=' * 70)
