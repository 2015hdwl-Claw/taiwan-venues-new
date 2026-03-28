#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思台中新烏日會議中心 - 完整爬取（PDF + 會議室詳情頁）
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "https://www.meeting.com.tw/xinwuri/"

print("=" * 100)
print("集思台中新烏日會議中心 - 完整爬取")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

os.makedirs('jhsi_wuri_docs', exist_ok=True)

# 1. 獲取下載頁面的 PDF
print("1. 下載 PDF 資料")
print("-" * 100)

download_url = base_url + "download.php"
response = requests.get(download_url, timeout=15, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# 找到新烏日相關的 PDF
pdf_links = [a.get('href') for a in soup.find_all('a', href=True)
            if '.pdf' in a.get('href', '') and '烏日' in a.get('href', '')]

print(f"找到 {len(pdf_links)} 個新烏日相關 PDF")

from urllib.parse import urljoin
downloaded_pdfs = []

for pdf_href in pdf_links:
    if pdf_href.startswith('http'):
        pdf_url = pdf_href
    else:
        pdf_url = urljoin(download_url, pdf_href)

    pdf_filename = pdf_href.split('/')[-1]
    if not pdf_filename.endswith('.pdf'):
        continue

    print(f"下載: {pdf_filename}")

    try:
        response = requests.get(pdf_url, timeout=30, verify=False)

        if response.status_code == 200:
            filepath = os.path.join('jhsi_wuri_docs', pdf_filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            size_kb = len(response.content) / 1024
            print(f"  ✅ 已儲存 ({size_kb:.1f} KB)")
            downloaded_pdfs.append(filepath)
        else:
            print(f"  ❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

print(f"\n✅ PDF 下載完成: {len(downloaded_pdfs)} 個\n")

# 2. 找到會議室詳情頁面
print("2. 找到會議室詳情頁面")
print("-" * 100)

response = requests.get(base_url + 'index.php', timeout=15, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# 從階段2我們知道有這些會議室
room_names = ['301會議室', '303會議室', '401會議室', '402會議室']

# 嘗試找到會議室詳情頁
room_links = []
for a in soup.find_all('a', href=True):
    href = a.get('href', '')
    text = a.get_text()

    # 尋找可能的會議室詳情頁
    if any(name.split('會')[0] in href for name in room_names):
        room_links.append({
            'name': text,
            'url': urljoin(base_url, href)
        })

print(f"找到 {len(room_links)} 個會議室詳情頁")
for link in room_links:
    print(f"  - {link['name']}: {link['url']}")

# 3. 如果沒有找到詳情頁，嘗試其他格式
if len(room_links) == 0:
    print("\n  未找到詳情頁，嘗試標準格式...")

    # 嘗試標準格式：room-301.php, room-303.php 等
    for room in room_names:
        room_num = room.split('會')[0]
        possible_url = f"room-{room_num}.php"
        full_url = urljoin(base_url, possible_url)

        try:
            response = requests.get(full_url, timeout=10, verify=False)

            if response.status_code == 200:
                room_links.append({
                    'name': room,
                    'url': full_url
                })
                print(f"  ✅ {room}: {full_url}")
        except:
            pass

print(f"\n總共找到 {len(room_links)} 個會議室詳情頁")

# 4. 爬取會議室資料
print("\n3. 爬取會議室資料")
print("-" * 100)

all_rooms_data = []

for room_info in room_links:
    print(f"\n爬取: {room_info['name']}")
    print(f"URL: {room_info['url']}")

    try:
        response = requests.get(room_info['url'], timeout=15, verify=False)

        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 儲存 HTML
        html_file = f"jhsi_wuri_docs/{room_info['name']}_detail.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

        # 提取文字內容
        page_text = soup.get_text()

        # 尋找容量
        capacity = None
        match = re.search(r'容量[：:]\s*(\d+)\s*人', page_text)
        if match:
            capacity = int(match.group(1))
        else:
            # 嘗試其他格式
            match = re.search(r'(\d+)\s*人', page_text)
            if match:
                cap = int(match.group(1))
                if cap < 500:  # 合理容量範圍
                    capacity = cap

        # 尋找坪數
        area_ping = None
        match = re.search(r'面積[：:]\s*(\d+\.?\d*)\s*坪', page_text)
        if match:
            area_ping = float(match.group(1))

        # 尋找照片
        photos = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'lease' in src.lower() or 'room' in src.lower():
                if not src.startswith('http'):
                    src = urljoin(room_info['url'], src)
                if src not in photos:
                    photos.append(src)

        room_data = {
            'name': room_info['name'],
            'url': room_info['url'],
            'capacity': capacity,
            'areaPing': area_ping,
            'photos': photos,
            'html_file': html_file
        }

        all_rooms_data.append(room_data)

        print(f"  容量: {capacity} 人" if capacity else "  容量: 未找到")
        print(f"  面積: {area_ping} 坪" if area_ping else "  面積: 未找到")
        print(f"  照片: {len(photos)} 張")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

# 儲存結果
output_file = 'jhsi_wuri_rooms_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_rooms_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 會議室資料已儲存: {output_file}")

print("\n" + "=" * 100)
print("✅ 集思台中新烏日爬取完成")
print("=" * 100)
