#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析台北世貿價目表 PDF 並更新 venues.json
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_price(price_str):
    """清理價格字串"""
    if not price_str or price_str in ['-', '', '0', '0', '1']:
        return None
    try:
        # 移除逗號和其他符號
        cleaned = price_str.replace(',', '').replace('NT$', '').replace('元', '').strip()
        return int(cleaned) if cleaned else None
    except:
        return None


def main():
    print('=' * 80)
    print('解析台北世貿價目表並更新 venues.json')
    print('=' * 80)
    print()

    # 載入提取的資料
    with open('twtc_pricing_extraction.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    table = data['tables'][0]['data']

    print('[1/3] 解析會議室價格資料...')
    print()

    # 根據表格結構解析會議室
    # Row 4: 第1會議室
    # Row 5: 第2會議室
    # Row 6: 第3會議室
    # Row 7: 第4會議室
    # Row 9: 第5會議室
    # Row 10: A+會議室
    # Row 11: 第1、5間廊廳
    # Row 12: 1樓貴賓室

    rooms_pricing = {}

    # 第1會議室 (Row 4, index 3)
    if len(table) > 4:
        row = table[4]
        weekday = parse_price(row[4])  # 日間每時段租金
        holiday = parse_price(row[5])  # 例假日每時段租金
        if weekday and holiday:
            rooms_pricing['第一會議室'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # 第2會議室 (Row 5)
    if len(table) > 5:
        row = table[5]
        weekday = parse_price(row[4])
        holiday = parse_price(row[5])
        if weekday and holiday:
            rooms_pricing['第二會議室'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # 第3會議室 (Row 6)
    if len(table) > 6:
        row = table[6]
        weekday = parse_price(row[4])
        holiday = parse_price(row[5])
        if weekday and holiday:
            rooms_pricing['第三會議室'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # 第4會議室 (Row 7)
    if len(table) > 7:
        row = table[7]
        weekday = parse_price(row[4])
        holiday = parse_price(row[5])
        if weekday and holiday:
            rooms_pricing['第四會議室'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # 第5會議室 (Row 9)
    if len(table) > 9:
        row = table[9]
        weekday = parse_price(row[4])
        holiday = parse_price(row[5])
        if weekday and holiday:
            rooms_pricing['第五會議室'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # A+會議室 (Row 10)
    if len(table) > 10:
        row = table[10]
        weekday = parse_price(row[4])
        holiday = parse_price(row[5])
        if weekday and holiday:
            rooms_pricing['A+會議室'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # 第1、5間廊廳 (Row 11)
    if len(table) > 11:
        row = table[11]
        weekday = parse_price(row[4])
        holiday = parse_price(row[5])
        if weekday and holiday:
            rooms_pricing['第1、5間廊廳'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # 1樓貴賓室 (Row 12)
    if len(table) > 12:
        row = table[12]
        weekday = parse_price(row[4])
        holiday = parse_price(row[5])
        if weekday and holiday:
            rooms_pricing['1樓貴賓室'] = {
                'weekday': weekday,
                'holiday': holiday
            }

    # 顯示解析結果
    print(f'成功解析 {len(rooms_pricing)} 個會議室的價格:')
    for name, price in rooms_pricing.items():
        print(f'  ✅ {name}:')
        print(f'     平日: NT${price["weekday"]:,}/時段')
        print(f'     假日: NT${price["holiday"]:,}/時段')
        print()

    # 更新 venues.json
    print('[2/3] 更新 venues.json...')

    # 載入 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到台北世貿中心
    venue_idx = next((i for i, v in enumerate(venues) if v.get('id') == 1049), None)
    if not venue_idx:
        print('❌ 找不到台北世貿中心')
        return

    venue = venues[venue_idx]

    # 備份
    backup_path = f"venues.json.backup.twtc_pricing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'✅ 備份: {backup_path}')
    print()

    # 更新會議室價格
    rooms = venue.get('rooms', [])
    updated_count = 0

    for room in rooms:
        room_name = room.get('name', '')

        # 對照名稱
        if '第一會議室' in room_name:
            if '第一會議室' in rooms_pricing:
                room['price'] = rooms_pricing['第一會議室']
                room['source'] = '官方 PDF 2025.10'
                updated_count += 1

        elif '第二會議室' in room_name:
            if '第二會議室' in rooms_pricing:
                room['price'] = rooms_pricing['第二會議室']
                room['source'] = '官方 PDF 2025.10'
                updated_count += 1

        elif '第三會議室' in room_name:
            if '第三會議室' in rooms_pricing:
                room['price'] = rooms_pricing['第三會議室']
                room['source'] = '官方 PDF 2025.10'
                updated_count += 1

        elif '第四會議室' in room_name:
            if '第四會議室' in rooms_pricing:
                room['price'] = rooms_pricing['第四會議室']
                room['source'] = '官方 PDF 2025.10'
                updated_count += 1

        elif '第五會議室' in room_name:
            if '第五會議室' in rooms_pricing:
                room['price'] = rooms_pricing['第五會議室']
                room['source'] = '官方 PDF 2025.10'
                updated_count += 1

        elif 'A+會議室' in room_name:
            if 'A+會議室' in rooms_pricing:
                room['price'] = rooms_pricing['A+會議室']
                room['source'] = '官方 PDF 2025.10'
                updated_count += 1

    print(f'✅ 已更新 {updated_count} 個會議室的價格')
    print()

    # 更新 metadata
    if 'metadata' not in venue:
        venue['metadata'] = {}

    venue['metadata'].update({
        'lastScrapedAt': datetime.now().isoformat(),
        'scrapeVersion': 'pdfplumber_twtc_pricing',
        'pdfParser': 'pdfplumber',
        'pdfUrl': 'https://www.twtc.com.tw/file/DB/images_G1/2025會議室價目表2025.10版.pdf',
        'pdfFilename': 'twtc_pricing_2025.pdf',
        'priceSource': '官方 PDF: 會議室暨設備價目表 2025.10版',
        'priceCoverage': f'{updated_count}/{len(rooms)}',
        'dataQuality': '使用 pdfplumber 解析官方 PDF',
        'discoveredVia': 'meeting_form 頁面'
    })

    # 儲存
    venues[venue_idx] = venue
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print('[3/3] 儲存完成')

    print()
    print('=' * 80)
    print('✅ 台北世貿中心價格資料更新完成')
    print('=' * 80)
    print()
    print(f'更新會議室數: {updated_count}/{len(rooms)}')
    print(f'價格覆蓋率: {updated_count * 100 // len(rooms)}%')
    print()
    print('價格格式:')
    print('  - weekday: 平日每時段租金（NT$）')
    print('  - holiday: 例假日每時段租金（NT$）')
    print()
    print('資料來源:')
    print('  - PDF: 2025會議室價目表2025.10版.pdf')
    print('  - URL: https://www.twtc.com.tw/meeting_form')
    print()


if __name__ == '__main__':
    main()
