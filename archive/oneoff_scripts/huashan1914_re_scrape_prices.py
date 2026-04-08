#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 重新爬取所有 24 個場地的價格資料（修復版）
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
print("華山1914 - 重新爬取價格資料（修復版）")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取場地列表
with open('huashan1914_svg_venues_20260326_205431.json', encoding='utf-8') as f:
    venue_list = json.load(f)

venues = venue_list['venues']
print(f"總場地數: {len(venues)} 個\n")

# 價格模式（修復版，支援 $88,000元/時 格式）
price_patterns = [
    r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*元',  # $88,000元
    r'(\d{2,6}(?:,\d{3})*)\s*元[/時天]',  # 88000元/時
    r'租金[：:]\s*\$?(\d{1,3}(?:,\d{3})*)',  # 租金: $88000
    r'場地費[：:]\s*\$?(\d{1,3}(?:,\d{3})*)',  # 場地費: $88000
    r'NT\$?\s*(\d{1,3}(?:,\d{3})*)',  # NT$88,000
]

all_venues_with_price = []

for i, venue in enumerate(venues, 1):
    print(f"{'=' * 100}")
    print(f"場地 {i}/{len(venues)}: {venue['name']}")
    print(f"URL: {venue['full_url']}")
    print(f"{'=' * 100}")

    if not venue['full_url']:
        print("⚠️  無詳情頁 URL，跳過\n")
        continue

    try:
        response = requests.get(venue['full_url'], timeout=15, verify=False)
        print(f"HTTP 狀態: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ 頁面訪問失敗\n")
            time.sleep(2)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 嘗試所有價格模式
        price_found = None
        price_source = None

        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                # 清理並轉換為數字
                for match in matches:
                    try:
                        # 移除逗號
                        clean_price = match.replace(',', '')
                        price_int = int(float(clean_price))

                        # 合理價格範圍檢查：1,000 - 500,000
                        if 1000 <= price_int <= 500000:
                            price_found = price_int
                            price_source = f"匹配模式: {pattern[:30]}..."
                            break
                    except:
                        continue

                if price_found:
                    break

        if price_found:
            print(f"✅ 價格: ${price_found:,}")
            if price_source:
                print(f"   來源: {price_source}")
        else:
            print(f"⚠️  未找到價格資料")
            # 調試：顯示包含"元"的行
            lines_with_yuan = [line.strip() for line in page_text.split('\n') if '元' in line and len(line.strip()) < 100]
            if lines_with_yuan:
                print(f"   發現包含'元'的行: {lines_with_yuan[0][:80]}...")

        venue_with_price = {
            'name': venue['name'],
            'url': venue['full_url'],
            'price': price_found,
            'price_found': bool(price_found)
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

result_file = f'huashan1914_prices_fixed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
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

    print(f"\n有價格的場地:")
    for v in with_price:
        print(f"  - {v['name']}: ${v['price']:,}")

if without_price:
    print(f"\n無價格的場地:")
    for v in without_price:
        print(f"  - {v['name']}")

print("\n" + "=" * 100)
print("✅ 華山1914 價格重新爬取完成")
print("=" * 100)
