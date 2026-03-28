#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 快速修復 - 突破無頁面場地
"""
import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scrapling.fetchers import Fetcher

# 修復清單
fixes = {
    # meeting.com.tw 404 修復
    1495: {'url': 'https://www.meeting.com.tw/', 'reason': '404子域名改用主域名'},
    1496: {'url': 'https://www.meeting.com.tw/', 'reason': '404子域名改用主域名'},
    1497: {'url': 'https://www.meeting.com.tw/', 'reason': '404子域名改用主域名'},
    1498: {'url': 'https://www.meeting.com.tw/', 'reason': '404子域名改用主域名'},
    1499: {'url': 'https://www.meeting.com.tw/', 'reason': '404子域名改用主域名'},

    # 國際酒店 URL 修正 (需要手動查找正確頁面)
    # 這些URL需要人工確認正確的酒店頁面
    1075: {'url': 'https://www.sheratongrandtaipei.com/', 'reason': '保持原URL，需檢查重定向'},
    1082: {'url': 'https://www.eclathotels.com/zt/taipei', 'reason': '保持原URL，需檢查重定向'},
    1083: {'url': 'https://www.citizenm.com/hotels/asia/taipei/taipei-north-gate', 'reason': '重定向到品牌頁，需修正'},
    1086: {'url': 'https://www.regenttaiwan.com/', 'reason': '保持原URL，需檢查重定向'},
    1103: {'url': 'https://www.taipeimarriott.com.tw/', 'reason': '保持原URL，需檢查重定向'},
}

print('=== V4 Quick Fix for Zero-Page Venues ===')
print()

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed_count = 0
for venue_id, fix_info in fixes.items():
    venue = next((v for v in data if v['id'] == venue_id), None)
    if venue:
        old_url = venue.get('url', '')
        new_url = fix_info['url']

        print(f'[Venue {venue_id}] {venue.get("name", "")[:40]}')
        print(f'  Reason: {fix_info["reason"]}')
        print(f'  Old URL: {old_url}')

        # 測試新 URL 是否可訪問
        try:
            response = Fetcher.get(new_url, impersonate='chrome', timeout=10)
            status = '✅ OK' if response.status == 200 else f'❌ {response.status}'
            print(f'  New URL: {new_url}')
            print(f'  Test: {status}')

            if response.status == 200:
                # 更新 URL
                venue['url'] = new_url
                fixed_count += 1
        except Exception as e:
            print(f'  New URL: {new_url}')
            print(f'  Test: ❌ Error - {str(e)[:40]}')

        print()

# 儲存修正後的資料
if fixed_count > 0:
    # 備份
    backup_file = f'venues.json.backup.quickfix_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'[BACKUP] Saved to {backup_file}')

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'[OK] Fixed {fixed_count} venues')
    print('[OK] Saved to venues.json')
else:
    print('[INFO] No fixes applied')
