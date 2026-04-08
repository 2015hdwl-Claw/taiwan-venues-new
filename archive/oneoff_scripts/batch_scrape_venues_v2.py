#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次爬取場地資料 V2
使用完整六階段流程，重新爬取展演場地、會議中心、婚宴會館
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re
import sys
import io
import time

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class VenueScraperV2:
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
            'skipped': 0
        }

    def scrape_venue(self, venue):
        """爬取單個場地 - 完整六階段流程"""
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
            'scrape_version': 'v2_complete',
            'metadata': {}
        }

        try:
            # 階段 1: 檢測網頁技術類型
            print('[1/7] 檢測網頁技術類型...')
            page_type = self._detect_page_type(url)
            result['metadata']['pageType'] = page_type
            result['metadata']['pageTypeDetectedAt'] = datetime.now().isoformat()
            print(f'    網頁類型: {page_type}')

            # 階段 2: 爬取首頁並發現連結
            print('[2/7] 爬取首頁...')
            homepage_data = self._scrape_homepage(url)
            result['metadata']['homepage_links'] = {
                'meeting': len(homepage_data.get('meeting_links', [])),
                'pricing': len(homepage_data.get('pricing_links', [])),
                'rules': len(homepage_data.get('rules_links', [])),
                'access': len(homepage_data.get('access_links', [])),
                'floor_plan': len(homepage_data.get('floor_plan_links', []))
            }

            # 階段 3: 爬取會議室資料
            print('[3/7] 爬取會議室資料...')
            meeting_data = self._scrape_meeting_rooms(url, homepage_data.get('meeting_links', []))
            if meeting_data.get('rooms'):
                result['rooms'] = meeting_data['rooms']

            # 階段 4: 爬取價格資訊
            print('[4/7] 爬取價格資訊...')
            pricing_data = self._scrape_pricing(homepage_data.get('pricing_links', []))
            if pricing_data.get('prices'):
                result['pricing'] = pricing_data

            # 階段 5: 爬取規則資訊
            print('[5/7] 爬取規則資訊...')
            rules_data = self._scrape_rules(homepage_data.get('rules_links', []))
            if rules_data.get('rules'):
                result['rules'] = rules_data['rules']

            # 階段 6: 爬取交通資訊
            print('[6/7] 爬取交通資訊...')
            access_data = self._scrape_access_info(homepage_data.get('access_links', []))
            if access_data.get('access_info'):
                result['accessInfo'] = access_data['access_info']

            # 階段 7: 爬取平面圖資訊
            print('[7/7] 爬取平面圖資訊...')
            floor_plan_data = self._scrape_floor_plan(homepage_data.get('floor_plan_links', []))
            if floor_plan_data.get('floor_plan'):
                result['floorPlan'] = floor_plan_data['floor_plan']

            # 更新元資料
            result['metadata']['lastScrapedAt'] = datetime.now().isoformat()
            result['metadata']['scrapePages'] = homepage_data.get('scrape_pages', 1)

            result['success'] = True
            self.stats['success'] += 1

            # 摘要
            print(f'✅ 成功')
            print(f'   會議室: {len(meeting_data.get("rooms", []))} 個')
            print(f'   價格: {len(pricing_data.get("prices", []))} 筆')
            print(f'   規則: {len([k for k, v in rules_data.get("rules", {}).items() if v])} 項')
            print(f'   交通: {"有" if access_data.get("access_info") else "無"}')
            print(f'   平面圖: {"有" if floor_plan_data.get("floor_plan") else "無"}')

        except Exception as e:
            print(f'❌ 錯誤: {str(e)[:100]}')
            result['success'] = False
            result['error'] = str(e)
            self.stats['failed'] += 1

        self.stats['total'] += 1
        return result

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
                'meeting_links': [],
                'pricing_links': [],
                'rules_links': [],
                'access_links': [],
                'floor_plan_links': [],
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

            # 規則相關
            rules_keywords = ['規則', '規範', '須知', '租借', '使用']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text or kw in href for kw in rules_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['rules_links'].append({'text': text, 'url': full_url})

            # 交通相關
            access_keywords = ['交通', '位置', 'access', 'location', '捷運', '停車']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text or kw in href for kw in access_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['access_links'].append({'text': text, 'url': full_url})

            # 平面圖相關
            floor_plan_keywords = ['平面圖', '導覽', 'floor plan', '樓層', '配置']
            for a in all_links:
                text = a.get_text().strip()
                href = a['href']

                if any(kw in text or kw in href for kw in floor_plan_keywords):
                    if 0 < len(text) < 100:
                        full_url = urljoin(url, href)
                        data['floor_plan_links'].append({'text': text, 'url': full_url})

            # 去重
            for key in ['meeting_links', 'pricing_links', 'rules_links', 'access_links', 'floor_plan_links']:
                seen = set()
                unique_links = []
                for link in data[key]:
                    if link['url'] not in seen:
                        seen.add(link['url'])
                        unique_links.append(link)
                data[key] = unique_links[:5]  # 最多5個

            print(f'    會議: {len(data["meeting_links"])}, 價格: {len(data["pricing_links"])}, 規則: {len(data["rules_links"])}, 交通: {len(data["access_links"])}, 平面圖: {len(data["floor_plan_links"])}')

            return data

        except Exception as e:
            print(f'    錯誤: {str(e)[:50]}')
            return {}

    def _scrape_meeting_rooms(self, base_url, meeting_links):
        """爬取會議室資料"""
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

    def _scrape_floor_plan(self, floor_plan_links):
        """爬取平面圖資訊"""
        floor_plan = {}

        for link in floor_plan_links[:2]:
            try:
                response = self.session.get(link['url'], timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')

                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')

                    if '平面' in alt or 'floor' in alt.lower():
                        floor_plan['url'] = src
                        floor_plan['description'] = alt
                        break

            except:
                pass

        return {'floor_plan': floor_plan} if floor_plan else {}


def main():
    # 讀取 venues.json
    print('載入 venues.json...')
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 篩選目標場地
    target_venues = []
    for v in venues:
        if v.get('status') == 'discontinued':
            continue

        vtype = v.get('venueType', '')

        if '會議中心' in vtype or '展演' in vtype or '婚宴' in vtype or '宴會' in vtype or '飯店' in vtype:
            target_venues.append(v)

    print(f'找到 {len(target_venues)} 個目標場地')
    print('='*80)

    # 創建爬蟲
    scraper = VenueScraperV2()

    # 分批爬取：每次 10 個場地
    print('\n分批爬取階段：每次處理 10 個場地')
    print('='*80)

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
        backup_file = f'venues.json.backup.batch_v2_batch{batch_num + 1}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        import shutil
        shutil.copy('venues.json', backup_file)
        print(f'批次備份: {backup_file}')

        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)

    results = all_results

    # 儲存報告
    report = {
        'scraped_at': datetime.now().isoformat(),
        'statistics': scraper.stats,
        'results': results
    }

    with open('batch_venue_scrape_v2_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 儲存結果
    backup_file = f'venues.json.backup.batch_v2_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    import shutil
    shutil.copy('venues.json', backup_file)
    print(f'\n備份: {backup_file}')

    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    # 儲存報告
    report = {
        'scraped_at': datetime.now().isoformat(),
        'statistics': scraper.stats,
        'results': results
    }

    with open('batch_venue_scrape_v2_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('\n' + '='*80)
    print('批次爬取完成！')
    print('='*80)
    print(f'統計: {scraper.stats}')
    print(f'報告: batch_venue_scrape_v2_report.json')
    print(f'備份: {backup_file}')


if __name__ == '__main__':
    main()
