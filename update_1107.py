#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 ID 1107: 台北體育館
注意: 官網URL為 taipeiarena.com.tw，但目前網路爬取失敗
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
print('更新 ID 1107: 台北體育館')
print('注意: 使用佔位照片，官網爬取失敗')
print('=' * 70)
print()

updater = VenueUpdater('venues.json')

result = updater.add_photos(
    venue_id=1107,
    main_photo='https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=800',
    gallery_photos=[
        'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800',
        'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=800',
        'https://images.unsplash.com/photo-1599586120429-48281b6f0ece?w=800'
    ],
    source_url='https://taipeiarena.com.tw',
    verified=False,
    note='使用運動場地相關照片，待爬取官網真實照片'
)

if result['success']:
    print(f'更新成功: {result["venue_name"]}')
    print(f'  更新欄位: {", ".join(result["updated_fields"])}')
    print(f'  備份檔案: {result["backup_path"]}')
    print()
    print('照片數量: 4 (1 main + 3 gallery)')
    print('狀態: verified=False (待爬取官網)')
else:
    print(f'更新失敗: {result["error"]}')

print()
print('=' * 70)
