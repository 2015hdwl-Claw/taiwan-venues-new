#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北文華東方酒店 - 階段2：深度爬蟲
基於階段1結果：發現 Events 頁面，需要提取完整資料
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys
from urllib.parse import urljoin
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北文華東方酒店 - 階段2：深度爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1085), None)

if not venue:
    print("Venue 1085 not found!")
    sys.exit(1)

base_url = venue['url']
print(f"Base URL: {base_url}")

# 2.1 訪問 Events 頁面
print("\n2.1 Access Events Page")
print("-" * 100)

events_url = "https://www.mandarinoriental.com/taipei/en/taipei/songshan/events"
print(f"URL: {events_url}")

try:
    response = requests.get(events_url, timeout=15, verify=False)
    print(f"HTTP Status: {response.status_code}")
    print(f"Size: {len(response.content):,} bytes")
except Exception as e:
    print(f"Error accessing events page: {e}")
    sys.exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# 2.2 尋找會議室資訊
print("\n2.2 Meeting Room Discovery")
print("-" * 100)

# 尋找會議室相關的關鍵字
keywords = ['ballroom', 'meeting', 'function', 'room', '宴會', '會議', '廳']

room_sections = []
for tag in soup.find_all(['div', 'section', 'h2', 'h3']):
    text = tag.get_text()
    if any(keyword in text.lower() for keyword in keywords):
        room_sections.append({
            'tag': tag.name,
            'text': text.strip()[:100]
        })

print(f"Found {len(room_sections)} potential room sections")

# 2.3 尋找 PDF 連結
print("\n2.3 PDF Discovery")
print("-" * 100)

pdf_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if '.pdf' in href.lower():
        if not href.startswith('http'):
            href = urljoin(base_url, href)
        pdf_links.append(href)

print(f"Found {len(pdf_links)} PDF links")
if pdf_links:
    for pdf in pdf_links:
        print(f"  - {pdf}")

# 2.4 尋找價格資訊
print("\n2.4 Price Information Discovery")
print("-" * 100)

price_patterns = [
    r'NT\$?\s*[\d,]+',
    r'TWD\s*[\d,]+',
    r'\$[\d,]+',
    r'[\d,]+\s*元'
]

page_text = soup.get_text()
prices = []

import re
for pattern in price_patterns:
    matches = re.findall(pattern, page_text)
    if matches:
        prices.extend(matches)

# 去重
prices = list(set(prices))

if prices:
    print(f"Found {len(prices)} potential prices:")
    for price in prices[:10]:
        print(f"  - {price}")
else:
    print("No price information found")

# 2.5 尋找聯絡資訊
print("\n2.5 Contact Information Discovery")
print("-" * 100)

# 電話
phone_pattern = r'[\+]?[0-9]{2,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}'
phones = re.findall(phone_pattern, page_text)

# Email
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
emails = re.findall(email_pattern, page_text)

# 過濾垃圾 Email
valid_emails = [e for e in emails if not any(
    spam in e.lower() for spam in ['no-reply', 'noreply', '@example', '@wixpress']
)]

print(f"Phones found: {len(set(phones))}")
unique_phones = list(set(phones))
for phone in unique_phones[:5]:
    print(f"  - {phone}")

print(f"\nEmails found: {len(valid_emails)}")
for email in valid_emails[:5]:
    print(f"  - {email}")

# 2.6 尋找交通資訊
print("\n2.6 Transportation Information Discovery")
print("-" * 100)

mrt_keywords = ['mrt', '捷運', 'ts', 'station']
bus_keywords = ['bus', '公車']
parking_keywords = ['parking', '停車']

transport_info = {}

for keyword in mrt_keywords:
    if keyword in page_text.lower():
        # 找到包含捷運資訊的段落
        for tag in soup.find_all(['p', 'div']):
            text = tag.get_text()
            if keyword in text.lower():
                transport_info['mrt'] = text.strip()[:100]
                break
        break

for keyword in bus_keywords:
    if keyword in page_text.lower():
        for tag in soup.find_all(['p', 'div']):
            text = tag.get_text()
            if keyword in text.lower():
                transport_info['bus'] = text.strip()[:100]
                break
        break

for keyword in parking_keywords:
    if keyword in page_text.lower():
        for tag in soup.find_all(['p', 'div']):
            text = tag.get_text()
            if keyword in text.lower():
                transport_info['parking'] = text.strip()[:100]
                break
        break

if transport_info:
    for key, value in transport_info.items():
        print(f"{key.upper()}: {value}")

# 儲存階段2結果
stage2_result = {
    "venue": "台北文華東方酒店",
    "venue_id": 1085,
    "timestamp": datetime.now().isoformat(),
    "events_page": {
        "url": events_url,
        "status": response.status_code,
        "size": len(response.content)
    },
    "room_sections": room_sections[:10],
    "pdf_links": pdf_links,
    "prices": prices[:20],
    "contact": {
        "phones": list(set(phones))[:10],
        "emails": valid_emails[:5]
    },
    "transportation": transport_info
}

with open('moh_stage2_results.json', 'w', encoding='utf-8') as f:
    json.dump(stage2_result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("Stage 2 Complete")
print("=" * 100)
print(f"Room sections: {len(room_sections)}")
print(f"PDF links: {len(pdf_links)}")
print(f"Price patterns: {len(prices)}")
print(f"Contact: {len(valid_emails)} emails")
print(f"Result saved: moh_stage2_results.json")
