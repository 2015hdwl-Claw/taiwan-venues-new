#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北喜瑞飯店 - 檢查 about 和 contact 頁面
"""

import requests
from bs4 import BeautifulSoup
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北喜瑞飯店 - 檢查 About 和 Contact 頁面")
print("=" * 100)

base_url = 'https://www.ambiencehotel.com.tw'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

pages_to_check = [
    ('About', '/tw/about-t/'),
    ('Contact', '/tw/contact-t/'),
    ('Rooms', '/tw/rooms-t/'),
    ('Location', '/tw/location-t/'),
    ('News', '/tw/news-t/'),
]

for page_name, path in pages_to_check:
    url = base_url + path
    print(f"\n{'=' * 100}")
    print(f"頁面: {page_name}")
    print(f"URL: {url}")
    print("=" * 100)

    try:
        r = requests.get(url, timeout=20, verify=False, headers=headers)
        print(f"狀態: {r.status_code}")

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text()

            # 顯示標題
            title = soup.find('title')
            if title:
                print(f"標題: {title.get_text(strip=True)}")

            # 檢查是否包含會議/宴會相關內容
            keywords = ['會議', '宴會', '會議室', '婚宴', '活動', '會議設備',
                       'meeting', 'banquet', 'conference', 'event']

            found_keywords = []
            for kw in keywords:
                if kw in page_text:
                    found_keywords.append(kw)

            if found_keywords:
                print(f"\n✓ 發現關鍵字: {', '.join(found_keywords)}")

                # 提取相關內容
                lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 200]

                # 找出包含關鍵字的行
                relevant_lines = []
                for line in lines:
                    if any(kw in line for kw in found_keywords):
                        relevant_lines.append(line)

                if relevant_lines:
                    print(f"\n相關內容:")
                    for line in relevant_lines[:10]:
                        print(f"  {line[:100]}")

                # 提取容量
                capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
                if capacities:
                    print(f"\n容量數據: {capacities}")

                # 提取面積
                areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
                if areas:
                    print(f"面積數據: {areas[:10]}")

                # 提取會議室名稱
                room_patterns = [
                    r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])',
                    r'(宴會廳|會議室|會議廳)'
                ]

                for pattern in room_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        print(f"會議室: {matches[:10]}")
                        break

            else:
                print(f"無會議/宴會相關內容")

            # 檢查頁面內的所有連結
            print(f"\n頁面連結:")
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)

                if text and len(text) < 80 and 'ambiencehotel' in href:
                    print(f"  {text[:50]:50s} -> {href}")

    except Exception as e:
        print(f"錯誤: {e}")
