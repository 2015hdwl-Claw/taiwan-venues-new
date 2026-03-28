#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正所有場地的 pagesDiscovered 值
根據 V4 批次處理的實際輸出記錄修正
"""
import json

# 從批次處理輸出中提取的實際頁面發現數
actual_pages_discovered = {
    # 最新的批次處理（已知確切數字）
    1051: 20,  # 台北亞都麗緻 - 20 pages (8 meeting, 4 access, 2 contact, 3 policy, 3 gallery)
    1082: 0,   # 台北怡亨酒店 - 0 pages (無法發現頁面)
    1083: 0,   # 台北北門世民酒店 - 0 pages (無法發現頁面)
    1085: 2,   # 台北文華東方酒店 - 2 pages (1 meeting, 1 gallery)
    1121: 0,   # 神旺大飯店 - 0 pages (無法發現頁面)
    1122: 9,   # 維多麗亞酒店 - 9 pages (5 meeting, 2 gallery, 1 contact, 1 access)
    1124: 7,   # 花園大酒店 - 7 pages (4 meeting, 1 gallery, 1 contact, 1 access)
    1125: 2,   # 華山1914 - 2 pages (1 access, 1 gallery)
    1126: 2,   # 豪景大酒店 - 2 pages (1 meeting, 1 access)
    1128: 8,   # 集思台大會議中心 - 8 pages (7 meeting, 1 access)
    1129: 2,   # 青青婚宴會館 - 2 pages (1 meeting, 1 contact)
    1334: 1,   # 台北中山運動中心 - 1 page (1 access)
    1448: 1,   # 台北國際會議中心 - 1 page (1 access)
    1493: 20,  # 師大進修推廣學院 - 20 pages (7 meeting, 5 access, 3 contact, 3 policy, 3 gallery)
    1494: 2,   # 集思交通部國際會議中心 - 2 pages (1 access, 1 meeting)
    1495: 0,   # 集思北科大會議中心 - 0 pages (404 error)
    1496: 0,   # 集思竹科會議中心 - 0 pages (404 error)
    1497: 0,   # 集思台中文心會議中心 - 0 pages (404 error)
    1498: 0,   # 集思台中新烏日會議中心 - 0 pages (404 error)
    1499: 0,   # 集思國際會議高雄分公司 - 0 pages (404 error)
}

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed_count = 0
for venue_id, correct_pages in actual_pages_discovered.items():
    venue = next((v for v in data if v.get('id') == venue_id), None)
    if venue and venue.get('metadata', {}).get('fullSiteScraped'):
        current_pages = venue.get('metadata', {}).get('pagesDiscovered', -1)
        if current_pages != correct_pages:
            if 'metadata' not in venue:
                venue['metadata'] = {}
            venue['metadata']['pagesDiscovered'] = correct_pages
            fixed_count += 1
            print(f'[FIX] Venue {venue_id}: {current_pages} -> {correct_pages} pages')

# 儲存修正後的資料
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n[OK] Fixed {fixed_count} venues')
print('[OK] Saved to venues.json')
