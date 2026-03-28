#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查台北世貿會議室詳細頁面
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('台北世貿會議室詳細頁面檢查')
    print('=' * 80)
    print()

    base_url = 'https://www.twtc.com.tw/'

    # 會議室頁面列表
    meeting_rooms = [
        {'name': '第一會議室', 'url': 'https://www.twtc.com.tw/meeting1'},
        {'name': 'A+會議室', 'url': 'https://www.twtc.com.tw/meeting11'},
        {'name': '第二會議室', 'url': 'https://www.twtc.com.tw/meeting2'},
        {'name': '第三會議室', 'url': 'https://www.twtc.com.tw/meeting3'},
    ]

    all_room_data = []

    for room in meeting_rooms:
        name = room['name']
        url = room['url']

        print(f'檢查: {name}')
        print(f'URL: {url}')

        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取頁面文字
            page_text = soup.get_text()

            # 尋找價格資訊
            import re
            price_pattern = r'[nN][tT]\$?\s*[\d,]+|[\d,]+\s*元'
            prices = re.findall(price_pattern, page_text)

            # 尋找容量資訊
            capacity_pattern = r'容量\s*[:：]?\s*\d+\s*人|\d+\s*人'
            capacities = re.findall(capacity_pattern, page_text)

            # 尋找面積資訊
            area_pattern = r'面積\s*[:：]?\s*[\d.]+\s*(坪|㎡|平方公尺|平方米)'
            areas = re.findall(area_pattern, page_text)

            room_data = {
                'name': name,
                'url': url,
                'has_price': len(prices) > 0,
                'prices': prices[:5],  # 只儲存前 5 個
                'has_capacity': len(capacities) > 0,
                'capacities': capacities[:5],
                'has_area': len(areas) > 0,
                'areas': areas[:5],
                'page_snippet': page_text[:200]  # 前 200 字元
            }

            print(f'  價格: {"✅ " + str(prices[:3]) if prices else "❌ 無"}')
            print(f'  容量: {"✅ " + str(capacities[:3]) if capacities else "❌ 無"}')
            print(f'  面積: {"✅ " + str(areas[:3]) if areas else "❌ 無"}')

            all_room_data.append(room_data)

        except Exception as e:
            print(f'  ❌ 錯誤: {e}')

        print()

    # 儲存結果
    print('[儲存檢查結果]')

    with open('twtc_meeting_rooms_check.json', 'w', encoding='utf-8') as f:
        json.dump(all_room_data, f, ensure_ascii=False, indent=2)

    print('✅ 結果已儲存到 twtc_meeting_rooms_check.json')

    # 總結
    print()
    print('=' * 80)
    print('總結:')
    print('=' * 80)
    print()

    has_price = sum(1 for r in all_room_data if r['has_price'])
    has_capacity = sum(1 for r in all_room_data if r['has_capacity'])

    print(f'檢查了 {len(all_room_data)} 個會議室')
    print(f'有價格資訊: {has_price}/{len(all_room_data)}')
    print(f'有容量資訊: {has_capacity}/{len(all_room_data)}')

    if has_price == 0:
        print()
        print('⚠️  所有會議室都沒有價格資訊')
        print('建議: 標記為「需聯絡詢問」')


if __name__ == '__main__':
    main()
