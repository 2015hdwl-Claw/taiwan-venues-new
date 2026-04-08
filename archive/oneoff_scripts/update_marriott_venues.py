#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北萬豪 venues.json - 完整欄位
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
    print('更新台北萬豪 venues.json - 完整欄位')
    print('=' * 80)
    print()

    # 載入完整會議室資料
    with open('marriott_rooms_complete.json', 'r', encoding='utf-8') as f:
        complete_rooms = json.load(f)

    # 載入 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到台北萬豪
    venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1103), None)
    if not venue_idx:
        print('❌ 找不到台北萬豪')
        return

    venue = venues[venue_idx]

    # 備份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'venues.json.backup.marriott_{timestamp}'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'[1/3] 備份: {backup_path}')
    print()

    # 顯示會議室統計
    print('[2/3] 會議室資料統計...')
    print()

    has_area = sum(1 for r in complete_rooms if r['areaSqm'])
    has_theater = sum(1 for r in complete_rooms if r['capacity']['theater'])
    has_price = sum(1 for r in complete_rooms if r['price']['setup'])

    print(f'總會議室: {len(complete_rooms)}')
    print(f'面積覆蓋: {has_area}/{len(complete_rooms)} ({has_area*100//len(complete_rooms)}%)')
    print(f'容量覆蓋: {has_theater}/{len(complete_rooms)} ({has_theater*100//len(complete_rooms)}%)')
    print(f'價格覆蓋: {has_price}/{len(complete_rooms)} ({has_price*100//len(complete_rooms)}%)')
    print()

    # 更新 venues.json
    print('[3/3] 更新 venues.json...')
    print()

    venue['rooms'] = complete_rooms

    # 計算最大容量
    max_theater = max([r['capacity']['theater'] for r in complete_rooms if r['capacity']['theater']], default=None)
    if max_theater:
        venue['maxCapacityTheater'] = max_theater

    # 更新 metadata
    if 'metadata' not in venue:
        venue['metadata'] = {}

    venue['metadata'].update({
        'lastScrapedAt': datetime.now().isoformat(),
        'scrapeVersion': 'pdfplumber_complete_structure',
        'pdfParser': 'pdfplumber',
        'pdfUrl': 'https://www.taipeimarriott.com.tw/files/page_176778676814ut99b82.pdf',
        'discoveryUrl': 'https://www.taipeimarriott.com.tw/websev?cat=page&id=39',
        'priceSource': '官方 PDF: 場租表',
        'totalRooms': len(complete_rooms),
        'priceCoverage': f'{has_price}/{len(complete_rooms)}',
        'areaCoverage': f'{has_area}/{len(complete_rooms)}',
        'capacityCoverage': f'{has_theater}/{len(complete_rooms)}',
        'dataQuality': '完整 30 欄位結構',
        'hasCompleteStructure': True,
        'hasAreaData': True,
        'hasPriceData': True
    })

    # 儲存
    venues[venue_idx] = venue
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f'✅ 已更新 venues.json')
    print()

    print('=' * 80)
    print('✅ 台北萬豪完整資料更新完成')
    print('=' * 80)
    print()
    print(f'會議室數: {len(complete_rooms)}')
    print(f'價格覆蓋: {has_price}/{len(complete_rooms)} ({has_price*100//len(complete_rooms)}%)')
    print(f'面積覆蓋: {has_area}/{len(complete_rooms)} ({has_area*100//len(complete_rooms)}%)')
    print(f'容量覆蓋: {has_theater}/{len(complete_rooms)} ({has_theater*100//len(complete_rooms)}%)')
    print()
    print('關鍵改進:')
    print('  ✅ 添加完整欄位結構（30 個欄位）')
    print('  ✅ 面積資料（平方公尺/坪）')
    print('  ✅ 容量資料（Theater/Classroom 等）')
    print('  ✅ 價格資料（Setup/Full Day/Overnight 等）')
    print('  ✅ 空值用 NULL 呈現')
    print()
    print('下一步: 檢查文華東方')


if __name__ == '__main__':
    main()
