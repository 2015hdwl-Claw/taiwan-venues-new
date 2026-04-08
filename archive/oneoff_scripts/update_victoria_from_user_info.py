#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
維多麗亞酒店 - 根據用戶提供的正確資訊更新
資料來源: https://grandvictoria.com.tw/會議室會/
PDF: https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf
用戶確認: 大宴會廳裡面的貴賓室，上/下午每時段 NT$10,000
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('維多麗亞酒店 - 根據官網 PDF 價格表更新')
    print('=' * 80)
    print()

    # 用戶提供的正確資訊
    meeting_url = 'https://grandvictoria.com.tw/會議室會/'
    pdf_url = 'https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf'

    print(f'資料來源: {meeting_url}')
    print(f'PDF 價格表: {pdf_url}')
    print(f'用戶確認: 貴賓室上/下午每時段 NT$10,000')
    print()

    # Load venues.json
    print('[1/3] 載入 venues.json...')
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # Find Victoria
    venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1122), None)
    if not venue_idx:
        print('❌ 找不到維多麗亞酒店')
        return

    venue = venues[venue_idx]
    print(f'✅ 找到: {venue["name"]}')
    print()

    # 根據 PDF 更新會議室資料
    print('[2/3] 更新會議室資料（根據官方 PDF）...')
    print('-' * 80)

    corrected_rooms = [
        {
            'id': '1122-01',
            'name': '大宴會廳',
            'nameEn': 'Grand Ballroom',
            'floor': '1F',
            'capacity': {
                'theater': 500,
                'banquet': 360
            },
            'area': 165,
            'areaUnit': '坪',
            'price': {
                'morning': 100000,
                'afternoon': 100000,
                'evening': 300000,
                'fullDay': 360000,
                'note': '含貴賓室：上/下午每時段 NT$10,000'
            },
            'equipment': '投影機、音響、麥克風、舞台',
            'source': '官方 PDF 2022: 會議宴席容納場租表'
        },
        {
            'id': '1122-02',
            'name': '維多麗亞廳',
            'nameEn': 'Victoria Hall',
            'floor': '3F',
            'capacity': {
                'theater': 300,
                'banquet': 200
            },
            'area': 120,
            'areaUnit': '坪',
            'price': {
                'morning': 80000,
                'afternoon': 80000,
                'evening': 240000,
                'fullDay': 280000
            },
            'equipment': '投影機、音響、麥克風',
            'source': '官方 PDF 2022'
        },
        {
            'id': '1122-03',
            'name': '天璳廳',
            'nameEn': 'Tianxi Hall',
            'floor': '3F',
            'capacity': {
                'theater': 200,
                'banquet': 140
            },
            'area': 80,
            'areaUnit': '坪',
            'price': {
                'morning': 60000,
                'afternoon': 60000,
                'evening': 180000,
                'fullDay': 240000
            },
            'equipment': '投影機、音響、麥克風',
            'source': '官方 PDF 2022'
        },
        {
            'id': '1122-04',
            'name': '貴賓室',
            'nameEn': 'VIP Room',
            'floor': '1F',
            'description': '位於大宴會廳內',
            'capacity': {
                'theater': 50,
                'banquet': 30
            },
            'price': {
                'morning': 10000,
                'afternoon': 10000,
                'note': '每時段 NT$10,000（用戶確認）'
            },
            'equipment': None,
            'source': '官方 PDF 2022'
        },
        {
            'id': '1122-05',
            'name': 'N°168 PRIME 牛排館',
            'floor': '1F',
            'capacity': {
                'banquet': 80
            },
            'equipment': None,
            'price': None,
            'source': '官網'
        },
        {
            'id': '1122-06',
            'name': 'LA FESTA 餐廳',
            'floor': '1F',
            'capacity': {
                'banquet': 60
            },
            'equipment': None,
            'price': None,
            'source': '官網'
        },
        {
            'id': '1122-07',
            'name': '雙囍中餐廳',
            'floor': '1F',
            'capacity': {
                'banquet': 100
            },
            'equipment': None,
            'price': None,
            'source': '官網'
        }
    ]

    for room in corrected_rooms:
        name = room['name']
        name_en = room.get('nameEn', '')
        floor = room.get('floor', 'N/A')
        cap = room['capacity'].get('theater') or room['capacity'].get('banquet', 'N/A')
        price = room.get('price')

        print(f'✅ {name}')
        if name_en:
            print(f'   {name_en}')
        print(f'   樓層: {floor}, 容量: {cap} 人')
        if price:
            if price.get('morning'):
                print(f'   價格: 上午${price["morning"]:,}, 下午${price["afternoon"]:,}')
                if price.get('evening'):
                    print(f'          晚上${price["evening"]:,}, 全天${price["fullDay"]:,}')
            if price.get('note'):
                print(f'   備註: {price["note"]}')
        print()

    # Update venue
    venue['rooms'] = corrected_rooms
    venue['url'] = 'https://www.grandvictoria.com.tw/會議室會/'
    venue['maxCapacityTheater'] = 500

    # Update metadata
    if 'metadata' not in venue:
        venue['metadata'] = {}

    venue['metadata'].update({
        'lastScrapedAt': datetime.now().isoformat(),
        'scrapeVersion': 'Official_Meeting_Page_PDF_2022_Corrected',
        'pdfUrl': pdf_url,
        'meetingPageUrl': meeting_url,
        'priceSource': '官方 PDF: 會議宴席容納場租表',
        'userConfirmed': '貴賓室上/下午每時段 NT$10,000',
        'totalRooms': len(corrected_rooms),
        'priceCoverage': '57% (4/7 有價格)',
        'dataQuality': 'Corrected by user'
    })

    # Save
    print('[3/3] 儲存更新...')

    # Backup
    backup_path = f"venues.json.backup.victoria_corrected_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'✅ 備份: {backup_path}')

    # Save main file
    venues[venue_idx] = venue
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'✅ 已更新 venues.json')

    print()
    print('=' * 80)
    print('✅ 維多麗亞酒店資料更新完成')
    print('=' * 80)
    print()
    print('會議室數: 7')
    print('價格覆蓋: 4/7 (57%)')
    print()
    print('關鍵更新:')
    print('  ✅ 大宴會廳 - 完整價格')
    print('  ✅ 貴賓室 - 上/下午 NT$10,000/時段')
    print('  ✅ 維多麗亞廳 - 完整價格')
    print('  ✅ 天璳廳 - 完整價格')
    print()
    print(f'資料來源:')
    print(f'  會議室頁面: {meeting_url}')
    print(f'  PDF 價格表: {pdf_url}')


if __name__ == '__main__':
    main()
