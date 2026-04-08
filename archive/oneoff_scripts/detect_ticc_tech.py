#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢測 TICC 網頁技術類型
決定使用哪種擷取方式
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

class WebpageTechDetector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def detect_full(self, url, url_name=""):
        """完整檢測單一 URL"""
        print(f'\n{"="*80}')
        print(f'檢測: {url_name}')
        print(f'URL: {url}')
        print('='*80)

        result = {
            'url': url,
            'url_name': url_name,
            'detected_at': datetime.now().isoformat(),
            'tests': {}
        }

        # 測試 1: 基本 HTTP 請求
        print('\n[測試 1] 基本 HTTP 請求')
        http_result = self._test_basic_http(url)
        result['tests']['basic_http'] = http_result
        print(f'  狀態: {http_result["status_code"]}')
        print(f'  Content-Type: {http_result["content_type"]}')

        if http_result['status_code'] != 200:
            print(f'  ❌ 頁面無法存取')
            return result

        # 測試 2: 檢查是否為 WordPress
        print('\n[測試 2] WordPress API')
        wp_result = self._test_wordpress(url)
        result['tests']['wordpress'] = wp_result
        print(f'  WordPress API: {"✅ 發現" if wp_result["has_wordpress_api"] else "❌ 未發現"}')

        # 測試 3: 分析 HTML 結構
        print('\n[測試 3] HTML 結構分析')
        soup = BeautifulSoup(http_result['text'], 'html.parser')
        html_result = self._analyze_html_structure(soup)
        result['tests']['html_structure'] = html_result
        print(f'  標題數量: {html_result["title_count"]}')
        print(f'  連結數量: {html_result["link_count"]}')
        print(f'  圖片數量: {html_result["image_count"]}')
        print(f'  表格數量: {html_result["table_count"]}')
        print(f'  表單數量: {html_result["form_count"]}')

        # 測試 4: JavaScript 檢測
        print('\n[測試 4] JavaScript 依賴檢測')
        js_result = self._detect_javascript_dependency(soup, http_result['text'])
        result['tests']['javascript'] = js_result
        print(f'  Script 標籤: {js_result["script_count"]} 個')
        print(f'  主要框架: {js_result["frameworks"] if js_result["frameworks"] else "無"}')
        print(f'  React/Vue/Angular: {js_result["spa_framework"] if js_result["spa_framework"] else "無"}')

        # 測試 5: 內容載入方式
        print('\n[測試 5] 內容載入方式')
        content_result = self._detect_content_loading(soup, http_result['text'])
        result['tests']['content_loading'] = content_result
        print(f'  主要內容在 HTML 中: {"✅ 是" if content_result["content_in_html"] else "❌ 否"}')
        print(f'  可能需要 JS 渲染: {"✅ 是" if content_result["needs_js_rendering"] else "❌ 否"}')

        # 測試 6: 特殊技術檢測
        print('\n[測試 6] 特殊技術檢測')
        tech_result = self._detect_special_tech(soup, http_result['text'])
        result['tests']['special_tech'] = tech_result
        print(f'  使用 jQuery: {"✅ 是" if tech_result["uses_jquery"] else "❌ 否"}')
        print(f'  使用 AJAX: {"✅ 可能" if tech_result["uses_ajax"] else "❌ 否"}')
        print(f'  使用 iframe: {"✅ 是" if tech_result["uses_iframe"] else "❌ 否"}')

        # 綜合判斷
        print('\n[綜合判斷]')
        conclusion = self._make_conclusion(result['tests'])
        result['conclusion'] = conclusion
        print(f'  網頁類型: {conclusion["page_type"]}')
        print(f'  推薦擷取方式: {conclusion["recommended_method"]}')
        print(f'  信心度: {conclusion["confidence"]}')

        return result

    def _test_basic_http(self, url):
        """測試基本 HTTP 請求"""
        try:
            response = self.session.get(url, timeout=15, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 不儲存 soup 物件（避免 JSON 序列化錯誤）
            return {
                'success': True,
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type', ''),
                'content_length': len(response.content),
                'text': response.text,
                'soup_preview': soup.get_text()[:500]  # 只保留預覽
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': None,
                'content_type': None
            }

    def _test_wordpress(self, url):
        """測試是否為 WordPress"""
        result = {
            'has_wordpress_api': False,
            'wordpress_version': None,
            'api_endpoints': []
        }

        # 檢查 WordPress REST API
        api_urls = [
            urljoin(url, '/wp-json/wp/v2/pages'),
            urljoin(url, '/wp-json/'),
            urljoin(url, '/wp-admin/')
        ]

        for api_url in api_urls:
            try:
                response = self.session.get(api_url, timeout=5, verify=False)
                if response.status_code == 200:
                    result['has_wordpress_api'] = True
                    result['api_endpoints'].append(api_url)
            except:
                pass

        return result

    def _analyze_html_structure(self, soup):
        """分析 HTML 結構"""
        return {
            'title_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'link_count': len(soup.find_all('a', href=True)),
            'image_count': len(soup.find_all('img')),
            'table_count': len(soup.find_all('table')),
            'form_count': len(soup.find_all('form')),
            'div_count': len(soup.find_all('div')),
            'has_meta_tags': len(soup.find_all('meta')) > 0
        }

    def _detect_javascript_dependency(self, soup, html_text):
        """檢測 JavaScript 依賴"""
        scripts = soup.find_all('script')
        frameworks = []
        spa_framework = None

        for script in scripts:
            src = script.get('src', '').lower()
            content = script.get_text().lower()

            # 檢測框架
            if 'jquery' in src or 'jquery' in content:
                if 'jquery' not in frameworks:
                    frameworks.append('jQuery')

            if 'bootstrap' in src or 'bootstrap' in content:
                if 'Bootstrap' not in frameworks:
                    frameworks.append('Bootstrap')

            if 'react' in src or 'react' in content:
                spa_framework = 'React'
                if 'React' not in frameworks:
                    frameworks.append('React')

            if 'vue' in src or 'vue' in content:
                spa_framework = 'Vue.js'
                if 'Vue' not in frameworks:
                    frameworks.append('Vue.js')

            if 'angular' in src or 'angular' in content:
                spa_framework = 'Angular'
                if 'Angular' not in frameworks:
                    frameworks.append('Angular')

        return {
            'script_count': len(scripts),
            'external_scripts': len([s for s in scripts if s.get('src')]),
            'inline_scripts': len([s for s in scripts if not s.get('src')]),
            'frameworks': ', '.join(frameworks) if frameworks else None,
            'spa_framework': spa_framework,
            'needs_js_runtime': len(scripts) > 3
        }

    def _detect_content_loading(self, soup, html_text):
        """檢測內容載入方式"""
        # 檢查主要內容是否在 HTML 中
        main_content_indicators = [
            '會議室', '場地', '會議', '樓層', '容量', '價格'
        ]

        content_in_html = any(indicator in html_text for indicator in main_content_indicators)

        # 檢查是否明確需要 JS 渲染
        needs_js_rendering = False
        js_indicators = [
            'react-root',
            'ng-app',
            'v-app',
            'data-reactroot',
            '__INITIAL_STATE__',
            'window.__STATE__'
        ]

        for indicator in js_indicators:
            if indicator in html_text.lower():
                needs_js_rendering = True
                break

        # 檢查 body 是否為空
        body = soup.find('body')
        empty_body = False
        if body:
            body_text = body.get_text().strip()
            empty_body = len(body_text) < 100
        else:
            empty_body = True

        return {
            'content_in_html': content_in_html,
            'needs_js_rendering': needs_js_rendering,
            'empty_body': empty_body
        }

    def _detect_special_tech(self, soup, html_text):
        """檢測特殊技術"""
        uses_jquery = 'jquery' in html_text.lower()
        uses_ajax = 'ajax' in html_text.lower() or 'xhr' in html_text.lower()
        uses_iframe = len(soup.find_all('iframe')) > 0

        return {
            'uses_jquery': uses_jquery,
            'uses_ajax': uses_ajax,
            'uses_iframe': uses_iframe,
            'iframe_count': len(soup.find_all('iframe'))
        }

    def _make_conclusion(self, tests):
        """綜合判斷"""
        conclusion = {
            'page_type': 'Unknown',
            'recommended_method': 'Unknown',
            'confidence': 'Low',
            'reasoning': []
        }

        # 判斷邏輯
        if tests.get('wordpress', {}).get('has_wordpress_api'):
            conclusion['page_type'] = 'WordPress API'
            conclusion['recommended_method'] = 'WordPress REST API'
            conclusion['confidence'] = 'High'
            conclusion['reasoning'].append('發現 WordPress API 端點')

        elif tests.get('javascript', {}).get('spa_framework'):
            framework = tests['javascript']['spa_framework']
            conclusion['page_type'] = f'SPA ({framework})'
            conclusion['recommended_method'] = 'Playwright (Headless Browser)'
            conclusion['confidence'] = 'High'
            conclusion['reasoning'].append(f'使用 {framework} SPA 框架')

        elif tests.get('content_loading', {}).get('needs_js_rendering'):
            conclusion['page_type'] = 'JavaScript (CSR)'
            conclusion['recommended_method'] = 'Playwright (Headless Browser)'
            conclusion['confidence'] = 'Medium'
            conclusion['reasoning'].append('需要 JavaScript 渲染')

        elif tests.get('content_loading', {}).get('content_in_html'):
            conclusion['page_type'] = 'Static/SSR'
            conclusion['recommended_method'] = 'requests + BeautifulSoup'
            conclusion['confidence'] = 'High'
            conclusion['reasoning'].append('內容已在 HTML 中')

        elif not tests.get('basic_http', {}).get('success'):
            conclusion['page_type'] = 'Inaccessible'
            conclusion['recommended_method'] = 'Manual Inspection Required'
            conclusion['confidence'] = 'Medium'
            conclusion['reasoning'].append('HTTP 請求失敗')

        else:
            conclusion['page_type'] = 'Complex/Hybrid'
            conclusion['recommended_method'] = 'Playwright (Safe Choice)'
            conclusion['confidence'] = 'Low'
            conclusion['reasoning'].append('無法明確判斷')

        return conclusion


# 測試 TICC 的所有重要 URL
ticc_urls = {
    '首頁': 'https://www.ticc.com.tw/',
    '場地介紹（原）': 'https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueIntroduction.jsp&ctNode=321&CtUnit=98&BaseDSD=7&mp=1',
    '場地查詢（原）': 'https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueSearch.jsp&ctNode=322&CtUnit=99&BaseDSD=7&mp=1',
    '價目表': 'https://www.ticc.com.tw/wSite/lp?ctNode=335&CtUnit=109&BaseDSD=7&mp=1',
    '租借規範': 'https://www.ticc.com.tw/wSite/lp?ctNode=336&CtUnit=110&BaseDSD=7&mp=1',
    '交通資訊': 'https://www.ticc.com.tw/wSite/ct?xItem=922&ctNode=31',
    '場地導覽': 'https://www.ticc.com.tw/wSite/np?ctNode=320&mp=1'
}

detector = WebpageTechDetector()

print('='*80)
print('TICC 網頁技術檢測')
print('='*80)

results = []

for url_name, url in ticc_urls.items():
    result = detector.detect_full(url, url_name)
    results.append(result)

    # 休息一下
    import time
    time.sleep(1)

# 儲存結果
with open('ticc_tech_detection.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n' + '='*80)
print('檢測完成！')
print('詳細結果已儲存到 ticc_tech_detection.json')
print('='*80)

# 總結
print('\n【總結】')
print('='*80)

success_count = 0
static_count = 0
js_count = 0
wordpress_count = 0

for result in results:
    conclusion = result.get('conclusion', {})
    url_name = result.get('url_name', 'Unknown')

    if conclusion.get('confidence') in ['High', 'Medium']:
        success_count += 1

    page_type = conclusion.get('page_type', '')
    if 'Static' in page_type or 'SSR' in page_type:
        static_count += 1
    elif 'JS' in page_type or 'JavaScript' in page_type or 'SPA' in page_type:
        js_count += 1
    elif 'WordPress' in page_type:
        wordpress_count += 1

    print(f'\n{url_name}:')
    print(f'  類型: {page_type}')
    print(f'  推薦方式: {conclusion.get("recommended_method", "Unknown")}')
    print(f'  信心度: {conclusion.get("confidence", "Unknown")}')

print(f'\n統計:')
print(f'  成功檢測: {success_count}/{len(results)}')
print(f'  Static/SSR: {static_count}')
print(f'  JavaScript/SPA: {js_count}')
print(f'  WordPress: {wordpress_count}')
