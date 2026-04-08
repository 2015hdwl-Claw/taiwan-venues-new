#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 ID 1066: 台北商務會館
注意: 官網URL可能不正確，照片來源需驗證
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
print('更新 ID 1066: 台北商務會館')
print('注意: URL和照片來源需進一步驗證')
print('=' * 70)
print()

updater = VenueUpdater('venues.json')

result = updater.add_photos(
    venue_id=1066,
    main_photo='https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
    gallery_photos=[
        'https://images.unsplash.com/photo-1517502884422-41e646b6c8c6?w=800',
        'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800',
        'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=800'
    ],
    source_url='http://www.tbc-group.com/',
    verified=False,
    note='待尋找正確官網URL，目前使用佔位照片'
)

if result['success']:
    print(f'更新成功: {result["venue_name"]}')
    print(f'  更新欄位: {", ".join(result["updated_fields"])}')
    print(f'  備份檔案: {result["backup_path"]}')
    print()
    print('照片數量: 4 (1 main + 3 gallery)')
    print('狀態: verified=False (待驗證正確URL)')
else:
    print(f'更新失敗: {result["error"]}')

print()
print('=' * 70)
