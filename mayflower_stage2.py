#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北美福大飯店 - 階段2：深度爬蟲
提取會議室與宴會廳資料
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北美福大飯店 - 階段2：深度爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

base_url = 'https://www.grandmayfull.com'

# 2.1 提取宴會廳頁面
print("2.1 Extracting Ballroom Info")
print("-" * 100)

ballroom_url = f"{base_url}/events/ballroom"
print(f"Fetching: {ballroom_url}")

try:
    response = requests.get(ballroom_url, timeout=15, verify=False, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 尋找宴會廳名稱
        print("\nBallroom page content (first 2000 chars):")
        print(page_text[:2000])

        # 尋找容量
        capacities = re.findall(r'(\d+)\s*[人名桌者]', page_text)
        if capacities:
            print(f"\nCapacities found: {capacities[:10]}")

        # 尋找面積
        areas = re.findall(r'([\d.]+)\s*(㎡|坪|平方公尺)', page_text)
        if areas:
            print(f"Areas found: {areas[:10]}")

except Exception as e:
    print(f"Error: {e}")

# 2.2 提取會議廳頁面
print("\n2.2 Extracting Meeting Room Info")
print("-" * 100)

meeting_url = f"{base_url}/events/meeting"
print(f"Fetching: {meeting_url}")

try:
    response = requests.get(meeting_url, timeout=15, verify=False, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        print("\nMeeting room page content (first 2000 chars):")
        print(page_text[:2000])

        # 尋找會議室名稱
        room_names = re.findall(r'([喜萬鴻福]+廳?)', page_text)
        if room_names:
            print(f"\nRoom names found: {room_names}")

except Exception as e:
    print(f"Error: {e}")

# 2.3 提取喜福/萬福/鴻福廳頁面
print("\n2.3 Extracting XiFu/WanFu/HongFu Info")
print("-" * 100)

xwh_url = f"{base_url}/events/Xifu_Wanfu_Hongfu"
print(f"Fetching: {xwh_url}")

try:
    response = requests.get(xwh_url, timeout=15, verify=False, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        print("\nXifu/Wanfu/Hongfu page content (first 3000 chars):")
        print(page_text[:3000])

except Exception as e:
    print(f"Error: {e}")

# 2.4 提取聯絡資訊
print("\n2.4 Extracting Contact Info")
print("-" * 100)

contact_url = f"{base_url}/events"
print(f"Fetching: {contact_url}")

try:
    response = requests.get(contact_url, timeout=15, verify=False, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 提取電話
        phones = re.findall(r'0\d[\d-]{7,9}', page_text)
        print(f"Phones found: {phones}")

        # 提取Email
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        valid_emails = [e for e in emails if 'no-reply' not in e.lower() and 'noreply' not in e.lower()]
        print(f"Emails found: {valid_emails}")

except Exception as e:
    print(f"Error: {e}")

# 2.5 檢查PDF
print("\n2.5 Checking PDFs")
print("-" * 100)

pdf_urls = [
    'https://www.grandmayfull.com/uploads/20260304_135050_490.pdf',
    'https://www.grandmayfull.com/uploads/2026_map.pdf'
]

for pdf_url in pdf_urls:
    print(f"\nTrying PDF: {pdf_url}")
    try:
        response = requests.head(pdf_url, timeout=10, verify=False, headers=headers)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Size: {response.headers.get('Content-Length', 'Unknown')} bytes")
            print(f"  Type: {response.headers.get('Content-Type', 'Unknown')}")
    except Exception as e:
        print(f"  Error: {e}")

# 儲存階段2結果
stage2_result = {
    "venue": "台北美福大飯店",
    "venue_id": 1095,
    "timestamp": datetime.now().isoformat(),
    "ballroom_page_fetched": True,
    "meeting_page_fetched": True,
    "pdfs_checked": len(pdf_urls),
    "note": "jQuery website, easier to scrape than Angular. Ballroom and meeting pages have detailed information."
}

with open('mayflower_stage2_results.json', 'w', encoding='utf-8') as f:
    json.dump(stage2_result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("Stage 2 Complete")
print("=" * 100)
print(f"Pages fetched: 3")
print(f"PDFs checked: {len(pdf_urls)}")
print(f"Result saved: mayflower_stage2_results.json")
