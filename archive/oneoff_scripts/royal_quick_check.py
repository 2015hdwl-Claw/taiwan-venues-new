#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提升台北老爺大酒店品質分數
從完整來源提取會議室資料
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
print("台北老爺大酒店 - 完整資料提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.royal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1097), None)
if not venue:
    print("Venue 1097 not found!")
    sys.exit(1)

base_url = 'https://www.hotelroyal.com.tw/zh-tw/taipei/'

print(f"場地: {venue['name']}")
print(f"URL: {base_url}")
print(f"當前品質: {venue.get('metadata', {}).get('qualityScore', 'N/A')}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# 提取所有連結
print("提取主頁所有連結...")

try:
    r = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP 狀態: {r.status_code}")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')

        all_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if not href or href.startswith('javascript:') or href.startswith('#'):
                continue

            # 轉換為絕對URL
            if href.startswith('/'):
                full_url = 'https://www.hotelroyal.com.tw' + href
            elif not href.startswith('http'):
                full_url = base_url + href
            else:
                full_url = href

            all_links.append({
                'text': text[:60],
                'url': full_url
            })

        print(f"找到 {len(all_links)} 個連結\n")

        # 尋找會議/宴會相關連結
        meeting_links = []
        for link in all_links:
            text_lower = link['text'].lower()
            url_lower = link['url'].lower()

            if any(kw in text_lower or kw in url_lower for kw in
                   ['會議', '宴會', '會議室', '婚宴', '活動', 'meeting', 'banquet', 'event']):
                meeting_links.append(link)

        if meeting_links:
            print(f"會議/宴會相關連結 ({len(meeting_links)}):")
            for link in meeting_links[:15]:
                print(f"  {link['text']}")
                print(f"    {link['url']}")
        else:
            print("無明顯的會議/宴會連結")

        # 尋找PDF
        pdf_links = []
        for link in all_links:
            if '.pdf' in link['url'].lower():
                pdf_links.append(link)

        if pdf_links:
            print(f"\nPDF連結 ({len(pdf_links)}):")
            for link in pdf_links:
                print(f"  {link['url']}")

except Exception as e:
    print(f"錯誤: {e}")

print(f"\n備份: {backup_file}")
print(f"\n✅ 資料提取完成")
print(f"下一步: 根據發現的連結深度提取會議室資料")
