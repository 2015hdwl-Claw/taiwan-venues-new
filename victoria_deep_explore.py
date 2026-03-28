#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
維多麗亞酒店 - 深度探索
"""

import requests
from bs4 import BeautifulSoup
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("維多麗亞酒店 - 深度探索")
print("=" * 100)

base_url = 'https://grandvictoria.com.tw/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# 1. 檢查主頁所有連結
print("\n檢查主頁所有連結:")
print("-" * 100)

try:
    r = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP Status: {r.status_code}")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')

        # 提取所有連結
        all_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if not href or href.startswith('javascript:') or href.startswith('#'):
                continue

            # 只保留內部連結
            if 'grandvictoria.com.tw' in href or href.startswith('/'):
                all_links.append({
                    'text': text,
                    'url': href
                })

        print(f"找到 {len(all_links)} 個連結\n")

        # 尋找會議/宴會相關連結
        meeting_links = []
        for link in all_links:
            text_lower = link['text'].lower()
            url_lower = link['url'].lower()

            if any(kw in text_lower or kw in url_lower for kw in ['會議', '宴會', '會議室', '婚宴', '活動', 'meeting', 'banquet', 'event', 'venue', 'capacity']):
                meeting_links.append(link)

        if meeting_links:
            print("會議/宴會相關連結:")
            for link in meeting_links[:20]:
                print(f"  {link['text'][:60]}")
                print(f"    {link['url']}")

        # 尋找PDF連結
        pdf_links = []
        for link in all_links:
            if '.pdf' in link['url'].lower():
                pdf_links.append(link)

        if pdf_links:
            print(f"\nPDF連結:")
            for link in pdf_links:
                print(f"  {link['text'][:60]}")
                print(f"    {link['url']}")

except Exception as e:
    print(f"錯誤: {e}")

# 2. 嘗試常見會議路徑
print(f"\n嘗試常見會議路徑:")
print("-" * 100)

meeting_paths = [
    '/會議室',
    '/會議室議',
    '/meeting',
  '/meetings',
  '/banquet',
  '/event',
  '/events',
  '/venue',
  '/venues',
  '/capacity',
  '/rental',
  '/facility',
  '/facilities'
]

for path in meeting_paths:
    url = base_url.rstrip('/') + path
    print(f"\n嘗試: {path}")

    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        print(f"  狀態: {r.status_code}")

        if r.status_code == 200:
            print(f"  ✓ 200 OK - 找到頁面！")

            # 簡短檢查內容
            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text()

            if '會議' in page_text or '宴會' in page_text:
                print(f"  ✓ 包含會議/宴會內容")

    except Exception as e:
        print(f"  錯誤: {e}")

# 3. 嘗試直接訪問PDF（不同編碼）
print(f"\n嘗試直接訪問PDF:")
print("-" * 100)

pdf_urls = [
    'https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf',
    'https://grandvictoria.com.tw/wp-content/uploads/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf',
    'https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf?download=1',
]

for pdf_url in pdf_urls:
    print(f"\n嘗試: {pdf_url.split('/')[-1]}")

    try:
        r = requests.get(pdf_url, timeout=15, verify=False, headers=headers)
        print(f"  狀態: {r.status_code}")
        print(f"  大小: {len(r.content)} bytes")

        if r.status_code == 200 and len(r.content) > 1000:
            print(f"  ✓ PDF下載成功！")
            break
    except Exception as e:
        print(f"  錯誤: {e}")

print("\n" + "=" * 100)
print("探索完成")
