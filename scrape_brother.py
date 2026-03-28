#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北兄弟大飯店 - 深度爬取會議/婚宴專案
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from datetime import datetime
from urllib.parse import urljoin
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北兄弟大飯店 - 深度爬取會議/婚宴專案")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.brotherhotel.com.tw/"

# 關鍵頁面
pages = [
    {'name': '會議專案', 'url': 'https://www.brotherhotel.com.tw/?cat=76'},
    {'name': '婚宴專案', 'url': 'https://www.brotherhotel.com.tw/?cat=75'},
]

all_rooms = []

for page_info in pages:
    print(f"\n{'=' * 100}")
    print(f"訪問: {page_info['name']}")
    print(f"URL: {page_info['url']}")
    print("=" * 100)

    try:
        response = requests.get(page_info['url'], timeout=30, verify=False)
        print(f"HTTP 狀態: {response.status_code}")

        if response.status_code != 200:
            print("❌ 頁面訪問失敗")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 儲存頁面
        page_file = f"brother_{page_info['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"✅ 頁面已儲存: {page_file}\n")

        # 尋找會議廳/宴會廳資訊
        print("尋找會議廳/宴會廳...")

        # 常見的宴會廳名稱
        hall_keywords = ['廳', '會議室', '宴會廳']

        # 方法 1: 尋找所有連結
        hall_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)

            if any(kw in text for kw in hall_keywords) and len(text) > 1:
                full_url = urljoin(base_url, href)
                hall_links.append({
                    'name': text,
                    'url': full_url
                })

        print(f"找到 {len(hall_links)} 個廳連結:")
        for link in hall_links[:10]:
            print(f"  - {link['name']}")
            print(f"    {link['url']}")

        # 方法 2: 尋找標題
        print("\n尋找標題...")
        titles = []
        for tag in ['h1', 'h2', 'h3']:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if any(kw in text for kw in hall_keywords):
                    titles.append(text)

        if titles:
            print(f"找到 {len(titles)} 個標題:")
            for title in titles[:10]:
                print(f"  - {title}")

        # 方法 3: 尋找文章/貼文
        print("\n尋找貼文...")
        articles = []
        for article in soup.find_all('article'):
            text = article.get_text(strip=True)
            if any(kw in text for kw in hall_keywords):
                articles.append(text[:200])

        if articles:
            print(f"找到 {len(articles)} 篇相關貼文")
            for article in articles[:5]:
                print(f"  - {article}...")

        # 解析頁面文字
        page_text = soup.get_text()

        # 尋找容量
        capacity_pattern = r'(\d+)\s*[人名桌]'
        capacities = re.findall(capacity_pattern, page_text)
        if capacities:
            print(f"\n找到容量資訊: {len(capacities)} 處")

        # 尋找坪數
        area_pattern = r'(\d+\.?\d*)\s*[坪平米]'
        areas = re.findall(area_pattern, page_text)
        if areas:
            print(f"找到面積資訊: {len(areas)} 處")

        # 尋找價格
        price_pattern = r'(\d+[,.]?\d*)\s*元'
        prices = re.findall(price_pattern, page_text)
        if prices:
            print(f"找到價格資訊: {len(prices)} 處")

        # 深度爬取各廳的詳細頁面
        if hall_links:
            print(f"\n深度爬取前 3 個廳...")
            for i, link in enumerate(hall_links[:3], 1):
                print(f"\n廳 {i}: {link['name']}")
                print(f"URL: {link['url']}")

                try:
                    time.sleep(1)
                    response = requests.get(link['url'], timeout=15, verify=False)
                    print(f"  HTTP 狀態: {response.status_code}")

                    if response.status_code == 200:
                        hall_soup = BeautifulSoup(response.text, 'html.parser')
                        hall_text = hall_soup.get_text()

                        # 尋找詳細資訊
                        caps = re.findall(capacity_pattern, hall_text)
                        if caps:
                            print(f"  容量: {caps[:5]}")

                        ars = re.findall(area_pattern, hall_text)
                        if ars:
                            print(f"  面積: {ars[:5]}")

                        prs = re.findall(price_pattern, hall_text)
                        if prs:
                            print(f"  價格: {prs[:5]}")

                        # 儲存廳頁面
                        hall_file = f"brother_{link['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                        with open(hall_file, 'w', encoding='utf-8') as f:
                            f.write(str(hall_soup.prettify()))
                        print(f"  ✅ 頁面已儲存: {hall_file}")

                except Exception as e:
                    print(f"  ❌ 錯誤: {e}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 100}")
print("✅ 台北兄弟大飯店爬取完成")
print("=" * 100)
