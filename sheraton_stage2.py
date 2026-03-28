#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北寒舍喜來登大飯店 - 階段2：深度爬蟲
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
print("台北寒舍喜來登 - 階段2：深度爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.sheratongrandtaipei.com/"

# 2.1 訪問主頁並尋找會議/宴會頁面
print("2.1 Access Main Page and Find Meeting Pages")
print("-" * 100)

response = requests.get(base_url, timeout=15, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# 尋找會議/宴會相關連結
meeting_pages = []

for link in soup.find_all('a', href=True):
    href = link['href']
    text = link.get_text().lower()

    # 尋找包含會議/宴會關鍵字的連結
    keywords = ['meeting', 'banquet', '會議', '宴會', '婚宴', '會議室', '宴會廳']

    if any(keyword in href.lower() or keyword in text for keyword in keywords):
        full_url = href if href.startswith('http') else base_url + href
        meeting_pages.append({
            'text': link.get_text(strip=True)[:60],
            'url': full_url
        })

# 去重
seen = set()
unique_pages = []
for page in meeting_pages:
    if page['url'] not in seen:
        seen.add(page['url'])
        unique_pages.append(page)

print(f"Found {len(unique_pages)} unique meeting/banquet pages:\n")
for page in unique_pages:
    print(f"  - {page['text']}")
    print(f"    URL: {page['url']}\n")

# 2.2 訪問宴會會議頁面
print("\n2.2 Access Banquet/Meeting Pages")
print("-" * 100)

all_rooms = []

for page in unique_pages[:5]:  # 最多訪問前5個頁面
    url = page['url']
    print(f"\nAccessing: {page['text']}")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=15, verify=False)
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找會議室/宴會廳資訊
        # 常見的會議室命名模式
        room_keywords = ['廳', '室', '廳房', '會議室', '宴會廳', 'ballroom', 'room', 'hall']

        # 方法1: 尋找標題中包含廳/室的元素
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'div', 'span']:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if any(keyword in text for keyword in room_keywords):
                    # 檢查是否可能是會議室名稱
                    if len(text) >= 3 and len(text) <= 20:
                        print(f"  Potential room: {text}")
                        all_rooms.append({'name': text, 'source': url})

        # 方法2: 尋找 class 或 id 包含 room/banquet 的元素
        for selector in ['class', 'id']:
            pattern = re.compile(r'(room|banquet|meeting|hall)', re.I)
            for element in soup.find_all(attrs={selector: pattern}):
                text = element.get_text(strip=True)
                if len(text) >= 3 and len(text) <= 30:
                    if any(keyword in text for keyword in room_keywords):
                        print(f"  Potential room (by {selector}): {text}")
                        all_rooms.append({'name': text, 'source': url})

        # 方法3: 尋找表格中的場地資訊
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if any(keyword in text for keyword in room_keywords):
                        if len(text) >= 3 and len(text) <= 20:
                            print(f"  Potential room (table): {text}")
                            all_rooms.append({'name': text, 'source': url})

    except Exception as e:
        print(f"  Error: {e}")
        continue

# 2.3 去重會議室名稱
print("\n\n2.3 Deduplicate Room Names")
print("-" * 100)

seen_rooms = set()
unique_rooms = []

for room in all_rooms:
    name = room['name']
    # 簡單清理名稱
    clean_name = re.sub(r'\s+', ' ', name).strip()

    if clean_name and clean_name not in seen_rooms:
        seen_rooms.add(clean_name)
        unique_rooms.append({
            'name': clean_name,
            'source': room['source']
        })

print(f"\nFound {len(unique_rooms)} unique rooms:\n")
for i, room in enumerate(unique_rooms, 1):
    print(f"{i}. {room['name']}")

# 2.4 尋找 PDF 檔案
print("\n\n2.4 Search for PDF Files")
print("-" * 100)

pdf_urls = []

# 在主頁和所有找到的頁面中尋找 PDF
urls_to_check = [base_url] + [page['url'] for page in unique_pages]

for url in urls_to_check[:10]:
    try:
        response = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href']
            if '.pdf' in href.lower():
                full_pdf_url = href if href.startswith('http') else base_url + href
                if full_pdf_url not in pdf_urls:
                    pdf_urls.append(full_pdf_url)
                    print(f"  Found PDF: {link.get_text(strip=True)[:50]}")
                    print(f"    URL: {full_pdf_url}\n")

    except Exception as e:
        continue

# 2.5 尋找容量、面積資訊
print("\n2.5 Extract Capacity and Area Information")
print("-" * 100)

room_details = {}

for room in unique_rooms:
    room_name = room['name']
    print(f"\n{room_name}:")

    # 嘗試從來源頁面提取詳細資訊
    try:
        response = requests.get(room['source'], timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 尋找容量資訊
        capacity_patterns = [
            r'容量[：:]\s*(\d+)',
            r'人數[：:]\s*(\d+)',
            r'(\d+)\s*人',
        ]

        capacity = None
        for pattern in capacity_patterns:
            match = re.search(pattern, page_text)
            if match:
                capacity = int(match.group(1))
                print(f"  Capacity: {capacity} 人")
                break

        # 尋找面積資訊
        area_patterns = [
            r'面積[：:]\s*(\d+(?:\.\d+)?)\s*坪',
            r'(\d+(?:\.\d+)?)\s*坪',
            r'(\d+(?:\.\d+)?)\s*平方米',
        ]

        area = None
        for pattern in area_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                area = float(matches[0])
                print(f"  Area: {area} 坪")
                break

        room_details[room_name] = {
            'capacity': capacity,
            'areaPing': area,
            'source': room['source']
        }

    except Exception as e:
        print(f"  Error extracting details: {e}")
        room_details[room_name] = {
            'capacity': None,
            'areaPing': None,
            'source': room['source']
        }

# 2.6 儲存階段2結果
stage2_result = {
    "venue": "台北寒舍喜來登大飯店",
    "venue_id": 1075,
    "timestamp": datetime.now().isoformat(),
    "meeting_pages": unique_pages,
    "pdf_urls": pdf_urls,
    "rooms_found": unique_rooms,
    "room_details": room_details
}

with open('sheraton_stage2_results.json', 'w', encoding='utf-8') as f:
    json.dump(stage2_result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("Stage 2 Complete")
print("=" * 100)
print(f"Meeting pages: {len(unique_pages)}")
print(f"PDFs found: {len(pdf_urls)}")
print(f"Rooms found: {len(unique_rooms)}")
print(f"Rooms with details: {len(room_details)}")
print(f"\nResult saved: sheraton_stage2_results.json")
