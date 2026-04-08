#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華山1914 - 階段3：深度爬取場地資料
基於階段2找到的 2 個有場地資訊的連結
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import re
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("華山1914 - 階段3：深度爬取場地資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 階段2找到的 2 個有場地資訊的連結
venue_links = [
    {
        "name": "申請辦法",
        "url": "https://www.huashan1914.com/w/huashan1914/AppPlace"
    },
    {
        "name": "傳音樂展演空間",
        "url": "https://www.huashan1914.com/w/huashan1914/CustomShops_17072615244330041"
    }
]

all_rooms = []
all_data = {
    "venue": "華山1914",
    "venue_id": 1125,
    "pages": [],
    "total_rooms": 0
}

for i, link_info in enumerate(venue_links, 1):
    print(f"{'=' * 100}")
    print(f"頁面 {i}/{len(venue_links)}: {link_info['name']}")
    print(f"URL: {link_info['url']}")
    print(f"{'=' * 100}\n")

    try:
        response = requests.get(link_info['url'], timeout=15, verify=False)
        print(f"HTTP 狀態: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ 頁面訪問失敗")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 儲存頁面
        page_file = f"huashan1914_page{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"✅ 頁面已儲存: {page_file}\n")

        # 分析頁面
        page_text = soup.get_text()
        page_data = {
            "name": link_info['name'],
            "url": link_info['url'],
            "file": page_file,
            "rooms": []
        }

        # 尋找容量資訊
        print("尋找場地資訊...")

        # 容量模式
        capacity_patterns = [
            r'(\d+)\s*[人名]',
            r'容量[：:]?\s*(\d+)',
            r'人數[：:]?\s*(\d+)',
        ]

        capacities = []
        for pattern in capacity_patterns:
            matches = re.findall(pattern, page_text)
            capacities.extend([int(m) for m in matches])

        if capacities:
            print(f"  容量資訊: {len(capacities)} 處")
            print(f"  範圍: {min(capacities)} - {max(capacities)} 人")
            page_data['capacities'] = capacities[:10]

        # 坪數
        area_patterns = [
            r'(\d+\.?\d*)\s*[坪平米]',
            r'(\d+)\s*坪',
        ]

        areas = []
        for pattern in area_patterns:
            matches = re.findall(pattern, page_text)
            areas.extend([float(m) for m in matches])

        if areas:
            print(f"  面積資訊: {len(areas)} 處")
            print(f"  範圍: {min(areas)} - {max(areas)} 坪")
            page_data['areas'] = areas[:10]

        # 價格
        price_patterns = [
            r'(\d{2,6}[,.]?\d{0,3})\s*元',
            r'NT\$?\s*(\d+[,.]?\d*)',
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            prices.extend([m.replace(',', '') for m in matches])

        if prices:
            print(f"  價格資訊: {len(prices)} 處")
            # 轉換為數字並過濾合理範圍
            valid_prices = []
            for p in prices:
                try:
                    price = int(p)
                    if 1000 <= price <= 100000:  # 合理價格範圍
                        valid_prices.append(price)
                except:
                    pass

            if valid_prices:
                print(f"  合理價格範圍: ${min(valid_prices):,} - ${max(valid_prices):,}")
                page_data['prices'] = valid_prices[:10]

        # 尋找會議室/場地名稱
        # 華山1914 的場地命名可能比較特殊，尋找可能的模式
        room_patterns = [
            r'([^\s]{2,10}(?:展區|空間|劇場|廳|室|館))',
            r'(\d+\s*[號樓F層]\s*(?:展區|空間))',
        ]

        potential_rooms = []
        for pattern in room_patterns:
            matches = re.findall(pattern, page_text)
            potential_rooms.extend(matches)

        if potential_rooms:
            # 去重
            unique_rooms = list(set(potential_rooms))[:20]
            print(f"  可能的場地名稱: {len(unique_rooms)} 個")
            page_data['potential_rooms'] = unique_rooms

            # 嘗試建構會議室資料
            for room_name in unique_rooms:
                # 尋找該場地的相關資訊
                room_context = page_text

                room = {
                    'name': room_name,
                    'nameEn': None,
                    'floor': None,
                    'capacity': {},
                    'area': {},
                    'price': {},
                    'equipment': None,
                    'source': link_info['url']
                }

                page_data['rooms'].append(room)

        # 尋找表格
        tables = soup.find_all('table')
        if tables:
            print(f"  表格數量: {len(tables)} 個")
            page_data['tables_count'] = len(tables)

            # 分析第一個表格
            if tables[0]:
                table_text = tables[0].get_text()
                print(f"  第一個表格文字量: {len(table_text)} 字元")

                # 尋找表格中的關鍵字
                if any(kw in table_text for kw in ['場地', '空間', '租金', '費用']):
                    print(f"  ✅ 第一個表格可能包含場地資訊")
                    page_data['first_table_has_info'] = True

        # 尋找連結
        all_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if len(text) > 1 and len(text) < 100:
                all_links.append({'text': text, 'href': href})

        if all_links:
            print(f"  連結數量: {len(all_links)} 個")
            page_data['links_count'] = len(all_links)

            # 尋找可能包含更多場地資料的連結
            venue_links = [l for l in all_links if any(kw in l['text'] for kw in
                         ['展區', '空間', '場地', '劇場', '展間'])]

            if venue_links:
                print(f"  場地相關連結: {len(venue_links)} 個")
                page_data['venue_links'] = venue_links[:5]

        all_data['pages'].append(page_data)

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

# 統計
print("\n" + "=" * 100)
print("深度爬取統計")
print("=" * 100)

total_pages = len(all_data['pages'])
total_potential_rooms = sum(len(p.get('potential_rooms', [])) for p in all_data['pages'])
total_capacities = sum(len(p.get('capacities', [])) for p in all_data['pages'])
total_areas = sum(len(p.get('areas', [])) for p in all_data['pages'])
total_prices = sum(len(p.get('prices', [])) for p in all_data['pages'])

print(f"成功爬取頁面: {total_pages} 個")
print(f"可能的場地: {total_potential_rooms} 個")
print(f"容量資訊: {total_capacities} 處")
print(f"面積資訊: {total_areas} 處")
print(f"價格資訊: {total_prices} 處")

# 儲存結果
result_file = f'huashan1914_stage3_deep_scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 深度爬取結果已儲存: {result_file}")

# 下一步建議
print("\n" + "=" * 100)
print("下一步建議")
print("=" * 100)

if total_potential_rooms > 0:
    print(f"✅ 找到 {total_potential_rooms} 個可能的場地")
    print(f"建議：")
    print(f"  1. 手動檢查保存的 HTML 檔案")
    print(f"  2. 分析場地命名規則")
    print(f"  3. 提取完整 30 欄位資料")
else:
    print(f"⚠️  未找到明確的場地資訊")
    print(f"建議：")
    print(f"  1. 手動訪問華山1914官網")
    print(f"  2. 直接聯繫華山1914索取場地資料")

print("\n" + "=" * 100)
print("✅ 華山1914 階段3深度爬取完成")
print("=" * 100)
