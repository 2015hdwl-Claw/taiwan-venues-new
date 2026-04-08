#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思系列批次處理 - 階段1：技術檢測
交通部、台中文心、高雄
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

venues_info = [
    {"id": 1494, "name": "集思交通部國際會議中心", "url": "https://www.meeting.com.tw/motc/"},
    {"id": 1497, "name": "集思台中文心會議中心", "url": "https://www.meeting.com.tw/tc/"},
    {"id": 1499, "name": "集思高雄分公司", "url": "https://www.meeting.com.tw/khh/"},
]

for venue_info in venues_info:
    venue_id = venue_info["id"]
    venue_name = venue_info["name"]
    base_url = venue_info["url"]

    print("\n" + "=" * 100)
    print(f"{venue_name} - 階段1：技術檢測")
    print("=" * 100)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1.1 訪問主頁
    print("1.1 訪問主頁")
    print("-" * 100)

    try:
        response = requests.get(base_url, timeout=15, verify=False)
        print(f"HTTP 狀態: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ 主頁訪問失敗: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1.2 發現會議室列表
        print("\n1.2 發現會議室列表")
        print("-" * 100)

        room_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if href.endswith('.php') and not any(
                exclude in href for exclude in ['index', 'download', 'about', 'contact', 'access', 'activity', 'location']
            ):
                full_url = href if href.startswith('http') else base_url + href
                room_links.append({'name': text, 'url': full_url})

        # 去重
        seen = set()
        unique_rooms = []
        for room in room_links:
            if room['url'] not in seen:
                seen.add(room['url'])
                unique_rooms.append(room)

        print(f"發現 {len(unique_rooms)} 個會議室頁面：")
        for room in unique_rooms[:20]:
            print(f"  - {room['name']}: {room['url']}")

        # 1.3 檢查【表單下載】頁面
        print("\n1.3 檢查【表單下載】頁面")
        print("-" * 100)

        download_url = base_url + "download.php"
        response = requests.get(download_url, timeout=15, verify=False)
        print(f"HTTP 狀態: {response.status_code}")

        pdf_count = 0
        pdf_url = None

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'pdf' in href.lower():
                    if not href.startswith('http'):
                        href = base_url + href
                    pdf_links.append(href)

            pdf_count = len(pdf_links)
            print(f"發現 {pdf_count} 個 PDF 檔案")

            # 尋找場地租用 PDF
            for pdf in pdf_links:
                if '租用' in pdf or '申請' in pdf or venue_name.split('集思')[-1][:2] in pdf:
                    pdf_url = pdf
                    print(f"  場地租用 PDF: {pdf_url}")
                    break

        # 1.4 技術檢測每個會議室頁面
        print("\n1.4 技術檢測會議室頁面")
        print("-" * 100)

        stage1_results = []

        for room in unique_rooms[:15]:
            print(f"\n檢測: {room['name']}")

            result = {'name': room['name'], 'url': room['url']}

            try:
                response = requests.get(room['url'], timeout=15, verify=False)
                http_status = response.status_code
                result['http_status'] = http_status

                if http_status != 200:
                    result['error'] = f"HTTP {http_status}"
                    stage1_results.append(result)
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()

                images = soup.find_all('img')
                room_images = [img['src'] for img in images if 'lease' in img.get('src', '').lower()]
                result['room_images'] = len(room_images)

                price_patterns = [r'\(平日\).*?每時段.*?NT\$', r'每時段.*?NT\$']
                has_price = any(re.search(pattern, page_text) for pattern in price_patterns)
                result['has_price'] = has_price

                capacity_match = re.search(r'(\d+)\s*人', page_text)
                result['has_capacity'] = capacity_match is not None

                area_match = re.search(r'(\d+\.?\d*)\s*坪', page_text)
                result['has_area'] = area_match is not None

                print(f"  HTTP {http_status}, 照片: {len(room_images)}, 價格: {has_price}, 容量: {result['has_capacity']}, 面積: {result['has_area']}")

            except Exception as e:
                result['error'] = str(e)
                print(f"  ❌ 錯誤: {e}")

            stage1_results.append(result)

        # 儲存結果
        prefix = venue_name.split('集思')[-1].split('會')[0].lower()
        output = {
            "venue": venue_name,
            "venue_id": venue_id,
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "rooms_found": len(unique_rooms),
            "pdfs_found": pdf_count,
            "pdf_rental_url": pdf_url,
            "rooms": stage1_results
        }

        filename = f'{prefix}_room_stage1_results.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 階段1完成 - {venue_name}")
        print(f"  會議室: {len(unique_rooms)} 個")
        print(f"  PDF: {pdf_count} 個")
        print(f"  結果已儲存: {filename}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 100)
print("✅ 所有場地階段1完成")
print("=" * 100)
