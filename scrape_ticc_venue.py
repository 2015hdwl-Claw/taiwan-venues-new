#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC - 深度爬取場地資料
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime
from urllib.parse import urljoin
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - 深度爬取場地資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.ticc.com.tw/"

# TICC 關鍵頁面
venue_pages = [
    {
        'name': '場地導覽',
        'url': 'https://www.ticc.com.tw/np?ctNode=320&mp=1'
    },
    {
        'name': '場地介紹',
        'url': 'https://www.ticc.com.tw/sp?xdUrl=/wSite/ap/lp_VenueIntroduction.jsp&ctNode=321&CtUnit=98&BaseDSD=7&mp=1'
    },
    {
        'name': '場地查詢',
        'url': 'https://www.ticc.com.tw/sp?xdUrl=/wSite/ap/lp_VenueSearch.jsp&ctNode=322&CtUnit=99&BaseDSD=7&mp=1'
    },
    {
        'name': '詳情與租借規範',
        'url': 'https://www.ticc.com.tw/lp?ctNode=336&CtUnit=110&BaseDSD=7&mp=1'
    }
]

all_rooms = []

for page_info in venue_pages:
    print(f"\n{'=' * 100}")
    print(f"訪問: {page_info['name']}")
    print(f"URL: {page_info['url']}")
    print("=" * 100)

    try:
        response = requests.get(page_info['url'], timeout=15, verify=False)
        print(f"HTTP 狀態: {response.status_code}")

        if response.status_code != 200:
            print("❌ 頁面訪問失敗")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找會議室/場地資訊
        # 尋找所有可能的場地名稱
        venue_keywords = ['會議室', '宴會廳', '會議廳', '國際', '廳']

        # 方法 1: 尋找所有標題
        print("\n尋找場地標題...")
        titles = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if any(kw in text for kw in venue_keywords):
                    titles.append({
                        'tag': tag,
                        'text': text
                    })

        if titles:
            print(f"找到 {len(titles)} 個標題:")
            for title in titles[:10]:
                print(f"  {title['tag']}: {title['text']}")

        # 方法 2: 尋找連結
        print("\n尋找場地連結...")
        venue_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if any(kw in text for kw in venue_keywords) and len(text) > 2:
                venue_links.append({
                    'text': text,
                    'href': urljoin(base_url, href)
                })

        if venue_links:
            print(f"找到 {len(venue_links)} 個場地連結:")
            for link in venue_links[:10]:
                print(f"  - {link['text']}")
                print(f"    {link['href']}")

        # 方法 3: 尋找表格或列表
        print("\n尋找表格和列表...")
        tables = soup.find_all('table')
        lists = soup.find_all(['ul', 'ol'])

        print(f"表格數量: {len(tables)}")
        print(f"列表數量: {len(lists)}")

        # 提取頁面主要內容
        main_content = soup.get_text()
        print(f"\n頁面文字量: {len(main_content)} 字元")

        # 尋找容量資訊
        capacity_pattern = r'(\d+)\s*[人名]'
        capacities = re.findall(capacity_pattern, main_content)
        if capacities:
            print(f"找到容量資訊: {len(capacities)} 處")
            print(f"範圍: {min(int(c) for c in capacities)} - {max(int(c) for c in capacities)} 人")

        # 尋找面積資訊
        area_pattern = r'(\d+\.?\d*)\s*[坪平米㎡㎡]'
        areas = re.findall(area_pattern, main_content)
        if areas:
            print(f"找到面積資訊: {len(areas)} 處")
            print(f"範圍: {min(float(a) for a in areas)} - {max(float(a) for a in areas)}")

        # 尋找樓層資訊
        floor_pattern = r'(\d+[F樓層])'
        floors = re.findall(floor_pattern, main_content)
        if floors:
            print(f"找到樓層資訊: {len(set(floors))} 種")
            print(f"樓層: {', '.join(set(floors[:10]))}")

        # 儲存頁面內容供後續分析
        page_file = f"ticc_{page_info['name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"\n✅ 頁面已儲存: {page_file}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

# 嘗試從主頁尋找所有可能的場地連結
print(f"\n{'=' * 100}")
print("從主頁尋找所有場地相關連結")
print("=" * 100)

try:
    response = requests.get(base_url, timeout=15, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 尋找所有連結
    all_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        href_lower = href.lower()

        # 尋找包含場地/會議關鍵字的連結
        if any(kw in text or kw in href_lower for kw in
               ['venue', 'room', 'meeting', 'banquet', '場地', '會議', '宴會', '廳']):
            if not href_lower.startswith('mailto:') and not href_lower.startswith('tel:'):
                full_url = urljoin(base_url, href)
                all_links.append({
                    'text': text[:100],
                    'href': full_url
                })

    print(f"找到 {len(all_links)} 個場地相關連結:")
    for link in all_links[:20]:
        print(f"  - {link['text']}")
        print(f"    {link['href']}")

    # 儲存所有連結
    result = {
        'venue': 'TICC',
        'venue_id': 1448,
        'base_url': base_url,
        'total_links': len(all_links),
        'links': all_links,
        'timestamp': datetime.now().isoformat()
    }

    result_file = f'ticc_links_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 連結已儲存: {result_file}")

except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'=' * 100}")
print("✅ TICC 深度爬取完成")
print("=" * 100)
print(f"\n下一步建議:")
print("1. 檢查儲存的 HTML 檔案")
print("2. 分析連結列表，訪問關鍵頁面")
print("3. 如果有 PDF，下載並解析")
print("4. 手動提取會議室資料")
