#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北國賓大飯店 - 標記為改建中
官網顯示：2022-2028年改建期間，只營運餐廳，無會議場地
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北國賓大飯店 - 標記為改建中")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.ambassador_renovation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# 找到場地
venue = next((v for v in venues if v['id'] == 1069), None)

if not venue:
    print("Venue 1069 not found!")
    sys.exit(1)

print(f"Found venue: {venue['name']}")
print(f"Current URL: {venue['url']}\n")

# 更新資訊
print("更新場地狀態...")
print("-" * 100)

# 添加改建資訊到 metadata
if 'metadata' not in venue:
    venue['metadata'] = {}

venue['active'] = False
venue['renovation'] = {
    'status': 'under_renovation',
    'startDate': '2022-01-01',
    'expectedEndDate': '2028-12-31',
    'note': '2022-2028年改建期間，餐廳持續於2樓營運，無會議場地可提供',
    'currentOperation': '只營運餐廳（A CUT 牛排館、國賓中餐廳）'
}

venue['discontinuedAt'] = datetime.now().isoformat()
venue['discontinueReason'] = '飯店改建中（2022-2028），無會議場地可提供'

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = 'V3_RenovationCheck'
venue['metadata']['note'] = '三階段流程發現改建資訊 - 階段1技術檢測'

# 更新聯絡資訊（從官網提取）
venue['contact'] = {
    'phone': '+886-2-2100-2100',
    'tollFree': '0800-051-111',
    'email': 'service@ambassador-hotels.com'
}

print(f"Status: Active → False (改建中)")
print(f"Renovation: 2022-2028")
print(f"Current operation: 只營運餐廳")
print(f"Contact: {venue['contact']['phone']}")

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("台北國賓大飯店標記完成")
print("=" * 100)
print(f"\n狀態：改建中 (2022-2028)")
print(f"會議場地：暫時無法提供")
print(f"Backup: {backup_file}")
print(f"\n⚠️  建議2028年後重新爬取")
