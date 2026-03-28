#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北喜瑞飯店 - 顯示所有連結
"""

import requests
from bs4 import BeautifulSoup
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北喜瑞飯店 - 所有連結分析")
print("=" * 100)

base_url = 'https://www.ambiencehotel.com.tw/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

try:
    r = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP Status: {r.status_code}\n")

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
            if 'ambiencehotel.com.tw' in href or href.startswith('/'):
                all_links.append({
                    'text': text,
                    'url': href
                })

        # 去重
        seen = set()
        unique_links = []
        for link in all_links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)

        print(f"總共找到 {len(unique_links)} 個內部連結\n")

        # 分類顯示
        print("=" * 100)
        print("所有內部連結（按重要性排序）:")
        print("=" * 100)

        # 優先顯示可能包含會議資訊的連結
        priority_keywords = ['會議', '宴會', '會議室', '婚宴', '活動', '服務', '設施',
                           'meeting', 'banquet', 'event', 'service', 'facility']

        priority_links = []
        other_links = []

        for link in unique_links:
            text_lower = link['text'].lower()
            url_lower = link['url'].lower()

            if any(kw in text_lower or kw in url_lower for kw in priority_keywords):
                priority_links.append(link)
            else:
                other_links.append(link)

        print("\n【優先連結 - 可能包含會議/服務資訊】\n")
        for link in priority_links[:30]:
            print(f"  {link['text'][:50]:50s}")
            print(f"    {link['url']}")

        print(f"\n【其他連結 - 前30個】\n")
        for link in other_links[:30]:
            text = link['text'][:50] if link['text'] else '[無文字]'
            print(f"  {text:50s}")
            print(f"    {link['url']}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
