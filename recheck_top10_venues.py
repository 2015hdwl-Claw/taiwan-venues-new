#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新檢視 Top 10 場地 - 應用新的深度爬蟲邏輯

檢查每個場地的官網是否有：
1. JavaScript 變數（room_data, venue_data 等）
2. JSON-LD 結構化資料
3. data-* 屬性
4. API 端點
5. 詳情頁 URL
"""

import sys
import io
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_data_sources(html_content):
    """檢查頁面中所有可能的資料來源"""

    sources = {
        'javascript_variables': [],
        'json_ld': False,
        'data_attributes': [],
        'api_endpoints': [],
        'detail_pages': []
    }

    # 1. 檢查 JavaScript 變數
    js_patterns = [
        (r'var\s+(room_data|venue_data|event_data|space_data|meeting_data)\s*=', 'var'),
        (r'const\s+(room_data|venue_data|event_data|space_data|meeting_data)\s*=', 'const'),
        (r'let\s+(room_data|venue_data|event_data|space_data|meeting_data)\s*=', 'let'),
        (r'window\.(room_data|venue_data|event_data|space_data|meeting_data)\s*=', 'window'),
    ]

    for pattern, var_type in js_patterns:
        matches = re.findall(pattern, html_content)
        if matches:
            sources['javascript_variables'].extend(matches)

    # 去重
    sources['javascript_variables'] = list(set(sources['javascript_variables']))

    # 2. 檢查 JSON-LD
    if '<script type="application/ld+json">' in html_content:
        sources['json_ld'] = True

    # 3. 檢查 data-* 屬性
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(attrs={'data-room': True}):
        sources['data_attributes'].append('data-room')
    for element in soup.find_all(attrs={'data-venue': True}):
        sources['data_attributes'].append('data-venue')

    # 去重
    sources['data_attributes'] = list(set(sources['data_attributes']))

    # 4. 檢查 API 端點
    api_patterns = [
        r'"/api/[a-z]+',
        r'\$\.ajax\(',
        r'\.get\(',
        r'\.post\(',
        r'fetch\('
    ]

    for pattern in api_patterns:
        if re.search(pattern, html_content):
            sources['api_endpoints'].append(pattern)
            break

    # 5. 檢查詳情頁 URL
    detail_keywords = ['detail', '詳情', '介紹', 'room/', 'space/', 'venue/']
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(kw in href.lower() for kw in detail_keywords):
            sources['detail_pages'].append(href)
            if len(sources['detail_pages']) >= 5:  # 限制數量
                break

    return sources


def analyze_venue(venue_id, venue_name, venue_url):
    """分析單一場地"""

    print(f'\n{"=" * 80}')
    print(f'場地 [{venue_id}] {venue_name[:40]}')
    print(f'URL: {venue_url}')
    print('=' * 80)

    result = {
        'id': venue_id,
        'name': venue_name,
        'url': venue_url,
        'accessible': False,
        'data_sources': {}
    }

    try:
        # 獲取頁面
        response = requests.get(venue_url, timeout=15)
        response.raise_for_status()

        result['accessible'] = True
        html_content = response.text

        print('[檢測] 資料來源分析...')

        # 檢查資料來源
        sources = check_data_sources(html_content)

        # JavaScript 變數
        if sources['javascript_variables']:
            print(f'  ✅ JavaScript 變數: {", ".join(set(sources["javascript_variables"]))}')

            # 嘗試提取
            for var_name in sources['javascript_variables'][:3]:  # 只檢查前 3 個
                var_pattern = rf'{var_name}\s*=\s*(\[.*?\]);'
                match = re.search(var_pattern, html_content, re.DOTALL)

                if match:
                    try:
                        json_str = match.group(1)
                        data = json.loads(json_str)

                        if isinstance(data, list):
                            print(f'     類型: 陣列，長度: {len(data)}')
                            if len(data) > 0:
                                first_item = data[0]
                                if isinstance(first_item, dict):
                                    keys = list(first_item.keys())[:5]
                                    print(f'     欄位: {", ".join(keys)}')
                        elif isinstance(data, dict):
                            print(f'     類型: 物件')
                            keys = list(data.keys())[:5]
                            print(f'     欄位: {", ".join(keys)}')

                        result['data_sources']['javascript_extractable'] = True
                        break
                    except:
                        continue

        else:
            print(f'  ❌ JavaScript 變數: 未找到')

        # JSON-LD
        if sources['json_ld']:
            print(f'  ✅ JSON-LD: 找到結構化資料')
            result['data_sources']['json_ld'] = True
        else:
            print(f'  ❌ JSON-LD: 未找到')

        # data-* 屬性
        if sources['data_attributes']:
            print(f'  ✅ data-* 屬性: {", ".join(set(sources["data_attributes"]))}')
            result['data_sources']['data_attributes'] = True
        else:
            print(f'  ❌ data-* 屬性: 未找到')

        # API 端點
        if sources['api_endpoints']:
            print(f'  ⚠️  API 端點: 發現可能的 API 調用')
            result['data_sources']['api_endpoints'] = True
        else:
            print(f'  ❌ API 端點: 未找到')

        # 詳情頁
        if sources['detail_pages']:
            print(f'  ✅ 詳情頁: 找到 {len(sources["detail_pages"])} 個詳情頁連結')
            result['data_sources']['detail_pages'] = True
        else:
            print(f'  ❌ 詳情頁: 未找到')

        # 判斷推薦方法
        print()
        print('[推薦] 最佳爬蟲方法:')

        if sources['javascript_variables']:
            print('  🥇 優先: 提取 JavaScript 變數（最快、最準確）')
        elif sources['json_ld']:
            print('  🥇 優先: 提取 JSON-LD 結構化資料')
        elif sources['data_attributes']:
            print('  🥈 次選: 提取 data-* 屬性')
        elif sources['detail_pages']:
            print('  🥉 次選: 爬取詳情頁')
        elif sources['api_endpoints']:
            print('  🥉 次選: 調用 API 端點')
        else:
            print('  ❓ 其他: 需要 Playwright 或手動處理')

    except requests.exceptions.Timeout:
        print('  ❌ 連線超時')
        result['accessible'] = False

    except requests.exceptions.ConnectionError:
        print('  ❌ 無法連線')
        result['accessible'] = False

    except Exception as e:
        print(f'  ❌ 錯誤: {str(e)[:50]}')
        result['accessible'] = False

    return result


def main():
    # Top 10 場地
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
    print('重新檢視 Top 10 場地 - 深度爬蟲分析')
    print('=' * 80)
    print(f'檢測場地數: {len(top10)}')
    print()

    results = []

    for i, venue in enumerate(top10, 1):
        print(f'\n{"=" * 80}')
        print(f'進度: [{i}/{len(top10)}]')
        print('=' * 80)

        result = analyze_venue(
            venue['id'],
            venue['name'],
            venue['url']
        )
        results.append(result)

    # 生成總結報告
    print('\n' + '=' * 80)
    print('檢測結果總結')
    print('=' * 80)
    print()

    # 統計
    accessible = sum(1 for r in results if r['accessible'])

    has_js_var = sum(1 for r in results if r['data_sources'].get('javascript_extractable'))
    has_json_ld = sum(1 for r in results if r['data_sources'].get('json_ld'))
    has_data_attr = sum(1 for r in results if r['data_sources'].get('data_attributes'))
    has_api = sum(1 for r in results if r['data_sources'].get('api_endpoints'))
    has_detail = sum(1 for r in results if r['data_sources'].get('detail_pages'))

    print(f'可訪問: {accessible}/{len(results)}')
    print(f'有 JavaScript 變數: {has_js_var}/{len(results)}')
    print(f'有 JSON-LD: {has_json_ld}/{len(results)}')
    print(f'有 data-* 屬性: {has_data_attr}/{len(results)}')
    print(f'有 API 端點: {has_api}/{len(results)}')
    print(f'有詳情頁: {has_detail}/{len(results)}')
    print()

    # 詳細結果
    print('=' * 80)
    print('各場地推薦方法')
    print('=' * 80)
    print()

    for result in results:
        if not result['accessible']:
            continue

        vid = result['id']
        name = result['name'][:40]

        # 判斷推薦方法
        if result['data_sources'].get('javascript_extractable'):
            method = 'JavaScript 變數提取'
            priority = '🥇'
        elif result['data_sources'].get('json_ld'):
            method = 'JSON-LD 提取'
            priority = '🥇'
        elif result['data_sources'].get('data_attributes'):
            method = 'data-* 屬性提取'
            priority = '🥈'
        elif result['data_sources'].get('detail_pages'):
            method = '詳情頁爬取'
            priority = '🥉'
        elif result['data_sources'].get('api_endpoints'):
            method = 'API 調用'
            priority = '🥉'
        else:
            method = 'Playwright/手動'
            priority = '❓'

        print(f'{priority} [{vid}] {name}')
        print(f'     方法: {method}')
        print()


if __name__ == '__main__':
    main()
