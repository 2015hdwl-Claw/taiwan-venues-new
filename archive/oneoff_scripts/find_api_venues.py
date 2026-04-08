#!/usr/bin/env python3
"""
檢查哪些場地有可用的 API
"""
import requests
import json
from urllib.parse import urljoin

def check_api_endpoints(base_url):
    """檢查常見的 API 端點"""

    api_endpoints = [
        '/api/rooms',
        '/api/venue/rooms',
        '/api/meeting-rooms',
        '/api/v1/rooms',
        '/wp-json/wp/v2/rooms',  # WordPress REST API
        '/wp-json/wp/v2/pages',  # WordPress 頁面
        '/jsonapi/rooms',        # JSON:API
    ]

    found_apis = []

    for endpoint in api_endpoints:
        try:
            api_url = urljoin(base_url, endpoint)
            response = requests.get(api_url, timeout=5, headers={
                'Accept': 'application/json'
            })

            if response.status_code == 200:
                try:
                    data = response.json()
                    # 檢查是否為有效資料
                    if data and isinstance(data, (dict, list)):
                        found_apis.append({
                            'endpoint': endpoint,
                            'url': api_url,
                            'status': response.status_code,
                            'data_keys': list(data.keys())[:5] if isinstance(data, dict) else f"array with {len(data)} items"
                        })
                except:
                    pass
        except:
            continue

    return found_apis

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 選擇活躍場地進行測試
active_venues = [v for v in venues if v.get('status') != 'discontinued' and v.get('url')]

print(f'測試 {len(active_venues)} 個場地的 API 可用性...\n')
print('='*80)

venues_with_api = []

for i, venue in enumerate(active_venues, 1):
    venue_id = venue['id']
    name = venue.get('name', '')
    url = venue.get('url', '')

    if not url:
        continue

    print(f'\n[{i}/{len(active_venues)}] ID {venue_id}: {name[:40]}')
    print(f'URL: {url}')

    apis = check_api_endpoints(url)

    if apis:
        print(f'[OK] Found {len(apis)} API endpoints:')
        for api in apis:
            print(f'  - {api["endpoint"]}')
            print(f'    {api["data_keys"]}')

        venues_with_api.append({
            'id': venue_id,
            'name': name,
            'url': url,
            'apis': apis
        })
    else:
        print('[X] No API found')

print('\n' + '='*80)
print(f'\n總計: {len(venues_with_api)} 個場地有 API ({len(venues_with_api)/len(active_venues)*100:.1f}%)')

if venues_with_api:
    print('\n有 API 的場地列表:')
    for venue in venues_with_api:
        print(f'  ID {venue["id"]}: {venue["name"][:50]}')
        for api in venue['apis']:
            print(f'    {api["endpoint"]}')

# 儲存結果
with open('api_venues_report.json', 'w', encoding='utf-8') as f:
    json.dump(venues_with_api, f, ensure_ascii=False, indent=2)

print(f'\n詳細結果已儲存到 api_venues_report.json')
