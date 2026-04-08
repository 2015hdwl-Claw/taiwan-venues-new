#!/usr/bin/env python3
"""
移除重複的寒舍艾美酒店記錄
ID 1113 是重複/錯誤的記錄
ID 1076 是正確的記錄
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

original_count = len(venues)

# 移除重複的寒舍艾美酒店 (ID: 1113) - 地址錯誤，與ID 1076重複
venues = [v for v in venues if v['id'] != 1113]

new_count = len(venues)
removed_count = original_count - new_count

print(f'[OK] Original venue count: {original_count}')
print(f'[OK] After removing duplicate: {new_count}')
print(f'[OK] Removed: {removed_count} venue')
print(f'[OK] Reason: ID 1113 (寒舍艾美酒店) is duplicate/incorrect')
print(f'[OK] Kept: ID 1076 (台北寒舍艾美酒店) with correct address')

# 備份原檔案
import shutil
backup_name = f'venues.json.backup.remove_duplicate_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'[OK] venues.json updated')
print(f'[OK] Total venues: {new_count}')
