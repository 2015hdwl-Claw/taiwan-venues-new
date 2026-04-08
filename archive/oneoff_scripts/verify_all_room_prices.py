#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐一驗證竹科與新烏日所有會議室的價格
實際爬取每個頁面，提取正確的平日/假日價格
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("價格驗證 - 實際爬取每個會議室頁面")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 竹科所有會議室 URL（包括更多會議室）
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

# 新烏日所有會議室 URL
wuri_rooms = [
    {'name': '瓦特廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-301.php'},
    {'name': '巴本廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-303.php'},
    {'name': '富蘭克林廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-401.php'},
    {'name': '史蒂文生廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-402.php'},
]

def extract_price_from_page(url):
    """從頁面提取價格資訊"""
    try:
        response = requests.get(url, timeout=15, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        prices = {}

        # 尋找平日價格
        weekday_patterns = [
            r'平日.*?每時段.*?新台幣.*?(\d{1,6})\s*元',
            r'每時段.*?新台幣.*?(\d{1,6})\s*元',
            r'平日.*?(\d{1,6})\s*元.*?時段',
        ]

        for pattern in weekday_patterns:
            match = re.search(pattern, page_text)
            if match:
                prices['weekday'] = int(match.group(1))
                break

        # 尋找假日價格
        holiday_patterns = [
            r'假日.*?每時段.*?新台幣.*?(\d{1,6})\s*元',
            r'例假日.*?(\d{1,6})\s*元.*?時段',
        ]

        for pattern in holiday_patterns:
            match = re.search(pattern, page_text)
            if match:
                prices['holiday'] = int(match.group(1))
                break

        # 如果沒有找到假日價格，嘗試找第二個價格
        if 'holiday' not in prices and 'weekday' in prices:
            all_prices = re.findall(r'新台幣.*?(\d{1,6})\s*元', page_text)
            if len(all_prices) > 1:
                prices['holiday'] = int(all_prices[1])

        return prices

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return None

# 驗證竹科
print("=== 集思竹科會議中心 ===\n")
hcph_results = {}

for room in hcph_rooms:
    print(f"檢查: {room['name']}")
    print(f"URL: {room['url']}")

    prices = extract_price_from_page(room['url'])

    if prices:
        hcph_results[room['name']] = prices
        print(f"  ✅ 平日: {prices.get('weekday', 'N/A'):,} 元")
        print(f"  ✅ 假日: {prices.get('holiday', 'N/A'):,} 元")
    else:
        print(f"  ⚠️  無法提取價格")

    print()

# 驗證新烏日
print("\n=== 集思台中新烏日會議中心 ===\n")
wuri_results = {}

for room in wuri_rooms:
    print(f"檢查: {room['name']}")
    print(f"URL: {room['url']}")

    prices = extract_price_from_page(room['url'])

    if prices:
        wuri_results[room['name']] = prices
        print(f"  ✅ 平日: {prices.get('weekday', 'N/A'):,} 元")
        print(f"  ✅ 假日: {prices.get('holiday', 'N/A'):,} 元")
    else:
        print(f"  ⚠️  無法提取價格")

    print()

# 讀取 venues.json 比對
print("\n" + "=" * 100)
print("與 venues.json 比對")
print("=" * 100)

with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

hcph_venue = next((v for v in venues if v['id'] == 1496), None)
wuri_venue = next((v for v in venues if v['id'] == 1498), None)

def compare_prices(venue, correct_prices, venue_name):
    """比對並顯示差異"""
    print(f"\n{venue_name}:")

    issues = []

    for room in venue.get('rooms', []):
        room_name = room.get('name')
        current_price = room.get('price', {})

        if room_name in correct_prices:
            correct = correct_prices[room_name]
            current_weekday = current_price.get('weekday')
            current_holiday = current_price.get('holiday')

            errors = []
            if current_weekday != correct.get('weekday'):
                errors.append(f"平日 {current_weekday} → {correct.get('weekday')}")
            if current_holiday != correct.get('holiday'):
                errors.append(f"假日 {current_holiday} → {correct.get('holiday')}")

            if errors:
                issues.append({
                    'room': room_name,
                    'errors': errors,
                    'correct': correct
                })
                print(f"  ❌ {room_name}: {', '.join(errors)}")
            else:
                print(f"  ✅ {room_name}: 正確")

    return issues

# 比對竹科
hcph_issues = compare_prices(hcph_venue, hcph_results, "集思竹科會議中心")

# 比對新烏日
wuri_issues = compare_prices(wuri_venue, wuri_results, "集思台中新烏日會議中心")

# 總結
print("\n" + "=" * 100)
print("總結")
print("=" * 100)

total_issues = len(hcph_issues) + len(wuri_issues)

if total_issues == 0:
    print("✅ 所有價格都正確！")
else:
    print(f"⚠️  發現 {total_issues} 個價格錯誤")
    print("\n建議修正:")
    for issue in hcph_issues + wuri_issues:
        print(f"  {issue['room']}: {', '.join(issue['errors'])}")

# 儲存驗證結果
verification_result = {
    "timestamp": datetime.now().isoformat(),
    "hcph": {
        "venue": "集思竹科會議中心",
        "correct_prices": hcph_results,
        "issues": len(hcph_issues)
    },
    "wuri": {
        "venue": "集思台中新烏日會議中心",
        "correct_prices": wuri_results,
        "issues": len(wuri_issues)
    },
    "total_issues": total_issues
}

with open('price_verification_results.json', 'w', encoding='utf-8') as f:
    json.dump(verification_result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 驗證結果已儲存: price_verification_results.json")
