#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北美福大飯店 - 階段2深度爬蟲
發現所有頁面與PDF並提取完整資料
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
print("台北美福大飯店 - 階段2深度爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1095), None)
if not venue:
    print("Venue 1095 not found!")
    sys.exit(1)

base_url = 'https://www.grandmayfull.com/'
print(f"場地: {venue['name']}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

all_meeting_data = {
    'rooms': [],
    'capacities': [],
    'areas': [],
    'prices': [],
    'floors': [],
    'features': [],
    'contact': {}
}

# ========== 1. 搜尋所有可能的動態ID頁面 ==========
print("=" * 100)
print("1. 搜尋動態ID頁面 (?cat=page&id=XX)")
print("=" * 100)

valid_pages = []
for id_num in range(100, 201):
    test_url = f"{base_url}?cat=page&id={id_num}"

    try:
        r = requests.head(test_url, timeout=5, verify=False, headers=headers)
        if r.status_code == 200:
            print(f"✓ ID {id_num}: 200 OK")
            valid_pages.append(id_num)
    except:
        pass

print(f"\n找到 {len(valid_pages)} 個有效頁面\n")

# ========== 2. 訪問所有有效頁面並提取資料 ==========
print("=" * 100)
print("2. 訪問有效頁面提取資料")
print("=" * 100)

for page_id in valid_pages:
    url = f"{base_url}?cat=page&id={page_id}"
    print(f"\n頁面 ID {page_id}:")
    print("-" * 100)

    try:
        r = requests.get(url, timeout=15, verify=False, headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')

            # 提取標題
            title = soup.find('title')
            if title:
                print(f"  標題: {title.get_text(strip=True)[:60]}")

            # 提取頁面文字
            page_text = soup.get_text()

            # 尋找會議室相關資訊
            if '會議' in page_text or '宴會' in page_text or '會議室' in page_text or '廳' in page_text:
                print(f"  ✓ 包含會議/宴會相關內容")

                # 提取容量
                capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
                if capacities:
                    print(f"  容量: {capacities[:10]}")
                    all_meeting_data['capacities'].extend([int(c) for c in capacities[:10]])

                # 提取面積
                areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
                if areas:
                    print(f"  面積: {areas[:10]}")
                    all_meeting_data['areas'].extend(areas[:10])

                # 提取價格
                prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
                if prices:
                    print(f"  價格: {prices[:10]}")
                    all_meeting_data['prices'].extend(prices[:10])

                # 提取會議室名稱
                room_names = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
                if room_names:
                    print(f"  會議室: {room_names[:10]}")
                    all_meeting_data['rooms'].extend(room_names[:10])

    except Exception as e:
        print(f"  ✗ 錯誤: {e}")

# ========== 3. 搜尋常見會議路徑 ==========
print("\n" + "=" * 100)
print("3. 搜尋常見會議路徑")
print("=" * 100)

meeting_paths = ['/meeting', '/meetings', '/banquet', '/banquets', '/conference',
                  '/event', '/events', '/wedding', '/facility', '/facilities',
                  '/會議', '/宴會', '/會議室', '/婚宴', '/活動', '/宴會廳']

for path in meeting_paths:
    url = base_url.rstrip('/') + path
    print(f"\n嘗試: {url}")

    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        print(f"  狀態: {r.status_code}")

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text()

            # 檢查是否包含會議相關內容
            if '會議' in page_text or '宴會' in page_text or '會議室' in page_text:
                print(f"  ✓ 包含會議相關內容")

                # 提取關鍵資訊
                lines = [l.strip() for l in page_text.split('\n') if 20 < len(l.strip()) < 150]
                if lines:
                    print(f"  內容預覽:")
                    for line in lines[:3]:
                        print(f"    {line[:80]}")

    except Exception as e:
        print(f"  ✗ 錯誤: {e}")

# ========== 4. 下載並解析PDF ==========
print("\n" + "=" * 100)
print("4. 下載並解析PDF")
print("=" * 100)

pdf_urls = [
    'https://www.grandmayfull.com/uploads/2026%20Ocard%E7%BE%8E%E7%A6%8F%E9%9B%86%E9%BB%9E%E5%8D%A1EDM.pdf',
    'https://www.grandmayfull.com/uploads/20260304_135050_490.pdf',
    'https://www.grandmayfull.com/uploads/2026_map.pdf'
]

for pdf_url in pdf_urls:
    print(f"\nPDF: {pdf_url.split('/')[-1]}")
    print("-" * 100)

    try:
        r = requests.get(pdf_url, timeout=30, verify=False)
        print(f"  下載狀態: {r.status_code}")
        print(f"  檔案大小: {len(r.content):,} bytes")

        if r.status_code == 200 and len(r.content) > 1000:
            # 保存PDF
            pdf_filename = pdf_url.split('/')[-1]
            with open(pdf_filename, 'wb') as f:
                f.write(r.content)
            print(f"  ✓ 已保存: {pdf_filename}")

            # 嘗試解析PDF
            try:
                import pdfplumber

                with pdfplumber.open(pdf_filename) as pdf:
                    print(f"  PDF頁數: {len(pdf.pages)}")

                    # 提取所有文字
                    all_text = ""
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            all_text += text + "\n"

                    # 提取關鍵資訊
                    capacities = re.findall(r'(\d+)\s*[人名桌者席位]', all_text)
                    if capacities:
                        print(f"  容量: {capacities[:15]}")
                        all_meeting_data['capacities'].extend([int(c) for c in capacities[:15]])

                    areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', all_text)
                    if areas:
                        print(f"  面積: {areas[:15]}")
                        all_meeting_data['areas'].extend(areas[:15])

                    prices = re.findall(r'(\d+,?\d*)\s*元', all_text)
                    if prices:
                        print(f"  價格: {prices[:15]}")
                        all_meeting_data['prices'].extend(prices[:15])

                    # 提取會議室名稱
                    room_names = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', all_text)
                    if room_names:
                        print(f"  會議室: {room_names[:15]}")
                        all_meeting_data['rooms'].extend(room_names[:15])

                    # 顯示前1000字
                    print(f"\n  PDF內容預覽:")
                    lines = [l.strip() for l in all_text.split('\n') if 10 < len(l.strip()) < 100]
                    for line in lines[:10]:
                        print(f"    {line[:90]}")

            except ImportError:
                print("  ✗ pdfplumber 未安裝")

    except Exception as e:
        print(f"  ✗ 錯誤: {e}")

# ========== 5. 提取聯絡資訊 ==========
print("\n" + "=" * 100)
print("5. 提取聯絡資訊")
print("=" * 100)

try:
    r = requests.get(base_url, timeout=15, verify=False, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 提取電話
        phone_patterns = [
            r'0\d-?\d{3,4}-?\d{3,4}',
            r'\+886-?[\d-]+',
            r'\+886\s?\d[\d-]{7,9}'
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                all_meeting_data['contact']['phone'] = matches[0]
                print(f"電話: {matches[0]}")
                break

        # 提取Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, page_text)
        valid_emails = [e for e in emails if 'no-reply' not in e.lower() and 'noreply' not in e.lower()]

        if valid_emails:
            all_meeting_data['contact']['email'] = valid_emails[0]
            print(f"Email: {valid_emails[0]}")

except Exception as e:
    print(f"錯誤: {e}")

# ========== 6. 匯總結果 ==========
print("\n" + "=" * 100)
print("6. 提取資料匯總")
print("=" * 100)

print(f"\n會議室數量: {len(set(all_meeting_data['rooms']))}")
print(f"  發現的會議室: {list(set(all_meeting_data['rooms']))[:20]}")

print(f"\n容量數據: {len(all_meeting_data['capacities'])} 個")
print(f"  範圍: {min(all_meeting_data['capacities']) if all_meeting_data['capacities'] else 'N/A'} - {max(all_meeting_data['capacities']) if all_meeting_data['capacities'] else 'N/A'} 人")

print(f"\n面積數據: {len(all_meeting_data['areas'])} 個")

print(f"\n價格數據: {len(all_meeting_data['prices'])} 個")
print(f"  範例: {all_meeting_data['prices'][:10]}")

print(f"\n聯絡資訊:")
print(f"  電話: {all_meeting_data['contact'].get('phone', 'N/A')}")
print(f"  Email: {all_meeting_data['contact'].get('email', 'N/A')}")

print("\n" + "=" * 100)
print("階段2完成 - 資料已收集")
print("=" * 100)
print(f"\n下一步: 執行階段3更新 venues.json")
