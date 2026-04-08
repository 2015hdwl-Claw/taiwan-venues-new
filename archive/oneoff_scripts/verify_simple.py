#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import sys
import io

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 測試場地
test_venues = [
    {
        "id": 1042,
        "name": "公務人力發展學院",
        "url": "https://www.hrd.gov.tw",
        "type": "會議中心"
    },
    {
        "id": 1034,
        "name": "NUZONE展演空間",
        "url": "https://www.nuzone.com.tw/",
        "type": "展演場地"
    },
    {
        "id": 1448,
        "name": "台北國際會議中心(TICC)",
        "url": "https://www.ticc.com.tw/",
        "type": "會議中心"
    },
    {
        "id": 1049,
        "name": "台北國際展演中心(TWTCA)",
        "url": "https://www.twtc.com.tw/",
        "type": "展演場地"
    }
]

print('='*80)
print('驗證會議中心和展演場地')
print('='*80)

results = []

for venue in test_venues:
    vid = venue['id']
    name = venue['name']
    url = venue['url']
    vtype = venue['type']

    print(f'\n[{vtype}] ID {vid}: {name}')
    print(f'URL: {url}')
    print('-'*60)

    result = {
        'id': vid,
        'name': name,
        'type': vtype,
        'url': url
    }

    try:
        # 測試1: 檢查頁面類型
        print('[1] 檢測網頁類型...')

        # 檢查 WordPress API
        api_url = urljoin(url, '/wp-json/wp/v2/pages')
        has_api = False

        try:
            api_resp = requests.get(api_url, timeout=5)
            if api_resp.status_code == 200:
                print(f'    類型: WordPress API')
                result['page_type'] = 'WordPress API'
                has_api = True
            else:
                print(f'    無WordPress API (status {api_resp.status_code})')
        except:
            print(f'    無WordPress API')

        if not has_api:
            # 檢查靜態內容
            resp = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            text = soup.get_text().lower()
            if '會議' in text or 'meeting' in text or '展演' in text:
                print(f'    類型: Static/SSR')
                result['page_type'] = 'Static/SSR'
            else:
                print(f'    類型: JavaScript (may need Playwright)')
                result['page_type'] = 'JavaScript (CSR)'

        # 測試2: 擷取基本資料
        print('[2] 擷取基本資料...')

        resp = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 電話
        import re
        phones = re.findall(r'0\d-\d{4}-\d{4}', soup.get_text())
        if phones:
            print(f'    電話: {phones[0]}')
            result['phone'] = phones[0]

        # Email
        emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', soup.get_text())
        if emails:
            print(f'    Email: {emails[0]}')
            result['email'] = emails[0]

        # 測試3: 尋找會議室相關連結
        print('[3] 尋找會議室連結...')

        meeting_links = []
        keywords = ['會議', 'meeting', '宴會', 'banquet']

        for a in soup.find_all('a', href=True):
            text = a.get_text().lower()
            href = a['href'].lower()

            if any(kw in text or kw in href for kw in keywords):
                meeting_links.append({
                    'text': a.get_text().strip()[:30],
                    'url': urljoin(url, a['href'])
                })

        print(f'    找到 {len(meeting_links)} 個會議連結')
        result['meeting_links_count'] = len(meeting_links)

        if meeting_links:
            print(f'    範例: {meeting_links[0]["text"]}: {meeting_links[0]["url"][:50]}')

        # 測試4: 統計連結數
        all_links = soup.find_all('a', href=True)
        print(f'[4] 總連結數: {len(all_links)}')
        result['total_links'] = len(all_links)

        result['success'] = True

    except Exception as e:
        print(f'    錯誤: {str(e)[:100]}')
        result['success'] = False
        result['error'] = str(e)

    results.append(result)
    print()

# 儲存結果
report = {
    'tested_at': datetime.now().isoformat(),
    'total_tested': len(results),
    'results': results
}

with open('venue_verification_simple.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print('='*80)
print('測試完成')
print(f'結果已儲存到 venue_verification_simple.json')

# 統計
static = sum(1 for r in results if r.get('page_type') == 'Static/SSR')
api_count = sum(1 for r in results if r.get('page_type') == 'WordPress API')
js = sum(1 for r in results if r.get('page_type') == 'JavaScript (CSR)')

print('\n統計:')
print(f'  Static/SSR: {static}')
print(f'  WordPress API: {api_count}')
print(f'  JavaScript: {js}')
