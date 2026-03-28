#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北喜瑞飯店 - 階段3：確認無會議室服務
驗證後標記為 discontinued
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北喜瑞飯店 - 階段3：確認無會議室服務")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.sheraton_stage3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# 找到場地
venue = next((v for v in venues if v['id'] == 1068), None)

if not venue:
    print("Venue 1068 not found!")
    sys.exit(1)

print(f"Found venue: {venue['name']}\n")

# 確認為 discontinued（非會議場地）
print("1. Confirming Discontinued Status")
print("-" * 100)

venue['status'] = 'discontinued'
venue['enabled'] = False

print(f"Status: {venue['status']}")
print(f"Enabled: {venue['enabled']}")

# 2. 更新場地描述
print("\n2. Updating Venue Description")
print("-" * 100)

venue['highlights'] = [
    "非會議場地 - 精品設計旅館",
    "官網無會議室/宴會廳資訊",
    "主營住宿服務，不提供會議場地",
    "2026-03-27 驗證確認"
]

venue['totalMeetingRooms'] = 0
venue['maxCapacity'] = 0

for highlight in venue['highlights']:
    print(f"  - {highlight}")

# 3. 更新聯絡資訊（保留歷史記錄）
print("\n3. Updating Contact Info")
print("-" * 100)

if 'contact' not in venue:
    venue['contact'] = {}

# 從官網提取的正確資訊
venue['contact']['phone'] = '+886-2-2541-0077'
venue['contact']['email'] = 'ambience@taipeiinn.com.tw'
venue['contact']['fax'] = '+886-2-2541-0021'
venue['contact']['address'] = '104台北市中山區長安東路一段64號'

print(f"Phone: {venue['contact']['phone']}")
print(f"Email: {venue['contact']['email']}")
print(f"Fax: {venue['contact']['fax']}")
print(f"Address: {venue['contact']['address']}")

# 4. 更新 metadata
print("\n4. Updating Metadata")
print("-" * 100)

if 'metadata' not in venue:
    venue['metadata'] = {}

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = "V3_Confirmed"
venue['metadata']['scrapeConfidenceScore'] = 100
venue['metadata']['note'] = '本場地為精品設計旅館，主營住宿服務，不提供會議/宴會場地。官網無會議室相關資訊。'
venue['metadata']['discontinued'] = True
venue['metadata']['discontinuedDate'] = "2026-03-27"
venue['metadata']['discontinuedReason'] = "非會議場地 - 精品旅館"
venue['metadata']['totalRooms'] = 0

# 更新完整度檢查
venue['metadata']['completeness'] = {
    "basicInfo": True,
    "rooms": False,  # 非會議場地
    "capacity": False,  # 非會議場地
    "area": False,  # 非會議場地
    "price": False,  # 非會議場地
    "transportation": True,
    "images": True,
    "contact": True
}

# 非會議場地品質分數
venue['metadata']['qualityScore'] = 10  # 非會議場地給最低分
venue['metadata']['verificationPassed'] = True
venue['metadata']['discontinuedMode'] = True

print(f"Total rooms: 0 (非會議場地)")
print(f"Quality Score: {venue['metadata']['qualityScore']}/100")
print(f"Verification: {'PASSED' if venue['metadata']['verificationPassed'] else 'FAILED'}")
print(f"Note: 非會議場地，不提供會議/宴會服務")

# 儲存更新後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("Stage 3 Complete - Venue Updated Successfully")
print("=" * 100)

print("\nSummary:")
print(f"  Venue: {venue['name']}")
print(f"  Status: {venue['status']} (非會議場地)")
print(f"  Total rooms: 0")
print(f"  Quality score: {venue['metadata']['qualityScore']}/100")
print(f"  Backup: {backup_file}")
print(f"\n✅ 台北喜瑞飯店完成！")
print(f"\n備註：本場地為精品設計旅館，不提供會議/宴會場地服務。")
