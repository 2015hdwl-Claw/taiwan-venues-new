#!/usr/bin/env python3
"""
移除非會議場地 - 兄弟大飯店（僅婚宴，無會議場地）
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

original_count = len(venues)

# 移除兄弟大飯店 (ID: 1041) - 僅提供婚宴，無會議場地
venues = [v for v in venues if v['id'] != 1041]

new_count = len(venues)
removed_count = original_count - new_count

print(f'[OK] Original venue count: {original_count}')
print(f'[OK] After removing Brother Hotel: {new_count}')
print(f'[OK] Removed: {removed_count} venue')
print(f'[OK] Reason: Brother Hotel only provides wedding banquets, no meeting rooms')

# 備份原檔案
import shutil
backup_name = f'venues.json.backup.remove_brother_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'[OK] venues.json updated')
print(f'[OK] Total venues: {new_count}')
