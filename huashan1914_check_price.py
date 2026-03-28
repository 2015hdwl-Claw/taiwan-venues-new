#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查華山1914網頁的價格資料
"""

import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.huashan1914.com/w/huashan1914/AppPlaceInfo?pid=21'
response = requests.get(url, timeout=15, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

print("=" * 100)
print("檢查東3B-烏梅劇院價格資料")
print("=" * 100)

# 尋找所有數字+元的模式
page_text = soup.get_text()

# 價格模式（修復正則表達式）
price_pattern = r'(\d{2,6})\s*元'
prices = re.findall(price_pattern, page_text)

print(f"\n找到的價格: {len(prices)} 處")
for price in prices[:20]:
    print(f"  {price} 元")

# 檢查表格
tables = soup.find_all('table')
print(f"\n表格數量: {len(tables)}")

if tables:
    print("\n第一個表格:")
    for i, row in enumerate(tables[0].find_all('tr')[:10]):
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        if cells:
            print(f"  行{i}: {cells}")

# 儲存完整頁面文字以便查看
print("\n" + "=" * 100)
print("頁面文字片段（包含價格）")
print("=" * 100)

# 找出包含"元"的段落
lines = page_text.split('\n')
for i, line in enumerate(lines):
    if '元' in line and len(line.strip()) > 5 and len(line.strip()) < 100:
        print(f"{i}: {line.strip()}")
