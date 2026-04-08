#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
階段1：技術檢測 - 文華東方
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def technical_detection(base_url):
    """階段1：技術檢測"""

    print('=' * 80)
    print('階段1：技術檢測')
    print('=' * 80)
    print(f'目標: {base_url}')
    print()

    detection_result = {
        'url': base_url,
        'http_status': None,
        'content_type': None,
        'page_type': None,
        'loading_method': None,
        'data_location': None,
        'anti_scraping': None
    }

    try:
        # 1. HTTP 狀態檢測
        print('[1/5] HTTP 狀態檢測...')
        response = requests.get(base_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        detection_result['http_status'] = response.status_code
        detection_result['content_type'] = response.headers.get('Content-Type', '')
        print(f'  狀態碼: {response.status_code}')
        print(f'  Content-Type: {detection_result["content_type"]}')
        print()

        # 2. 網頁類型判斷
        print('[2/5] 網頁類型判斷...')
        soup = BeautifulSoup(response.text, 'html.parser')

        # 檢查是否為動態載入
        has_react = 'react' in response.text.lower() or 'data-reactroot' in response.text.lower()
        has_vue = 'vue' in response.text.lower()
        has_nextjs = 'next' in response.text.lower() and 'data-nextjs' in response.text.lower()

        dynamic_scripts = []
        for script in soup.find_all('script'):
            src = script.get('src', '')
            if any(keyword in src.lower() for keyword in ['react', 'vue', 'angular', 'next', 'webpack']):
                dynamic_scripts.append(src)

        if dynamic_scripts:
            detection_result['page_type'] = 'Dynamic (SPA)'
            detection_result['loading_method'] = 'JavaScript'
            print(f'  ✅ 動態網頁 (JavaScript 載入)')
            print(f'  框架: {", ".join(dynamic_scripts[:3])}')
        else:
            detection_result['page_type'] = 'Static HTML'
            detection_result['loading_method'] = 'Server-side'
            print(f'  ✅ 靜態 HTML (Server-side Rendering)')
        print()

        # 3. 資料位置分析
        print('[3/5] 資料位置分析...')

        # 檢查 JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            print(f'  ✅ 找到 {len(json_ld_scripts)} 個 JSON-LD 腳本')
            detection_result['data_location'] = 'JSON-LD'

        # 檢查內嵌 JSON
        inline_data = []
        for script in soup.find_all('script'):
            if not script.get('src') and script.string:
                if any(keyword in script.string for keyword in ['window.__INITIAL_STATE__', '__NEXT_DATA__', '__NUXT__']):
                    inline_data.append('initial_state')

        if inline_data:
            print(f'  ✅ 找到內嵌資料: {", ".join(set(inline_data))}')
            if not detection_result['data_location']:
                detection_result['data_location'] = 'Inline JSON'

        # 檢查 API 端點
        api_patterns = [
            r'/api/\w+',
            r'https?://[^"\']*\.(?:json|graphql)'
        ]
        import re
        page_text = response.text
        api_endpoints = re.findall(r'"(/api/[^"]+)"', page_text)
        if api_endpoints:
            print(f'  ✅ 找到 API 端點: {len(set(api_endpoints))} 個')
            for endpoint in list(set(api_endpoints))[:3]:
                print(f'     - {endpoint}')
            if not detection_result['data_location']:
                detection_result['data_location'] = 'API endpoints'

        # 檢查 HTML 結構
        meeting_sections = soup.find_all(['section', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['meeting', 'event', 'banquet', 'conference', '會議', '宴會']
        ))

        if meeting_sections:
            print(f'  ✅ 找到 {len(meeting_sections)} 個會議相關區塊')
            if not detection_result['data_location']:
                detection_result['data_location'] = 'HTML structure'

        print()

        # 4. 反爬蟲檢測
        print('[4/5] 反爬蟲檢測...')

        # 檢查 Cloudflare
        if 'cloudflare' in response.text.lower():
            detection_result['anti_scraping'] = 'Cloudflare'
            print('  ⚠️  Cloudflare 保護')

        # 檢查 rate limit headers
        rate_limit_headers = ['X-RateLimit-Limit', 'X-RateLimit-Remaining']
        rate_limits = [h for h in rate_limit_headers if h in response.headers]
        if rate_limits:
            print(f'  ⚠️  Rate Limiting: {", ".join(rate_limits)}')
            detection_result['anti_scraping'] = detection_result.get('anti_scraping', '') + ', Rate Limiting'

        # 檢查 cookies requirement
        if 'set-cookie' in response.headers:
            print(f'  ⚠️  需要 Cookies')
            if not detection_result['anti_scraping']:
                detection_result['anti_scraping'] = 'Cookies required'

        if not detection_result['anti_scraping']:
            print('  ✅ 無明顯反爬蟲機制')

        print()

        # 5. 資料可達性評估
        print('[5/5] 資料可達性評估...')

        accessibility_score = 0
        max_score = 5

        # Static HTML content
        if detection_result['page_type'] == 'Static HTML':
            accessibility_score += 2
            print('  ✅ 靜態 HTML (+2)')

        # Clear data location
        if detection_result['data_location']:
            accessibility_score += 1
            print(f'  ✅ 資料位置明確: {detection_result["data_location"]} (+1)')

        # No anti-scraping
        if not detection_result['anti_scraping']:
            accessibility_score += 1
            print('  ✅ 無反爬蟲 (+1)')

        # Meeting sections found
        if meeting_sections:
            accessibility_score += 1
            print('  ✅ 找到會議區塊 (+1)')

        print()
        print(f'可達性評分: {accessibility_score}/{max_score}')

        if accessibility_score >= 3:
            print('✅ 易於爬取')
        elif accessibility_score >= 2:
            print('⚠️  需要特殊處理')
        else:
            print('❌ 難以爬取')

        detection_result['accessibility_score'] = accessibility_score
        detection_result['accessibility_max'] = max_score

        print()
        print('=' * 80)
        print('技術檢測完成')
        print('=' * 80)
        print()

        return detection_result

    except Exception as e:
        print(f'❌ 技術檢測失敗: {e}')
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    # 檢測用戶提供的 URL
    urls = [
        'https://www.mandarinoriental.com/zh-hk/taipei/songshan/meet',
        'https://www.mandarinoriental.com/en/taipei/songshan/meet'
    ]

    all_results = []

    for url in urls:
        result = technical_detection(url)
        if result:
            all_results.append(result)
        print()

    # 儲存結果
    with open('mandarin_technical_detection.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print('✅ 已儲存技術檢測結果到 mandarin_technical_detection.json')
