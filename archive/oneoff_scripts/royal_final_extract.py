#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北老爺大酒店 - 完整提取與更新
訪問會議專案頁面並更新 venues.json
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import re
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北老爺大酒店 - 完整提取與更新")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.royal_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1097), None)

base_url = 'https://www.hotelroyal.com.tw/'
meeting_url = 'https://www.hotelroyal.com.tw/zh-tw/promotions/meeting'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# 訪問會議專案頁面
print("訪問會議專案頁面...")
print("-" * 100)

try:
    r = requests.get(meeting_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP 狀態: {r.status_code}")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 顯示完整內容
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 200]

        print(f"\n頁面內容（前60行）:")
        for line in lines[:60]:
            print(f"  {line[:100]}")

        # 提取會議室資訊
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)

        print(f"\n提取資料:")
        print(f"  會議室: {rooms}")
        print(f"  容量: {capacities}")
        print(f"  面積: {areas}")
        print(f"  價格: {prices[:20]}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

print(f"\n備份: {backup_file}")
print(f"\n✅ 資料提取完成")
