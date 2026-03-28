#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正確提取價格 - 根據實際頁面格式
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("正確提取價格 - 實際爬取每個會議室頁面")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 竹科所有會議室
hcph_rooms = [
    {'name': '巴哈廳', 'url': 'https://www.meeting.com.tw/hsp/bach.php'},
    {'name': '羅西尼廳', 'url': 'https://www.meeting.com.tw/hsp/rossini.php'},
    {'name': '蕭邦廳', 'url': 'https://www.meeting.com.tw/hsp/chopin.php'},
    {'name': '莫札特廳', 'url': 'https://www.meeting.com.tw/hsp/mozart.php'},
    {'name': '鄧肯廳', 'url': 'https://www.meeting.com.tw/hsp/duncan.php'},
    {'name': '達爾文廳', 'url': 'https://www.meeting.com.tw/hsp/darwin.php'},
    {'name': '牛頓廳', 'url': 'https://www.meeting.com.tw/hsp/newton.php'},
    {'name': '愛因斯坦廳', 'url': 'https://www.meeting.com.tw/hsp/einstein.php'},
    {'name': '愛迪生廳', 'url': 'https://www.meeting.com.tw/hsp/edison.php'},
    {'name': '莎士比亞廳', 'url': 'https://www.meeting.com.tw/hsp/shakespeare.php'},
]

# 新烏日所有會議室
wuri_rooms = [
    {'name': '瓦特廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-301.php'},
    {'name': '巴本廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-303.php'},
    {'name': '富蘭克林廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-401.php'},
    {'name': '史蒂文生廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-402.php'},
]

def extract_price_correctly(url):
    """正確提取價格 - 根據實際頁面格式 (平日)每時段NT$7,000元"""
    try:
        response = requests.get(url, timeout=15, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        prices = {}

        # 新的 pattern：匹配 (平日)每時段NT$7,000元 或 (例假日)每時段NT$8,000元
        weekday_pattern = r'\(平日\).*?每時段.*?NT\$\s*([\d,]+)'
        holiday_pattern = r'\(例假日\).*?每時段.*?NT\$\s*([\d,]+)'

        weekday_match = re.search(weekday_pattern, page_text)
        if weekday_match:
            price_str = weekday_match.group(1).replace(',', '')
            prices['weekday'] = int(price_str)

        holiday_match = re.search(holiday_pattern, page_text)
        if holiday_match:
            price_str = holiday_match.group(1).replace(',', '')
            prices['holiday'] = int(price_str)

        # 如果沒找到例假日，嘗試其他格式
        if 'holiday' not in prices:
            alt_patterns = [
                r'\(假日\).*?每時段.*?NT\$\s*([\d,]+)',
                r'\(週休\).*?每時段.*?NT\$\s*([\d,]+)',
            ]
            for pattern in alt_patterns:
                match = re.search(pattern, page_text)
                if match:
                    price_str = match.group(1).replace(',', '')
                    prices['holiday'] = int(price_str)
                    break

        return prices

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return None

# 測試一個房間
print("=== 測試：巴哈廳 ===\n")
test_price = extract_price_correctly('https://www.meeting.com.tw/hsp/bach.php')
print(f"提取結果: {test_price}")
print()

# 如果測試成功，繼續全部
if test_price and test_price.get('weekday'):
    print("測試成功！開始提取所有價格...\n")

    # 提取竹科
    print("=== 集思竹科會議中心 ===\n")
    hcph_prices = {}

    for room in hcph_rooms:
        print(f"{room['name']}:")
        prices = extract_price_correctly(room['url'])

        if prices and (prices.get('weekday') or prices.get('holiday')):
            hcph_prices[room['name']] = prices
            print(f"  ✅ 平日: {prices.get('weekday', 'N/A'):,} 元")
            print(f"  ✅ 假日: {prices.get('holiday', 'N/A'):,} 元")
        else:
            print(f"  ⚠️  無法提取價格")

        print()

    # 提取新烏日
    print("\n=== 集思台中新烏日會議中心 ===\n")
    wuri_prices = {}

    for room in wuri_rooms:
        print(f"{room['name']}:")
        prices = extract_price_correctly(room['url'])

        if prices and (prices.get('weekday') or prices.get('holiday')):
            wuri_prices[room['name']] = prices
            print(f"  ✅ 平日: {prices.get('weekday', 'N/A'):,} 元")
            print(f"  ✅ 假日: {prices.get('holiday', 'N/A'):,} 元")
        else:
            print(f"  ⚠️  無法提取價格")

        print()

    # 儲存結果
    result = {
        "timestamp": datetime.now().isoformat(),
        "hcph": hcph_prices,
        "wuri": wuri_prices
    }

    with open('correct_prices_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ 價格已儲存到 correct_prices_extracted.json")
else:
    print("❌ 測試失敗，需要調整提取邏輯")
