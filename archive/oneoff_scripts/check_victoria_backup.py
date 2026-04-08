#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查維多麗亞備份中的價格資料"""

import json
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load backup
with open('venues.json.backup.victoria_pdf_20260324_223235', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Victoria
victoria = next((v for v in data if v.get('id') == 1122), None)
if not victoria:
    print("找不到維多麗亞酒店")
    sys.exit(1)

print('='*80)
print(f"備份檔案: venues.json.backup.victoria_pdf_20260324_223235")
print(f"場地: {victoria['name']}")
print('='*80)

rooms = victoria.get('rooms', [])
print(f'\n會議室數: {len(rooms)}')
print()

# Check prices
has_price = 0
for i, room in enumerate(rooms, 1):
    name = room.get('name', 'Unknown')
    price = room.get('price')

    if price:
        has_price += 1
        if isinstance(price, dict):
            price_str = f"早上: {price.get('morning', 'N/A')}, 下午: {price.get('afternoon', 'N/A')}, 晚上: {price.get('evening', 'N/A')}, 全天: {price.get('fullDay', 'N/A')}"
        else:
            price_str = str(price)
        print(f'{i}. {name}')
        print(f'   價格: {price_str}')
    else:
        print(f'{i}. {name} - 無價格')

print()
print('='*80)
print(f'總計: {has_price}/{len(rooms)} 個會議室有價格資料')
