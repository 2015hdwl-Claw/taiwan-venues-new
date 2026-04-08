#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析維多麗亞酒店 PDF 表格結構
建立正確的場地細分資料
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_victoria_pdf():
    """解析維多麗亞酒店 PDF 表格"""

    print('=' * 80)
    print('維多麗亞酒店 PDF 表格解析')
    print('=' * 80)
    print()

    # 載入原始提取資料
    with open('victoria_pdf_extraction_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    table = data['tables'][0]['table']

    # 表格結構分析
    # 欄位：樓層, 廳名, 坪, 平方, 長, 寬, 高, 上/下午時段, 晚餐時段, 全日時段, 超時計費, 夜間佈置, U-Shape, Classroom, Theater, Cocktail, Round

    venues = []

    i = 0
    while i < len(table):
        row = table[i]

        # 跳過標題和空行
        if len(row) < 2 or not row[1]:
            i += 1
            continue

        venue_name = row[1]

        # 跳過標題行
        if venue_name in ['廳名', 'Venues', 'Grand Ballroom', 'Area A', 'Area B', 'Area C',
                          'Victoria Ballroom', 'VIP Room', 'Victoria Garden', 'Noble Ballroom',
                          'Noble Ballroom 1', 'Noble Ballroom 2', 'Noble Ballroom 3']:
            i += 1
            continue

        # 檢查是否有坪數資料（index 2）
        if row[2] and row[2].replace('.', '').isdigit():
            ping = float(row[2]) if row[2] else None
            sqm = float(row[3]) if len(row) > 3 and row[3] else None

            # 價格資料
            price_morning = row[7] if len(row) > 7 else None
            price_evening = row[8] if len(row) > 8 else None
            price_full = row[9] if len(row) > 9 else None

            # 清理價格字串
            def clean_price(price_str):
                if not price_str or price_str == '-':
                    return None
                try:
                    return int(price_str.replace('NT$', '').replace(',', '').replace('.', '').strip())
                except:
                    return None

            venue = {
                'name': venue_name,
                'areaPing': ping,
                'areaSqm': sqm,
                'priceMorning': clean_price(price_morning),
                'priceEvening': clean_price(price_evening),
                'priceFull': clean_price(price_full),
                'rawRow': row
            }

            venues.append(venue)
            print(f'✅ {venue_name}')
            print(f'   面積: {ping} 坪 ({sqm} ㎡)')
            if venue['priceMorning']:
                print(f'   價格: 上午 NT${venue["priceMorning"]:,}, 晚上 NT${venue["priceEvening"]:,}, 全天 NT${venue["priceFull"]:,}')
            print()

        i += 1

    print(f'總共找到 {len(venues)} 個場地')
    print()

    # 儲存結果
    result = {
        'extractedAt': datetime.now().isoformat(),
        'totalVenues': len(venues),
        'venues': venues
    }

    with open('victoria_venues_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print('✅ 已儲存到 victoria_venues_parsed.json')

    return venues


if __name__ == '__main__':
    parse_victoria_pdf()
