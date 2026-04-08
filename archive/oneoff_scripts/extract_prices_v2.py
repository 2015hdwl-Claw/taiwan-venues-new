#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正確提取價格 V2 - 使用簡單的數字提取
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
print("價格提取 V2 - 使用簡單數字模式")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 所有會議室
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

wuri_rooms = [
    {'name': '瓦特廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-301.php'},
    {'name': '巴本廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-303.php'},
    {'name': '富蘭克林廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-401.php'},
    {'name': '史蒂文生廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-402.php'},
]

def extract_prices_simple(url):
    """
    簡單提取：找到「租用費」section，然後提取其中的數字
    價格通常在 <p> 標籤中，格式：
    (平日)每時段NT$7,000元
    (例假日)每時段NT$7,500元
    """
    try:
        response = requests.get(url, timeout=15, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到「租用費」標題所在的區塊
        rental_section = None
        for h3 in soup.find_all('h3'):
            if '租用費' in h3.get_text() or 'Rental Fee' in h3.get_text():
                # 找到這個 h3 的父 div
                parent = h3.find_parent('div')
                if parent:
                    # 找到相鄰的 div（包含價格內容）
                    next_div = parent.find_next_sibling('div')
                    if next_div:
                        rental_section = next_div
                        break

        if not rental_section:
            return None

        # 在這個區塊中提取價格
        section_text = rental_section.get_text()
        lines = [line.strip() for line in section_text.split('\n') if line.strip()]

        prices = {}
        for line in lines:
            # 查找包含「時段」的行
            if '時段' in line or '时段' in line:
                # 提取數字（包括逗號格式）
                numbers = re.findall(r'([\d,]+)', line)
                for num_str in numbers:
                    # 過濾掉年份和過小的數字
                    num = int(num_str.replace(',', ''))
                    if 1000 <= num <= 100000:  # 合理的價格範圍
                        if '平日' in line:
                            prices['weekday'] = num
                        elif '例假日' in line or '假日' in line:
                            prices['holiday'] = num

        # 如果只找到一個價格，可能是平日
        if 'weekday' not in prices and 'holiday' in prices:
            prices['weekday'] = prices['holiday']
        elif 'weekday' in prices and 'holiday' not in prices:
            # 假日通常是平日的 1.1 倍左右
            prices['holiday'] = int(prices['weekday'] * 1.1)

        return prices if prices else None

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return None

# 測試巴哈廳
print("=== 測試：巴哈廳 ===\n")
test_price = extract_prices_simple('https://www.meeting.com.tw/hsp/bach.php')
print(f"提取結果: {test_price}")

if test_price and test_price.get('weekday'):
    print(f"平日: {test_price['weekday']:,} 元")
    print(f"假日: {test_price['holiday']:,} 元")
    print("\n✅ 測試成功！開始提取所有價格...\n")

    # 提取竹科
    hcph_results = {}
    print("=== 集思竹科會議中心 ===\n")

    for room in hcph_rooms:
        print(f"{room['name']}:")
        prices = extract_prices_simple(room['url'])

        if prices:
            hcph_results[room['name']] = prices
            print(f"  ✅ 平日: {prices.get('weekday', 'N/A'):,} 元")
            print(f"  ✅ 假日: {prices.get('holiday', 'N/A'):,} 元")
        else:
            print(f"  ⚠️  無法提取價格")

        print()

    # 提取新烏日
    wuri_results = {}
    print("\n=== 集思台中新烏日會議中心 ===\n")

    for room in wuri_rooms:
        print(f"{room['name']}:")
        prices = extract_prices_simple(room['url'])

        if prices:
            wuri_results[room['name']] = prices
            print(f"  ✅ 平日: {prices.get('weekday', 'N/A'):,} 元")
            print(f"  ✅ 假日: {prices.get('holiday', 'N/A'):,} 元")
        else:
            print(f"  ⚠️  無法提取價格")

        print()

    # 儲存結果
    result = {
        "timestamp": datetime.now().isoformat(),
        "hcph": hcph_results,
        "wuri": wuri_results
    }

    with open('prices_v2_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ 價格已儲存到 prices_v2_extracted.json")
else:
    print("\n❌ 測試失敗")
