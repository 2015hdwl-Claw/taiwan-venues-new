#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 V4 metadata - 為已處理但缺少標記的場地補上 V4 標記
"""
import json
from datetime import datetime

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 在批次處理中已經爬取但沒有正確設定 metadata 的場地
# 根據批次處理輸出，這些場地成功發現了頁面：
processed_venues = {
    1051: 20,  # 台北亞都麗緻 - 20 pages
    1082: 0,   # 台北怡亨酒店 - 0 pages
    1083: 0,   # 台北北門世民酒店 - 0 pages
    1085: 2,   # 台北文華東方酒店 - 2 pages
    1121: 0,   # 神旺大飯店 - 0 pages
    1495: 0,   # 集思北科大會議中心 - 0 pages
    1496: 0,   # 集思竹科會議中心 - 0 pages
    1497: 0,   # 集思台中文心會議中心 - 0 pages
    1498: 0,   # 集思台中新烏日會議中心 - 0 pages
    1499: 0,   # 集思國際會議高雄分公司 - 0 pages
}

fixed_count = 0
for venue_id, pages_discovered in processed_venues.items():
    venue = next((v for v in data if v.get('id') == venue_id), None)
    if venue:
        if 'metadata' not in venue:
            venue['metadata'] = {}

        # 檢查是否已經有 V4 標記
        if venue['metadata'].get('scrapeVersion') != 'V4':
            venue['metadata'].update({
                'lastScrapedAt': datetime.now().isoformat(),
                'scrapeVersion': 'V4',
                'pagesDiscovered': pages_discovered,
                'fullSiteScraped': True
            })
            fixed_count += 1
            print(f'[FIX] Venue {venue_id}: {pages_discovered} pages')

# 儲存修正後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n[OK] Fixed {fixed_count} venues')
print('[OK] Saved to venues.json')
