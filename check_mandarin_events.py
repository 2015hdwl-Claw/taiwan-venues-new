#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入檢查文華東方 Events 頁面
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_events_page():
    """檢查文華東方 Events 頁面"""
    url = 'https://www.mandarinoriental.com/en/taipei/songshan/events'

    print('=' * 80)
    print('檢查: 文華東方 Events 頁面')
    print('=' * 80)
    print(f'URL: {url}')
    print()

    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找 PDF 連結
        print('[1/3] 查找 PDF 連結...')
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(url, href)
                link_text = link.get_text(strip=True)
                pdf_links.append({
                    'url': full_url,
                    'text': link_text
                })

        if pdf_links:
            print(f'✅ 找到 {len(pdf_links)} 個 PDF:')
            for pdf in pdf_links:
                print(f'  - {pdf["text"][:60]}')
                print(f'    {pdf["url"]}')
        else:
            print('⚠️  未找到 PDF 連結')

        print()

        # 分析頁面內容
        print('[2/3] 分析頁面內容...')
        page_text = soup.get_text()

        # 尋找會議室名稱
        room_patterns = [
            r'Ballroom',
            r'Meeting\s+Room',
            r'Function\s+Room',
            r'宴會廳',
            r'會議室'
        ]

        rooms_found = []
        for pattern in room_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            rooms_found.extend(matches)

        if rooms_found:
            unique_rooms = list(set(rooms_found))[:10]
            print(f'✅ 可能的會議室名稱:')
            for room in unique_rooms:
                print(f'  - {room}')
        else:
            print('⚠️  未找到明顯的會議室名稱')

        print()

        # 尋找容量資訊
        capacity_patterns = [
            r'capacity[：:]\s*(\d+)',
            r'(\d+)\s*people?',
            r'(\d+)\s*guests?',
            r'(\d+)\s*人',
        ]

        capacities = []
        for pattern in capacity_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            capacities.extend([int(m) for m in matches if m.isdigit()])

        if capacities:
            unique_caps = sorted(set(capacities))[:10]
            print(f'✅ 可能的容量資訊:')
            for cap in unique_caps:
                print(f'  - {cap} 人/people')
        else:
            print('⚠️  未找到容量資訊')

        print()

        # 尋找聯絡資訊
        print('[3/3] 尋找聯絡資訊...')

        # Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, page_text)

        if emails:
            print(f'✅ Email: {emails[0]}')
        else:
            print('⚠️  未找到 Email')

        # Phone
        phone_patterns = [
            r'\+886-[\d-]+',
            r'\+886\s?\d[\d-]{7,9}',
            r'0\d[\d-]{7,9}'
        ]

        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, page_text)
            phones.extend(matches)

        if phones:
            print(f'✅ Phone: {phones[0]}')
        else:
            print('⚠️  未找到電話')

        print()
        print('=' * 80)
        print('總結:')
        print('=' * 80)
        print(f'PDF 連結: {len(pdf_links)}')
        print(f'會議室名稱: {len(rooms_found)}')
        print(f'容量資訊: {len(capacities)}')
        print(f'聯絡資訊: {"有" if emails or phones else "無"}')
        print()

        if len(pdf_links) == 0:
            print('⚠️  文華東方沒有提供 PDF 價格表')
            print()
            print('建議方案:')
            print('1. 標記為「需詢問」')
            print('2. 使用完整欄位結構，所有欄位設為 NULL')
            print('3. 聯絡資訊已更新，可直接詢問')
            print()
            if emails or phones:
                print('聯絡方式:')
                if emails:
                    print(f'  Email: {emails[0]}')
                if phones:
                    print(f'  Phone: {phones[0]}')

        return {
            'pdfs': pdf_links,
            'rooms': rooms_found[:10],
            'capacities': capacities[:10],
            'contact': {
                'email': emails[0] if emails else None,
                'phone': phones[0] if phones else None
            }
        }

    except Exception as e:
        print(f'❌ 錯誤: {e}')
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    result = check_events_page()

    # 儲存結果
    with open('mandarin_events_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
