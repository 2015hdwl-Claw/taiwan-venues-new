#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3 場地爬蟲 - 完整版
支援功能：
1. PDF 發現與解析
2. 深入會議室詳細頁面
3. URL 驗證與自動修正
4. 表格解析器
5. 完整六階段流程
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import re
import sys
import io
import time
import PyPDF2
import urllib3

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VenueScraperV3:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        })

        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'pdfs_found': 0,
            'pdfs_parsed': 0,
            'detail_pages_found': 0,
            'tables_parsed': 0
        }

    def scrape_venue(self, venue):
        """爬取單個場地 - V3 完整流程"""
        vid = venue['id']
        name = venue['name']
        url = venue.get('url', '')

        if not url:
            return {'id': vid, 'success': False, 'error': 'No URL', 'skipped': True}

        print(f'\n[{self.stats["success"] + 1}] ID {vid}: {name}')
        print(f'URL: {url}')
        print('-' * 60)

        result = {
            'id': vid,
            'scraped_at': datetime.now().isoformat(),
            'scrape_version': 'v3_complete',
            'metadata': {}
        }

        try:
            # 階段 1: URL 驗證與修正
            print('[1/9] URL 驗證與修正...')
            url = self._validate_and_fix_url(url, venue)
            result['metadata']['validated_url'] = url

            # 階段 2: 檢測網頁技術類型
            print('[2/9] 檢測網頁技術類型...')
            page_type = self._detect_page_type(url)
            result['metadata']['pageType'] = page_type
            result['metadata']['pageTypeDetectedAt'] = datetime.now().isoformat()
            print(f'    網頁類型: {page_type}')

            # 階段 3: 爬取首頁並發現連結
            print('[3/9] 爬取首頁...')
            homepage_data = self._scrape_homepage(url)
            result['metadata']['homepage_links'] = {
                'meeting': len(homepage_data.get('meeting_links', [])),
                'pricing': len(homepage_data.get('pricing_links', [])),
                'rules': len(homepage_data.get('rules_links', [])),
                'access': len(homepage_data.get('access_links', [])),
                'floor_plan': len(homepage_data.get('floor_plan_links', []))
            }

            # 階段 4: 發現並解析 PDF
            print('[4/9] 發現並解析 PDF...')
            pdf_data = self._discover_and_parse_pdfs(url, homepage_data)
            if pdf_data.get('rooms'):
                result['rooms'] = pdf_data['rooms']
                result['metadata']['pdf_source'] = True
                self.stats['pdfs_parsed'] += 1
            print(f'    PDF 數量: {len(pdf_data.get("pdfs", []))} 個')
            print(f'    PDF 會議室: {len(pdf_data.get("rooms", []))} 個')

            # 階段 5: 深入會議室詳細頁面
            print('[5/9] 深入會議室詳細頁面...')
            detail_data = self._scrape_meeting_detail_pages(url, homepage_data)
            if detail_data.get('rooms'):
                # 合併 PDF 和詳細頁面的會議室資料
                existing_rooms = result.get('rooms', [])
                result['rooms'] = self._merge_rooms(existing_rooms, detail_data['rooms'])
                self.stats['detail_pages_found'] += len(detail_data.get('pages', []))
            print(f'    詳細頁面: {len(detail_data.get("pages", []))} 個')
            print(f'    詳細頁會議室: {len(detail_data.get("rooms", []))} 個')

            # 階段 6: 爬取會議室資料（一般頁面）
            if 'rooms' not in result:
                print('[6/9] 爬取會議室資料...')
                meeting_data = self._scrape_meeting_rooms(url, homepage_data.get('meeting_links', []))
                if meeting_data.get('rooms'):
                    result['rooms'] = meeting_data['rooms']

            # 階段 7: 爬取價格資訊
            print('[7/9] 爬取價格資訊...')
            pricing_data = self._scrape_pricing(homepage_data.get('pricing_links', []))
            if pricing_data.get('prices'):
                result['pricing'] = pricing_data

            # 階段 8: 爬取規則資訊
            print('[8/9] 爬取規則資訊...')
            rules_data = self._scrape_rules(homepage_data.get('rules_links', []))
            if rules_data.get('rules'):
                result['rules'] = rules_data['rules']

            # 階段 9: 爬取交通資訊
            print('[9/9] 爬取交通資訊...')
            access_data = self._scrape_access_info(homepage_data.get('access_links', []))
            if access_data.get('access_info'):
                result['accessInfo'] = access_data['access_info']

            # 更新元資料
            result['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            result['metadata']['scrapePages'] = homepage_data.get('scrape_pages', 1)

            result['success'] = True
            self.stats['success'] += 1

            # 摘要
            print(f'✅ 成功')
            print(f'   會議室: {len(result.get("rooms", []))} 個')
            print(f'   價格: {len(result.get("pricing", {}).get("prices", []))} 筆')
            print(f'   規則: {len([k for k, v in result.get("rules", {}).items() if v])} 項')
            print(f'   交通: {"有" if result.get("accessInfo") else "無"}')

        except Exception as e:
            print(f'❌ 錯誤: {str(e)[:100]}')
            result['success'] = False
            result['error'] = str(e)
            self.stats['failed'] += 1

        self.stats['total'] += 1
        return result

    def _validate_and_fix_url(self, url, venue):
        """驗證並自動修正 URL"""
        vid = venue.get('id')

        # 檢查 HTTP 狀態
        try:
            response = self.session.head(url, timeout=5, verify=False)

            if response.status_code == 404:
                print(f'    ⚠️  HTTP 404，嘗試自動修正...')

                # 集思會議中心修正
                if vid in [1495, 1496, 1497, 1498, 1499]:
                    url_fixes = {
                        1495: 'https://www.meeting.com.tw/ntut/',
                        1496: 'https://www.meeting.com.tw/hsp/',
                        1497: 'https://www.meeting.com.tw/tc/',
                        1498: 'https://www.meeting.com.tw/wuri/',
                        1499: 'https://www.meeting.com.tw/khh/',
                    }
                    if vid in url_fixes:
                        new_url = url_fixes[vid]
                        test_resp = self.session.head(new_url, timeout=5, verify=False)
                        if test_resp.status_code == 200:
                            print(f'    ✅ 修正URL: {new_url}')
                            return new_url

                # 通用修正嘗試
                fixes = [
                    url.rstrip('/') + '/index.php',
                    url.rstrip('/') + '/meeting',
                    url.rstrip('/') + '/rooms',
                ]

                for fix_url in fixes:
                    try:
                        test_resp = self.session.head(fix_url, timeout=5, verify=False)
                        if test_resp.status_code == 200:
                            print(f'    ✅ 修正URL: {fix_url}')
                            return fix_url
                    except:
                        pass

        except Exception as e:
            print(f'    ⚠️  URL 驗證失敗: {str(e)[:50]}')

        return url

    def _detect_page_type(self, url):
        """檢測網頁技術類型"""
        try:
            # 檢查 WordPress API
            api_url = urljoin(url, '/wp-json/wp/v2/pages')
            api_resp = self.session.get(api_url, timeout=5, verify=False)
            if api_resp.status_code == 200:
                return 'WordPress API'
        except:
            pass

        try:
            # 檢查靜態內容
            resp = self.session.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = soup.get_text().lower()

            if 'react' in text or 'vue' in text or 'angular' in text:
                return 'JavaScript (SPA)'
            else:
                return 'Static/SSR'
        except:
            return 'Unknown'

    def _scrape_homepage(self, url):
        """爬取首頁，發現所有連結"""
        try:
            response = self.session.get(url, timeout=15, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')

            data = {
                'soup': soup,  # 保存 soup 供後續使用
                'meeting_links': [],
                'pricing_links': [],
                'rules_links': [],
                'access_links': [],
                'floor_plan_links': [],
                'pdf_links': [],
                'scrape_pages': 1
            }

            all_links = soup.find_all('a', href=True)

            # 會議室相關
            meeting_keywords = ['會議', 'meeting', '會議室', '場地', 'space', 'room', 'venue']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text.lower() or kw in href.lower() for kw in meeting_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['meeting_links'].append({'text': text, 'url': full_url})

            # 價格相關
            pricing_keywords = ['價目', '價格', '收費', 'rate']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text or kw in href for kw in pricing_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['pricing_links'].append({'text': text, 'url': full_url})

            # PDF 連結
            for a in all_links:
                href = a['href'].lower()
                if href.endswith('.pdf') or 'pdf' in href:
                    full_url = urljoin(url, a['href'])
                    text = a.get_text().strip()
                    data['pdf_links'].append({'text': text, 'url': full_url})

            # 規則、交通、平面圖連結
            rules_keywords = ['規則', '規範', '須知', '租借', '使用']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']
                if any(kw in text or kw in href for kw in rules_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['rules_links'].append({'text': text, 'url': full_url})

            access_keywords = ['交通', '位置', 'access', 'location', '捷運', '停車']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']
                if any(kw in text or kw in href for kw in access_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['access_links'].append({'text': text, 'url': full_url})

            floor_plan_keywords = ['平面圖', '導覽', 'floor plan', '樓層', '配置']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']
                if any(kw in text or kw in href for kw in floor_plan_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['floor_plan_links'].append({'text': text, 'url': full_url})

            # 去重
            for key in ['meeting_links', 'pricing_links', 'rules_links', 'access_links', 'floor_plan_links', 'pdf_links']:
                seen = set()
                unique_links = []
                for link in data[key]:
                    if link['url'] not in seen:
                        seen.add(link['url'])
                        unique_links.append(link)
                data[key] = unique_links[:5]  # 最多5個

            self.stats['pdfs_found'] += len(data['pdf_links'])

            return data

        except Exception as e:
            print(f'    錯誤: {str(e)[:50]}')
            return {}

    def _discover_and_parse_pdfs(self, base_url, homepage_data):
        """發現並解析 PDF"""
        pdf_links = homepage_data.get('pdf_links', [])
        rooms_from_pdfs = []

        for pdf in pdf_links:
            try:
                print(f'    解析 PDF: {pdf["text"][:40]}')
                rooms = self._parse_pdf(pdf['url'])
                rooms_from_pdfs.extend(rooms)
                self.stats['pdfs_parsed'] += 1
            except Exception as e:
                print(f'    PDF 解析失敗: {str(e)[:50]}')

        return {
            'pdfs': pdf_links,
            'rooms': rooms_from_pdfs
        }

    def _parse_pdf(self, pdf_url):
        """解析 PDF 文件"""
        try:
            response = self.session.get(pdf_url, timeout=30, verify=False)
            pdf_file = io.BytesIO(response.content)

            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            # 簡單解析（尋找會議室相關行）
            rooms = []
            lines = text.split('\n')

            for line in lines:
                # 識別會議室（簡化版，實際應根據場地格式調整）
                if re.search(r'會議室|廳|全室', line):
                    # 提取數字（容量、面積等）
                    numbers = re.findall(r'[\d,]+', line)
                    if len(numbers) >= 2:
                        room = {
                            'name': line[:30].strip(),
                            'capacity': numbers[0].replace(',', ''),
                            'area': numbers[1] if len(numbers) > 1 else None,
                            'source': 'pdf'
                        }
                        rooms.append(room)

            return rooms

        except Exception as e:
            print(f'    PDF 錯誤: {str(e)[:50]}')
            return []

    def _scrape_meeting_detail_pages(self, base_url, homepage_data):
        """深入爬取會議室詳細頁面"""
        detail_pages = []
        rooms_from_details = []

        # 從會議室連結中尋找詳細頁面
        meeting_links = homepage_data.get('meeting_links', [])

        for link in meeting_links:
            url = link['url']

            # 識別詳細頁面模式
            if re.search(r'/meeting\d*$', url) or re.search(r'/room/', url):
                try:
                    print(f'    深入頁面: {url}')
                    response = self.session.get(url, timeout=10, verify=False)
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 尋找表格
                    tables = soup.find_all('table')
                    for table in tables:
                        room = self._parse_meeting_table(soup, table)
                        if room:
                            rooms_from_details.append(room)
                            self.stats['tables_parsed'] += 1

                    detail_pages.append(url)

                except Exception as e:
                    print(f'    錯誤: {str(e)[:50]}')

        return {
            'pages': detail_pages,
            'rooms': rooms_from_details
        }

    def _parse_meeting_table(self, soup, table):
        """解析會議室表格"""
        try:
            rows = table.find_all('tr')
            if len(rows) < 2:
                return None

            # 尋找會議室名稱（通常是 h1 或 h2）
            name_elem = soup.find(['h1', 'h2'])
            name = name_elem.get_text().strip() if name_elem else "Unknown"

            room = {
                'name': name,
                'source': 'detail_page_table'
            }

            # 解析表格內容（簡化版）
            for row in rows[1:]:  # 跳過標題列
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    for cell in cells:
                        text = cell.get_text().strip()
                        # 尋找容量
                        if re.search(r'\d+\s*人', text):
                            match = re.search(r'(\d+)\s*人', text)
                            if match:
                                room['capacity'] = match.group(1)
                        # 尋找面積
                        if re.search(r'[\d.]+\s*(坪|㎡|m²|平方公尺)', text):
                            match = re.search(r'([\d.]+)\s*(坪|㎡|m²|平方公尺)', text)
                            if match:
                                room['area'] = match.group(1) + ' ' + match.group(2)

            return room if len(room) > 2 else None

        except Exception as e:
            return None

    def _merge_rooms(self, rooms1, rooms2):
        """合併兩組會議室資料"""
        # 簡單合併，實際應該根據名稱去重
        all_rooms = list(rooms1) if rooms1 else []
        if rooms2:
            all_rooms.extend(rooms2)
        return all_rooms

    def _scrape_meeting_rooms(self, base_url, meeting_links):
        """爬取會議室資料（一般頁面）"""
        rooms = []

        if not meeting_links:
            return {'rooms': rooms}

        for i, link in enumerate(meeting_links[:3], 1):
            try:
                response = self.session.get(link['url'], timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 尋找會議室
                room_keywords = ['會議室', '教室', '廳', 'Room', 'Hall']

                for elem in soup.find_all(['div', 'section', 'li', 'td']):
                    text = elem.get_text().strip()

                    if any(kw in text for kw in room_keywords):
                        # 提取會議室名稱
                        for tag in elem.find_all(['h1', 'h2', 'h3', 'strong', 'b']):
                            name = tag.get_text().strip()
                            if name and len(name) < 100 and any(kw in name for kw in room_keywords):
                                room_info = self._extract_room_info(elem)

                                rooms.append({
                                    'name': name,
                                    'floor': room_info.get('floor', ''),
                                    'capacity': room_info.get('capacity', ''),
                                    'area': room_info.get('area', ''),
                                    'equipment': room_info.get('equipment', '')
                                })
                                break

            except Exception as e:
                pass

        return {'rooms': rooms}

    def _extract_room_info(self, elem):
        """從元素中提取會議室資訊"""
        info = {}
        text = elem.get_text()

        # 樓層
        floor_match = re.search(r'(\d+[F樓層]|[B1-B]\s*F)', text)
        if floor_match:
            info['floor'] = floor_match.group(1)

        # 容量
        capacity_match = re.search(r'容[納量]*[：:]\s*(\d+)', text)
        if capacity_match:
            info['capacity'] = capacity_match.group(1)

        # 面積
        area_match = re.search(r'面積[：:]\s*([\d.]+\s*坪|[\d.]+\s*m²)', text)
        if area_match:
            info['area'] = area_match.group(1)

        # 設備
        equipment_keywords = ['投影機', '麥克風', '音響', '螢幕', '白板']
        equipment_found = [kw for kw in equipment_keywords if kw in text]
        if equipment_found:
            info['equipment'] = ', '.join(equipment_found)

        return info

    def _scrape_pricing(self, pricing_links):
        """爬取價格資訊"""
        prices = []

        for link in pricing_links[:2]:
            try:
                response = self.session.get(link['url'], timeout=10, verify=False)
                text = response.text

                price_patterns = [
                    r'NT\$?\s*([\d,]+)',
                    r'([\d,]+)\s*元',
                    r'(\d{4,6})\s*元'
                ]

                for pattern in price_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        clean_price = match.replace(',', '').replace('NT$', '').replace('$', '').strip()
                        if clean_price.isdigit() and len(clean_price) >= 3:
                            prices.append(clean_price)

            except:
                pass

        return {'prices': list(set(prices))[:10]}

    def _scrape_rules(self, rules_links):
        """爬取規則資訊"""
        rules = {}

        rule_keywords = {
            'catering': ['餐飲', '食物'],
            'smoking': ['吸菸', '禁菸'],
            'decoration': ['佈置', '裝潢'],
            'cleanup': ['清理', '復原'],
            'deposit': ['押金', '保證金']
        }

        for link in rules_links[:2]:
            try:
                response = self.session.get(link['url'], timeout=10, verify=False)
                text = response.text

                for rule_type, keywords in rule_keywords.items():
                    if rule_type not in rules:
                        sentences = re.split(r'[。；\n]', text)
                        for sentence in sentences:
                            if any(kw in sentence for kw in keywords):
                                rules[rule_type] = sentence.strip()[:100]
                                break

            except:
                pass

        return {'rules': rules}

    def _scrape_access_info(self, access_links):
        """爬取交通資訊"""
        access_info = {}

        for link in access_links[:2]:
            try:
                response = self.session.get(link['url'], timeout=10, verify=False)
                text = response.text

                # 捷運
                if 'mrt' not in access_info and '捷運' in text:
                    sentences = re.split(r'[。；\n]', text)
                    for sentence in sentences:
                        if '捷運' in sentence:
                            access_info['mrt'] = sentence.strip()[:100]
                            break

                # 公車
                if 'bus' not in access_info and '公車' in text:
                    sentences = re.split(r'[。；\n]', text)
                    for sentence in sentences:
                        if '公車' in sentence:
                            access_info['bus'] = sentence.strip()[:100]
                            break

                # 停車
                if 'parking' not in access_info and '停車' in text:
                    sentences = re.split(r'[。；\n]', text)
                    for sentence in sentences:
                        if '停車' in sentence:
                            access_info['parking'] = sentence.strip()[:100]
                            break

            except:
                pass

        return {'access_info': access_info} if access_info else {}


def main():
    # 讀取 venues.json
    print('載入 venues.json...')
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 篩選會展中心和會議中心
    target_venues = []
    for v in venues:
        if v.get('status') == 'discontinued':
            continue

        vtype = v.get('venueType', '')

        if '會展中心' in vtype or '會議中心' in vtype or '展覽' in vtype:
            target_venues.append(v)

    print(f'找到 {len(target_venues)} 個目標場地（會展中心、會議中心）')
    print('='*80)

    # 創建爬蟲
    scraper = VenueScraperV3()

    # 分批爬取
    batch_size = 10
    total_batches = (len(target_venues) + batch_size - 1) // batch_size

    all_results = []

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(target_venues))
        current_batch = target_venues[start_idx:end_idx]

        print(f'\n批次 {batch_num + 1}/{total_batches}：場地 {start_idx + 1}-{end_idx}')
        print('='*80)

        batch_results = []

        for venue in current_batch:
            result = scraper.scrape_venue(venue)
            batch_results.append(result)

            # 更新 venues.json
            for i, v in enumerate(venues):
                if v['id'] == result['id']:
                    for key, value in result.items():
                        if key != 'id':
                            v[key] = value
                    break

            # 休息一下避免被封鎖
            time.sleep(2)

        all_results.extend(batch_results)

        # 每批次後儲存一次
        print(f'\n批次 {batch_num + 1} 完成，已處理 {len(all_results)}/{len(target_venues)} 個場地')

        # 備份
        backup_file = f'venues.json.backup.v3_batch{batch_num + 1}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        import shutil
        shutil.copy('venues.json', backup_file)
        print(f'批次備份: {backup_file}')

        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)

    # 儲存報告
    report = {
        'scraped_at': datetime.now().isoformat(),
        'statistics': scraper.stats,
        'results': all_results
    }

    with open('batch_venue_scrape_v3_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 最後備份
    backup_file = f'venues.json.backup.v3_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy('venues.json', backup_file)
    print(f'\n備份: {backup_file}')

    print('\n' + '='*80)
    print('V3 批次爬取完成！')
    print('='*80)
    print(f'統計: {scraper.stats}')
    print(f'報告: batch_venue_scrape_v3_report.json')
    print(f'備份: {backup_file}')


if __name__ == '__main__':
    main()
