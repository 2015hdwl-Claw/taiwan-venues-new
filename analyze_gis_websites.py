#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢測集思會議中心網頁技術
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == 'win32':
    import io as sys_io
    sys.stdout = sys_io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class WebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def analyze(self, url, name=""):
        """完整分析網站"""
        print("="*80)
        print(f"分析網站: {name or url}")
        print("="*80)
        print(f"URL: {url}")
        print()

        result = {
            'url': url,
            'name': name,
            'tests': {}
        }

        # 測試 1: 基本 HTTP 請求
        print("[1/6] 基本 HTTP 請求...")
        try:
            response = self.session.get(url, timeout=10, verify=False)
            result['tests']['http_status'] = response.status_code
            result['tests']['http_success'] = response.status_code == 200

            if response.status_code == 200:
                print(f"    ✅ HTTP {response.status_code}")
                result['tests']['content_length'] = len(response.text)
            else:
                print(f"    ❌ HTTP {response.status_code}")
        except Exception as e:
            result['tests']['http_error'] = str(e)
            print(f"    ❌ 錯誤: {str(e)[:50]}")
            return result

        # 測試 2: WordPress API
        print("[2/6] 檢測 WordPress API...")
        try:
            api_url = urljoin(url, '/wp-json/wp/v2/pages')
            api_resp = self.session.get(api_url, timeout=5, verify=False)
            if api_resp.status_code == 200:
                result['tests']['wordpress_api'] = True
                print(f"    ✅ WordPress API 可用")
            else:
                result['tests']['wordpress_api'] = False
                print(f"    ❌ WordPress API 不可用 (HTTP {api_resp.status_code})")
        except:
            result['tests']['wordpress_api'] = False
            print(f"    ❌ WordPress API 不可用")

        # 測試 3: 分析 HTML 結構
        print("[3/6] 分析 HTML 結構...")
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()

        # 檢測 JavaScript 框架
        jquery_found = 'jquery' in text or soup.find('script', src=lambda x: x and 'jquery' in x.lower())
        js_frameworks = {
            'react': 'react' in text,
            'vue': 'vue' in text,
            'angular': 'angular' in text,
            'jquery': bool(jquery_found)  # Convert to boolean
        }

        result['tests']['js_frameworks'] = js_frameworks
        for framework, detected in js_frameworks.items():
            if detected:
                print(f"    ✅ {framework.upper()}")
            else:
                print(f"    - {framework.upper()}: 無")

        # 測試 4: 尋找會議室相關連結
        print("[4/6] 尋找會議室連結...")
        meeting_links = self._find_meeting_links(soup, url)
        result['tests']['meeting_links'] = meeting_links
        print(f"    找到 {len(meeting_links)} 個會議室相關連結")

        for link in meeting_links[:5]:
            print(f"    - {link['text'][:40]}: {link['url'][:60]}")

        # 測試 5: 尋找特定路徑
        print("[5/6] 檢測常見路徑...")
        common_paths = [
            '/meeting/',
            '/rooms/',
            '/space/',
            '/venue/',
            '/facilities/',
            '/about/',
        ]

        found_paths = []
        for path in common_paths:
            test_url = urljoin(url, path)
            try:
                test_resp = self.session.head(test_url, timeout=5, verify=False)
                if test_resp.status_code == 200:
                    found_paths.append(path)
                    print(f"    ✅ {path}")
            except:
                pass

        result['tests']['common_paths'] = found_paths

        # 測試 6: 分析 URL 結構
        print("[6/6] 分析 URL 結構...")
        parsed = urlparse(url)
        result['tests']['url_structure'] = {
            'domain': parsed.netloc,
            'path': parsed.path,
            'is_subdomain': parsed.netloc.count('.') > 2
        }
        print(f"    網域: {parsed.netloc}")
        print(f"    路徑: {parsed.path}")

        # 結論
        print()
        print("-"*80)
        print("【結論】")
        print("-"*80)

        if result['tests'].get('wordpress_api'):
            conclusion = "WordPress 網站"
        elif js_frameworks.get('react') or js_frameworks.get('vue') or js_frameworks.get('angular'):
            conclusion = "JavaScript SPA (Single Page Application)"
        else:
            conclusion = "Static/SSR 網站"

        print(f"網頁類型: {conclusion}")
        print(f"會議室連結: {len(meeting_links)} 個")
        print(f"可用路徑: {len(found_paths)} 個")

        return result

    def _find_meeting_links(self, soup, base_url):
        """尋找會議室相關連結"""
        meeting_links = []
        meeting_keywords = [
            '會議', 'meeting', '場地', 'space', 'room',
            '教室', '廳', '設施', 'facilities'
        ]

        all_links = soup.find_all('a', href=True)
        for a in all_links:
            text = a.get_text().strip()
            href = a['href']

            if any(kw in text.lower() or kw in href.lower() for kw in meeting_keywords):
                if 0 < len(text) < 100:
                    full_url = urljoin(base_url, href)
                    meeting_links.append({
                        'text': text,
                        'url': full_url
                    })

        # 去重
        seen = set()
        unique_links = []
        for link in meeting_links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)

        return unique_links[:10]


def main():
    analyzer = WebsiteAnalyzer()

    # 集思會議中心 URLs
    urls_to_analyze = [
        ('https://www.meeting.com.tw/', '集思首頁'),
        ('https://www.meeting.com.tw/motc/', '集思交通部國際會議中心'),
        ('https://www.meeting.com.tw/ntu/', '集思台大會議中心'),
        ('https://www.meeting.com.tw/tech/', '集思北科大會議中心'),
    ]

    all_results = []

    for url, name in urls_to_analyze:
        result = analyzer.analyze(url, name)
        all_results.append(result)
        print()

    # 儲存結果
    report = {
        'analyzed_at': '2026-03-25',
        'total_websites': len(all_results),
        'results': all_results
    }

    with open('gis_websites_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("="*80)
    print("分析完成")
    print("="*80)
    print(f"結果已儲存至: gis_websites_analysis.json")


if __name__ == '__main__':
    main()
