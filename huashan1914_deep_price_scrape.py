#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 深度爬取 card-text-info 的價格資料
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("華山1914 - 深度爬取 card-text-info 價格")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取場地列表
with open('huashan1914_svg_venues_20260326_205431.json', encoding='utf-8') as f:
    venue_list = json.load(f)

venues = venue_list['venues']
print(f"總場地數: {len(venues)} 個\n")

all_venues_with_price = []

for i, venue in enumerate(venues, 1):
    print(f"{'=' * 100}")
    print(f"場地 {i}/{len(venues)}: {venue['name']}")
    print(f"{'=' * 100}")

    if not venue['full_url']:
        print("⚠️  無詳情頁 URL\n")
        continue

    try:
        response = requests.get(venue['full_url'], timeout=15, verify=False)
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}\n")
            time.sleep(2)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 專門尋找 card-text-info 的 div
        info_divs = soup.find_all('div', class_='card-text-info')

        if not info_divs:
            print("⚠️  未找到 card-text-info 區塊\n")
            time.sleep(2)
            continue

        # 合併所有 info div 的文字
        all_info_text = ' '.join([div.get_text() for div in info_divs])

        # 尋找價格模式
        prices_found = []

        # 模式1: $數字/日 或 $數字/時
        pattern1 = r'\$\s*(\d{1,3}(?:,\d{3})*)\s*/(?:日|時|小時)'
        matches1 = re.findall(pattern1, all_info_text)
        for m in matches1:
            try:
                price = int(m.replace(',', ''))
                if 1000 <= price <= 500000:
                    prices_found.append(price)
            except:
                pass

        # 模式2: 數字元/日 或 數字元/時
        pattern2 = r'(\d{1,3}(?:,\d{3})*)\s*元\s*/(?:日|時|小時)'
        matches2 = re.findall(pattern2, all_info_text)
        for m in matches2:
            try:
                price = int(m.replace(',', ''))
                if 1000 <= price <= 500000:
                    prices_found.append(price)
            except:
                pass

        # 模式3: $數字（無單位）
        pattern3 = r'\$\s*(\d{1,3}(?:,\d{3})*)\s*(?:/)?(?:[^0-9\s]|$)'
        matches3 = re.findall(pattern3, all_info_text)
        for m in matches3:
            try:
                price = int(m.replace(',', ''))
                if 1000 <= price <= 500000:
                    prices_found.append(price)
            except:
                pass

        # 去重並排序
        if prices_found:
            prices_found = sorted(set(prices_found))
            print(f"✅ 找到價格: {len(prices_found)} 個")
            for p in prices_found:
                print(f"   ${p:,}")

            # 通常最低價是基準價
            main_price = prices_found[0]
            print(f"   主要價格: ${main_price:,}")

            venue_with_price = {
                'name': venue['name'],
                'url': venue['full_url'],
                'price': main_price,
                'all_prices': prices_found,
                'price_found': True
            }
        else:
            print(f"⚠️  未找到價格")
            # 調試：顯示 card-text-info 的內容片段
            if len(all_info_text) > 0:
                lines = all_info_text.split('.')
                for line in lines[:3]:
                    if len(line.strip()) > 10:
                        print(f"   片段: {line.strip()[:100]}...")

            venue_with_price = {
                'name': venue['name'],
                'url': venue['full_url'],
                'price': None,
                'all_prices': [],
                'price_found': False
            }

        all_venues_with_price.append(venue_with_price)
        time.sleep(2)

    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        time.sleep(2)
        continue

# 儲存結果
result = {
    'venue': '華山1914文化創意產業園區',
    'venue_id': 1125,
    'total_venues': len(all_venues_with_price),
    'venues_with_price': [v for v in all_venues_with_price if v['price_found']],
    'venues_without_price': [v for v in all_venues_with_price if not v['price_found']],
    'price_coverage': f"{len([v for v in all_venues_with_price if v['price_found']])}/{len(all_venues_with_price)}",
    'timestamp': datetime.now().isoformat()
}

result_file = f'huashan1914_prices_deep_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 價格資料已儲存: {result_file}")

# 統計
print("\n" + "=" * 100)
print("統計資訊")
print("=" * 100)

with_price = [v for v in all_venues_with_price if v['price_found']]
without_price = [v for v in all_venues_with_price if not v['price_found']]

print(f"總場地數: {len(all_venues_with_price)}")
print(f"有價格: {len(with_price)} 個 ({len(with_price)/len(all_venues_with_price)*100:.1f}%)")
print(f"無價格: {len(without_price)} 個")

if with_price:
    prices = [v['price'] for v in with_price]
    print(f"\n價格範圍:")
    print(f"  最低: ${min(prices):,}")
    print(f"  最高: ${max(prices):,}")
    print(f"  平均: ${sum(prices)//len(prices):,}")

    print(f"\n所有場地價格:")
    for v in all_venues_with_price:
        if v['price_found']:
            print(f"  ✅ {v['name']}: ${v['price']:,}")
        else:
            print(f"  ❌ {v['name']}: 無價格")

print("\n" + "=" * 100)
print("✅ 華山1914 深度價格爬取完成")
print("=" * 100)
