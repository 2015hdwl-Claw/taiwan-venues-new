#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整資料提取 - 一次性到位
窮盡所有可能的資料來源和方法
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import shutil
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("完整資料提取 - 一次性到位")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.complete_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

# 完整提取函數
def extract_venue_complete(venue_id, venue_name, base_url):
    """完整提取單個場地的所有資料"""
    print(f"\n{'=' * 100}")
    print(f"完整提取: {venue_name} (ID: {venue_id})")
    print("=" * 100)

    venue = next((v for v in venues if v['id'] == venue_id), None)
    if not venue:
        print("✗ 場地未找到")
        return None

    # 1. 嘗試所有可能的URL
    possible_urls = []

    # 主頁
    possible_urls.append(('主頁', base_url))

    # 常見會議路徑
    meeting_paths = ['/meeting', '/meetings', '/banquet', '/banquets', '/conference',
                      '/event', '/events', '/wedding', '/facility', '/facilities',
                      '/會議', '/宴會', '/會議室', '/婚宴', '/活動']

    for path in meeting_paths:
        possible_urls.append((f'路徑: {path}', base_url.rstrip('/') + path))

    # 2. 爬取所有URL
    all_data = {
        'urls_tried': 0,
        'urls_success': 0,
        'meeting_rooms': [],
        'pdfs': [],
        'contact': {},
        'raw_data': []
    }

    for desc, url in possible_urls:
        print(f"\n  嘗試: {desc}")
        print(f"  URL: {url}")
        all_data['urls_tried'] += 1

        try:
            r = requests.get(url, timeout=15, verify=False, headers=headers)
            print(f"  狀態: {r.status_code}")

            if r.status_code == 200:
                all_data['urls_success'] += 1
                soup = BeautifulSoup(r.text, 'html.parser')
                page_text = soup.get_text()

                # 提取所有數據
                data = extract_all_data_from_page(soup, page_text, url)
                if data:
                    all_data['raw_data'].append(data)
                    print(f"  ✓ 提取到資料: {len(data.get('rooms', []))}個會議室, "
                          f"{len(data.get('capacities', []))}個容量, "
                          f"{len(data.get('areas', []))}個面積")

                # 尋找PDF
                pdfs = find_pdfs(soup, base_url)
                if pdfs:
                    all_data['pdfs'].extend(pdfs)
                    print(f"  ✓ 發現 {len(pdfs)} 個PDF")

            elif r.status_code == 404:
                print(f"  ✗ 404 Not Found")
            else:
                print(f"  ~ {r.status_code}")

        except Exception as e:
            print(f"  ✗ 錯誤: {e}")

    # 3. 提取聯絡資訊
    print(f"\n  提取聯絡資訊:")
    contact = extract_contact_info(all_data)
    if contact:
        all_data['contact'] = contact
        print(f"    電話: {contact.get('phone', 'N/A')}")
        print(f"    Email: {contact.get('email', 'N/A')}")

    # 4. 處理PDF
    if all_data['pdfs']:
        print(f"\n  處理 {len(all_data['pdfs'])} 個PDF:")
        for pdf_url in all_data['pdfs'][:5]:  # 最多處理5個
            print(f"    - {pdf_url}")

    return all_data

def extract_all_data_from_page(soup, page_text, url):
    """從頁面提取所有可能的會議室資料"""
    data = {
        'url': url,
        'rooms': [],
        'capacities': [],
        'areas': [],
        'prices': [],
        'floors': [],
        'features': []
    }

    # 提取會議室名稱
    room_patterns = [
        r'([^\s]{2,10}[廳室])',  # XX廳, XX室
        r'(會議室[^\s]{1,5})',  # 會議室XX
        r'([A-Z][a-z]+\s+(?:Room|Hall|Ballroom))'  # 英文會議室
    ]

    for pattern in room_patterns:
        matches = re.findall(pattern, page_text)
        for match in matches:
            if match and len(match) > 2 and match not in data['rooms']:
                data['rooms'].append(match)

    # 提取容量（所有可能的格式）
    capacity_patterns = [
        r'容量[：:]\s*(\d+)',
        r'(\d+)\s*[人名者]',
        r'可容納\s*(\d+)',
        r'適合\s*(\d+)\s*人',
        r'劇院式\s*[：:]*\s*(\d+)',
        r'教室型\s*[：:]*\s*(\d+)',
        r'宴會\s*[：:]*\s*(\d+)',
        r'U型\s*[：:]*\s*(\d+)',
    ]

    for pattern in capacity_patterns:
        matches = re.findall(pattern, page_text)
        for match in matches:
            if match.isdigit():
                cap = int(match)
                if 5 <= cap <= 5000 and cap not in data['capacities']:
                    data['capacities'].append(cap)

    # 提取面積
    area_patterns = [
        r'面積[：:]\s*(\d+|\d+\.\d+)\s*([坪平方公尺㎡])',
        r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡])',
        r'(\d+)\s*坪',
        r'(\d+)\s*㎡',
    ]

    for pattern in area_patterns:
        matches = re.findall(pattern, page_text)
        for match in matches:
            if match:
                area_str = match[0] if isinstance(match, tuple) else match
                try:
                    area = float(area_str)
                    if 5 <= area <= 10000 and area not in data['areas']:
                        data['areas'].append(area)
                except:
                    pass

    # 提取價格
    price_patterns = [
        r'(\d+,?\d*)\s*元',
        r'NT\$\s*(\d+,?\d*)',
        r'TWD\s*[：:]*\s*(\d+,?\d*)',
        r'\$?(\d+,?\d*)\s*/',
    ]

    for pattern in price_patterns:
        matches = re.findall(pattern, page_text)
        for match in matches:
            if match:
                price_str = match.replace(',', '')
                try:
                    price = int(price_str)
                    if 1000 <= price <= 500000 and price not in data['prices']:
                        data['prices'].append(price)
                except:
                    pass

    # 提取樓層
    floor_patterns = [
        r'([1-9B][F樓層])',
        r'(\d+)\s*[樓層F]',
        r'(地下\s*[1-9B]?[F樓層])',
    ]

    for pattern in floor_patterns:
        matches = re.findall(pattern, page_text)
        for match in matches:
            if match and match not in data['floors']:
                data['floors'].append(match)

    # 提取設施
    feature_keywords = ['投影', '音響', '麥克風', '白板', 'LED', '網路', 'Wi-Fi', '無線',
                       '空調', '冷氣', '桌椅', '舞台', '燈光', '隔間', '隔音']

    for keyword in feature_keywords:
        if keyword in page_text:
            data['features'].append(keyword)

    return data

def find_pdfs(soup, base_url):
    """尋找所有PDF連結"""
    pdfs = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '.pdf' in href.lower():
            if not href.startswith('http'):
                href = href if href.startswith('/') else base_url + href
            pdfs.append(href)
    return list(set(pdfs))  # 去重

def extract_contact_info(all_data):
    """從所有資料中提取聯絡資訊"""
    contact = {}

    # 從所有頁面資料中提取
    all_text = ' '.join([json.dumps(d, ensure_ascii=False) for d in all_data.get('raw_data', [])])

    # 提取電話
    phone_patterns = [
        r'0\d-?\d{3,4}-?\d{3,4}',  # 02-1234-5678, 02-12345678
        r'\+886-?\d{1,2}-?\d{3,4}-?\d{3,4}',  # +886-2-1234-5678
    ]

    for pattern in phone_patterns:
        matches = re.findall(pattern, all_text)
        if matches:
            contact['phone'] = '+886-' + matches[0][1:].replace('-', '-')
            break

    # 提取Email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, all_text)
    valid_emails = [e for e in emails if 'no-reply' not in e.lower() and 'noreply' not in e.lower()]

    if valid_emails:
        contact['email'] = valid_emails[0]

    return contact

# ============ 主程序 ============

# 要完整處理的場地
venues_to_process = [
    (1090, '茹曦酒店', 'https://www.theillumehotel.com/zh/'),
    (1095, '台北美福大飯店', 'https://www.grandmayfull.com/'),
    (1097, '台北老爺大酒店', 'https://www.hotelroyal.com.tw/zh-tw/taipei'),
    (1100, '台北花園大酒店', 'https://www.taipeigarden.com.tw/'),
    (1121, '神旺大飯店', 'https://www.sanwant.com'),
    (1124, '花園大酒店', 'https://www.taipeigarden.com.tw/'),
]

results = []

for vid, name, url in venues_to_process:
    result = extract_venue_complete(vid, name, url)
    if result:
        results.append((vid, name, result))

# 儲存結果
with open('complete_extraction_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("完整提取完成")
print("=" * 100)
print(f"處理場地: {len(venues_to_process)}")
print(f"結果已儲存: complete_extraction_results.json")
print(f"備份: {backup_file}")

# 顯示摘要
print("\n提取摘要:")
for vid, name, data in results:
    if data:
        print(f"\n{name}:")
        print(f"  嘗試URL: {data['urls_tried']}")
        print(f"  成功URL: {data['urls_success']}")
        print(f"  提取會議室: {len(data.get('rooms', []))}")
        print(f"  提取容量: {len(data.get('capacities', []))}")
        print(f"  提取面積: {len(data.get('areas', []))}")
        print(f"  提取價格: {len(data.get('prices', []))}")
        print(f"  發現PDF: {len(data.get('pdfs', []))}")
        print(f"  聯絡資訊: {data.get('contact', {})}")
