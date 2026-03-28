#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 專用爬蟲
針對 TICC (台北國際會議中心) 的 WordPress 網站
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urljoin
import re
import sys
import io

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class WordPressVenueScraper:
    def __init__(self):
        self.session = requests.Session()
        # 使用完整的瀏覽器 headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })

    def scrape_ticc_complete(self):
        """完整爬取 TICC 所有資料"""

        print('='*80)
        print('TICC WordPress 專用爬蟲')
        print('='*80)

        result = {
            'id': 1448,
            'name': '台北國際會議中心(TICC)',
            'url': 'https://www.ticc.com.tw/',
            'scraped_at': datetime.now().isoformat(),
            'data': {}
        }

        # TICC 的所有重要頁面
        pages = {
            '會議室資料': 'https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueIntroduction.jsp&ctNode=321&CtUnit=98&BaseDSD=7&mp=1',
            '場地查詢': 'https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueSearch.jsp&ctNode=322&CtUnit=99&BaseDSD=7&mp=1',
            '價目表': 'https://www.ticc.com.tw/wSite/lp?ctNode=335&CtUnit=109&BaseDSD=7&mp=1',
            '租借規範': 'https://www.ticc.com.tw/wSite/lp?ctNode=336&CtUnit=110&BaseDSD=7&mp=1',
            '交通資訊': 'https://www.ticc.com.tw/wSite/ct?xItem=922&ctNode=31',
            '場地導覽': 'https://www.ticc.com.tw/wSite/np?ctNode=320&mp=1'
        }

        # 爬取各個頁面
        for page_name, url in pages.items():
            print(f'\n[爬取] {page_name}')
            print(f'  URL: {url}')

            try:
                response = self.session.get(url, timeout=15, verify=False)
                print(f'  狀態: {response.status_code}')

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 根據頁面類型擷取資料
                    if page_name == '會議室資料':
                        data = self._extract_meeting_rooms(soup, url)
                        result['data']['meeting_rooms'] = data
                    elif page_name == '價目表':
                        data = self._extract_pricing(soup, url)
                        result['data']['pricing'] = data
                    elif page_name == '租借規範':
                        data = self._extract_rules(soup, url)
                        result['data']['rules'] = data
                    elif page_name == '交通資訊':
                        data = self._extract_access_info(soup, url)
                        result['data']['access'] = data
                    elif page_name == '場地導覽':
                        data = self._extract_floor_plan(soup, url)
                        result['data']['floor_plan'] = data

                    print(f'  ✅ 成功')

                else:
                    print(f'  ❌ HTTP {response.status_code}')

            except Exception as e:
                print(f'  ❌ 錯誤: {str(e)[:80]}')

        result['success'] = True

        return result

    def _extract_meeting_rooms(self, soup, page_url):
        """擷取會議室資料"""
        rooms = []

        # WordPress 常見的結構
        # 1. 尋找包含「會議室」、「場地」的元素
        room_keywords = ['會議室', '會場', '廳', 'Room', 'Hall']

        # 方法 1: 尋找卡片或列表項目
        for elem in soup.find_all(['div', 'li', 'article']):
            # 檢查 class 屬性
            classes = ' '.join(elem.get('class', []))

            if any(kw in classes or kw in elem.get_text() for kw in room_keywords):
                # 提取會議室名稱
                for tag in elem.find_all(['h1', 'h2', 'h3', 'h4', 'strong']):
                    name = tag.get_text().strip()
                    if name and len(name) < 100 and any(kw in name for kw in room_keywords):
                        # 擷取詳細資訊
                        room_info = self._extract_room_details(elem)

                        rooms.append({
                            'name': name,
                            'source': page_url,
                            'floor': room_info.get('floor', ''),
                            'area': room_info.get('area', ''),
                            'capacity': room_info.get('capacity', ''),
                            'equipment': room_info.get('equipment', ''),
                            'description': room_info.get('description', '')
                        })
                        break

        # 方法 2: 尋找表格
        if not rooms:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # 跳過標題列
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        name = cells[0].get_text().strip()
                        if name and any(kw in name for kw in room_keywords):
                            rooms.append({
                                'name': name,
                                'source': page_url,
                                'description': cells[1].get_text().strip() if len(cells) > 1 else ''
                            })

        return {
            'total_rooms_found': len(rooms),
            'rooms': rooms
        }

    def _extract_room_details(self, elem):
        """從元素中提取會議室詳細資訊"""
        info = {}
        text = elem.get_text()

        # 提取樓層
        floor_match = re.search(r'(\d+[F樓層]|[B1-B]\s*F)', text)
        if floor_match:
            info['floor'] = floor_match.group(1)

        # 提取容量
        capacity_match = re.search(r'容[納量]*[：:]\s*(\d+)', text)
        if capacity_match:
            info['capacity'] = capacity_match.group(1)

        # 提取面積
        area_match = re.search(r'面積[：:]\s*([\d.]+\s*坪|[\d.]+\s*m²)', text)
        if area_match:
            info['area'] = area_match.group(1)

        # 提取設備
        equipment_keywords = ['投影機', '麥克風', '音響', '螢幕', '白板', '擴音']
        equipment_found = []
        for kw in equipment_keywords:
            if kw in text:
                equipment_found.append(kw)
        if equipment_found:
            info['equipment'] = ', '.join(equipment_found)

        # 提取描述（前 500 字）
        info['description'] = text[:500].strip()

        return info

    def _extract_pricing(self, soup, page_url):
        """擷取價格資訊"""
        prices = []

        # 尋找所有價格相關的段落
        text = soup.get_text()

        # 價格模式
        price_patterns = [
            r'NT\$?\s*([\d,]+)\s*元',
            r'([\d,]+)\s*元',
            r'[\$]([\d,]+)',
            r'(\d{4,6})\s*元'
        ]

        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 清理價格字串
                price = match.replace(',', '').replace('NT$', '').replace('$', '').strip()
                if price.isdigit() and len(price) >= 3:
                    prices.append(price)

        # 去重
        prices = list(set(prices))[:20]

        return {
            'total_prices_found': len(prices),
            'prices': prices
        }

    def _extract_rules(self, soup, page_url):
        """擷取規則資訊"""
        rules = {
            'catering': None,
            'smoking': None,
            'decoration': None,
            'noise': None,
            'cleanup': None,
            'deposit': None,
            'cancellation': None,
            'terms': []
        }

        text = soup.get_text()

        # 提取各類規則
        rule_keywords = {
            'catering': ['餐飲', '食物', '外食', '自備'],
            'smoking': ['吸菸', '禁菸', '抽菸'],
            'decoration': ['佈置', '裝潢', '釘子', '貼紙'],
            'noise': ['噪音', '音量', '分貝'],
            'cleanup': ['清理', '復原', '歸還'],
            'deposit': ['押金', '保證金'],
            'cancellation': ['取消', '退費', '退訂']
        }

        for rule_type, keywords in rule_keywords.items():
            sentences = re.split(r'[。；\n]', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if 20 <= len(sentence) <= 200:
                    if any(kw in sentence for kw in keywords):
                        if not rules[rule_type]:
                            rules[rule_type] = sentence
                        elif len(rules[rule_type]) < 200:
                            rules[rule_type] += ' | ' + sentence

        # 提取完整條款
        paragraphs = soup.find_all(['p', 'div'])
        for p in paragraphs:
            p_text = p.get_text().strip()
            if 50 <= len(p_text) <= 500:
                if any(kw in p_text for kw in ['租借', '使用', '須知', '注意']):
                    rules['terms'].append(p_text[:300])

        rules['terms'] = rules['terms'][:5]

        return rules

    def _extract_access_info(self, soup, page_url):
        """擷取交通資訊"""
        access = {
            'mrt': None,
            'bus': None,
            'parking': None,
            'car': None
        }

        text = soup.get_text()

        # 捷運
        mrt_sentences = re.split(r'[。；\n]', text)
        for sentence in mrt_sentences:
            if '捷運' in sentence or 'MRT' in sentence:
                access['mrt'] = sentence.strip()[:100]
                break

        # 公車
        for sentence in mrt_sentences:
            if '公車' in sentence:
                access['bus'] = sentence.strip()[:100]
                break

        # 停車
        for sentence in mrt_sentences:
            if '停車' in sentence:
                access['parking'] = sentence.strip()[:100]
                break

        # 開車
        for sentence in mrt_sentences:
            if any(kw in sentence for kw in ['開車', '國道', '交流道']):
                access['car'] = sentence.strip()[:100]
                break

        return access

    def _extract_floor_plan(self, soup, page_url):
        """擷取平面圖資訊"""
        floor_plan = {
            'images': [],
            'description': None
        }

        # 尋找圖片
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')

            if '平面' in alt or 'floor' in alt.lower() or '配置' in alt:
                floor_plan['images'].append({
                    'url': urljoin(page_url, src),
                    'description': alt
                })

        # 提取文字描述
        text = soup.get_text()
        if '樓層' in text or '平面' in text:
            floor_plan['description'] = text[:500]

        return floor_plan


# 執行爬蟲
scraper = WordPressVenueScraper()

result = scraper.scrape_ticc_complete()

# 儲存結果
with open('ticc_wordpress_scrape_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n' + '='*80)
print('TICC 爬取完成！')
print('結果已儲存到 ticc_wordpress_scrape_result.json')
print('='*80)

# 顯示摘要
print('\n【摘要】')
print(f'會議室數量: {result["data"].get("meeting_rooms", {}).get("total_rooms_found", 0)}')
print(f'價格數量: {result["data"].get("pricing", {}).get("total_prices_found", 0)}')
print(f'規則類型: {len([k for k, v in result["data"].get("rules", {}).items() if v and k != "terms"])}')
print(f'交通資訊: {"✅ 有" if result["data"].get("access") else "❌ 無"}')
print(f'平面圖: {"✅ 有" if result["data"].get("floor_plan") else "❌ 無"}')
