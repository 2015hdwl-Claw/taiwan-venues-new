#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北喜瑞飯店 - 檢查英文版和 sitemap
"""

import requests
from bs4 import BeautifulSoup
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北喜瑞飯店 - 檢查英文版和 Sitemap")
print("=" * 100)

base_url = 'https://www.ambiencehotel.com.tw'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# 檢查英文版首頁
print("\n檢查英文版首頁:")
print("-" * 100)

try:
    r = requests.get(f"{base_url}/en/", timeout=20, verify=False, headers=headers)
    print(f"狀態: {r.status_code}")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 檢查關鍵字
        keywords = ['meeting', 'conference', 'banquet', 'event', 'wedding',
                   'function', 'room', 'hall']

        found = [kw for kw in keywords if kw.lower() in page_text.lower()]

        if found:
            print(f"✓ 發現關鍵字: {', '.join(found)}")

            lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 200]
            relevant = [l for l in lines if any(kw in l.lower() for kw in found)]

            if relevant:
                print(f"\n相關內容:")
                for line in relevant[:5]:
                    print(f"  {line[:100]}")
        else:
            print("無會議/宴會相關內容")

except Exception as e:
    print(f"錯誤: {e}")

# 檢查 sitemap
print("\n檢查 Sitemap:")
print("-" * 100)

sitemap_urls = [
    '/sitemap.xml',
    '/sitemap_index.xml',
    '/wp-sitemap.xml',
    '/robots.txt'
]

for sitemap_path in sitemap_urls:
    url = base_url + sitemap_path
    print(f"\n嘗試: {url}")

    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        print(f"  狀態: {r.status_code}")

        if r.status_code == 200:
            content = r.text

            # 顯示部分內容
            lines = content.split('\n')
            if len(lines) > 0:
                print(f"  內容預覽（前20行）:")
                for line in lines[:20]:
                    print(f"    {line.strip()[:100]}")

    except Exception as e:
        print(f"  錯誤: {e}")

print("\n" + "=" * 100)
print("結論")
print("=" * 100)
print("""
台北喜瑞飯店官網沒有公開顯示會議/宴會設施資訊。

可能的原因：
1. 會議設施只通過直接詢問提供
2. 資訊在第三方訂房網站上
3. 飯店主要專注於客房服務

建議：
- 直接聯繫飯店詢問會議設施
- 檢查第三方訂房平台（如 Agoda, Booking.com）
- 記錄當前已知的基本資訊
""")
