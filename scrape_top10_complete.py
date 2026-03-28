#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Top 10 場地三級爬蟲 - 完整版

實作完整的三級爬取：
1級：主頁 → 基本資訊、聯絡
2級：會議頁 → 會議室列表
3級：詳情頁 → 容量、面積、價格、設備
"""

import sys
import io
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re
import time

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class ThreeStageScraper:
    """三級爬蟲"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def scrape_venue(self, venue_id, venue_name, venue_url):
        """完整三級爬取"""
        print(f'\n{"="*80}')
        print(f'場地 [{venue_id}] {venue_name[:50]}')
        print(f'URL: {venue_url}')
        print("="*80)

        result = {
            'id': venue_id,
            'name': venue_name,
            'url': venue_url,
            'stage1_success': False,
            'stage2_success': False,
            'stage3_success': False,
            'rooms_discovered': 0,
            'rooms_enhanced': 0,
            'contact_extracted': False,
            'pdfs_discovered': []
        }

        try:
            # ========== 階段 1：主頁爬取 ==========
            print('\n[階段 1/3] 爬取主頁...')
            response = self.session.get(venue_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            homepage_text = soup.get_text()
            print(f'  主頁長度: {len(homepage_text):,} 字元')

            # 提取聯絡資訊
            contact = self._extract_contact(soup)
            if contact.get('phone') or contact.get('email'):
                result['contact_extracted'] = True
                print(f'  電話: {contact.get("phone", "N/A")}')
                print(f'  Email: {contact.get("email", "N/A")}')

            result['stage1_success'] = True

            # ========== 階段 2：會議頁爬取 ==========
            print('\n[階段 2/3] 發現會議頁...')

            meeting_links = self._discover_meeting_pages(soup, venue_url)
            print(f'  發現會議頁: {len(meeting_links)} 個')

            if not meeting_links:
                print('  ⚠️ 未發現會議頁，嘗試從主頁提取...')

            # ========== 階段 3：詳情頁爬取 ==========
            print('\n[階段 3/3] 深入會議室詳情頁...')

            all_rooms = []

            # 嘗試從會議頁發現會議室
            if meeting_links:
                for i, meeting_url in enumerate(meeting_links[:5], 1):  # 限制最多 5 個會議頁
                    print(f'  [{i}/{len(meeting_links)}] 爬取: {meeting_url[:60]}...')
                    rooms = self._extract_rooms_from_page(meeting_url)
                    all_rooms.extend(rooms)
                    time.sleep(1)  # 避免請求過快

            # 如果沒有找到會議室，嘗試從主頁提取
            if not all_rooms:
                print('  從主頁提取會議室...')
                all_rooms = self._extract_rooms_from_page(venue_url)

            # 去重
            seen = set()
            unique_rooms = []
            for room in all_rooms:
                room_key = f"{room.get('name', '')}{room.get('floor', '')}"
                if room_key not in seen and room.get('name'):
                    seen.add(room_key)
                    unique_rooms.append(room)

            result['rooms_discovered'] = len(unique_rooms)
            print(f'  總共發現會議室: {len(unique_rooms)} 個')

            # 深入爬取每個會議室的詳情頁
            enhanced_rooms = []
            for i, room in enumerate(unique_rooms[:30], 1):  # 限制最多 30 個會議室
                print(f'  [{i}/{len(unique_rooms)}] 處理: {room["name"][:30]}...')

                # 如果有 detail_url，深入爬取
                if room.get('detail_url'):
                    detail_data = self._scrape_room_detail_page(room['detail_url'])
                    # 合併資料
                    merged_room = room.copy()
                    merged_room.update(detail_data)
                    enhanced_rooms.append(merged_room)

                    # 檢查是否成功提取到關鍵資料
                    if merged_room.get('capacity') or merged_room.get('area') or merged_room.get('price'):
                        result['rooms_enhanced'] += 1
                else:
                    enhanced_rooms.append(room)

                time.sleep(0.5)

            result['stage2_success'] = len(meeting_links) > 0 or len(all_rooms) > 0
            result['stage3_success'] = result['rooms_enhanced'] > 0

            print(f'\n  處理會議室: {len(enhanced_rooms)} 個')
            print(f'  成功補強: {result["rooms_enhanced"]} 個')
            print(f'  補強率: {result["rooms_enhanced"]/len(enhanced_rooms)*100:.1f}%' if len(enhanced_rooms) > 0 else '  補強率: N/A')

            # 發現 PDF
            pdf_links = self._discover_pdfs(soup, venue_url)
            result['pdfs_discovered'] = pdf_links
            if pdf_links:
                print(f'\n  發現 PDF: {len(pdf_links)} 個')
                for pdf in pdf_links[:3]:
                    print(f'    - {pdf[:70]}...')

            # 寫入 venues.json
            self._update_venues_json(venue_id, contact, enhanced_rooms, pdf_links)

            print('\n  ✅ 已更新 venues.json')

        except requests.exceptions.Timeout:
            print('\n  ❌ 連線超時')
        except requests.exceptions.ConnectionError:
            print('\n  ❌ 無法連線')
        except Exception as e:
            print(f'\n  ❌ 錯誤: {str(e)[:100]}')

        return result

    def _extract_contact(self, soup):
        """提取聯絡資訊"""
        contact = {
            'phone': None,
            'email': None
        }

        page_text = soup.get_text()

        # 電話模式
        phone_patterns = [
            r'0\d-?\d{3,4}-?\d{3,4}',
            r'\+886-?\d-?\d{3,4}-?\d{3,4}',
            r'\+886\s?\d-?\d{3,4}-?\d{3,4}',
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                # 過濾明顯不是電話的
                for match in matches:
                    if len(re.sub(r'[\d-]', '', match)) >= 7:
                        contact['phone'] = match
                        break
            if contact['phone']:
                break

        # Email 模式
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, page_text)
        valid_emails = [m for m in matches if not any(spam in m.lower() for spam in ['no-reply', 'noreply', 'example', 'test'])]

        if valid_emails:
            contact['email'] = valid_emails[0]

        return contact

    def _discover_meeting_pages(self, soup, base_url):
        """發現會議頁連結"""
        meeting_links = []

        # 尋找包含會議相關關鍵字的連結
        keywords = ['meeting', 'conference', 'banquet', '會議', '宴會', '會議室', '宴會廳',
                    'events', 'mice', 'space', '場地', '租借']

        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            link_text = link.get_text().lower()

            # 檢查 URL 或連結文字是否包含關鍵字
            if any(kw in href for kw in keywords) or any(kw in link_text for kw in keywords):
                full_url = urljoin(base_url, link['href'])
                # 避免重複
                if full_url not in meeting_links and full_url != base_url:
                    meeting_links.append(full_url)

        return meeting_links

    def _extract_rooms_from_page(self, page_url):
        """從頁面提取會議室"""
        rooms = []

        try:
            response = self.session.get(page_url, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 尋找標題
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                text = heading.get_text(strip=True)
                # 過濾掉明顯不是會議室的標題
                if any(kw in text for kw in ['廳', '室', '會議', '宴會', '空間', 'Room', 'Hall', 'Meeting']):
                    if len(text) > 2 and len(text) < 100:
                        rooms.append({
                            'name': text,
                            'page_url': page_url,
                            'source': 'heading'
                        })

            # 尋找列表項
            for li in soup.find_all('li'):
                text = li.get_text(strip=True)
                if any(kw in text for kw in ['廳', '室', '會議', '宴會']):
                    if len(text) > 2 and len(text) < 100:
                        # 提取樓層
                        floor_match = re.search(r'(\d+[F樓層])', text)
                        floor = floor_match.group(1) if floor_match else None

                        rooms.append({
                            'name': text,
                            'floor': floor,
                            'page_url': page_url,
                            'source': 'list_item'
                        })

        except Exception as e:
            print(f'    錯誤: {str(e)[:50]}')

        return rooms

    def _scrape_room_detail_page(self, detail_url):
        """深入爬取會議室詳情頁"""
        try:
            response = self.session.get(detail_url, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()

            detail_data = {
                'capacity': None,
                'area': None,
                'price': None,
                'equipment': None
            }

            # 提取容量
            capacity_patterns = [
                r'容量[：:]?\s*(\d+)\s*人',
                r'可容納\s*(\d+)\s*人',
                r'(\d{2,4})\s*[人名]',
                r'(\d+)\s*people',
            ]

            for pattern in capacity_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        detail_data['capacity'] = int(match.group(1))
                        break
                    except ValueError:
                        continue

            # 提取面積
            area_patterns = [
                r'(\d+\.?\d*)\s*坪',
                r'(\d+\.?\d*)\s*平方公尺',
                r'(\d+\.?\d*)\s*㎡',
                r'(\d+\.?\d*)\s*m²',
            ]

            for pattern in area_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        detail_data['area'] = float(match.group(1))
                        break
                    except ValueError:
                        continue

            # 提取價格
            price_patterns = [
                r'NT\$\s*([\d,]+)',
                r'TWD\s*([\d,]+)',
                r'([\d,]+)\s*元',
                r'價格[：:]?\s*NT\$\s*([\d,]+)',
                r'([\d,]+)\s*起',
            ]

            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    try:
                        detail_data['price'] = int(match.group(1).replace(',', ''))
                        break
                    except ValueError:
                        continue

            # 提取設備
            equipment_keywords = ['投影', '音響', '麥克風', '螢幕', '白板', 'Wi-Fi', '網路', '投影機']
            found_equipment = []
            for keyword in equipment_keywords:
                if keyword in page_text:
                    found_equipment.append(keyword)

            if found_equipment:
                detail_data['equipment'] = ', '.join(found_equipment)

            return detail_data

        except Exception as e:
            return {
                'capacity': None,
                'area': None,
                'price': None,
                'equipment': None
            }

    def _discover_pdfs(self, soup, base_url):
        """發現 PDF 連結"""
        pdf_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(base_url, href)
                if full_url not in pdf_links:
                    pdf_links.append(full_url)

        return pdf_links

    def _update_venues_json(self, venue_id, contact, rooms, pdf_links):
        """更新 venues.json"""
        with open('venues.json', 'r', encoding='utf-8') as f:
            venues = json.load(f)

        for venue in venues:
            if venue['id'] == venue_id:
                # 更新聯絡資訊
                if contact.get('phone'):
                    if 'contact' not in venue:
                        venue['contact'] = {}
                    venue['contact']['phone'] = contact['phone']

                if contact.get('email'):
                    if 'contact' not in venue:
                        venue['contact'] = {}
                    venue['contact']['email'] = contact['email']

                # 更新會議室資料
                if rooms:
                    # 合併策略：更新現有會議室的資料
                    existing_rooms = venue.get('rooms', [])
                    updated_rooms = []

                    for existing in existing_rooms:
                        existing_name = existing.get('name', '')

                        # 從新資料中找匹配的
                        matched = False
                        for new_room in rooms:
                            new_name = new_room.get('name', '')
                            if new_name in existing_name or existing_name in new_name:
                                # 合併資料（保留原有，補充新資料）
                                merged = existing.copy()
                                if new_room.get('capacity') and not merged.get('capacity'):
                                    merged['capacity'] = new_room['capacity']
                                if new_room.get('area') and not merged.get('area'):
                                    merged['area'] = new_room['area']
                                if new_room.get('price') and not merged.get('price'):
                                    merged['price'] = new_room['price']
                                if new_room.get('equipment') and not merged.get('equipment'):
                                    merged['equipment'] = new_room['equipment']

                                updated_rooms.append(merged)
                                matched = True
                                break

                        if not matched:
                            updated_rooms.append(existing)

                    # 添加新發現的會議室
                    existing_names = [r.get('name', '') for r in existing_rooms]
                    for new_room in rooms:
                        if new_room.get('name', '') not in existing_names:
                            updated_rooms.append(new_room)

                    venue['rooms'] = updated_rooms

                # 更新 metadata
                if 'metadata' not in venue:
                    venue['metadata'] = {}

                venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
                venue['metadata']['scrapeVersion'] = 'ThreeStage_Scraper_V1'

                if pdf_links:
                    venue['metadata']['pdfUrls'] = pdf_links
                    venue['metadata']['pdfDiscoveredAt'] = datetime.now().isoformat()

                # 計算品質分數
                total_rooms = len(venue.get('rooms', []))
                rooms_with_capacity = sum(1 for r in venue.get('rooms', []) if r.get('capacity'))
                rooms_with_area = sum(1 for r in venue.get('rooms', []) if r.get('area'))
                rooms_with_price = sum(1 for r in venue.get('rooms', []) if r.get('price'))

                if total_rooms > 0:
                    capacity_score = (rooms_with_capacity / total_rooms) * 30
                    area_score = (rooms_with_area / total_rooms) * 25
                    price_score = (rooms_with_price / total_rooms) * 30
                    quantity_score = min(total_rooms * 2, 15)  # 最多 15 分

                    venue['qualityScore'] = int(capacity_score + area_score + price_score + quantity_score)
                else:
                    venue['qualityScore'] = 0

                break

        # 寫回
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)


def main():
    # Top 10 場地（能夠連線的 7 個 + 嘗試處理無法連線的 3 個）
    top10 = [
        {'id': 1493, 'name': '師大進修推廣學院', 'url': 'https://www.sce.ntnu.edu.tw/home/index.php'},
        {'id': 1042, 'name': '公務人力發展學院', 'url': 'https://www.hrd.gov.tw'},
        {'id': 1448, 'name': '台北國際會議中心(TICC)', 'url': 'https://www.ticc.com.tw/'},
        {'id': 1125, 'name': '華山1914', 'url': 'https://www.huashan1914.com'},
        {'id': 1053, 'name': '台北兄弟大飯店', 'url': 'https://www.brotherhotel.com.tw/?cat=75'},
        {'id': 1122, 'name': '維多麗亞酒店', 'url': 'https://www.grandvictoria.com.tw/'},
        {'id': 1129, 'name': '青青婚宴會館', 'url': 'https://www.77-67.com/'},
        {'id': 1049, 'name': '台北世貿中心', 'url': 'https://www.twtc.com.tw/'},
        {'id': 1103, 'name': '台北萬豪酒店', 'url': 'https://www.taipeimarriott.com.tw/'},
        {'id': 1128, 'name': '集思台大會議中心', 'url': 'https://www.meeting.com.tw/ntu/'}
    ]

    print('=' * 80)
    print('Top 10 場地三級爬蟲 - 完整版')
    print('=' * 80)
    print(f'處理場地數: {len(top10)}')
    print()

    scraper = ThreeStageScraper()
    results = []

    for i, venue in enumerate(top10, 1):
        print(f'\n{"="*80}')
        print(f'總進度: [{i}/{len(top10)}]')
        print("="*80)

        result = scraper.scrape_venue(
            venue['id'],
            venue['name'],
            venue['url']
        )
        results.append(result)

        # 避免請求過快
        time.sleep(2)

    # 生成最終報告
    print('\n' + '=' * 80)
    print('最終處理報告')
    print('=' * 80)
    print()

    successful = [r for r in results if r['stage1_success']]
    stage2_success = [r for r in results if r['stage2_success']]
    stage3_success = [r for r in results if r['stage3_success']]

    print(f'階段 1 成功（主頁）: {len(successful)}/{len(results)}')
    print(f'階段 2 成功（會議頁）: {len(stage2_success)}/{len(results)}')
    print(f'階段 3 成功（詳情頁）: {len(stage3_success)}/{len(results)}')
    print()

    total_rooms = sum(r['rooms_discovered'] for r in results)
    total_enhanced = sum(r['rooms_enhanced'] for r in results)
    total_pdfs = sum(len(r['pdfs_discovered']) for r in results)

    print(f'總發現會議室: {total_rooms}')
    print(f'成功補強會議室: {total_enhanced}')
    print(f'發現 PDF 連結: {total_pdfs}')
    print()

    # 詳細結果
    print('=' * 80)
    print('各場地詳細結果')
    print('=' * 80)
    print()

    for result in results:
        s1 = '✅' if result['stage1_success'] else '❌'
        s2 = '✅' if result['stage2_success'] else '❌'
        s3 = '✅' if result['stage3_success'] else '❌'

        print(f'{s1} {s2} {s3} [{result["id"]}] {result["name"][:40]}')
        print(f'   發現會議室: {result["rooms_discovered"]} | 補強: {result["rooms_enhanced"]}')
        if result['pdfs_discovered']:
            print(f'   PDF: {len(result["pdfs_discovered"])} 個')
        print()


if __name__ == '__main__':
    main()
