#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下架無法訪問的場地
1. Regus商務中心 (1035) - Cookie 錯誤
2. 台北一樂園大飯店 (1048) - DNS 解析失敗
3. 台北友春大飯店 (1059) - DNS 解析失敗
4. 台北唯客樂文旅 (1065) - 連接超時
5. 台北商務會館 (1066) - DNS 解析失敗
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*100)
print("下架無法訪問的場地")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.discontinue_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# Venues to discontinue
venues_to_discontinue = {
    1035: {
        'name': 'Regus商務中心',
        'reason': 'Cookie 錯誤 - 網站使用複雜的 Cookie 設置，導致爬蟲無法正常訪問',
        'website_status': 'inaccessible'
    },
    1048: {
        'name': '台北一樂園大飯店',
        'reason': 'DNS 解析失敗 - www.ile-hotel.com 域名無法解析，網站可能已下線',
        'website_status': 'dns_failed'
    },
    1059: {
        'name': '台北友春大飯店',
        'reason': 'DNS 解析失敗 - www.youchun-hotel.com 域名無法解析',
        'website_status': 'dns_failed'
    },
    1065: {
        'name': '台北唯客樂文旅',
        'reason': '連接超時 - 網站回應超時 (>15秒)',
        'website_status': 'timeout'
    },
    1066: {
        'name': '台北商務會館',
        'reason': 'DNS 解析失敗 - www.tbc-group.com 域名無法解析',
        'website_status': 'dns_failed'
    },
    1073: {
        'name': '台北姿美大飯店',
        'reason': 'DNS 解析失敗 - 域名無法解析，網站可能已下線',
        'website_status': 'dns_failed'
    },
    1080: {
        'name': '台北康華大飯店',
        'reason': 'DNS 解析失敗 - 域名無法解析',
        'website_status': 'dns_failed'
    },
    1084: {
        'name': '台北慶泰大飯店',
        'reason': 'TLS 錯誤 - SSL 憑證問題，無法建立安全連接',
        'website_status': 'tls_error'
    },
    1092: {
        'name': '台北第一大飯店',
        'reason': '連接失敗 - 無法建立連接',
        'website_status': 'connection_failed'
    }
}

print("="*100)
print("處理下架場地")
print("="*100)
print()

for venue_id, info in venues_to_discontinue.items():
    venue_idx = next((i for i, v in enumerate(data) if v.get('id') == venue_id), None)

    if venue_idx is None:
        print(f"❌ 找不到場地 ID {venue_id}")
        continue

    venue = data[venue_idx]
    print(f"處理: {venue['name']} (ID: {venue_id})")

    # 記錄原會議室數量
    original_rooms = venue.get('rooms', [])
    room_count = len(original_rooms)

    # 下架會議室
    venue['rooms'] = []

    # 標記為下架
    if 'metadata' not in venue:
        venue['metadata'] = {}

    venue['metadata']['meetingRoomsStatus'] = 'discontinued'
    venue['metadata']['meetingRoomsRemovedAt'] = datetime.now().isoformat()
    venue['metadata']['originalRoomCount'] = room_count
    venue['metadata']['discontinueReason'] = info['reason']
    venue['metadata']['websiteStatus'] = info['website_status']
    venue['metadata']['discontinuedAt'] = datetime.now().isoformat()
    venue['metadata']['discontinuedBy'] = 'universal_scraper'

    # 標記場地狀態
    venue['status'] = 'discontinued'
    venue['enabled'] = False

    data[venue_idx] = venue

    print(f"   ✅ 已下架所有會議室 (原 {room_count} 間)")
    print(f"   原因: {info['reason']}")
    print()

# 儲存更新
print("="*100)
print("儲存更新")
print("="*100)

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存更新到 venues.json\n")

# 總結
print("="*100)
print("✅ 下架完成")
print("="*100)
print()

print(f"總共下架: {len(venues_to_discontinue)} 個場地")
print()

print("下架場地列表:")
for i, (venue_id, info) in enumerate(venues_to_discontinue.items(), 1):
    print(f"   {i}. {info['name']} (ID: {venue_id})")
    print(f"      原因: {info['reason']}")
print()

print("備註:")
print("- 所有會議室已移除")
print("- 保留歷史記錄在 metadata")
print("- 場地狀態標記為 discontinued")
print("- 已備份原始資料")
print()

print(f"備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
