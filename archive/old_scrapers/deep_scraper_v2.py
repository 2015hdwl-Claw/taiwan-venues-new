#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整官網深度爬蟲 V2
修正：會議室細分、詳細資料擷取、URL 處理
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import sys
import io

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class CompleteVenueScraperV2:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def scrape_complete_venue(self, venue_id, venue_name, base_url, specific_urls=None):
        """完整爬取單個場地"""

        print('='*80)
        print(f'完整爬取: {venue_name} (ID {venue_id})')
        print(f'URL: {base_url}')
        print('='*80)

        result = {
            'id': venue_id,
            'name': venue_name,
            'url': base_url,
            'scraped_at': datetime.now().isoformat(),
            'scrape_pages': [],
            'data': {}
        }

        try:
            # 階段1: 爬取首頁
            print('\n[1/6] 爬取首頁')
            homepage_data = self._scrape_homepage(base_url)
            result['data']['homepage'] = homepage_data
            result['scrape_pages'].append(base_url)

            # 如果有指定特定 URL，使用它們
            if specific_urls:
                if 'meeting_url' in specific_urls:
                    homepage_data['meeting_links'].insert(0, {
                        'text': '指定會議室頁面',
                        'url': specific_urls['meeting_url']
                    })
                if 'pricing_url' in specific_urls:
                    homepage_data['pricing_links'].insert(0, {
                        'text': '指定價格頁面',
                        'url': specific_urls['pricing_url']
                    })
                if 'rules_url' in specific_urls:
                    homepage_data['rules_links'].insert(0, {
                        'text': '指定規則頁面',
                        'url': specific_urls['rules_url']
                    })
                if 'access_url' in specific_urls:
                    homepage_data['access_links'].insert(0, {
                        'text': '指定交通頁面',
                        'url': specific_urls['access_url']
                    })

            # 階段2: 爬取會議室詳細頁面
            print('\n[2/6] 爬取會議室頁面')
            meeting_rooms_data = self._scrape_meeting_rooms(base_url, homepage_data['meeting_links'])
            result['data']['meeting_rooms'] = meeting_rooms_data

            # 階段3: 爬取價格頁面
            print('\n[3/6] 爬取價格頁面')
            pricing_data = self._scrape_pricing(base_url, homepage_data['pricing_links'])
            result['data']['pricing'] = pricing_data

            # 階段4: 爬取場地規則頁面
            print('\n[4/6] 爬取場地規則頁面')
            rules_data = self._scrape_rules(base_url, homepage_data['rules_links'])
            result['data']['rules'] = rules_data

            # 階段5: 爬取交通資訊頁面
            print('\n[5/6] 爬取交通資訊頁面')
            access_data = self._scrape_access_info(base_url, homepage_data['access_links'])
            result['data']['access'] = access_data

            # 階段6: 爬取平面圖頁面
            print('\n[6/6] 爬取平面圖頁面')
            floor_plan_data = self._scrape_floor_plan(base_url, homepage_data['floor_plan_links'])
            result['data']['floor_plan'] = floor_plan_data

            # 統計
            result['success'] = True
            result['total_pages_scraped'] = len(result['scrape_pages'])

        except Exception as e:
            print(f'\n錯誤: {e}')
            import traceback
            traceback.print_exc()
            result['success'] = False
            result['error'] = str(e)

        return result

    def _scrape_homepage(self, url):
        """爬取首頁，發現所有重要連結"""
        print(f'  抓取: {url}')

        try:
            response = self.session.get(url, timeout=15, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            data = {
                'url': url,
                'title': soup.find('title').get_text().strip() if soup.find('title') else '',
                'meeting_links': [],
                'pricing_links': [],
                'rules_links': [],
                'access_links': [],
                'floor_plan_links': [],
                'contact_links': []
            }

            # 尋找各類型連結
            all_links = soup.find_all('a', href=True)

            # 會議室相關
            meeting_keywords = ['會議', 'meeting', '會議室', '場地', 'space', 'room', 'venue']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                # 過濾掉過長或無意義的連結
                if any(kw in text.lower() or kw in href.lower() for kw in meeting_keywords):
                    if len(text) > 0 and len(text) < 100:
                        full_url = urljoin(url, href)
                        data['meeting_links'].append({
                            'text': text,
                            'url': full_url
                        })

            # 價格相關
            pricing_keywords = ['價目', '價格', '收費', 'rate', '費用', 'charge']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text.lower() or kw in href.lower() for kw in pricing_keywords):
                    if len(text) > 0 and len(text) < 100:
                        full_url = urljoin(url, href)
                        data['pricing_links'].append({
                            'text': text,
                            'url': full_url
                        })

            # 規則相關
            rules_keywords = ['規則', '規範', '須知', '注意', '租借', '使用', '注意事項']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text or kw in href for kw in rules_keywords):
                    if len(text) > 0 and len(text) < 100:
                        full_url = urljoin(url, href)
                        data['rules_links'].append({
                            'text': text,
                            'url': full_url
                        })

            # 交通相關
            access_keywords = ['交通', '位置', 'access', 'location', '怎麼去', 'direction', '捷運', '停車']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text or kw in href for kw in access_keywords):
                    if len(text) > 0 and len(text) < 100:
                        full_url = urljoin(url, href)
                        data['access_links'].append({
                            'text': text,
                            'url': full_url
                        })

            # 平面圖相關
            floor_plan_keywords = ['平面圖', '導覽', 'floor plan', '樓層', '配置', '示意圖']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text or kw in href for kw in floor_plan_keywords):
                    if len(text) > 0 and len(text) < 100:
                        full_url = urljoin(url, href)
                        data['floor_plan_links'].append({
                            'text': text,
                            'url': full_url
                        })

            # 去重
            for key in ['meeting_links', 'pricing_links', 'rules_links', 'access_links', 'floor_plan_links']:
                seen = set()
                unique_links = []
                for link in data[key]:
                    if link['url'] not in seen:
                        seen.add(link['url'])
                        unique_links.append(link)
                data[key] = unique_links

            print(f'    會議連結: {len(data["meeting_links"])}')
            print(f'    價格連結: {len(data["pricing_links"])}')
            print(f'    規則連結: {len(data["rules_links"])}')
            print(f'    交通連結: {len(data["access_links"])}')
            print(f'    平面圖連結: {len(data["floor_plan_links"])}')

            return data

        except Exception as e:
            print(f'    錯誤: {e}')
            import traceback
            traceback.print_exc()
            return {}

    def _scrape_meeting_rooms(self, base_url, meeting_links):
        """深入爬取會議室頁面，擷取完整資料"""
        print(f'  會議連結數量: {len(meeting_links)}')

        rooms_data = {
            'total_links_found': len(meeting_links),
            'detailed_pages_scraped': 0,
            'rooms': []
        }

        # 深入爬取前5個會議室頁面
        for i, link in enumerate(meeting_links[:5], 1):
            print(f'    [{i}/{min(5, len(meeting_links))}] {link["text"][:40]}')

            try:
                response = self.session.get(link['url'], timeout=15, verify=False)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # 尋找所有會議室
                rooms = self._extract_rooms_detailed(soup, link['url'])
                rooms_data['rooms'].extend(rooms)
                rooms_data['detailed_pages_scraped'] += 1

                print(f'      找到 {len(rooms)} 個會議室')

            except Exception as e:
                print(f'      錯誤: {str(e)[:80]}')

        # 去重會議室
        unique_rooms = {}
        for room in rooms_data['rooms']:
            key = f"{room['name']}_{room.get('floor', '')}"
            if key not in unique_rooms:
                unique_rooms[key] = room

        rooms_data['rooms'] = list(unique_rooms.values())
        rooms_data['total_rooms_found'] = len(rooms_data['rooms'])

        print(f'    總計找到 {len(rooms_data["rooms"])} 個會議室')

        return rooms_data

    def _extract_rooms_detailed(self, soup, page_url):
        """從頁面提取會議室完整資料，包括細分"""
        rooms = []

        # 嘗試1: 表格結構
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                # 假設第一列是標題
                headers = [th.get_text().strip() for th in rows[0].find_all(['th', 'td'])]

                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) > 0:
                        room_data = {}
                        for j, cell in enumerate(cells):
                            if j < len(headers):
                                room_data[headers[j]] = cell.get_text().strip()

                        # 提取會議室名稱
                        room_name = None
                        for key in ['名稱', '會議室名稱', '場地名稱', '名稱稱']:
                            if key in room_data:
                                room_name = room_data[key]
                                break

                        if room_name:
                            # 檢查是否需要細分
                            subdivisions = self._detect_room_subdivisions(room_name)
                            if subdivisions:
                                # 展開細分
                                for sub_name in subdivisions:
                                    rooms.append({
                                        'name': sub_name,
                                        'source': page_url,
                                        'floor': self._extract_floor(room_name),
                                        'area': room_data.get('面積', ''),
                                        'capacity': room_data.get('容量', ''),
                                        'capacity_type': room_data.get('容量類型', ''),
                                        'equipment': room_data.get('設備', ''),
                                        'price_half_day': room_data.get('半天', ''),
                                        'price_full_day': room_data.get('全天', ''),
                                        'raw_data': room_data
                                    })
                            else:
                                rooms.append({
                                    'name': room_name,
                                    'source': page_url,
                                    'floor': self._extract_floor(room_name),
                                    'area': room_data.get('面積', ''),
                                    'capacity': room_data.get('容量', ''),
                                    'capacity_type': room_data.get('容量類型', ''),
                                    'equipment': room_data.get('設備', ''),
                                    'price_half_day': room_data.get('半天', ''),
                                    'price_full_day': room_data.get('全天', ''),
                                    'raw_data': room_data
                                })

        # 嘗試2: 卡片/列表結構
        if not rooms:
            # 尋找包含「室」、「廳」的元素
            room_keywords = ['會議室', '教室', '廳', 'Room', 'Hall']

            for elem in soup.find_all(['div', 'section', 'article', 'li']):
                # 檢查是否包含會議室相關字詞
                text = elem.get_text().strip()

                if any(kw in text for kw in room_keywords):
                    # 提取會議室名稱
                    for tag in elem.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
                        name = tag.get_text().strip()
                        if name and len(name) < 100 and any(kw in name for kw in room_keywords):
                            # 擷取詳細資訊
                            room_info = self._extract_room_info_from_element(elem)

                            # 檢查是否需要細分
                            subdivisions = self._detect_room_subdivisions(name)
                            if subdivisions:
                                for sub_name in subdivisions:
                                    rooms.append({
                                        'name': sub_name,
                                        'source': page_url,
                                        'floor': self._extract_floor(name),
                                        'area': room_info.get('area', ''),
                                        'capacity': room_info.get('capacity', ''),
                                        'capacity_type': room_info.get('capacity_type', ''),
                                        'equipment': room_info.get('equipment', ''),
                                        'price_half_day': room_info.get('price_half_day', ''),
                                        'price_full_day': room_info.get('price_full_day', '')
                                    })
                            else:
                                rooms.append({
                                    'name': name,
                                    'source': page_url,
                                    'floor': self._extract_floor(name),
                                    'area': room_info.get('area', ''),
                                    'capacity': room_info.get('capacity', ''),
                                    'capacity_type': room_info.get('capacity_type', ''),
                                    'equipment': room_info.get('equipment', ''),
                                    'price_half_day': room_info.get('price_half_day', ''),
                                    'price_full_day': room_info.get('price_full_day', '')
                                })
                            break

        return rooms

    def _detect_room_subdivisions(self, room_name):
        """檢測會議室是否需要細分，例如：101會議室 → 101全室, 101A, 101B, 101AB, 101C, 101D, 101CD"""
        # 常見的細分模式
        subdivisions = None

        # 匹配 "101會議室" 模式
        match = re.match(r'(\d+[室廳]?)會議室', room_name)
        if match:
            base_name = match.group(1)
            # 生成細分
            subdivisions = [
                f'{base_name}全室',
                f'{base_name}A',
                f'{base_name}B',
                f'{base_name}AB',
                f'{base_name}C',
                f'{base_name}D',
                f'{base_name}CD'
            ]
            print(f'        細分 {room_name} → {len(subdivisions)} 個場地')

        return subdivisions

    def _extract_floor(self, room_name):
        """從會議室名稱提取樓層"""
        # 匹配 "1F", "2F", "B1", "B2", "一樓", "二樓"
        match = re.search(r'([B1-9]\s*F|[一二三四五六七八九十]樓)', room_name, re.I)
        if match:
            return match.group(1)
        return ''

    def _extract_room_info_from_element(self, elem):
        """從元素中提取會議室詳細資訊"""
        info = {}
        text = elem.get_text()

        # 提取容量
        capacity_match = re.search(r'容[納量]*[：:]\s*(\d+)', text)
        if capacity_match:
            info['capacity'] = capacity_match.group(1)

        # 提取容量類型
        if '教室型' in text:
            info['capacity_type'] = '教室型'
        elif '標準型' in text:
            info['capacity_type'] = '標準型'
        elif '劇院型' in text:
            info['capacity_type'] = '劇院型'

        # 提取面積
        area_match = re.search(r'面積[：:]\s*([\d.]+\s*坪|[\d.]+\s*m²)', text)
        if area_match:
            info['area'] = area_match.group(1)

        # 提取價格
        price_half_match = re.search(r'半天[：:]\s*NT\$?\s*([\d,]+)', text)
        if price_half_match:
            info['price_half_day'] = price_half_match.group(1)

        price_full_match = re.search(r'全天[：:]\s*NT\$?\s*([\d,]+)', text)
        if price_full_match:
            info['price_full_day'] = price_full_match.group(1)

        # 提取設備
        equipment_keywords = ['投影機', '麥克風', '音響', '螢幕', '白板', '投影', '擴音']
        equipment_found = []
        for kw in equipment_keywords:
            if kw in text:
                equipment_found.append(kw)
        if equipment_found:
            info['equipment'] = ', '.join(equipment_found)

        return info

    def _scrape_pricing(self, base_url, pricing_links):
        """爬取價格頁面"""
        print(f'  價格連結數量: {len(pricing_links)}')

        data = {
            'links_found': len(pricing_links),
            'pages_scraped': 0,
            'price_info': []
        }

        for link in pricing_links[:2]:
            try:
                print(f'    價格頁: {link["text"][:40]}')

                response = self.session.get(link['url'], timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取價格資訊
                text = soup.get_text()

                # 尋找價格模式
                price_patterns = [
                    r'NT\$?\s*([\d,]+)',
                    r'[\$]([\d,]+)',
                    r'([\d,]+)\s*元',
                    r'半天[：:]\s*NT\$?\s*([\d,]+)',
                    r'全天[：:]\s*NT\$?\s*([\d,]+)'
                ]

                prices_found = []
                for pattern in price_patterns:
                    matches = re.findall(pattern, text, re.I)
                    prices_found.extend(matches)

                if prices_found:
                    # 清理價格資料
                    clean_prices = []
                    for p in prices_found:
                        clean_p = p.replace(',', '').replace('NT$', '').replace('$', '').strip()
                        if clean_p.isdigit() and len(clean_p) > 2:
                            clean_prices.append(clean_p)

                    data['price_info'].append({
                        'page': link['url'],
                        'prices': clean_prices[:10]
                    })

                data['pages_scraped'] += 1

            except Exception as e:
                print(f'      錯誤: {str(e)[:50]}')

        return data

    def _scrape_rules(self, base_url, rules_links):
        """爬取場地規則頁面"""
        print(f'  規則連結數量: {len(rules_links)}')

        data = {
            'links_found': len(rules_links),
            'rules_extracted': {}
        }

        for link in rules_links[:2]:
            try:
                print(f'    規則頁: {link["text"][:40]}')

                response = self.session.get(link['url'], timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取規則
                text = soup.get_text()

                rules = {
                    'catering': self._extract_rule_text(text, ['餐飲', '食物', '外食', '自備食物']),
                    'smoking': self._extract_rule_text(text, ['吸菸', '禁菸', '抽菸', '全面禁菸']),
                    'decoration': self._extract_rule_text(text, ['佈置', '裝潢', '釘子', '貼紙', '牆面']),
                    'noise': self._extract_rule_text(text, ['噪音', '音量', '分貝', '大聲']),
                    'cleanup': self._extract_rule_text(text, ['清理', '復原', '歸還', '恢復原狀']),
                    'deposit': self._extract_rule_text(text, ['押金', '保證金', '訂金']),
                    'cancellation': self._extract_rule_text(text, ['取消', '退費', '通知', '退訂']),
                    'terms': self._extract_rule_text(text, ['租借', '使用規範', '注意事項'])
                }

                data['rules_extracted'] = rules

            except Exception as e:
                print(f'      錯誤: {str(e)[:50]}')

        return data

    def _extract_rule_text(self, text, keywords):
        """從文字中提取特定規則（改進版）"""
        results = []
        sentences = re.split(r'[。；\n]', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 200:
                continue

            for keyword in keywords:
                if keyword in sentence:
                    results.append(sentence)
                    break

        # 返回所有符合的句子
        if results:
            return ' | '.join(results[:3])
        return None

    def _scrape_access_info(self, base_url, access_links):
        """爬取交通資訊頁面"""
        print(f'  交通連結數量: {len(access_links)}')

        data = {
            'links_found': len(access_links),
            'access_info': {}
        }

        for link in access_links[:2]:
            try:
                print(f'    交通頁: {link["text"][:40]}')

                response = self.session.get(link['url'], timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取交通資訊
                access_info = {
                    'mrt': self._extract_mrt_info(soup),
                    'bus': self._extract_bus_info(soup),
                    'parking': self._extract_parking_info(soup),
                    'car': self._extract_car_info(soup)
                }

                if any(access_info.values()):
                    data['access_info'] = access_info

            except Exception as e:
                print(f'      錯誤: {str(e)[:50]}')

        return data

    def _extract_mrt_info(self, soup):
        """提取捷運資訊（改進版）"""
        text = soup.get_text()
        keywords = ['捷運', 'MRT', 'mrt', '站']

        for kw in keywords:
            if kw in text:
                # 找站名和線路
                sentences = re.split(r'[。；\n]', text)
                for sentence in sentences:
                    if '捷運' in sentence or 'MRT' in sentence:
                        # 提取站名
                        station_match = re.search(r'捷運[^\s，。]{2,8}站|MRT[^\s，。]{2,8}Station', sentence)
                        if station_match:
                            return sentence.strip()[:100]

        return None

    def _extract_bus_info(self, soup):
        """提取公車資訊（改進版）"""
        text = soup.get_text()
        keywords = ['公車', 'bus', '路線']

        for kw in keywords:
            if kw in text:
                sentences = re.split(r'[。；\n]', text)
                for sentence in sentences:
                    if '公車' in sentence or 'bus' in sentence.lower():
                        return sentence.strip()[:100]

        return None

    def _extract_parking_info(self, soup):
        """提取停車資訊（改進版）"""
        text = soup.get_text()
        keywords = ['停車', 'parking']

        for kw in keywords:
            if kw in text:
                sentences = re.split(r'[。；\n]', text)
                for sentence in sentences:
                    if '停車' in sentence:
                        return sentence.strip()[:100]

        return None

    def _extract_car_info(self, soup):
        """提取開車資訊（改進版）"""
        text = soup.get_text()
        keywords = ['開車', '國道', '交流道', '高速公路']

        for kw in keywords:
            if kw in text:
                sentences = re.split(r'[。；\n]', text)
                for sentence in sentences:
                    if any(k in sentence for k in keywords):
                        return sentence.strip()[:100]

        return None

    def _scrape_floor_plan(self, base_url, floor_plan_links):
        """爬取平面圖頁面"""
        print(f'  平面圖連結數量: {len(floor_plan_links)}')

        data = {
            'links_found': len(floor_plan_links),
            'floor_plan': {}
        }

        for link in floor_plan_links[:2]:
            try:
                print(f'    平面圖頁: {link["text"][:40]}')

                response = self.session.get(link['url'], timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 尋找圖片
                images = []
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')

                    if '平面' in alt or 'floor' in alt.lower() or '配置' in alt:
                        full_url = urljoin(base_url, src)
                        images.append({
                            'url': full_url,
                            'description': alt
                        })

                if images:
                    data['floor_plan']['images'] = images

                # 提取文字說明
                text = soup.get_text()
                floor_info = self._extract_floor_info(text)
                if floor_info:
                    data['floor_plan']['description'] = floor_info

            except Exception as e:
                print(f'      錯誤: {str(e)[:50]}')

        return data

    def _extract_floor_info(self, text):
        """提取樓層資訊（改進版）"""
        floors = []

        # 尋找樓層資訊
        sentences = re.split(r'[。；\n]', text)
        for sentence in sentences:
            if '樓' in sentence or 'F' in sentence:
                if len(sentence) < 100:
                    floors.append(sentence.strip())

        if floors:
            return floors[:5]

        return None


# 測試三個具體場地
test_cases = [
    {
        'id': 1042,
        'name': '公務人力發展學院',
        'url': 'https://www.hrd.gov.tw',
        'meeting_url': 'https://www.hrd.gov.tw/1122/2141/3157/?nodeId=12634'
    },
    {
        'id': 1049,
        'name': '台北國際展演中心(TWTCA)',
        'url': 'https://www.twtc.com.tw',
        'meeting_url': 'https://www.twtc.com.tw/meeting?p=menu1'
    },
    {
        'id': 1448,
        'name': '台北國際會議中心(TICC)',
        'url': 'https://www.ticc.com.tw/',
        'meeting_url': 'https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueIntroduction.jsp&ctNode=321&CtUnit=98&BaseDSD=7&mp=1',
        'pricing_url': 'https://www.ticc.com.tw/wSite/lp?ctNode=335&CtUnit=109&BaseDSD=7&mp=1',
        'rules_url': 'https://www.ticc.com.tw/wSite/lp?ctNode=336&CtUnit=110&BaseDSD=7&mp=1',
        'access_url': 'https://www.ticc.com.tw/wSite/ct?xItem=922&ctNode=31'
    }
]

scraper = CompleteVenueScraperV2()

print('='*80)
print('深度爬取測試 V2：3個場地')
print('='*80)

results = []

for test_case in test_cases:
    specific_urls = {
        'meeting_url': test_case.get('meeting_url'),
        'pricing_url': test_case.get('pricing_url'),
        'rules_url': test_case.get('rules_url'),
        'access_url': test_case.get('access_url')
    }

    result = scraper.scrape_complete_venue(
        test_case['id'],
        test_case['name'],
        test_case['url'],
        specific_urls
    )
    results.append(result)

    # 休息一下
    import time
    time.sleep(2)

# 儲存結果
with open('deep_scrape_test_v2.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n' + '='*80)
print('測試完成！')
print('詳細結果已儲存到 deep_scrape_test_v2.json')
