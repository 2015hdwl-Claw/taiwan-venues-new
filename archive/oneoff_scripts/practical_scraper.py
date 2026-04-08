#!/usr/bin/env python3
"""
實用爬蟲 - 不依賴複雜的頁面發現邏輯
直接抓取並解析所有可能的內容
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse

class PracticalScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def scrape_venue(self, url, venue_id):
        """直接抓取場地所有資料"""
        print(f'\n[{venue_id}] Scraping: {url}')

        try:
            # 1. 抓取首頁
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # 檢查重定向
            if response.url != url:
                print(f'  Redirected: {response.url}')

            soup = BeautifulSoup(response.text, 'html.parser')

            # 2. 提取所有連結
            all_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text().strip()
                all_links.append({
                    'url': urljoin(url, href),
                    'text': text
                })

            # 3. 尋找會議相關連結（多種關鍵字）
            meeting_keywords = [
                'meeting', 'Meeting', '會議', '會議室',
                'banquet', 'Banquet', '宴會', '婚宴',
                'conference', 'Conference', '研討會',
                'event', 'Event', '活動',
                'mice', 'MICE',
                'function', 'Function', '場地',
                'space', 'Space', '空間'
            ]

            meeting_links = []
            for link in all_links:
                # 檢查文字和URL
                combined = (link['text'] + ' ' + link['url']).lower()
                if any(kw.lower() in combined for kw in meeting_keywords):
                    # 排除明顯無關的連結
                    if not any(exclude in link['url'].lower() for exclude in ['facebook', 'instagram', 'youtube', 'linkedin']):
                        meeting_links.append(link)

            # 4. 尋找電話和Email
            phone_pattern = re.compile(r'0\d{1,2}-?\d{3,4}-?\d{4}')
            email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

            phones = phone_pattern.findall(response.text)
            emails = email_pattern.findall(response.text)

            # 5. 組織結果
            result = {
                'id': venue_id,
                'url': url,
                'final_url': response.url,
                'status_code': response.status_code,
                'total_links': len(all_links),
                'meeting_links': len(meeting_links),
                'meeting_link_details': meeting_links[:10],  # 最多10個
                'phones': list(set(phones))[:5],
                'emails': list(set(emails))[:5],
                'has_nav': soup.find('nav') is not None,
                'has_footer': soup.find('footer') is not None
            }

            # 6. 輸出結果
            print(f'  Status: {response.status_code}')
            print(f'  Total links: {result["total_links"]}')
            print(f'  Meeting links: {result["meeting_links"]}')
            print(f'  Phones found: {len(result["phones"])}')
            print(f'  Emails found: {len(result["emails"])}')

            if result['meeting_links'] > 0:
                print(f'  Meeting examples:')
                for link in meeting_links[:3]:
                    print(f'    - {link["text"][:40]}: {link["url"][:60]}')

            return result

        except Exception as e:
            print(f'  Error: {str(e)}')
            return {
                'id': venue_id,
                'url': url,
                'error': str(e),
                'meeting_links': 0
            }

# 測試
if __name__ == '__main__':
    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 找出無頁面的場地
    zero_page_venues = [
        v for v in data
        if v.get('status') != 'discontinued'
        and v.get('metadata', {}).get('pagesDiscovered', 0) == 0
        and v.get('url')
    ][:10]  # 測試前10個

    print(f'Testing {len(zero_page_venues)} zero-page venues...\n')

    scraper = PracticalScraper()
    results = []

    for venue in zero_page_venues:
        result = scraper.scrape_venue(venue['url'], venue['id'])
        results.append(result)

    # 統計
    print(f'\n{"="*60}')
    print('SUMMARY')
    print(f'{"="*60}')

    successful = [r for r in results if r.get('meeting_links', 0) > 0]
    errors = [r for r in results if 'error' in r]

    print(f'Total tested: {len(results)}')
    print(f'Success (found meeting links): {len(successful)}')
    print(f'Errors: {len(errors)}')
    print(f'Zero meeting links: {len(results) - len(successful) - len(errors)}')

    if successful:
        print(f'\n✅ Successful venues:')
        for r in successful:
            print(f'  ID {r["id"]}: {r["meeting_links"]} meeting links')

    # 儲存結果
    with open('practical_scraper_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'\nResults saved to practical_scraper_results.json')
