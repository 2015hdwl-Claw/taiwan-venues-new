#!/usr/bin/env python3
"""
直接修正所有無頁面場地
使用實用的爬蟲方法更新 venues.json
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
from datetime import datetime

class VenueUpdater:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_venue_data(self, url):
        """提取場地資料"""
        try:
            response = self.session.get(url, timeout=15, verify=False)  # 忽略SSL錯誤
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取連結
            meeting_keywords = ['meeting', '會議', 'banquet', '宴會', 'conference', '研討會',
                              'event', '活動', 'mice', 'function', '場地', 'space', '空間']

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

            # 提取電話和Email
            phone_pattern = re.compile(r'0\d{1,2}-?\d{3,4}-?\d{4}')
            email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

            phones = list(set(phone_pattern.findall(response.text)))[:10]
            emails = list(set(email_pattern.findall(response.text)))[:10]

            # 提取捷運資訊
            mrt_stations = []
            mrt_keywords = ['捷運', 'MRT', 'mrt', '站']
            for kw in mrt_keywords:
                if kw in response.text:
                    # 找捷運站名
                    pattern = re.compile(rf'{kw}[^\s，。]+?站')
                    stations = pattern.findall(response.text)
                    mrt_stations.extend(stations[:3])

            return {
                'success': True,
                'url': url,
                'final_url': response.url,
                'pages_discovered': len(meeting_links) + 1,  # 至少算首頁
                'meeting_links': meeting_links,
                'phones': phones,
                'emails': emails,
                'mrt_stations': list(set(mrt_stations))[:3]
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'pages_discovered': 0
            }

    def update_venues(self):
        """更新所有無頁面場地"""
        # 讀取 venues.json
        with open('venues.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 找出無頁面場地
        zero_page_venues = [
            v for v in data
            if v.get('status') != 'discontinued'
            and v.get('metadata', {}).get('pagesDiscovered', 0) == 0
            and v.get('url')
        ]

        print(f'Found {len(zero_page_venues)} zero-page venues')
        print(f'Updating...\n')

        updated_count = 0
        results = []

        for venue in zero_page_venues:
            venue_id = venue['id']
            url = venue['url']
            name = venue.get('name', '')

            print(f'[{venue_id}] Processing...')

            # 提取資料
            extracted = self.extract_venue_data(url)

            if extracted['success']:
                # 更新 metadata
                if 'metadata' not in venue:
                    venue['metadata'] = {}

                old_pages = venue['metadata'].get('pagesDiscovered', 0)
                venue['metadata'].update({
                    'lastScrapedAt': datetime.now().isoformat(),
                    'scrapeVersion': 'V4-Practical',
                    'pagesDiscovered': extracted['pages_discovered'],
                    'fullSiteScraped': True
                })

                # 更新電話
                if extracted['phones'] and not venue.get('contactPhone'):
                    venue['contactPhone'] = extracted['phones'][0]

                # 更新Email
                if extracted['emails'] and not venue.get('contactEmail'):
                    venue['contactEmail'] = extracted['emails'][0]

                # 更新捷運資訊
                if extracted['mrt_stations']:
                    if 'accessInfo' not in venue:
                        venue['accessInfo'] = {}
                    if 'mrt' not in venue['accessInfo']:
                        venue['accessInfo']['mrt'] = {}
                    if not venue['accessInfo']['mrt'].get('station'):
                        venue['accessInfo']['mrt']['station'] = extracted['mrt_stations'][0]

                print(f'  OK: {old_pages} -> {extracted["pages_discovered"]} pages')
                print(f'    Meeting links: {len(extracted["meeting_links"])}')
                print(f'    Phones: {len(extracted["phones"])}')
                print(f'    Emails: {len(extracted["emails"])}')

                updated_count += 1
                results.append({
                    'id': venue_id,
                    'old_pages': old_pages,
                    'new_pages': extracted['pages_discovered'],
                    'success': True
                })
            else:
                print(f'  FAILED: {extracted.get("error", "Unknown")[:50]}')
                results.append({
                    'id': venue_id,
                    'error': extracted.get('error', 'Unknown'),
                    'success': False
                })

            print()

        # 儲存結果
        print(f'Saving changes...')

        # 備份
        backup_file = f'venues.json.backup.practical_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'Backup: {backup_file}')

        # 儲存
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f'Updated venues.json')
        print()
        print('='*60)
        print('SUMMARY')
        print('='*60)
        print(f'Total venues: {len(zero_page_venues)}')
        print(f'Successfully updated: {updated_count}')
        print(f'Failed: {len(zero_page_venues) - updated_count}')
        print()
        print(f'Success rate: {updated_count/len(zero_page_venues)*100:.1f}%')

        return results

if __name__ == '__main__':
    updater = VenueUpdater()
    results = updater.update_venues()

    # 儲存結果報告
    with open('practical_updater_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'\nResults saved to practical_updater_results.json')
