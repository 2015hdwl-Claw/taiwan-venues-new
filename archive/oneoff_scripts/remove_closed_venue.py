#!/usr/bin/env python3
"""
移除已停業場地
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

original_count = len(venues)

# 移除已停業場地 (ID: 1104 台北西華飯店)
venues = [v for v in venues if v['id'] != 1104]

new_count = len(venues)
removed_count = original_count - new_count

print(f'[OK] Original venue count: {original_count}')
print(f'[OK] After removing closed venues: {new_count}')
print(f'[OK] Removed: {removed_count} venue')

# 備份原檔案
import shutil
backup_name = f'venues.json.backup.remove_closed_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup_name)
print(f'\n[OK] Backup created: {backup_name}')

# 寫入更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f'[OK] venues.json updated')
print(f'[OK] Total venues: {new_count}')
