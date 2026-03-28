#!/usr/bin/env python3
import requests
import json
import time

# 從 venues.json 讀取場地
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

active_venues = [v for v in venues if v.get('status') != 'discontinued' and v.get('url')]

print('='*80)
print('系統化檢查場地 API 可用性')
print('='*80)

# 常見的 API 端點模式
api_patterns = [
    '/wp-json/wp/v2/pages',      # WordPress REST API
    '/wp-json/wp/v2/posts',      # WordPress posts
    '/wp-json/acf/v3/pages',     # WordPress ACF
    '/api/venues',               # 自定義 API
    '/api/rooms',
    '/api/v1/rooms',
    '/jsonapi/rooms',
    '/_next/data',               # Next.js
    '/api/graphql',              # GraphQL
]

venues_with_api = []
tested_count = 0
max_test = 20  # 只測試前20個，避免花太多時間

for i, venue in enumerate(active_venues[:max_test], 1):
    venue_id = venue['id']
    name = venue.get('name', '')
    url = venue.get('url', '').rstrip('/')

    if not url:
        continue

    tested_count += 1
    print(f'\n[{tested_count}/{max_test}] ID {venue_id}: {name[:50]}')

    found_for_this_venue = []

    for pattern in api_patterns:
        api_url = url + pattern

        try:
            response = requests.get(api_url, timeout=3, headers={
                'Accept': 'application/json'
            })

            if response.status_code == 200:
                try:
                    data = response.json()

                    # 檢查是否為有效資料
                    if isinstance(data, list) and len(data) > 0:
                        print(f'  [OK] {pattern} - Array with {len(data)} items')
                        found_for_this_venue.append({
                            'endpoint': pattern,
                            'url': api_url,
                            'type': 'array',
                            'count': len(data)
                        })
                    elif isinstance(data, dict) and len(data) > 0:
                        keys = list(data.keys())[:3]
                        print(f'  [OK] {pattern} - Object with keys: {keys}')
                        found_for_this_venue.append({
                            'endpoint': pattern,
                            'url': api_url,
                            'type': 'object',
                            'keys': keys
                        })
                except:
                    pass
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except Exception:
            continue

    if found_for_this_venue:
        venues_with_api.append({
            'id': venue_id,
            'name': name,
            'url': url,
            'apis': found_for_this_venue
        })

    # 稍微延遲，避免請求過快
    time.sleep(0.2)

print('\n' + '='*80)
print(f'測試了 {tested_count} 個場地')
print(f'找到 {len(venues_with_api)} 個場地有 API ({len(venues_with_api)/tested_count*100:.1f}%)')
print('='*80)

if venues_with_api:
    print('\n有 API 的場地詳細資訊:')
    for venue in venues_with_api:
        print(f'\nID {venue["id"]}: {venue["name"][:60]}')
        print(f'  URL: {venue["url"]}')
        for api in venue['apis']:
            print(f'  API: {api["endpoint"]}')
            if api['type'] == 'array':
                print(f'       Array with {api["count"]} items')
            else:
                print(f'       Object with keys: {api["keys"]}')
else:
    print('\n沒有找到有 API 的場地')
    print('\n結論: 台灣場地網站大多沒有公開的 API')
    print('建議使用 requests + BeautifulSoup 或 Playwright')

# 儲存結果
result = {
    'tested_count': tested_count,
    'found_count': len(venues_with_api),
    'percentage': len(venues_with_api)/tested_count*100 if tested_count > 0 else 0,
    'venues_with_api': venues_with_api
}

with open('api_check_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'\n詳細結果已儲存到 api_check_result.json')
