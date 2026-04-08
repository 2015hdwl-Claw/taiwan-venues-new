#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 ID 1057: 台北典華
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
print('更新 ID 1057: 台北典華')
print('=' * 70)
print()

updater = VenueUpdater('venues.json')

result = updater.add_photos(
    venue_id=1057,
    main_photo='https://img.denwell.com/denwell/wp-content/uploads/2024071502030648.jpg',
    gallery_photos=[
        'https://img.denwell.com/denwell/wp-content/uploads/2025/07/2025072907550938-scaled.jpg',
        'https://img.denwell.com/denwell/wp-content/uploads/2025/07/2025072907553721-scaled.jpg',
        'https://img.denwell.com/denwell/wp-content/uploads/2025/07/2025072907560819-scaled.jpg'
    ],
    source_url='https://www.denwell.com/dianhua-taipei',
    verified=True,
    note='使用官網會議室照片'
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
