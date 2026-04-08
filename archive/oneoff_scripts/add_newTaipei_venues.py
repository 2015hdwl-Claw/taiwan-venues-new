#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量新增新北市場地
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("批量新增新北市場地")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.new Taipei_add_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

# 確定下一個ID
existing_ids = [v['id'] for v in venues]
next_id = max(existing_ids) + 1 if existing_ids else 1000

print(f"當前場地數: {len(venues)}")
print(f"下一個ID: {next_id}\n")

# 新北市場地清單
new_venues_data = [
    {
        'id': next_id,
        'name': '瓏山林台北中和飯店',
        'venueType': '飯店場地',
        'city': '新北市',
        'address': '新北市中和區中山路三段119號',
        'url': 'https://taipei.rslhotel.com/meeting/',
        'contact': {
            'phone': '+886-2-2226-6688',
            'email': 'rsl.tp@rslhotels.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '會議頁面: /meeting/'
        }
    },
    {
        'id': next_id + 1,
        'name': 'Mega50宴會廳',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市板橋區縣民大道三段7號30樓',
        'url': 'https://www.mega50.com.tw/ch/dingdingballroom',
        'contact': {
            'phone': '+886-2-2955-8888',
            'email': 'service@mega50.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '頂樓宴會廳'
        }
    },
    {
        'id': next_id + 2,
        'name': '豪鼎飯店',
        'venueType': '飯店場地',
        'city': '新北市',
        'address': '新北市板橋區縣民大道236號',
        'url': 'https://www.how-dine.com.tw/',
        'contact': {
            'phone': '+886-2-2956-7868',
            'email': 'service@how-dine.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '婚宴場地'
        }
    },
    {
        'id': next_id + 3,
        'name': '晶宴會館 峇里斯莊園',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市林口區仁愛路二段1號',
        'url': 'https://www.amazinghall.com.tw/branch_intro/%E5%B3%87%E9%87%8C%E6%96%AF%E8%8A%8D%E5%9C%92/',
        'contact': {
            'phone': '+886-3-452-6688',
            'email': 'service@amazinghall.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '峇里斯莊園分店'
        }
    },
    {
        'id': next_id + 4,
        'name': '新莊典華（盛典等空間）',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市新莊區中正路642號',
        'url': 'https://www.denwell.com/',
        'contact': {
            'phone': '+886-2-2997-8181',
            'email': 'service@denwell.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '有會議空間'
        }
    },
    {
        'id': next_id + 5,
        'name': '翡麗詩莊園',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市樹林區中山路二段168號',
        'url': 'https://www.felicite-wed.com/',
        'contact': {
            'phone': '+886-2-8306-8688',
            'email': 'service@felicite-wed.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '婚宴場地'
        }
    },
    {
        'id': next_id + 6,
        'name': '台北新板希爾頓酒店',
        'venueType': '飯店場地',
        'city': '新北市',
        'address': '新北市板橋區縣民大道166號',
        'url': 'https://www.hilton.com.cn/zh-hk/hotel/taipei/hilton-taipei-sinban-TSATCHI/event.html',
        'contact': {
            'phone': '+886-2-2502-8888',
            'email': 'taipei.sinban@hilton.com'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '國際連鎖酒店'
        }
    },
    {
        'id': next_id + 7,
        'name': '汐止福泰大飯店',
        'venueType': '飯店場地',
        'city': '新北市',
        'address': '新北市汐止區大同路二段234號',
        'url': 'https://www.fortehotelxizhi.com.tw/banquet-detail/meeting/',
        'contact': {
            'phone': '+886-2-8647-7777',
            'email': 'service@fortehotelxizhi.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '有會議/宴會頁面'
        }
    }
]

# 新增場地
for venue_data in new_venues_data:
    venues.append(venue_data)
    print(f"✓ 新增: {venue_data['name']} (ID: {venue_data['id']})")
    print(f"    URL: {venue_data['url']}")

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("新增完成！")
print("=" * 100)
print(f"總場地數: {len(venues)}")
print(f"新增場地: 7")
print(f"  - 瓏山林台北中和飯店 (會議頁面)")
print(f"  - Mega50宴會廳 (頂樓宴會廳)")
print(f"  - 豪鼎飯店 (婚宴場地)")
print(f"  - 晶宴會館峇里斯莊園 (婚宴場地)")
print(f"  - 新莊典華 (盛典等空間)")
print(f"  - 翡麗詩莊園 (婚宴場地)")
print(f"  - 台北新板希爾頓酒店 (國際連鎖)")
print(f"  - 汐止福泰大飯店 (會議/宴會頁面)")
print(f"\n備份: {backup_file}")
print(f"\n下一步: 開始爬取這7個場地的完整資料")
