#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網頁技術檢測工具 - Top 10 場地

檢測場地官網的技術類型，決定使用哪一種爬蟲方法
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class TechDetector:
    """網頁技術檢測器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def detect(self, url, venue_id, venue_name):
        """檢測單一場地"""
        print(f'\n[{venue_id}] {venue_name[:40]}')
        print(f'URL: {url}')
        print('-' * 70)

        result = {
            'id': venue_id,
            'name': venue_name,
            'url': url,
            'status': None,
            'type': None,
            'loading': None,
            'data_location': None,
            'has_pdf': False,
            'recommendation': None
        }

        try:
            # 1. 檢測 HTTP 狀態碼
            print('[1/5] 檢測 HTTP 狀態碼...')
            response = self.session.head(url, timeout=10, allow_redirects=True)
            result['status'] = response.status_code
            print(f'      HTTP {response.status_code}: {self._get_status_meaning(response.status_code)}')

            if response.status_code != 200:
                result['recommendation'] = 'URL 錯誤，需要手動確認'
                return result

            # 2. 檢測網頁類型
            print('[2/5] 檢測網頁技術類型...')
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 檢查 WordPress
            is_wordpress = self._check_wordpress(soup, url)
            is_javascript = self._check_javascript(soup)
            is_static = not is_wordpress and not is_javascript

            if is_wordpress:
                result['type'] = 'WordPress'
                print(f'      類型: WordPress')
            elif is_javascript:
                result['type'] = 'JavaScript/SPA'
                print(f'      類型: JavaScript (可能需要 Playwright)')
            else:
                result['type'] = 'Static HTML'
                print(f'      類型: Static HTML')

            # 3. 檢測內容載入方式
            print('[3/5] 檢測內容載入方式...')
            script_count = len(soup.find_all('script'))
            has_react = 'react' in response.text.lower()
            has_vue = 'vue' in response.text.lower()
            has_ajax = any(['ajax' in s.get('src', '').lower() for s in soup.find_all('script')])

            if has_react or has_vue:
                result['loading'] = 'Dynamic/SPA'
                print(f'      載入: 動態 (React/Vue)')
            elif has_ajax:
                result['loading'] = 'AJAX'
                print(f'      載入: AJAX')
            else:
                result['loading'] = 'Server-side'
                print(f'      載入: 伺服器端渲染')

            # 4. 檢測資料位置
            print('[4/5] 檢測資料位置...')
            data_location = self._detect_data_location(soup, url)
            result['data_location'] = data_location

            if data_location == 'homepage':
                print(f'      位置: 主頁已有完整資料 ✨')
            elif data_location == 'meeting_page':
                print(f'      位置: 需要深入會議頁')
            elif data_location == 'detail_page':
                print(f'      位置: 需要深入詳情頁 ⭐')
            else:
                print(f'      位置: 不確定')

            # 5. 檢測 PDF
            print('[5/5] 檢測 PDF 連結...')
            pdf_links = self._find_pdfs(soup, url)
            result['has_pdf'] = len(pdf_links) > 0

            if pdf_links:
                print(f'      PDF: 找到 {len(pdf_links)} 個 PDF 連結')
                for pdf in pdf_links[:3]:
                    print(f'           - {pdf[:80]}')
            else:
                print(f'      PDF: 未找到')

            # 6. 生成建議
            result['recommendation'] = self._generate_recommendation(result)
            print(f'\n建議: {result["recommendation"]}')

        except requests.exceptions.Timeout:
            result['status'] = 'Timeout'
            print('      ❌ 連線超時')
            result['recommendation'] = '連線超時，稍後重試'

        except requests.exceptions.ConnectionError:
            result['status'] = 'Connection Error'
            print('      ❌ 無法連線')
            result['recommendation'] = 'URL 錯誤或網站不存在'

        except Exception as e:
            result['status'] = 'Error'
            print(f'      ❌ 錯誤: {str(e)[:50]}')
            result['recommendation'] = f'發生錯誤: {str(e)[:50]}'

        return result

    def _get_status_meaning(self, status_code):
        """HTTP 狀態碼說明"""
        meanings = {
            200: '正常',
            301: '永久重定向',
            302: '暫時重定向',
            403: '禁止訪問',
            404: '不存在',
            500: '伺服器錯誤',
            503: '服務不可用'
        }
        return meanings.get(status_code, '未知')

    def _check_wordpress(self, soup, url):
        """檢查是否為 WordPress"""
        indicators = [
            soup.find('meta', {'name': 'generator', 'content': lambda x: x and 'WordPress' in x}),
            soup.find('link', {'href': lambda x: x and 'wp-content' in x}),
            soup.find('script', {'src': lambda x: x and 'wp-includes' in x}),
        ]
        return any(indicators)

    def _check_javascript(self, soup):
        """檢查是否為 JavaScript 動態載入"""
        # 如果 body 內容很少，可能是動態載入
        body = soup.find('body')
        if body and len(body.get_text().strip()) < 500:
            return True

        # 檢查是否有 React/Vue/Angular
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src', '').lower()
            if any(fw in src for fw in ['react', 'vue', 'angular', 'jquery.min.js']):
                return True

        return False

    def _detect_data_location(self, soup, url):
        """檢測資料在哪一層"""
        page_text = soup.get_text().lower()

        # 檢查主頁是否已有會議室資料
        has_capacity = any(word in page_text for word in ['容量', '人', '席位'])
        has_area = any(word in page_text for word in ['坪', '平方公尺', '㎡', '面積'])
        has_price = any(word in page_text for word in ['價格', '費用', '元', 'nt$'])

        # 檢查是否有會議室連結
        room_links = soup.find_all('a', href=True)
        has_meeting_links = any(
            any(kw in link.get('href', '').lower() or kw in link.get_text().lower()
                for kw in ['meeting', 'room', 'banquet', '會議', '會議室', '宴會'])
            for link in room_links
        )

        if has_capacity and has_area:
            return 'homepage'
        elif has_meeting_links:
            # 需要判斷是在會議頁還是詳情頁
            if any(kw in page_text for kw in ['詳情', 'detail', '介紹']):
                return 'detail_page'
            return 'meeting_page'
        else:
            return 'unknown'

    def _find_pdfs(self, soup, base_url):
        """尋找 PDF 連結"""
        pdf_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                # 轉換為絕對 URL
                if href.startswith('http'):
                    pdf_links.append(href)
                elif href.startswith('/'):
                    parsed = urlparse(base_url)
                    pdf_links.append(f"{parsed.scheme}://{parsed.netloc}{href}")

        return pdf_links

    def _generate_recommendation(self, result):
        """生成爬蟲建議"""
        status = result['status']
        site_type = result['type']
        loading = result['loading']
        data_location = result['data_location']
        has_pdf = result['has_pdf']

        # 錯誤處理
        if status != 200:
            return '檢查 URL 正確性'

        # WordPress
        if site_type == 'WordPress':
            return '使用 scraper_wordpress_ticc.py'

        # JavaScript 動態載入
        if loading == 'Dynamic/SPA' or loading == 'AJAX':
            return '使用 Playwright 爬蟲'

        # Static HTML + PDF
        if has_pdf:
            return '使用 full_site_scraper_v4_enhanced.py (含 PDF)'

        # Static HTML + 詳情頁
        if data_location == 'detail_page':
            return '使用 deep_scraper_v2.py (三級爬取)'

        # Static HTML + 會議頁
        if data_location == 'meeting_page':
            return '使用 full_site_scraper_v4.py (二級爬取)'

        # 預設
        return '使用 full_site_scraper_v4.py (全站爬取)'


def main():
    # Top 10 場地 - 使用正確 URL
    top_10_venues = [
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
    print('Top 10 場地技術檢測')
    print('=' * 80)
    print(f'檢測場地數: {len(top_10_venues)}')
    print()

    detector = TechDetector()
    results = []

    for i, venue in enumerate(top_10_venues, 1):
        print(f'\n{"="*70}')
        print(f'進度: [{i}/{len(top_10_venues)}]')
        print("="*70)

        result = detector.detect(
            venue['url'],
            venue['id'],
            venue['name']
        )
        results.append(result)

        # 避免請求過快
        time.sleep(2)

    # 生成總結報告
    print('\n' + '=' * 80)
    print('檢測結果總結')
    print('=' * 80)
    print()

    # 統計各類型
    type_counts = {}
    recommendation_counts = {}

    for result in results:
        rec = result.get('recommendation', 'Unknown')
        recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1

    print('爬蟲建議分布:')
    for rec, count in sorted(recommendation_counts.items(), key=lambda x: -x[1]):
        print(f'  {rec}: {count} 個場地')
    print()

    # 詳細結果表
    print('=' * 80)
    print('詳細結果表')
    print('=' * 80)
    print()
    print(f'{"ID":<6} {"場地名稱":<30} {"狀態":<8} {"類型":<15} {"資料位置":<15} {"PDF":<5}')
    print('-' * 120)

    for result in results:
        status = result.get('status', 'N/A')
        site_type = result.get('type', 'N/A')
        data_loc = result.get('data_location', 'N/A')
        has_pdf = '✅' if result.get('has_pdf') else '❌'

        status_str = str(status) if status is not None else 'N/A'
        site_type_str = site_type if site_type is not None else 'N/A'
        data_loc_str = data_loc if data_loc is not None else 'N/A'

        print(f'{result["id"]:<6} {result["name"][:30]:<30} {status_str:<8} {site_type_str:<15} {data_loc_str:<15} {has_pdf:<5}')

    print()
    print('=' * 80)
    print('建議處理順序')
    print('=' * 80)
    print()

    # 按優先級排序
    priority_order = [
        '使用 scraper_wordpress_ticc.py',
        '使用 full_site_scraper_v4_enhanced.py (含 PDF)',
        '使用 deep_scraper_v2.py (三級爬取)',
        '使用 full_site_scraper_v4.py (全站爬取)',
        '使用 Playwright 爬蟲',
        '檢查 URL 正確性'
    ]

    for priority in priority_order:
        matching = [r for r in results if r.get('recommendation', '') == priority]
        if matching:
            print(f'\n【{priority}】({len(matching)} 個場地)')
            for r in matching:
                print(f"  [{r['id']}] {r['name'][:50]}")

    print()
    print('=' * 80)
    print('檢測完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
