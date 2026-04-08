#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速並行爬蟲 - 一次處理多個場地
使用 V4-Practical 方法 (93.5% 成功率)
新增並行處理加速
"""
import sys
import io
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class FastParallelScraper:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_venue_data(self, venue):
        """提取單個場地資料"""
        venue_id = venue['id']
        url = venue['url']
        name = venue.get('name', '')

        try:
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 會議關鍵字
            meeting_keywords = ['meeting', '會議', 'banquet', '宴會', 'conference', '研討會',
                              'event', '活動', 'mice', 'function', '場地', 'space', '空間']

            # 提取所有連結
            all_links = soup.find_all('a', href=True)
            meeting_links = []

            for a in all_links:
                href = a['href']
                text = a.get_text().strip()
                combined = (text + ' ' + href).lower()

                if any(kw.lower() in combined for kw in meeting_keywords):
                    full_url = urljoin(url, href)
                    meeting_links.append({
                        'text': text,
                        'url': full_url
                    })

            # 提取電話和Email - 增強版 (Phase 2)
            # 電話模式 - 支援多種格式
            phone_patterns = [
                r'0\d[\d-]{7,9}',           # 02-1234-5678, 0212345678
                r'\+886-[\d-]+',            # +886-2-1234-5678
                r'\+886\s?\d[\d-]{7,9}',    # +886 2 12345678
                r'0\d-\d{3,4}-\d{3,4}',     # 02-3366-4504
                r'0\d{2,4}-?\d{3,4}-?\d{3,4}', # 更靈活的格式
            ]

            # Email 模式 - 加入垃圾郵件過濾
            email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
            spam_keywords = ['no-reply', 'noreply', 'donotreply', '@spam', '@test', '@example', 'info@']

            phones = []
            emails = []

            # 嘗試所有電話模式
            for pattern in phone_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    # 過濾：至少要有 7 位數字
                    valid_phones = [m for m in matches if len(re.sub(r'[\D]', '', m)) >= 7]
                    phones.extend(valid_phones)

            # 去重並限制數量
            phones = list(set(phones))[:10]

            # 提取 Email 並過濾垃圾郵件
            email_matches = email_pattern.findall(response.text)
            for email in email_matches:
                email_lower = email.lower()
                # 過濾垃圾郵件
                if not any(spam in email_lower for spam in spam_keywords):
                    emails.append(email)

            # 去重並限制數量
            emails = list(set(emails))[:10]

            # 提取捷運資訊
            mrt_stations = []
            mrt_keywords = ['捷運', 'MRT', 'mrt', '站']
            for kw in mrt_keywords:
                if kw in response.text:
                    pattern = re.compile(rf'{kw}[^\s，。]+?站')
                    stations = pattern.findall(response.text)
                    mrt_stations.extend(stations[:3])

            return {
                'success': True,
                'id': venue_id,
                'name': name,
                'url': url,
                'final_url': response.url,
                'pages_discovered': len(meeting_links) + 1,
                'meeting_links': meeting_links,
                'phones': phones,
                'emails': emails,
                'mrt_stations': list(set(mrt_stations))[:3]
            }

        except Exception as e:
            return {
                'success': False,
                'id': venue_id,
                'name': name,
                'error': str(e),
                'pages_discovered': 0
            }

    def process_venues(self, venues):
        """並行處理多個場地"""
        results = []
        start_time = time.time()

        print(f'並行處理 {len(venues)} 個場地 (threads: {self.max_workers})')
        print('='*60)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            future_to_venue = {
                executor.submit(self.extract_venue_data, venue): venue
                for venue in venues
            }

            # 處理完成的任務
            for future in as_completed(future_to_venue):
                result = future.result()
                results.append(result)

                if result['success']:
                    name_safe = result["name"][:25].encode('ascii', 'ignore').decode('ascii', 'ignore')
                    print(f'[{result["id"]}] {name_safe:25} OK: {result["pages_discovered"]} pages')
                else:
                    name_safe = result["name"][:25].encode('ascii', 'ignore').decode('ascii', 'ignore')
                    error_msg = result.get('error', 'Unknown')[:35].encode('ascii', 'ignore').decode('ascii', 'ignore')
                    print(f'[{result["id"]}] {name_safe:25} FAILED: {error_msg}')

        elapsed = time.time() - start_time
        print('='*60)
        print(f'Completed! Time: {elapsed:.1f}s (Avg: {elapsed/len(venues):.1f}s/venue)')

        return results

    def update_venues_file(self, results, venues_data):
        """更新 venues.json"""
        updated_count = 0

        for result in results:
            if not result['success']:
                continue

            # 找到對應的場地
            venue = next((v for v in venues_data if v['id'] == result['id']), None)
            if not venue:
                continue

            # 更新 metadata
            if 'metadata' not in venue:
                venue['metadata'] = {}

            old_pages = venue['metadata'].get('pagesDiscovered', 0)
            venue['metadata'].update({
                'lastScrapedAt': datetime.now().isoformat(),
                'scrapeVersion': 'Fast-Parallel',
                'pagesDiscovered': result['pages_discovered'],
                'fullSiteScraped': True
            })

            # 更新電話
            if result['phones'] and not venue.get('contactPhone'):
                venue['contactPhone'] = result['phones'][0]

            # 更新Email
            if result['emails'] and not venue.get('contactEmail'):
                venue['contactEmail'] = result['emails'][0]

            # 更新捷運資訊
            if result['mrt_stations']:
                if 'accessInfo' not in venue:
                    venue['accessInfo'] = {}
                if 'mrt' not in venue['accessInfo']:
                    venue['accessInfo']['mrt'] = {}
                if not venue['accessInfo']['mrt'].get('station'):
                    venue['accessInfo']['mrt']['station'] = result['mrt_stations'][0]

            updated_count += 1

        return updated_count

def main():
    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 找出需要更新的場地
    # 選擇條件: 未爬取 或 頁面數少於5
    target_venues = [
        v for v in data
        if v.get('status') != 'discontinued'
        and v.get('url')
        and (
            v.get('metadata', {}).get('pagesDiscovered', 0) == 0
            or v.get('metadata', {}).get('pagesDiscovered', 0) < 5
        )
    ]

    print(f'找到 {len(target_venues)} 個需要更新的場地')

    if not target_venues:
        print('沒有需要更新的場地!')
        return

    # 並行爬取
    scraper = FastParallelScraper(max_workers=8)  # 8個並行
    results = scraper.process_venues(target_venues)

    # 更新資料
    print('\n更新 venues.json...')
    updated_count = scraper.update_venues_file(results, data)

    # 備份與儲存
    backup_file = f'venues.json.backup.parallel_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'備份: {backup_file}')
    print(f'已更新 {updated_count} 個場地')

    # 統計
    successful = sum(1 for r in results if r['success'])
    print('\n' + '='*60)
    print('統計摘要')
    print('='*60)
    print(f'總共處理: {len(results)}')
    print(f'成功: {successful}')
    print(f'失敗: {len(results) - successful}')
    print(f'成功率: {successful/len(results)*100:.1f}%')

    # 儲存結果報告
    with open('parallel_scraper_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print('結果已儲存到 parallel_scraper_results.json')

if __name__ == '__main__':
    main()
