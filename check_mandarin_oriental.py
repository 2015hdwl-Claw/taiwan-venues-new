#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入檢查文華東方的會議資源
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


def check_mandarin_oriental():
    """檢查文華東方官網"""
    url = 'https://www.mandarinoriental.com/taipei'

    print('=' * 80)
    print('檢查: 文華東方')
    print('=' * 80)
    print(f'URL: {url}')
    print()

    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找 PDF 連結
        print('[1/4] 查找 PDF 連結...')
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

        # 查找會議/婚宴頁面
        print('[2/4] 查找會議相關頁面...')
        meeting_keywords = ['meeting', 'banquet', 'wedding', 'event', 'conference', '會議', '婚宴', '活動']
        meeting_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()

            # 檢查連結文字和 URL
            if any(keyword in link_text for keyword in meeting_keywords) or \
               any(keyword in href.lower() for keyword in meeting_keywords):
                full_url = urljoin(url, href)
                meeting_links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True)
                })

        if meeting_links:
            print(f'✅ 找到 {len(meeting_links)} 個會議相關連結:')
            for link in meeting_links[:10]:
                print(f'  - {link["text"][:50]}')
                print(f'    {link["url"]}')
        else:
            print('⚠️  未找到會議相關連結')

        print()

        # 嘗試常見的會議頁面 URL 模式
        print('[3/4] 嘗試常見 URL 模式...')
        common_paths = [
            '/meetings',
            '/weddings',
            '/events',
            '/banquet',
            '/conference',
            '/taipei/meetings',
            '/taipei/weddings',
            '/taipei/events'
        ]

        for path in common_paths:
            test_url = urljoin(url, path)
            try:
                test_response = requests.head(test_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                if test_response.status_code == 200:
                    print(f'  ✅ {test_url}')
            except:
                pass

        print()

        # 分析頁面內容
        print('[4/4] 分析首頁內容...')
        page_text = soup.get_text()

        # 尋找關鍵詞
        keywords_found = []
        search_keywords = ['meeting room', 'ballroom', 'conference', 'event', 'banquet', 'wedding',
                          '會議室', '宴會廳', '會議', '婚宴', '活動']

        for keyword in search_keywords:
            if keyword.lower() in page_text.lower():
                keywords_found.append(keyword)

        if keywords_found:
            print(f'✅ 找到關鍵詞: {", ".join(keywords_found[:10])}')
        else:
            print('⚠️  未找到明顯的會議關鍵詞')

        print()
        print('=' * 80)
        print('總結:')
        print('=' * 80)
        print(f'PDF 連結: {len(pdf_links)}')
        print(f'會議連結: {len(meeting_links)}')
        print()

        if len(pdf_links) == 0 and len(meeting_links) == 0:
            print('⚠️  文華東方沒有明顯的會議資料')
            print()
            print('建議方案:')
            print('1. 聯繫飯店索取會議室資料')
            print('2. 使用完整欄位結構，標記為「需詢問」')
            print('3. 定期重新檢查官網更新')
        else:
            print('✅ 發現潛在資料來源，建議進一步分析')

        return {
            'pdfs': pdf_links,
            'meeting_links': meeting_links,
            'keywords': keywords_found
        }

    except Exception as e:
        print(f'❌ 錯誤: {e}')
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    result = check_mandarin_oriental()

    # 儲存結果
    with open('mandarin_oriental_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
