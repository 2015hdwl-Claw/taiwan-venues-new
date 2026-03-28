#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入檢查台北世貿中心的會議室頁面
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('台北世貿中心 - 深度檢查')
    print('=' * 80)
    print()

    base_url = 'https://www.twtc.com.tw/'

    print('[1/4] 訪問首頁...')
    try:
        response = requests.get(base_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        print(f'✅ 成功訪問: {base_url}')
        print()

        # 尋找會議室相關連結
        print('[2/4] 尋找會議室相關連結...')
        meeting_links = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)

            # 尋找包含關鍵字的連結
            keywords = ['會議', 'meeting', '會場', 'space', '租借', 'rent']
            if any(keyword in text.lower() or keyword in href.lower() for keyword in keywords):
                full_url = urljoin(base_url, href)
                meeting_links.append({
                    'text': text,
                    'url': full_url
                })

        # 去重
        seen_urls = set()
        unique_links = []
        for link in meeting_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)

        print(f'找到 {len(unique_links)} 個會議室相關連結:')
        for i, link in enumerate(unique_links[:10], 1):  # 只顯示前 10 個
            print(f'  {i}. {link["text"][:50]}')
            print(f'     {link["url"]}')

        print()

        # 檢查第一個會議室頁面
        if unique_links:
            print('[3/4] 檢查會議室頁面...')
            meeting_url = unique_links[0]['url']
            print(f'訪問: {meeting_url}')

            try:
                meeting_response = requests.get(meeting_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                meeting_response.raise_for_status()
                meeting_soup = BeautifulSoup(meeting_response.text, 'html.parser')

                # 尋找 PDF
                pdf_links = []
                for a in meeting_soup.find_all('a', href=True):
                    href = a['href'].lower()
                    if href.endswith('.pdf'):
                        full_pdf_url = urljoin(meeting_url, a['href'])
                        pdf_links.append({
                            'text': a.get_text(strip=True),
                            'url': full_pdf_url
                        })

                if pdf_links:
                    print(f'✅ 找到 {len(pdf_links)} 個 PDF 連結:')
                    for pdf in pdf_links:
                        print(f'  - {pdf["text"]}')
                        print(f'    {pdf["url"]}')
                else:
                    print('⚠️  未找到 PDF 連結')

                # 尋找價格資訊
                print()
                print('[4/4] 尋找價格資訊...')

                price_keywords = ['價格', '租金', '收費', '費用', 'nt$', 'ntd', '元']
                page_text = meeting_soup.get_text().lower()

                found_prices = []
                for keyword in price_keywords:
                    if keyword in page_text:
                        found_prices.append(keyword)

                if found_prices:
                    print(f'✅ 頁面包含價格相關關鍵字: {", ".join(found_prices)}')

                    # 嘗試提取價格資訊
                    import re
                    price_pattern = r'nt\$?\s*[\d,]+|\d+\s*元'
                    prices = re.findall(price_pattern, meeting_soup.get_text(), re.IGNORECASE)

                    if prices:
                        print(f'找到 {len(prices)} 個價格資訊（顯示前 5 個）:')
                        for price in prices[:5]:
                            print(f'  - {price}')
                else:
                    print('⚠️  未找到價格資訊')

                # 尋找會議室詳細頁面連結
                print()
                print('[尋找會議室詳細頁面]')

                detail_links = []
                for a in meeting_soup.find_all('a', href=True):
                    href = a['href']
                    text = a.get_text(strip=True)

                    # 尋找會議室名稱（如：第一會議室）
                    if any(keyword in text for keyword in ['會議室', '廳', 'Room']):
                        full_url = urljoin(meeting_url, href)
                        # 避免重複
                        if full_url not in [link['url'] for link in detail_links]:
                            detail_links.append({
                                'name': text,
                                'url': full_url
                            })

                if detail_links:
                    print(f'找到 {len(detail_links)} 個會議室詳細頁:')
                    for i, link in enumerate(detail_links[:5], 1):
                        print(f'  {i}. {link["name"]}')
                        print(f'     {link["url"]}')

                # 儲存結果
                result = {
                    'base_url': base_url,
                    'meeting_links': unique_links[:10],
                    'pdf_links': pdf_links,
                    'detail_links': detail_links[:10]
                }

                import json
                with open('twtc_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print()
                print('✅ 分析結果已儲存到 twtc_analysis.json')

            except Exception as e:
                print(f'❌ 無法訪問會議室頁面: {e}')

        else:
            print('⚠️  未找到會議室相關連結')

    except Exception as e:
        print(f'❌ 錯誤: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
