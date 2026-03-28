#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試華山1914爬蟲
"""
from scrapling import Fetcher
import re

url = "https://www.huashan1914.com"

print("="*100)
print(f"測試爬取: {url}")
print("="*100)
print()

# Fetch the page
fetcher = Fetcher()
page = fetcher.get(url)

print(f"狀態碼: {page.status}")
print(f"頁面長度: {len(page.text)} 字元")
print()

# 搜尋會議室相關關鍵字
keywords = ['會議室', '會議', '空間', '場地', '出租', '租賃', '宴會', '展場']
print("搜尋會議室相關關鍵字:")
print("-"*100)

all_text = page.text

for keyword in keywords:
    count = all_text.count(keyword)
    if count > 0:
        print(f"  ✅ '{keyword}': 出現 {count} 次")

print()
print("-"*100)

# 搜尋可能的會議室名稱
print()
print("搜尋可能的場地名稱:")
print("-"*100)

# 常見場地類型
venue_patterns = [
    r'[\u4e00-\u9fa5]{2,8}[廳場樓館室]',
    r'[\u4e00-\u9fa5]{2,8}(展場|空間|會議室|宴會廳)',
    r'\d+[F樓][\u4e00-\u9fa5]{2,8}',
]

found_venues = set()
for pattern in venue_patterns:
    matches = re.findall(pattern, all_text)
    for match in matches:
        if len(match) >= 4:
            found_venues.add(match)

for venue in sorted(found_venues):
    print(f"  - {venue}")

print()
print("-"*100)
print()
print("頁面前 500 字預覽:")
print("-"*100)
print(all_text[:500])
