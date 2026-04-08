#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全站智能爬蟲 V4 - Full Site Intelligent Scraper
=================================================

核心功能：
1. ✅ 全站爬取（不僅是首頁）
2. ✅ 頁面發現（導航、Footer、URL 模式）
3. ✅ 頁面分類（會議、交通、規則、照片）
4. ✅ 智能提取（會議室、尺寸、容量、設備）
5. ✅ 避免重複處理（檢查 lastScrapedAt）

使用方式：
    python full_site_scraper_v4.py --test 1043
    python full_site_scraper_v4.py --batch --sample 5
    python full_site_scraper_v4.py --report
"""

import json
import sys
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
from collections import defaultdict

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scrapling.fetchers import Fetcher, StealthyFetcher


@dataclass
class PageInfo:
    """頁面資訊"""
    url: str
    page_type: str  # meeting, access, contact, policy, gallery, other
    source: str     # navigation, footer, url_pattern, discovered
    title: str = ""
    content: str = ""

    def to_dict(self):
        return asdict(self)


class PageDiscoverer:
    """頁面發現器 - 找出官網所有相關頁面"""

    def __init__(self):
        self.visited_urls = set()

    def discover_all(self, base_url: str, max_pages: int = 30) -> List[PageInfo]:
        """發現所有相關頁面"""
        print(f"🔍 開始發現頁面: {base_url}")

        discovered_pages = []

        try:
            # 1. 抓取首頁
            print(f"   → 抓取首頁...")
            page = Fetcher.get(base_url, impersonate='chrome', timeout=15)
            self.visited_urls.add(base_url)

            # 2. 從導航列發現
            nav_pages = self._discover_from_navigation(page, base_url)
            print(f"   → 導航列發現: {len(nav_pages)} 個頁面")
            discovered_pages.extend(nav_pages)

            # 3. 從 Footer 發現
            footer_pages = self._discover_from_footer(page, base_url)
            print(f"   → Footer 發現: {len(footer_pages)} 個頁面")
            discovered_pages.extend(footer_pages)

            # 4. URL 模式猜測
            guessed_pages = self._discover_by_url_pattern(base_url)
            print(f"   → URL 模式猜測: {len(guessed_pages)} 個頁面")
            discovered_pages.extend(guessed_pages)

        except Exception as e:
            print(f"   ❌ 錯誤: {str(e)[:50]}")

        # 去重
        unique_pages = self._deduplicate_pages(discovered_pages)
        print(f"   ✅ 共發現 {len(unique_pages)} 個唯一頁面")

        return unique_pages[:max_pages]

    def _discover_from_navigation(self, page, base_url: str) -> List[PageInfo]:
        """從導航列發現頁面"""
        pages = []

        # 導航關鍵字對應的頁面類型
        nav_keywords = {
            'meeting': ['會議', '宴會', '會議室', 'Meeting', 'Banquet', 'Events', 'MICE'],
            'access': ['交通', '位置', '交通資訊', 'Access', 'Location', 'Traffic', 'Map'],
            'contact': ['聯絡', '聯絡我們', 'Contact', 'Contact Us'],
            'policy': ['規則', '政策', '注意事項', 'Policy', 'Terms', 'Rules'],
            'gallery': ['照片', '圖片', '媒體', 'Gallery', 'Photos', 'Images'],
        }

        # 查找導航連結
        nav_selectors = [
            'nav a::attr(href)',
            '.navigation a::attr(href)',
            '.menu a::attr(href)',
            '.nav a::attr(href)',
            'header a::attr(href)',
        ]

        for selector in nav_selectors:
            try:
                links = page.css(selector).getall()
                for link in links:
                    if link in self.visited_urls:
                        continue

                    # 取得連結文字
                    link_text = self._get_link_text(page, link)

                    # 判斷頁面類型
                    page_type = self._classify_by_text(link_text, nav_keywords)

                    if page_type:
                        absolute_url = self._to_absolute_url(link, base_url)
                        if absolute_url and absolute_url not in self.visited_urls:
                            pages.append(PageInfo(
                                url=absolute_url,
                                page_type=page_type,
                                source='navigation',
                                title=link_text
                            ))
                            self.visited_urls.add(absolute_url)
            except:
                continue

        return pages

    def _discover_from_footer(self, page, base_url: str) -> List[PageInfo]:
        """從 Footer 發現頁面"""
        pages = []

        try:
            footer_links = page.css('footer a::attr(href)').getall()

            for link in footer_links:
                if link in self.visited_urls:
                    continue

                link_text = self._get_link_text(page, link)

                # Footer 常見類型
                if any(kw in link_text for kw in ['交通', '位置', '聯絡', '聯繫']):
                    absolute_url = self._to_absolute_url(link, base_url)
                    if absolute_url:
                        pages.append(PageInfo(
                            url=absolute_url,
                            page_type='unknown',
                            source='footer',
                            title=link_text
                        ))
                        self.visited_urls.add(absolute_url)
        except:
            pass

        return pages

    def _discover_by_url_pattern(self, base_url: str) -> List[PageInfo]:
        """根據 URL 模式猜測頁面"""
        pages = []

        common_patterns = {
            '/meeting': 'meeting',
            '/meetings': 'meeting',
            '/banquet': 'meeting',
            '/banquets': 'meeting',
            '/events': 'meeting',
            '/mice': 'meeting',
            '/conference': 'meeting',
            '/access': 'access',
            '/location': 'access',
            '/traffic': 'access',
            '/transport': 'access',
            '/contact': 'contact',
            '/contact-us': 'contact',
            '/policy': 'policy',
            '/terms': 'policy',
            '/rules': 'policy',
            '/gallery': 'gallery',
            '/photos': 'gallery',
            '/media': 'gallery',
        }

        base_domain = base_url.rstrip('/')

        for pattern, page_type in common_patterns.items():
            guessed_url = base_domain + pattern

            if guessed_url in self.visited_urls:
                continue

            # 快速檢查 URL 是否存在（只檢查 HEAD）
            if self._url_exists(guessed_url):
                pages.append(PageInfo(
                    url=guessed_url,
                    page_type=page_type,
                    source='url_pattern',
                    title=""
                ))
                self.visited_urls.add(guessed_url)

        return pages

    def _classify_by_text(self, text: str, keyword_map: Dict[str, List[str]]) -> Optional[str]:
        """根據文字分類頁面類型"""
        if not text:
            return None

        for page_type, keywords in keyword_map.items():
            if any(kw in text for kw in keywords):
                return page_type

        return None

    def _get_link_text(self, page, url: str) -> str:
        """取得連結文字"""
        try:
            return page.css(f'a[href="{url}"]::text').get().strip()
        except:
            return ""

    def _to_absolute_url(self, url: str, base_url: str) -> Optional[str]:
        """轉換為絕對 URL"""
        if not url:
            return None

        # 過濾非 http 連結
        if url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
            return None

        try:
            return urljoin(base_url, url)
        except:
            return None

    def _url_exists(self, url: str) -> bool:
        """快速檢查 URL 是否存在"""
        try:
            import requests
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def _deduplicate_pages(self, pages: List[PageInfo]) -> List[PageInfo]:
        """去除重複頁面"""
        seen_urls = set()
        unique_pages = []

        for page in pages:
            if page.url not in seen_urls:
                seen_urls.add(page.url)
                unique_pages.append(page)

        return unique_pages


class PageClassifier:
    """頁面分類器 - 識別頁面類型"""

    def classify_pages(self, pages: List[PageInfo]) -> Dict[str, List[PageInfo]]:
        """分類所有頁面"""
        classified = defaultdict(list)

        for page in pages:
            # 如果已經有類型，直接使用
            if page.page_type and page.page_type != 'unknown':
                classified[page.page_type].append(page)
                continue

            # 否則嘗試分類
            page_type = self._classify_page(page)
            page.page_type = page_type
            classified[page_type].append(page)

        return dict(classified)

    def _classify_page(self, page: PageInfo) -> str:
        """分類單個頁面（需要抓取頁面內容）"""
        try:
            response = Fetcher.get(page.url, impersonate='chrome', timeout=10)
            text = ' '.join(response.css('::text').getall())
            title = response.css('title::text').get()

            # 檢查關鍵字
            if self._is_meeting_page(text, title, page.url):
                return 'meeting'
            elif self._is_access_page(text, title, page.url):
                return 'access'
            elif self._is_contact_page(text, title, page.url):
                return 'contact'
            elif self._is_policy_page(text, title, page.url):
                return 'policy'
            elif self._is_gallery_page(text, title, page.url):
                return 'gallery'
            else:
                return 'other'
        except:
            return 'other'

    def _is_meeting_page(self, text: str, title: str, url: str) -> bool:
        """判斷是否為會議/宴會頁面"""
        keywords = ['會議室', '宴會廳', '容量', '坪數', 'Meeting', 'Banquet', 'Conference']
        return any(kw in text or kw in title or kw in url for kw in keywords)

    def _is_access_page(self, text: str, title: str, url: str) -> bool:
        """判斷是否為交通頁面"""
        keywords = ['交通', '捷運', '公車', '停車', 'Access', 'Traffic', 'Parking', 'MRT']
        return any(kw in text or kw in title or kw in url for kw in keywords)

    def _is_contact_page(self, text: str, title: str, url: str) -> bool:
        """判斷是否為聯絡頁面"""
        keywords = ['聯絡', '聯繫', 'Contact', 'Contact Us']
        return any(kw in text or kw in title or kw in url for kw in keywords)

    def _is_policy_page(self, text: str, title: str, url: str) -> bool:
        """判斷是否為規則頁面"""
        keywords = ['規則', '政策', '注意事項', '付款', '取消', 'Policy', 'Terms', 'Rules']
        return any(kw in text or kw in title or kw in url for kw in keywords)

    def _is_gallery_page(self, text: str, title: str, url: str) -> bool:
        """判斷是否為照片頁面"""
        keywords = ['照片', '圖片', '相簿', 'Gallery', 'Photos', 'Images', 'Media']
        return any(kw in text or kw in title or kw in url for kw in keywords)


class DataExtractor:
    """資料提取器 - 從不同類型頁面提取資料"""

    def extract_basic_info(self, pages: List[PageInfo]) -> Dict:
        """提取基本資訊（從聯絡頁）"""
        info = {}

        for page in pages:
            try:
                response = Fetcher.get(page.url, impersonate='chrome', timeout=10)
                text = ' '.join(response.css('::text').getall())

                # 電話
                phone = self._extract_phone(text)
                if phone:
                    info['phone'] = phone

                # Email
                email = self._extract_email(text)
                if email:
                    info['email'] = email

                # 地址
                address = self._extract_address(text)
                if address:
                    info['address'] = address

            except:
                continue

        return info

    def extract_rooms(self, pages: List[PageInfo]) -> List[Dict]:
        """提取會議室資料"""
        rooms = []

        for page in pages:
            try:
                response = Fetcher.get(page.url, impersonate='chrome', timeout=10)

                # 策略 1: 從表格提取
                table_rooms = self._extract_from_table(response)
                rooms.extend(table_rooms)

                # 策略 2: 從卡片提取
                card_rooms = self._extract_from_cards(response)
                rooms.extend(card_rooms)

                # 策略 3: 從列表提取
                list_rooms = self._extract_from_list(response)
                rooms.extend(list_rooms)

            except:
                continue

        return self._deduplicate_rooms(rooms)

    def extract_access_info(self, pages: List[PageInfo]) -> Dict:
        """提取交通資訊"""
        access = {}

        for page in pages:
            try:
                response = Fetcher.get(page.url, impersonate='chrome', timeout=10)
                text = ' '.join(response.css('::text').getall())

                # 捷運
                if '捷運' in text or 'MRT' in text:
                    access['mrt'] = self._extract_mrt(text)

                # 公車
                if '公車' in text or 'Bus' in text:
                    access['bus'] = self._extract_bus(text)

                # 停車
                if '停車' in text or 'Parking' in text:
                    access['parking'] = self._extract_parking(text)

            except:
                continue

        return access

    def _extract_phone(self, text: str) -> Optional[str]:
        """提取電話"""
        patterns = [
            r'0\d{1,2}-\d{3,4}-\d{4}',
            r'0\d{9}',
            r'\+886-\d{1,2}-\d{3,4}-\d{4}',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match.startswith(('02', '03', '04', '05', '06', '07', '08', '09', '+886')):
                    return match
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """提取 Email"""
        emails = re.findall(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', text)
        valid_emails = [e for e in emails if not any(x in e for x in
            ['example', 'test', '.png', '.jpg', 'wppro.work'])]

        return valid_emails[0] if valid_emails else None

    def _extract_address(self, text: str) -> Optional[str]:
        """提取地址"""
        # 台灣地址通常以「台北市」、「高雄市」等開頭
        pattern = r'(臺北市|台北市|高雄市|臺中市|台中市|[六二]安市|桃園市|新北市).*?\d{1,3}([樓層F樓]|巷|弄|號|[街路大道])'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_mrt(self, text: str) -> Dict:
        """提取捷運資訊"""
        mrt = {}

        # 捷運站名
        station_pattern = r'捷運.*?([^\s]{2,4}站)'
        match = re.search(station_pattern, text)
        if match:
            mrt['station'] = match.group(1)

        return mrt

    def _extract_bus(self, text: str) -> List[str]:
        """提取公車資訊"""
        # 公車號碼
        buses = re.findall(r'\d{3,4}(?:\s*?(?:公車|聯營))?', text)
        return list(set(buses))

    def _extract_parking(self, text: str) -> Dict:
        """提取停車資訊"""
        parking = {}

        if '停車位' in text or 'Parking' in text:
            match = re.search(r'(\d+).*?[車位個]', text)
            if match:
                parking['spaces'] = int(match.group(1))

        return parking

    def _extract_from_table(self, page) -> List[Dict]:
        """從表格提取會議室"""
        rooms = []

        try:
            tables = page.css('table')

            for table in tables:
                headers = table.css('th::text').getall()

                # 檢查是否為容量表格
                if not any(kw in h for h in headers for kw in ['容量', '坪', '面積']):
                    continue

                rows = table.css('tr')[1:]  # 跳過標題
                for row in rows:
                    cells = row.css('td')

                    if len(cells) >= 2:
                        room_name = cells[0].css('::text').get()
                        if room_name and len(room_name) >= 2:
                            rooms.append({
                                'name': room_name.strip(),
                                'source': 'table'
                            })
        except:
            pass

        return rooms

    def _extract_from_cards(self, page) -> List[Dict]:
        """從卡片提取會議室"""
        rooms = []

        try:
            cards = page.css('.room, .room-card, .meeting-room, .banquet-room, [class*="room"]')

            for card in cards[:10]:  # 限制數量
                name = card.css('h2::text, h3::text, h4::text, .title::text, .name::text').get()

                if name and len(name.strip()) >= 2:
                    rooms.append({
                        'name': name.strip(),
                        'source': 'card'
                    })
        except:
            pass

        return rooms

    def _extract_from_list(self, page) -> List[Dict]:
        """從列表提取會議室"""
        rooms = []

        try:
            items = page.css('.room-list-item, .meeting-item, li')

            for item in items[:15]:
                text = ' '.join(item.css('::text').getall())

                # 尋找會議室名稱模式
                matches = re.findall(r'[\u4e00-\u9fa5]{2,6}[廳寶室]', text)
                for match in matches:
                    if match not in [r['name'] for r in rooms]:
                        rooms.append({
                            'name': match,
                            'source': 'list'
                        })
        except:
            pass

        return rooms

    def _deduplicate_rooms(self, rooms: List[Dict]) -> List[Dict]:
        """去除重複會議室"""
        seen_names = set()
        unique_rooms = []

        for room in rooms:
            name = room.get('name', '')
            if name and name not in seen_names:
                seen_names.add(name)
                unique_rooms.append(room)

        return unique_rooms


class FullSiteScraper:
    """全站智能爬蟲 V4"""

    def __init__(self, config_file='venues.json'):
        self.config_file = config_file
        self.data = self._load_data()
        self.discoverer = PageDiscoverer()
        self.classifier = PageClassifier()
        self.extractor = DataExtractor()

    def _load_data(self):
        """載入資料"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self):
        """儲存資料"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def scrape_venue_full_site(self, venue_id: int) -> Dict:
        """完整爬取場地官網"""
        venue = next((v for v in self.data if v.get('id') == venue_id), None)
        if not venue:
            return {'error': f'找不到場地 {venue_id}'}

        url = venue.get('url', '')
        if not url:
            return {'error': '沒有官網 URL'}

        print(f"\n{'='*80}")
        print(f"🏢 場地 [{venue_id}] {venue.get('name')}")
        print(f"🔗 URL: {url}")
        print(f"{'='*80}\n")

        result = {
            'id': venue_id,
            'name': venue.get('name'),
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'pages_discovered': 0,
            'pages_scraped': 0,
            'data': {}
        }

        try:
            # 1. 發現頁面
            pages = self.discoverer.discover_all(url, max_pages=20)
            result['pages_discovered'] = len(pages)

            if not pages:
                return {**result, 'error': '無法發現任何頁面'}

            # 2. 分類頁面
            classified = self.classifier.classify_pages(pages)
            print(f"🏷️  頁面分類:")
            for page_type, type_pages in classified.items():
                print(f"   {page_type}: {len(type_pages)} 個")

            # 3. 提取資料
            print(f"\n📥 提取資料:")

            # 基本資訊
            contact_pages = classified.get('contact', [])
            if contact_pages:
                basic = self.extractor.extract_basic_info(contact_pages)
                if basic:
                    result['data']['basic'] = basic
                    print(f"   ✅ 基本資訊: 電話={basic.get('phone', 'N/A')}, Email={basic.get('email', 'N/A')}")

            # 會議室
            meeting_pages = classified.get('meeting', [])
            if meeting_pages:
                rooms = self.extractor.extract_rooms(meeting_pages)
                if rooms:
                    result['data']['rooms'] = rooms
                    print(f"   ✅ 會議室: {len(rooms)} 個")

            # 交通資訊
            access_pages = classified.get('access', [])
            if access_pages:
                access = self.extractor.extract_access_info(access_pages)
                if access:
                    result['data']['access'] = access
                    print(f"   ✅ 交通資訊: 捷運={access.get('mrt', {}).get('station', 'N/A')}")

            result['pages_scraped'] = len(contact_pages) + len(meeting_pages) + len(access_pages)

            # 4. 更新 venues.json（即使沒有提取到資料也要更新 metadata）
            self._update_venue_data(venue_id, result['data'], result['pages_discovered'])
            if result['data']:
                print(f"\n✅ 已更新 venues.json")

        except Exception as e:
            result['error'] = str(e)
            print(f"\n❌ 錯誤: {str(e)}")

        return result

    def _update_venue_data(self, venue_id: int, data: Dict, pages_discovered: int = 0):
        """更新場地資料"""
        venue_idx = next((i for i, v in enumerate(self.data) if v.get('id') == venue_id), None)
        if venue_idx is None:
            return

        venue = self.data[venue_idx]

        # 更新基本資訊
        if 'basic' in data:
            basic = data['basic']
            if basic.get('phone'):
                venue['contactPhone'] = basic['phone']
            if basic.get('email'):
                venue['contactEmail'] = basic['email']
            if basic.get('address'):
                venue['address'] = basic['address']

        # 更新會議室
        if 'rooms' in data:
            # 將提取的會議室名稱轉換為標準格式
            existing_rooms = venue.get('rooms', [])

            # 補充新發現的會議室
            existing_names = {r.get('name') for r in existing_rooms}
            for room in data['rooms']:
                if room['name'] not in existing_names:
                    existing_rooms.append({
                        'id': f"{venue_id}-{len(existing_rooms)+1:02d}",
                        'name': room['name'],
                        'source': room.get('source', 'web_scraping')
                    })

            venue['rooms'] = existing_rooms

        # 更新 metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}

        venue['metadata'].update({
            'lastScrapedAt': datetime.now().isoformat(),
            'scrapeVersion': 'V4',
            'pagesDiscovered': pages_discovered,
            'fullSiteScraped': True
        })

        # 更新交通資訊
        if 'access' in data and data['access']:
            if 'accessInfo' not in venue:
                venue['accessInfo'] = {}
            venue['accessInfo'].update(data['access'])

        self.data[venue_idx] = venue

    def batch_process(self, venue_ids: List[int]) -> List[Dict]:
        """批次處理"""
        results = []

        for i, venue_id in enumerate(venue_ids, 1):
            print(f"\n{'#'*80}")
            print(f"# 進度: [{i}/{len(venue_ids)}]")
            print(f"{'#'*80}")

            result = self.scrape_venue_full_site(venue_id)
            results.append(result)

            # 每 2 個儲存一次（全站爬取較慢）
            if i % 2 == 0:
                self._save_data()

        self._save_data()
        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='全站智能爬蟲 V4')
    parser.add_argument('--test', type=int, help='測試單個場地')
    parser.add_argument('--batch', action='store_true', help='批次處理')
    parser.add_argument('--sample', type=int, default=5, help='批次處理數量（建議 3-5 個）')

    args = parser.parse_args()

    scraper = FullSiteScraper()

    if args.test:
        result = scraper.scrape_venue_full_site(args.test)
        print(f"\n{'='*80}")
        print("📄 最終結果")
        print(f"{'='*80}")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.batch:
        print("\n🚀 V4 全站爬蟲批次處理")
        print("="*80)

        # 找出未處理的場地（修復版：避免重複處理）
        unprocessed = []
        today = datetime.now().date()

        for venue in scraper.data:
            if venue.get('status') == 'discontinued':
                continue
            if venue.get('url') and venue.get('verified'):
                metadata = venue.get('metadata', {})
                last_scraped_str = metadata.get('lastScrapedAt')

                # 檢查是否已經用 V4 爬取過
                if metadata.get('scrapeVersion') == 'V4':
                    # 如果是 V4 爬取的，檢查時間
                    if last_scraped_str:
                        try:
                            last_scraped = datetime.fromisoformat(last_scraped_str)
                            if (today - last_scraped.date()) <= timedelta(days=7):
                                continue  # 跳過最近爬取的
                        except:
                            pass

                unprocessed.append(venue['id'])

        sample_size = min(args.sample, len(unprocessed))
        venue_ids = unprocessed[:sample_size]

        print(f"📊 可處理場地總數: {len(unprocessed)}")
        print(f"📝 本次處理: {len(venue_ids)} 個場地")
        print(f"⚠️  注意：全站爬取較慢，建議每次處理 3-5 個場地\n")

        if not venue_ids:
            print("❌ 沒有需要處理的場地")
            return

        results = scraper.batch_process(venue_ids)

        print(f"\n{'='*80}")
        print(f"✅ 批次處理完成")
        print(f"   處理: {len(results)} 個場地")
        print(f"   成功: {sum(1 for r in results if 'error' not in r)} 個")
        print(f"{'='*80}")

    else:
        print("📖 使用方式:")
        print("  python full_site_scraper_v4.py --test 1043")
        print("  python full_site_scraper_v4.py --batch --sample 3")


if __name__ == '__main__':
    main()
