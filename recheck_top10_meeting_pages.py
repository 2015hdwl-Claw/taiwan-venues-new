#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新檢視 Top 10 場地 - 會議頁面深度分析

直接檢查每個場地的會議/場地頁面
（不是主頁）
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


def check_meeting_page(url, venue_id, venue_name):
    """檢查場地的會議頁面"""

    print(f'\n{"=" * 80}')
    print(f'場地 [{venue_id}] {venue_name[:40]}')
    print(f'URL: {url}')
    print('=' * 80)

    result = {
        'id': venue_id,
        'name': venue_name,
        'url': url,
        'accessible': False,
        'data_sources': {}
    }

    try:
        # 獲取頁面
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        result['accessible'] = True
        html_content = response.text

        print('[檢測] 會議頁面資料來源分析...')

        # 1. 檢查 JavaScript 變數（重點）
        print('[1/6] JavaScript 變數檢測...')

        js_patterns = [
            r'var\s+(room_data|venue_data|event_data|space_data|meeting_data|facility_data)\s*=',
            r'const\s+(room_data|venue_data|event_data|space_data|meeting_data|facility_data)\s*=',
            r'let\s+(room_data|venue_data|event_data|space_data|meeting_data|facility_data)\s*=',
            r'window\.(room_data|venue_data|event_data|space_data|meeting_data|facility_data)\s*=',
        ]

        found_js_vars = []
        for pattern in js_patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                found_js_vars.extend(matches)

        if found_js_vars:
            # 去重
            unique_vars = list(set(found_js_vars))
            print(f'  ✅ 找到: {", ".join(unique_vars)}')

            # 嘗試提取並分析
            for var_match in unique_vars[:2]:  # 只分析前 2 個
                var_name = var_match.split()[0]  # 取變數名

                # 構建完整的提取模式
                full_pattern = rf'{var_match}\s*(\[.*?\]);'
                full_match = re.search(full_pattern, html_content, re.DOTALL)

                if full_match:
                    try:
                        json_str = full_match.group(1)
                        data = json.loads(json_str)

                        if isinstance(data, list):
                            print(f'     類型: 陣列，長度: {len(data)}')
                            if len(data) > 0:
                                first_item = data[0]
                                if isinstance(first_item, dict):
                                    keys = list(first_item.keys())[:8]
                                    print(f'     欄位: {", ".join(keys)}')

                                    # 檢查是否有價格資料
                                    sample_data = str(data[0])
                                    if 'price' in sample_data.lower() or 'cost' in sample_data.lower():
                                        print(f'     ⭐ 包含價格資料')

                                    if 'hardware' in sample_data.lower() or 'equipment' in sample_data.lower():
                                        print(f'     ⭐ 包含設備資料')

                        result['data_sources']['javascript_variables'] = var_name
                        result['data_sources']['js_extractable'] = True
                        break

                    except Exception as e:
                        print(f'     解析失敗: {str(e)[:30]}')
                        continue

            result['data_sources']['js_recommended'] = True
        else:
            print(f'  ❌ 未找到 JavaScript 變數')

        # 2. 檢查 JSON-LD
        print('[2/6] JSON-LD 檢測...')
        if '<script type="application/ld+json">' in html_content:
            print(f'  ✅ 找到 JSON-LD')

            soup = BeautifulSoup(html_content, 'html.parser')
            scripts = soup.find_all('script', {'type': 'application/ld+json'})

            for script in scripts[:2]:  # 只顯示前 2 個
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]

                    if isinstance(data, dict):
                        at_type = data.get('@type', 'Unknown')
                        print(f'     類型: {at_type}')
                        keys = list(data.keys())[:5]
                        print(f'     欄位: {", ".join(keys)}')

                    result['data_sources']['json_ld'] = True
                    break
                except:
                    continue
        else:
            print(f'  ❌ 未找到 JSON-LD')

        # 3. 檢查 data-* 屬性
        print('[3/6] data-* 屬性檢測...')
        soup = BeautifulSoup(html_content, 'html.parser')

        data_attrs = []
        for attr_name in ['data-room', 'data-venue', 'data-space', 'data-meeting']:
            elements = soup.find_all(attrs={attr_name: True})
            if elements:
                data_attrs.append(attr_name)

        if data_attrs:
            print(f'  ✅ 找到: {", ".join(data_attrs)}')
            result['data_sources']['data_attributes'] = True
        else:
            print(f'  ❌ 未找到 data-* 屬性')

        # 4. 檢查詳情頁
        print('[4/6] 詳情頁檢測...')
        detail_links = soup.find_all('a', href=True)

        meeting_links = []
        for link in detail_links[:50]:  # 只檢查前 50 個
            href = link['href'].lower()
            text = link.get_text(strip=True)

            # 尋找包含會議室相關關鍵字的連結
            if any(kw in href for kw in ['detail', 'room', 'space', 'venue']) and len(text) > 2:
                meeting_links.append(text[:30])

        if meeting_links:
            print(f'  ✅ 找到 {len(meeting_links)} 個可能的詳情頁連結')
            for link in meeting_links[:3]:
                print(f'     - {link}')
            result['data_sources']['detail_pages'] = True
        else:
            print(f'  ❌ 未找到詳情頁')

        # 5. 檢查 API
        print('[5/6] API 端點檢測...')
        api_found = False

        if re.search(r'\$\.ajax\(', html_content):
            print(f'  ⚠️  發現 AJAX 調用')
            api_found = True

        if re.search(r'\.get\(|\.post\(|fetch\(', html_content):
            print(f'  ⚠️  發現 API 調用')
            api_found = True

        if api_found:
            result['data_sources']['api_endpoints'] = True
        else:
            print(f'  ❌ 未找到 API 端點')

        # 6. 判斷推薦方法
        print('[6/6] 推薦方法...')

        if result['data_sources'].get('js_extractable'):
            print(f'  🥇 優先: 提取 JavaScript 變數')
            print(f'     預期完整度: 80-95%')
            print(f'     處理時間: 5-10 分鐘')

        elif result['data_sources'].get('json_ld'):
            print(f'  🥇 優先: 提取 JSON-LD')
            print(f'     預期完整度: 70-85%')
            print(f'     處理時間: 10-15 分鐘')

        elif result['data_sources'].get('data_attributes'):
            print(f'  🥈 次選: 提取 data-* 屬性')
            print(f'     預期完整度: 60-75%')
            print(f'     處理時間: 10-20 分鐘')

        elif result['data_sources'].get('detail_pages'):
            print(f'  🥉 次選: 爬取詳情頁')
            print(f'     預期完整度: 50-70%')
            print(f'     處理時間: 30-60 分鐘')

        elif result['data_sources'].get('api_endpoints'):
            print(f'  🥉 次選: 調用 API')
            print(f'     預期完整度: 40-60%')
            print(f'     處理時間: 20-40 分鐘')

        else:
            print(f'  ❓ 其他: Playwright 或手動處理')
            print(f'     預期完整度: 10-30%')
            print(f'     處理時間: 60-120 分鐘')

    except requests.exceptions.Timeout:
        print('  ❌ 連線超時')

    except requests.exceptions.ConnectionError:
        print('  ❌ 無法連線')

    except Exception as e:
        print(f'  ❌ 錯誤: {str(e)[:50]}')

    return result


def main():
    # Top 10 場地的會議頁面 URL（需要手動指定）
    # 這裡我們只檢測已知有會議頁面的場地

    test_venues = [
        {
            'id': 1493,
            'name': '師大進修推廣學院',
            'url': 'https://www.sce.ntnu.edu.tw/home/space/'
        },
        {
            'id': 1128,
            'name': '集思台大會議中心',
            'url': 'https://www.meeting.com.tw/ntu/'
        },
    ]

    print('=' * 80)
    print('重新檢視 Top 10 場地 - 會議頁面深度分析')
    print('=' * 80)
    print(f'檢測場地數: {len(test_venues)} (示範)')
    print()

    results = []

    for i, venue in enumerate(test_venues, 1):
        print(f'\n{"=" * 80}')
        print(f'進度: [{i}/{len(test_venues)}]')
        print('=' * 80)

        result = check_meeting_page(
            venue['url'],
            venue['id'],
            venue['name']
        )
        results.append(result)

    # 總結
    print('\n' + '=' * 80)
    print('檢測結果總結')
    print('=' * 80)
    print()

    for result in results:
        vid = result['id']
        name = result['name']

        if result.get('data_sources', {}).get('js_extractable'):
            status = '🥇 優先（JavaScript 變數）'
            recommendation = '立即提取 JavaScript 變數'
        elif result.get('data_sources', {}).get('json_ld'):
            status = '🥇 優先（JSON-LD）'
            recommendation = '提取 JSON-LD 資料'
        elif result.get('data_sources', {}).get('detail_pages'):
            status = '🥉 次選（詳情頁）'
            recommendation = '爬取詳情頁'
        else:
            status = '❓ 待處理'
            recommendation = 'Playwright 或手動'

        print(f'{status} [{vid}] {name[:40]}')
        print(f'     建議: {recommendation}')
        print()


if __name__ == '__main__':
    main()
