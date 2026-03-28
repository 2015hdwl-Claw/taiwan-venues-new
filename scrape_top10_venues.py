#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Top 10 場地專用爬蟲

針對技術檢測結果，使用不同的爬蟲策略
"""

import sys
import io
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class Top10Scraper:
    """Top 10 場地專用爬蟲"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_venue(self, venue_id, venue_name, venue_url, site_type):
        """爬取單一場地"""
        print(f'\n{"="*70}')
        print(f'場地 [{venue_id}] {venue_name[:40]}')
        print(f'URL: {venue_url}')
        print(f'類型: {site_type}')
        print("="*70)

        result = {
            'id': venue_id,
            'name': venue_name,
            'url': venue_url,
            'site_type': site_type,
            'success': False,
            'rooms_processed': 0,
            'rooms_enhanced': 0,
            'issues': []
        }

        try:
            # [1級] 爬取主頁
            print('[1/3] 爬取主頁...')
            response = self.session.get(venue_url, timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            homepage_text = soup.get_text()

            print(f'      頁面長度: {len(homepage_text)} 字元')

            # [2級] 發現並爬取會議頁/詳情頁
            print('[2/3] 發現會議頁/詳情頁...')

            if site_type == 'WordPress':
                # WordPress 需要特殊處理
                rooms = self._extract_wordpress_rooms(soup, venue_url)
            elif site_type == 'JavaScript/SPA':
                # JavaScript 動態載入，只能提取主頁資料
                rooms = self._extract_static_rooms(soup)
            else:
                # Static HTML
                rooms = self._extract_static_rooms(soup)

            print(f'      發現會議室: {len(rooms)} 個')

            # [3級] 提取會議室詳情
            print('[3/3] 提取會議室資料...')

            enhanced_rooms = []
            for room in rooms:
                enhanced_room = self._extract_room_details(room, soup)
                enhanced_rooms.append(enhanced_room)

                if enhanced_room.get('capacity') or enhanced_room.get('area'):
                    result['rooms_enhanced'] += 1

            result['rooms_processed'] = len(rooms)
            result['success'] = True

            print(f'      處理會議室: {len(rooms)} 個')
            print(f'      成功補強: {result["rooms_enhanced"]} 個')

            # 寫入 venues.json
            self._update_venues_json(venue_id, enhanced_rooms, site_type)
            print('      ✅ 已更新 venues.json')

        except requests.exceptions.Timeout:
            result['issues'].append('連線超時')
            print('      ❌ 連線超時')

        except requests.exceptions.ConnectionError:
            result['issues'].append('無法連線')
            print('      ❌ 無法連線')

        except Exception as e:
            result['issues'].append(str(e)[:100])
            print(f'      ❌ 錯誤: {str(e)[:100]}')

        return result

    def _extract_wordpress_rooms(self, soup, base_url):
        """提取 WordPress 網站的會議室"""
        rooms = []

        # WordPress 通常有特定的結構
        # 尋找會議室/宴會廳相關的頁面
        room_links = soup.find_all('a', href=True)

        for link in room_links:
            href = link['href']
            text = link.get_text(strip=True)

            # 尋找包含會議室關鍵字的連結
            keywords = ['會議室', '宴會廳', '會議', 'Meeting', 'Banquet', 'Room']
            if any(kw in text for kw in keywords) and len(text) > 2 and len(text) < 50:
                rooms.append({
                    'name': text,
                    'url': urljoin(base_url, href),
                    'source': 'wordpress_link'
                })

        # 去重
        seen = set()
        unique_rooms = []
        for room in rooms:
            if room['name'] not in seen:
                seen.add(room['name'])
                unique_rooms.append(room)

        return unique_rooms[:20]  # 限制最多 20 個

    def _extract_static_rooms(self, soup):
        """提取靜態 HTML 的會議室"""
        rooms = []

        # 尋找會議室相關的標題
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])

        for heading in headings:
            text = heading.get_text(strip=True)
            keywords = ['廳', '室', '會議', '宴會', '空間']

            if any(kw in text for kw in keywords) and len(text) > 2 and len(text) < 50:
                rooms.append({
                    'name': text,
                    'source': 'static_heading'
                })

        return rooms[:20]

    def _extract_room_details(self, room, soup):
        """提取會議室詳細資料"""
        page_text = soup.get_text()

        # 提取容量
        capacity = None
        import re
        capacity_patterns = [
            r'容量[：:]?\s*(\d+)\s*人',
            r'可容納\s*(\d+)\s*人',
            r'(\d{2,4})\s*[人名]',
        ]

        for pattern in capacity_patterns:
            match = re.search(pattern, page_text)
            if match:
                try:
                    capacity = int(match.group(1))
                    break
                except ValueError:
                    continue

        # 提取面積
        area = None
        area_patterns = [
            r'(\d+\.?\d*)\s*坪',
            r'(\d+\.?\d*)\s*平方公尺',
            r'(\d+\.?\d*)\s*㎡',
        ]

        for pattern in area_patterns:
            match = re.search(pattern, page_text)
            if match:
                try:
                    area = float(match.group(1))
                    break
                except ValueError:
                    continue

        # 提取價格
        price = None
        price_patterns = [
            r'NT\$\s*([\d,]+)',
            r'([\d,]+)\s*元',
            r'價格[：:]?\s*NT\$\s*([\d,]+)',
        ]

        for pattern in price_patterns:
            match = re.search(pattern, page_text)
            if match:
                try:
                    price = int(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue

        return {
            'name': room.get('name', ''),
            'capacity': capacity,
            'area': area,
            'price': price,
            'equipment': None,
            'images': None
        }

    def _update_venues_json(self, venue_id, enhanced_rooms, site_type):
        """更新 venues.json"""
        with open('venues.json', 'r', encoding='utf-8') as f:
            venues = json.load(f)

        # 找到對應場地
        for venue in venues:
            if venue['id'] == venue_id:
                # 更新會議室資料
                existing_rooms = venue.get('rooms', [])

                # 合併資料（保留原有，補充新資料）
                updated_rooms = []
                for existing_room in existing_rooms:
                    room_name = existing_room.get('name', '')
                    # 從 enhanced_rooms 中找匹配的
                    for enhanced in enhanced_rooms:
                        if enhanced['name'] in room_name or room_name in enhanced['name']:
                            # 合併
                            merged_room = existing_room.copy()
                            if enhanced.get('capacity') and not merged_room.get('capacity'):
                                merged_room['capacity'] = enhanced['capacity']
                            if enhanced.get('area') and not merged_room.get('area'):
                                merged_room['area'] = enhanced['area']
                            if enhanced.get('price') and not merged_room.get('price'):
                                merged_room['price'] = enhanced['price']
                            updated_rooms.append(merged_room)
                            break
                    else:
                        updated_rooms.append(existing_room)

                venue['rooms'] = updated_rooms

                # 更新 metadata
                if 'metadata' not in venue:
                    venue['metadata'] = {}
                venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
                venue['metadata']['scrapeVersion'] = f'Top10_Scraper_{site_type}'
                venue['metadata']['scrapeConfidenceScore'] = 70
                venue['metadata']['techDetection'] = site_type

                break

        # 寫回檔案
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)


def main():
    # Top 10 場地（只處理能夠連線的 7 個）
    top10 = [
        {'id': 1493, 'name': '師大進修推廣學院', 'url': 'https://www.sce.ntnu.edu.tw/home/index.php', 'type': 'JavaScript/SPA'},
        {'id': 1053, 'name': '台北兄弟大飯店', 'url': 'https://www.brotherhotel.com.tw/?cat=75', 'type': 'WordPress'},
        {'id': 1122, 'name': '維多麗亞酒店', 'url': 'https://www.grandvictoria.com.tw/', 'type': 'WordPress'},
        {'id': 1129, 'name': '青青婚宴會館', 'url': 'https://www.77-67.com/', 'type': 'WordPress'},
        {'id': 1049, 'name': '台北世貿中心', 'url': 'https://www.twtc.com.tw/', 'type': 'JavaScript/SPA'},
        {'id': 1103, 'name': '台北萬豪酒店', 'url': 'https://www.taipeimarriott.com.tw/', 'type': 'JavaScript/SPA'},
        {'id': 1128, 'name': '集思台大會議中心', 'url': 'https://www.meeting.com.tw/ntu/', 'type': 'Static HTML'}
    ]

    print('=' * 80)
    print('Top 10 場地深度爬蟲')
    print('=' * 80)
    print(f'處理場地數: {len(top10)}')
    print()

    scraper = Top10Scraper()
    results = []

    for i, venue in enumerate(top10, 1):
        print(f'\n{"="*80}')
        print(f'進度: [{i}/{len(top10)}]')
        print("="*80)

        result = scraper.scrape_venue(
            venue['id'],
            venue['name'],
            venue['url'],
            venue['type']
        )
        results.append(result)

    # 生成報告
    print('\n' + '=' * 80)
    print('處理結果總結')
    print('=' * 80)
    print()

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f'成功: {len(successful)}/{len(results)}')
    print(f'失敗: {len(failed)}/{len(results)}')
    print()

    total_rooms = sum(r['rooms_processed'] for r in results)
    total_enhanced = sum(r['rooms_enhanced'] for r in results)

    print(f'總處理會議室: {total_rooms} 個')
    print(f'成功補強: {total_enhanced} 個')
    print(f'補強率: {total_enhanced/total_rooms*100:.1f}%' if total_rooms > 0 else '')
    print()

    # 詳細結果
    print('=' * 80)
    print('詳細結果')
    print('=' * 80)
    print()

    for result in results:
        status = '✅' if result['success'] else '❌'
        print(f"{status} [{result['id']}] {result['name'][:40]}")
        print(f"   會議室: {result['rooms_processed']} | 補強: {result['rooms_enhanced']}")
        if result['issues']:
            print(f"   問題: {', '.join(result['issues'])}")
        print()


if __name__ == '__main__':
    main()
