#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
茹曦酒店 - 階段2：深度爬蟲
使用 requests + BeautifulSoup 提取會議室資料
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("茹曦酒店 - 階段2：深度爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 載入階段1結果
with open('juhsi_stage1_results.json', encoding='utf-8') as f:
    stage1 = json.load(f)

base_url = stage1['main_page']['url']
print(f"Base URL: {base_url}\n")

# 2.1 提取主頁會議資訊
print("2.1 Extracting Meeting Info from Main Page")
print("-" * 100)

try:
    response = requests.get(base_url, timeout=15, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 尋找會議/宴會相關文字
    page_text = soup.get_text()

    # 尋找關鍵資訊
    capacity_pattern = r'容量[：:]\s*(\d+)'
    area_pattern = r'面積[：:]\s*([\d.]+)\s*(㎡|坪|平方公尺)'
    floor_pattern = r'(\d+[F樓層])'

    capacities = re.findall(capacity_pattern, page_text)
    areas = re.findall(area_pattern, page_text)

    print(f"Capacities found: {capacities[:5] if capacities else 'None'}")
    print(f"Areas found: {areas[:5] if areas else 'None'}")

    # 尋找會議室相關段落
    meeting_keywords = ['會議室', '會議', '宴會', '活動', '會議', 'MICE']
    meeting_sections = []

    for p in soup.find_all(['p', 'div', 'section', 'h1', 'h2', 'h3']):
        text = p.get_text(strip=True)
        if any(keyword in text for keyword in meeting_keywords) and len(text) > 10:
            meeting_sections.append(text)

    print(f"\nMeeting related sections: {len(meeting_sections)}")
    for section in meeting_sections[:5]:
        print(f"  - {section[:100]}...")

except Exception as e:
    print(f"Error: {e}")

# 2.2 探索關鍵頁面
print("\n2.2 Exploring Key Pages")
print("-" * 100)

key_urls = [
    'https://www.theillumehotel.com/zh/overview-of-illume-taipei/contact-us/',
    'https://www.theillumehotel.com/zh/taipei-hotel-offers/',
    'https://www.theillumehotel.com/zh/overview-of-illume-taipei/',
]

for url in key_urls:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=15, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 尋找會議室資訊
            page_text = soup.get_text()

            # 提取關鍵資訊
            if '會議' in page_text or '宴會' in page_text or '會議室' in page_text:
                print(f"  ✓ Contains meeting/banquet keywords")

                # 尋找容量
                capacities = re.findall(r'(\d+)\s*[人名者]', page_text)
                if capacities:
                    print(f"  Capacities: {capacities[:5]}")

                # 尋找面積
                areas = re.findall(r'([\d.]+)\s*(㎡|坪)', page_text)
                if areas:
                    print(f"  Areas: {areas[:5]}")

                # 尋找電話和Email
                phones = re.findall(r'0\d[\d-]{7,9}', page_text)
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)

                if phones:
                    print(f"  Phones: {phones[:3]}")
                if emails:
                    print(f"  Emails: {emails[:3]}")

        elif response.status_code == 404:
            print(f"  ✗ 404 Not Found")
        else:
            print(f"  ✗ Status: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

# 2.3 嘗試常見會議頁面URL模式
print("\n2.3 Trying Common Meeting URL Patterns")
print("-" * 100)

meeting_patterns = [
    '/meeting',
    '/meetings',
    '/conference',
    '/banquet',
    '/wedding',
    '/events',
    '/mice',
    '/會議',
    '/宴會',
    '/婚宴',
]

for pattern in meeting_patterns:
    url = base_url.rstrip('/') + pattern
    print(f"Trying: {url}")
    try:
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            print(f"  ✓ Found (200)")
            # 保存這個URL以便後續處理
            break
        elif response.status_code == 404:
            print(f"  ✗ 404")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# 2.4 提取聯絡資訊
print("\n2.4 Extracting Contact Info")
print("-" * 100)

contact_url = 'https://www.theillumehotel.com/zh/overview-of-illume-taipei/contact-us/'
try:
    response = requests.get(contact_url, timeout=15, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    page_text = soup.get_text()

    # 提取電話
    phones = re.findall(r'0\d[\d-]{7,9}', page_text)
    print(f"Phones found: {phones}")

    # 提取Email
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
    valid_emails = [e for e in emails if 'no-reply' not in e.lower() and 'noreply' not in e.lower()]
    print(f"Emails found: {valid_emails}")

    # 提取地址
    address_pattern = r'(台北市.*[區|市].*\d+號)'
    addresses = re.findall(address_pattern, page_text)
    print(f"Address found: {addresses[0] if addresses else 'None'}")

except Exception as e:
    print(f"Error: {e}")

# 儲存階段2結果
stage2_result = {
    "venue": "茹曦酒店",
    "venue_id": 1090,
    "timestamp": datetime.now().isoformat(),
    "contact_info": {
        "phones": phones if 'phones' in locals() else [],
        "emails": valid_emails if 'valid_emails' in locals() else [],
        "address": addresses[0] if 'addresses' in locals() and addresses else None
    },
    "meeting_sections_count": len(meeting_sections) if 'meeting_sections' in locals() else 0,
    "note": "Angular website, content may be dynamically loaded. Consider using Playwright or manual extraction."
}

with open('juhsi_stage2_results.json', 'w', encoding='utf-8') as f:
    json.dump(stage2_result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("Stage 2 Complete")
print("=" * 100)
print(f"Contact info extracted")
print(f"Result saved: juhsi_stage2_results.json")
print("\n建議：此網站使用 Angular，會議室資訊可能需要手動提取或使用 Playwright")
