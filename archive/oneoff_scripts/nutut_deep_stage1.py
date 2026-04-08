#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思北科大會議中心 - 三階段深度爬蟲
階段1：技術檢測（發現會議室列表與【表單下載】頁面）
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
print("集思北科大會議中心 - 階段1：技術檢測")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.meeting.com.tw/ntut/"

# 1.1 訪問主頁
print("1.1 訪問主頁")
print("-" * 100)

try:
    response = requests.get(base_url, timeout=15, verify=False)
    print(f"HTTP 狀態: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")

    if response.status_code != 200:
        print("❌ 主頁訪問失敗")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1.2 發現會議室列表
    print("\n1.2 發現會議室列表")
    print("-" * 100)

    room_links = []

    # 尋找會議室連結（通常在 nav 或 menu 中）
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text(strip=True)

        # 匹配會議室頁面（排除 index, download, about 等非會議室頁面）
        if href.endswith('.php') and not any(
            exclude in href for exclude in ['index', 'download', 'about', 'contact', 'access']
        ):
            # 只包含主頁下的會議室
            full_url = href if href.startswith('http') else base_url + href

            room_links.append({
                'name': text,
                'url': full_url
            })

    # 去重
    seen = set()
    unique_rooms = []
    for room in room_links:
        if room['url'] not in seen:
            seen.add(room['url'])
            unique_rooms.append(room)

    print(f"發現 {len(unique_rooms)} 個會議室頁面：")
    for room in unique_rooms:
        print(f"  - {room['name']}: {room['url']}")

    # 1.3 檢查【表單下載】頁面
    print("\n1.3 檢查【表單下載】頁面")
    print("-" * 100)

    download_url = base_url + "download.php"
    print(f"URL: {download_url}")

    response = requests.get(download_url, timeout=15, verify=False)
    print(f"HTTP 狀態: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找 PDF 連結
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf') or '.pdf' in href.lower():
                if not href.startswith('http'):
                    href = base_url + href
                pdf_links.append(href)

        print(f"發現 {len(pdf_links)} 個 PDF 檔案")

        if pdf_links:
            print("\nPDF 列表：")
            for pdf in pdf_links:
                print(f"  - {pdf}")

    # 1.4 技術檢測每個會議室頁面
    print("\n\n1.4 技術檢測會議室頁面")
    print("-" * 100)

    stage1_results = []

    for room in unique_rooms[:15]:  # 限制最多 15 個
        print(f"\n檢測: {room['name']}")
        print(f"URL: {room['url']}")

        result = {
            'name': room['name'],
            'url': room['url']
        }

        try:
            response = requests.get(room['url'], timeout=15, verify=False)
            http_status = response.status_code
            result['http_status'] = http_status
            result['content_type'] = response.headers.get('Content-Type', '')

            if http_status != 200:
                result['error'] = f"HTTP {http_status}"
                stage1_results.append(result)
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()

            # 檢查照片
            images = soup.find_all('img')
            room_images = [img['src'] for img in images if 'lease' in img.get('src', '').lower()]
            result['room_images'] = len(room_images)

            # 檢查價格
            price_patterns = [
                r'\(平日\).*?每時段.*?NT\$\s*([\d,]+)',
                r'\(例假日\).*?每時段.*?NT\$\s*([\d,]+)',
                r'每時段.*?NT\$\s*([\d,]+)',
            ]
            has_price = any(re.search(pattern, page_text) for pattern in price_patterns)
            result['has_price'] = has_price

            # 檢查容量
            capacity_match = re.search(r'(\d+)\s*人', page_text)
            result['has_capacity'] = capacity_match is not None

            # 檢查面積
            area_match = re.search(r'(\d+\.?\d*)\s*坪', page_text)
            result['has_area'] = area_match is not None

            print(f"  HTTP {http_status}, 照片: {len(room_images)}, 價格: {has_price}, 容量: {result['has_capacity']}, 面積: {result['has_area']}")

        except Exception as e:
            result['error'] = str(e)
            print(f"  ❌ 錯誤: {e}")

        stage1_results.append(result)

    # 儲存階段1結果
    output = {
        "venue": "集思北科大會議中心",
        "venue_id": 1495,
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "rooms_found": len(unique_rooms),
        "pdfs_found": len(pdf_links) if response.status_code == 200 else 0,
        "rooms": stage1_results
    }

    with open('nutut_room_stage1_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ 階段1完成")
    print(f"  會議室: {len(unique_rooms)} 個")
    print(f"  PDF: {len(pdf_links) if response.status_code == 200 else 0} 個")
    print(f"  結果已儲存: nutut_room_stage1_results.json")

except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
