#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量新增所有新場地（新北、台中、高雄）
"""

import json
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("批量新增所有新場地")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.add_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

# 確定下一個ID
existing_ids = [v['id'] for v in venues]
next_id = max(existing_ids) + 1 if existing_ids else 1000

print(f"當前場地數: {len(venues)}")
print(f"下一個ID: {next_id}\n")

# 新北市場地
new_venues_newtaipei = [
    {
        'id': next_id,
        'name': '晶宴會館 峇里斯莊園',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市林口區仁愛路二段1號',
        'url': 'https://www.amazinghall.com.tw/',
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
        'id': next_id + 1,
        'name': '晶宴會館 府中館',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市板橋區',  # 需要詳細地址
        'url': 'https://www.amazinghall.com.tw/',
        'contact': {
            'phone': '+886-3-452-6688',
            'email': 'service@amazinghall.com.tw'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '府中館'
        }
    },
    {
        'id': next_id + 2,
        'name': '彭園婚宴會館 新店館',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市新店區',  # 需要詳細地址
        'url': 'https://www.pengyuan.com.tw/',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '新店館/新板館/三重館'
        }
    },
    {
        'id': next_id + 3,
        'name': '頤品大飯店 新莊晶冠館',
        'venueType': '飯店場地',
        'city': '新北市',
        'address': '新北市新莊區',  # 需要詳細地址
        'url': 'https://www.palaiscollection.com/',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '晶冠館'
        }
    },
    {
        'id': next_id + 4,
        'name': '靚點宴會館',
        'venueType': '婚宴場地',
        'city': '新北市',
        'address': '新北市新店區',
        'url': 'https://liang-life.com/',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '新店'
        }
    }
]

# 台中市場地
new_venues_taichung = [
    {
        'id': next_id + 5,
        'name': '葳格國際會議中心',
        'venueType': '會議中心',
        'city': '台中市',
        'address': '台中市',  # 需要詳細地址
        'url': 'https://www.weddingday.com.tw/store-venue/5651',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': 'Wagor'
        }
    },
    {
        'id': next_id + 6,
        'name': '寶麗金婚宴會館 市政店',
        'venueType': '婚宴場地',
        'city': '台中市',
        'address': '台中市西屯區',
        'url': 'https://www.weddings.tw/',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '市政店'
        }
    },
    {
        'id': next_id + 7,
        'name': '寶麗金婚宴會館 崇德店',
        'venueType': '婚宴場地',
        'city': '台中市',
        'address': '台中市北屯區',
        'url': 'https://www.weddings.tw/',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '崇德店'
        }
    },
    {
        'id': next_id + 8,
        'name': '天圓地方婚宴會館',
        'venueType': '婚宴場地',
        'city': '台中市',
        'address': '台中市',
        'url': 'https://xycuisinetw.com/',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '婚宴會館'
        }
    },
    {
        'id': next_id + 9,
        'name': '好運來洲際宴展中心',
        'venueType': '展演場地',
        'city': '台中市',
        'address': '台中市',
        'url': 'TBD',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '搜尋好運來洲際宴展中心台中'
        }
    },
    {
        'id': next_id + 10,
        'name': '林皇宮花園',
        'venueType': '婚宴場地',
        'city': '台中市',
        'address': '台中市',
        'url': 'TBD',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '搜尋台中林皇宮'
        }
    },
    {
        'id': next_id + 11,
        'name': '潮港城宴會廳 南屯店',
        'venueType': '婚宴場地',
        'city': '台中市',
        'address': '台中市南屯區',
        'url': 'https://www.ckcchao.com/rental',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '南屯等'
        }
    }
]

# 高雄市場地
new_venues_kaohsiung = [
    {
        'id': next_id + 12,
        'name': '蓮潭國際會館',
        'venueType': '飯店場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'TBD',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '會議+婚宴'
        }
    },
    {
        'id': next_id + 13,
        'name': '義大世界會議中心',
        'venueType': '會議中心',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'TBD',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '義大世界'
        }
    },
    {
        'id': next_id + 14,
        'name': '漢來國際宴會廳',
        'venueType': '婚宴場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'https://www.grand-hilai.com/',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '宴會廳部分'
        }
    },
    {
        'id': next_id + 15,
        'name': '福客來南北樓',
        'venueType': '婚宴場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'TBD',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '中式婚宴會館'
        }
    },
    {
        'id': next_id + 16,
        'name': '富苑喜宴會館',
        'venueType': '婚宴場地',
        'city': '高雄市',
        'address': '高雄市',
        'url': 'TBD',
        'contact': {
            'phone': 'TBD',
            'email': 'TBD'
        },
        'verified': False,
        'metadata': {
            'addedAt': '2026-03-27',
            'note': '婚宴會館'
        }
    }
]

# 合併所有新場地
all_new_venues = new_venues_newtaipei + new_venues_taichung + new_venues_kaohsiung

# 新增場地
for venue_data in all_new_venues:
    venues.append(venue_data)
    print(f"✓ 新增: {venue_data['name']} (ID: {venue_data['id']})")
    print(f"    城市: {venue_data['city']}")
    print(f"    URL: {venue_data['url']}")

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 100}")
print("新增完成！")
print("=" * 100)
print(f"總場地數: {len(venues)}")
print(f"新增場地: {len(all_new_venues)}")
print(f"  - 新北市: {len(new_venues_newtaipei)}")
print(f"  - 台中市: {len(new_venues_taichung)}")
print(f"  - 高雄市: {len(new_venues_kaohsiung)}")
print(f"\n備份: {backup_file}")
print(f"\n下一步: 開始爬取這些新場地的完整資料")
