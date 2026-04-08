#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入檢查台北萬豪會議頁面
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


def check_page_for_pdfs(url, page_name):
    """檢查單一頁面的 PDF 連結"""
    print(f'\n{"=" * 80}')
    print(f'檢查: {page_name}')
    print(f'{"=" * 80}')
    print(f'URL: {url}')
    print()

    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找 PDF 連結
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

        # 查找會議室資訊
        print()
        print('頁面內容分析:')

        # 尋找會議室名稱
        room_patterns = [
            r'會議室?\w*',
            r'宴會廳',
            r'Meeting\s+Room',
            r'Ballroom',
            r'Function\s+Room'
        ]

        page_text = soup.get_text()
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

        # 尋找容量資訊
        capacity_patterns = [
            r'容量[：:]\s*(\d+)',
            r'(\d+)\s*人',
            r'可容納\s*(\d+)',
        ]

        capacities = []
        for pattern in capacity_patterns:
            matches = re.findall(pattern, page_text)
            capacities.extend([int(m) for m in matches if m.isdigit()])

        if capacities:
            unique_caps = sorted(set(capacities))[:10]
            print(f'✅ 可能的容量資訊:')
            for cap in unique_caps:
                print(f'  - {cap} 人')
        else:
            print('⚠️  未找到容量資訊')

        # 尋找價格資訊
        price_patterns = [
            r'NT\$\s*[\d,]+',
            r'[\d,]+\s*元',
            r'TWD\s*[\d,]+'
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            prices.extend(matches)

        if prices:
            unique_prices = list(set(prices))[:10]
            print(f'✅ 可能的價格資訊:')
            for price in unique_prices:
                print(f'  - {price}')
        else:
            print('⚠️  未找到價格資訊')

        return {
            'page': page_name,
            'url': url,
            'pdfs': pdf_links,
            'rooms': rooms_found[:10] if rooms_found else [],
            'capacities': capacities[:10] if capacities else [],
            'prices': prices[:10] if prices else []
        }

    except Exception as e:
        print(f'❌ 錯誤: {e}')
        return None


def main():
    print('=' * 80)
    print('深入檢查台北萬豪會議頁面')
    print('=' * 80)

    # 萬豪會議頁面
    marriott_pages = [
        ('https://www.taipeimarriott.com.tw/websev?cat=page&subcat=17', '會議&宴會頁面'),
        ('https://www.taipeimarriott.com.tw/websev?cat=page&id=39', '會議 & 宴會頁面'),
        ('https://www.taipeimarriott.com.tw/websev?cat=page&subcat=7', '婚宴頁面'),
    ]

    results = []

    for url, name in marriott_pages:
        result = check_page_for_pdfs(url, name)
        if result:
            results.append(result)

    # 儲存結果
    with open('marriott_meeting_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print('=' * 80)
    print('✅ 已儲存結果到 marriott_meeting_analysis.json')
    print('=' * 80)

    # 總結
    print()
    print('總結:')
    total_pdfs = sum(len(r.get('pdfs', [])) for r in results)
    print(f'  PDF 連結: {total_pdfs}')

    if total_pdfs == 0:
        print()
        print('⚠️  台北萬豪沒有發現 PDF 價格表')
        print('   建議方案:')
        print('   1. 聯繫飯店索取資料')
        print('   2. 檢查是否有會議室清單頁面')
        print('   3. 使用完整欄位結構，標記為「需詢問」')


if __name__ == '__main__':
    main()
