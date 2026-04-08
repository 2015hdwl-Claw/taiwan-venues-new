#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 ID 1334: 台北中山運動中心
使用官網圖片
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
print('更新 ID 1334: 台北中山運動中心')
print('=' * 70)
print()

updater = VenueUpdater('venues.json')

result = updater.add_photos(
    venue_id=1334,
    main_photo='https://cssc.cyc.org.tw/upload/banner/粉專封面頁.jpg',
    gallery_photos=[
        'https://cssc.cyc.org.tw/upload/venue_logo/中山.jpg',
        'https://cssc.cyc.org.tw/images/activity.jpg',
        'https://cssc.cyc.org.tw/upload/banner/LINE_ALBUM_樂活_第四梯_728～81_250802_61.jpg'
    ],
    source_url='https://cssc.cyc.org.tw/',
    verified=True,
    note='使用官網照片和會議室照片'
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
