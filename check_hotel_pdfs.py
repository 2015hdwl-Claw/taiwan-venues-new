#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查萬豪和文華東方的 PDF 資源
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def discover_pdfs(base_url, venue_name):
    """發現網站上的 PDF 資源"""
    print(f'\n{"=" * 80}')
    print(f'檢查: {venue_name}')
    print(f'{"=" * 80}')
    print(f'URL: {base_url}')
    print()

    try:
        response = requests.get(base_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有 PDF 連結
        pdf_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(base_url, href)
                link_text = link.get_text(strip=True)
                pdf_links.append({
                    'url': full_url,
                    'text': link_text
                })

        # 顯示結果
        if pdf_links:
            print(f'✅ 找到 {len(pdf_links)} 個 PDF:')
            for i, pdf in enumerate(pdf_links, 1):
                print(f'  {i}. {pdf["text"][:50]}')
                print(f'     URL: {pdf["url"]}')
        else:
            print('⚠️  未找到 PDF 連結')

        # 尋找會議/婚宴頁面
        print()
        print('會議相關頁面:')

        meeting_keywords = ['meeting', 'banquet', 'wedding', 'mice', '會議', '婚宴', '宴會']
        meeting_pages = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()

            if any(keyword in link_text for keyword in meeting_keywords):
                full_url = urljoin(base_url, href)
                meeting_pages.append({
                    'url': full_url,
                    'text': link.get_text(strip=True)
                })

        if meeting_pages:
            print(f'✅ 找到 {len(meeting_pages)} 個會議相關頁面:')
            for i, page in enumerate(meeting_pages[:5], 1):
                print(f'  {i}. {page["text"][:40]}')
                print(f'     URL: {page["url"]}')
        else:
            print('⚠️  未找到會議相關頁面')

        return {
            'venue': venue_name,
            'base_url': base_url,
            'pdfs': pdf_links,
            'meeting_pages': meeting_pages
        }

    except Exception as e:
        print(f'❌ 錯誤: {e}')
        return None


def main():
    print('=' * 80)
    print('檢查萬豪和文華東方的 PDF 資源')
    print('=' * 80)

    # 載入 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到目標場地
    targets = [
        (1043, 'Courtyard by Marriott Taipei'),
        (1103, 'Taipei Marriott'),
        (1085, 'Mandarin Oriental Taipei')
    ]

    results = []

    for venue_id, venue_name in targets:
        venue = next((v for v in venues if v.get('id') == venue_id), None)
        if venue:
            result = discover_pdfs(venue.get('url'), venue_name)
            if result:
                results.append(result)

    # 儲存結果
    with open('hotel_pdfs_discovery.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print('=' * 80)
    print('✅ 已儲存結果到 hotel_pdfs_discovery.json')
    print('=' * 80)

    # 總結
    print()
    print('總結:')
    total_pdfs = sum(len(r.get('pdfs', [])) for r in results)
    total_meeting_pages = sum(len(r.get('meeting_pages', [])) for r in results)
    print(f'  PDF 連結: {total_pdfs}')
    print(f'  會議頁面: {total_meeting_pages}')


if __name__ == '__main__':
    main()
