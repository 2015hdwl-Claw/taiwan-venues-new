#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青青婚宴會館 - 謹慎爬取（注意 Cloudflare）
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
print("青青婚宴會館 - 謹慎爬取（注意 Cloudflare）")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.77-67.com/"

# 關鍵頁面
pages = [
    {'name': '空間介紹', 'url': 'https://www.77-67.com/#'},
    {'name': '南港青青星光', 'url': 'https://www.77-67.com/77-starlight'},
    {'name': '婚宴專案台北', 'url': 'https://www.77-67.com/category/wedding-packages/wedding-tp-77'},
]

all_venues = []

for page_info in pages:
    print(f"\n{'=' * 100}")
    print(f"訪問: {page_info['name']}")
    print(f"URL: {page_info['url']}")
    print("=" * 100)

    try:
        # 添加 headers 模擬真實瀏覽
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        response = requests.get(page_info['url'], timeout=30, verify=False, headers=headers)
        print(f"HTTP 狀態: {response.status_code}")

        if response.status_code != 200:
            print("❌ 頁面訪問失敗")
            continue

        # 檢查是否被 Cloudflare 攔截
        if 'cloudflare' in response.text.lower() or 'challenge' in response.text.lower():
            print("⚠️ 可能被 Cloudflare 攔截")
            print("嘗試等待後重新請求...")
            time.sleep(5)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 儲存頁面
        page_file = f"chingchiao_{page_info['name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"✅ 頁面已儲存: {page_file}\n")

        # 尋找場地資訊
        print("尋找場地資訊...")

        # 方法 1: 尋找場地連結
        print("\n尋找場地連結...")
        venue_links = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)

            # 尋找可能的場地連結
            if len(text) > 2 and len(text) < 100:
                if any(kw in text for kw in ['廳', '宴會', '婚宴', '會議', '空間', '館']):
                    full_url = urljoin(base_url, href)
                    venue_links.append({
                        'name': text,
                        'url': full_url
                    })

        print(f"找到 {len(venue_links)} 個場地連結:")
        for link in venue_links[:10]:
            print(f"  - {link['name']}")
            print(f"    {link['url']}")

        # 方法 2: 尋找標題
        print("\n尋找場地標題...")
        titles = []

        for tag in ['h1', 'h2', 'h3']:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if any(kw in text for kw in ['廳', '宴會', '婚宴', '會議']):
                    titles.append(text)

        if titles:
            print(f"找到 {len(titles)} 個標題:")
            for title in titles[:10]:
                print(f"  - {title}")

        # 方法 3: 尋找圖片（場地通常有圖片）
        print("\n尋找場地圖片...")
        images = []

        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')

            if alt and len(alt) > 2:
                if any(kw in alt for kw in ['廳', '宴會', '婚宴', '會議']):
                    full_src = urljoin(base_url, src)
                    images.append({
                        'alt': alt,
                        'src': full_src
                    })

        if images:
            print(f"找到 {len(images)} 個場地圖片:")
            for img in images[:5]:
                print(f"  - {img['alt']}")
                print(f"    {img['src']}")

        # 解析頁面文字
        page_text = soup.get_text()

        # 尋找容量
        capacity_pattern = r'(\d+)\s*[人名桌]'
        capacities = re.findall(capacity_pattern, page_text)
        if capacities:
            print(f"\n找到容量資訊: {len(capacities)} 處")
            unique_caps = list(set(capacities))
            print(f"容量: {unique_caps[:10]}")

        # 尋找坪數
        area_pattern = r'(\d+\.?\d*)\s*[坪平米]'
        areas = re.findall(area_pattern, page_text)
        if areas:
            print(f"找到面積資訊: {len(areas)} 處")
            print(f"面積: {areas[:10]}")

        # 尋找價格
        price_pattern = r'(\d+[,.]?\d*)\s*元'
        prices = re.findall(price_pattern, page_text)
        if prices:
            print(f"找到價格資訊: {len(prices)} 處")
            print(f"價格: {prices[:10]}")

        # 延遲以避免觸發 Cloudflare
        print("\n延遲 3 秒...")
        time.sleep(3)

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 100}")
print("✅ 青青婚宴會館爬取完成")
print("=" * 100)
print(f"\n⚠️ 注意: Cloudflare 保護可能會影響爬取結果")
print(f"建議: 檢查儲存的 HTML 檔案，手動提取場地資料")
