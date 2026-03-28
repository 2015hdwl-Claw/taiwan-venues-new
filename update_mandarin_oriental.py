#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新文華東方 venues.json - 標記為「需詢問」
使用完整欄位結構，所有欄位設為 NULL
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def create_complete_room_structure():
    """建立完整 30 欄位會議室資料結構（全部 NULL）"""
    return {
        # 基本資料
        'id': None,
        'name': None,
        'nameEn': None,
        'floor': None,
        # 面積資料
        'area': None,
        'areaUnit': None,
        'areaSqm': None,
        'areaPing': None,
        # 尺寸
        'dimensions': {'length': None, 'width': None, 'height': None},
        # 容量資料
        'capacity': {
            'theater': None,
            'banquet': None,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        # 價格資料
        'price': {
            'weekday': None,
            'holiday': None,
            'morning': None,
            'afternoon': None,
            'evening': None,
            'fullDay': None,
            'hourly': None,
            'note': '需詢問'
        },
        # 設備資料
        'equipment': None,
        'equipmentList': [],
        # 其他
        'features': '需聯繫飯店索取資料',
        'source': '需詢問',
        'lastUpdated': datetime.now().isoformat()
    }


def main():
    print('=' * 80)
    print('更新文華東方 venues.json - 標記為「需詢問」')
    print('=' * 80)
    print()

    # 載入 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到文華東方
    venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1085), None)
    if not venue_idx:
        print('❌ 找不到文華東方')
        return

    venue = venues[venue_idx]

    # 備份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'venues.json.backup.mandarin_{timestamp}'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'[1/2] 備份: {backup_path}')
    print()

    # 更新聯絡資訊
    print('[2/2] 更新聯絡資訊...')
    print()

    if 'contact' not in venue:
        venue['contact'] = {}

    venue['contact']['email'] = 'motpe-reservations@mohg.com'
    venue['contact']['inquiry_required'] = True

    # 建立佔位會議室（使用完整欄位結構）
    placeholder_room = create_complete_room_structure()
    placeholder_room['id'] = '1085-01'
    placeholder_room['name'] = '會議室（需詢問）'
    placeholder_room['nameEn'] = 'Meeting Room (Inquiry Required)'
    placeholder_room['features'] = '文華東方未提供網路會議室資料，需聯繫飯店索取'
    placeholder_room['source'] = '標記為需詢問 - 官網無會議室資料'

    venue['rooms'] = [placeholder_room]

    # 更新 metadata
    if 'metadata' not in venue:
        venue['metadata'] = {}

    venue['metadata'].update({
        'lastScrapedAt': datetime.now().isoformat(),
        'scrapeVersion': 'manual_inquiry_required',
        'inquiryRequired': True,
        'totalRooms': 1,
        'dataQuality': '需詢問 - 官網無會議室資料',
        'contactEmail': 'motpe-reservations@mohg.com',
        'hasCompleteStructure': True,
        'notes': '官網未提供會議室、容量、價格等資料。需聯繫飯店索取完整資訊。'
    })

    # 儲存
    venues[venue_idx] = venue
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f'✅ 已更新 venues.json')
    print()
    print(f'聯絡 Email: {venue["contact"]["email"]}')
    print(f'會議室: {len(venue["rooms"])} 個（佔位）')
    print()

    print('=' * 80)
    print('✅ 文華東方更新完成')
    print('=' * 80)
    print()
    print('處理方式:')
    print('  ✅ 使用完整欄位結構（30 欄位）')
    print('  ✅ 所有資料欄位設為 NULL')
    print('  ✅ 標記為「需詢問」')
    print('  ✅ 更新聯絡 Email')
    print('  ✅ 加入 metadata 說明')
    print()
    print('聯絡資訊:')
    print(f'  Email: {venue["contact"]["email"]}')


if __name__ == '__main__':
    main()
