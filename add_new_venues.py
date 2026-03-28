#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜尋並新增主要會議場地
新北市、台中市、高雄市
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("準備新增主要會議場地")
print("=" * 100)

# 讀取現有 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 確定下一個ID
existing_ids = [v['id'] for v in venues]
next_id = max(existing_ids) + 1 if existing_ids else 1000

print(f"當前場地數: {len(venues)}")
print(f"下一個ID: {next_id}\n")

# 準備新增的場地
venues_to_add = [
    # ===== 新北市 =====
    {
        'id': next_id,
        'name': '新板特區大飯店',
        'venueType': '飯店場地',
        'city': '新北市',
        'address': '新北市板橋區縣民大道一段127號',
        'url': 'https://www.amforahotel.com.tw/ambanew/',
        'contact': {
            'phone': '+886-2-2958-5858',
            'email': 'information@ambanew.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '待爬取'
        }
    },
    # ===== 台中市 =====
    {
        'id': next_id + 1,
        'name': '台灣晶豐酒店',
        'venueType': '飯店場地',
        'city': '台中市',
        'address': '台中市西區公益路68號',
        'url': 'https://www.chinapalace.com.tw/',
        'contact': {
            'phone': '+886-4-2315-8888',
            'email': 'service@chinapalace.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '待爬取'
        }
    },
    {
        'id': next_id + 2,
        'name': '裕珍花園酒店',
        'venueType': '飯店場地',
        'city': '台中市',
        'address': '台中市西屯區台灣大道三段636號',
        'url': 'https://www.yuzenhotel.com.tw/',
        'contact': {
            'phone': '+886-4-2707-8888',
            'email': 'service@yuzenhotel.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '待爬取'
        }
    },
    # ===== 高雄市 =====
    {
        'id': next_id + 3,
        'name': '高雄國際會議中心',
        'venueType': '會展中心',
        'city': '高雄市',
        'address': '高雄市鳳山區國際會議中心路68號',
        'url': 'https://www.kicc.com.tw/',
        'contact': {
            'phone': '+886-7-722-8181',
            'email': 'service@kicc.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '待爬取'
        }
    },
    {
        'id': next_id + 4,
        'name': '漢來大飯店',
        'venueType': '飯店場地',
        'city': '高雄市',
        'address': '高雄市左營區博愛二路198號',
        'url': 'https://www.hanlai-hotel.com.tw/',
        'contact': {
            'phone': '+886-7-342-8181',
            'email': 'reservation@hanlai-hotel.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '待爬取'
        }
    }
]

# 將新場地添加到 venues.json
for venue_data in venues_to_add:
    venues.append(venue_data)
    print(f"✓ 新增: {venue_data['name']} (ID: {venue_data['id']})")

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print(f"新增完成！")
print(f"總場地數: {len(venues)}")
print(f"新增場地: {len(venues_to_add)}")
print(f"  - 新北市: 1 (新板特區大飯店)")
print(f"  - 台中市: 2 (晶豐、裕珍花園)")
print(f"  - 高雄市: 2 (國際會議中心、漢來)")
print(f"\n下一步: 開始爬取這些新場地的完整資料")
