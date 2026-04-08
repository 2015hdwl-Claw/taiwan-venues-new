#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速檢查萬豪和文華東方的價格資訊
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import json
import re

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_venue_price_info(name, url):
    """檢查場地是否有價格資訊"""
    print(f'檢查: {name}')
    print(f'URL: {url}')

    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 尋找價格資訊
        price_pattern = r'[nN][tT]\$?\s*[\d,]+|[\d,]+\s*元|USD?\s*[\d,]+'
        prices = re.findall(price_pattern, page_text)

        # 尋找會議室/活動相關頁面
        meeting_keywords = ['meeting', 'event', 'conference', 'banquet', 'wedding', '會議', '宴會']
        meeting_links = []

        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            text = a.get_text().lower()
            if any(keyword in href or keyword in text for keyword in meeting_keywords):
                meeting_links.append({
                    'text': a.get_text(strip=True)[:50],
                    'href': a['href']
                })

        return {
            'name': name,
            'url': url,
            'has_price': len(prices) > 0,
            'price_count': len(prices),
            'sample_prices': prices[:5],
            'meeting_links_count': len(meeting_links),
            'sample_links': meeting_links[:5]
        }

    except Exception as e:
        return {
            'name': name,
            'url': url,
            'error': str(e)
        }


def main():
    print('=' * 80)
    print('快速檢查萬豪和文華東方')
    print('=' * 80)
    print()

    venues = [
        {'name': '台北萬豪酒店', 'url': 'https://www.taipeimarriott.com.tw/'},
        {'name': '台北文華東方酒店', 'url': 'https://www.mandarinoriental.com/taipei'}
    ]

    results = []

    for venue in venues:
        result = check_venue_price_info(venue['name'], venue['url'])
        results.append(result)

        if 'error' in result:
            print(f'  ❌ 錯誤: {result["error"]}')
        else:
            print(f'  價格資訊: {"✅ " + str(result["price_count"]) + " 個" if result["has_price"] else "❌ 無"}')
            if result['has_price']:
                print(f'    範例: {result["sample_prices"][:3]}')
            print(f'  會議/活動連結: {result["meeting_links_count"]} 個')
            if result["sample_links"]:
                print(f'    範例:')
                for link in result["sample_links"][:3]:
                    print(f'      - {link["text"]}')

        print()

    # 儲存結果
    with open('marriott_moh_check.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print('✅ 結果已儲存到 marriott_moh_check.json')

    # 總結
    print()
    print('=' * 80)
    print('總結:')
    print('=' * 80)
    print()

    has_price = sum(1 for r in results if r.get('has_price', False))
    print(f'有價格資訊: {has_price}/{len(results)}')

    if has_price == 0:
        print()
        print('⚠️  這些場地都沒有在首頁顯示價格')
        print('可能原因:')
        print('  1. 價格在會議室詳細頁面中')
        print('  2. 價格在 PDF 文件中')
        print('  3. 需要聯絡詢問')
        print()
        print('建議: 標記為「需聯絡詢問」或「需要深度爬取」')


if __name__ == '__main__':
    main()
