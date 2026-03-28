#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC 嚴謹三階段爬蟲
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://www.ticc.com.tw/'

print('=' * 100)
print('TICC - 嚴謹三階段爬蟲')
print('=' * 100)
print(f'URL: {url}\n')

# 階段1：技術檢測
try:
    response = requests.get(url, timeout=15, verify=False)
    print('階段1：技術檢測')
    print(f'  HTTP 狀態: {response.status_code}')
    print(f'  Content-Type: {response.headers.get("Content-Type")}')

    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script')
    print(f'  Script 數量: {len(scripts)}')

    # 檢查是否有 JS 框架
    js_found = False
    for script in scripts:
        if script.string:
            content = script.string.lower()
            if any(fw in content for fw in ['react', 'vue', 'angular', 'jquery']):
                js_found = True
                print(f'  發現 JS 框架')
                break

    if not js_found:
        print('  頁面類型: 靜態 HTML')

    # 階段2：尋找連結
    print('\n階段2：尋找會議室連結')

    meeting_links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        text = a.get_text(strip=True)
        href_lower = href.lower()

        if any(kw in href_lower or kw in text.lower() for kw in ['meet', 'room', 'floor', '會議', '場地']):
            if not href_lower.startswith('mailto:') and not href_lower.startswith('tel:'):
                meeting_links.append({
                    'text': text[:100],
                    'href': href
                })

    print(f'  找到 {len(meeting_links)} 個相關連結')

    for link in meeting_links[:8]:
        print(f"  {link['text']}")
        print(f"    {link['href']}")

    # 階段3：尋找 PDF
    print('\n階段3：尋找 PDF')

    pdf_links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        href_lower = href.lower()
        if '.pdf' in href_lower:
            pdf_links.append(href)

    print(f'  PDF 連結: {len(pdf_links)} 個')
    for pdf in pdf_links:
        print(f'  {pdf}')

    # 提取頁面文字尋找會議室資訊
    print('\n階段4：提取會議室資訊')

    page_text = soup.get_text()

    # 尋找樓層和會議室命名
    import re

    # TICC 常見會議室：101, 102, 201, 202, 203...
    room_pattern = r'\d+[樓F]?\s*會議室'
    rooms = re.findall(room_pattern, page_text)

    if rooms:
        print(f'  可能的會議室: {len(rooms)} 個')
        for room in list(set(rooms))[:10]:
            print(f'    {room}')

    # 儲存檢測結果
    result = {
        'venue': 'TICC',
        'url': url,
        'http_status': response.status_code,
        'meeting_links_count': len(meeting_links),
        'pdf_links_count': len(pdf_links),
        'potential_rooms': list(set(rooms)) if rooms else []
    }

    with open('ticc_rigorous_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print('\n✅ 檢測結果已儲存到 ticc_rigorous_result.json')

except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()
