#!/usr/bin/env python3
import requests
import json

# 測試幾個知名場地是否有 API
test_venues = [
    {
        "name": "集思台大會議中心",
        "url": "https://www.meeting.com.tw/",
        "possible_apis": [
            "https://www.meeting.com.tw/api/rooms",
            "https://www.meeting.com.tw/wp-json/wp/v2/pages"
        ]
    },
    {
        "name": "台北國際會議中心 (TICC)",
        "url": "https://www.ticc.com.tw/",
        "possible_apis": [
            "https://www.ticc.com.tw/api/rooms",
            "https://www.ticc.com.tw/wp-json/wp/v2/pages"
        ]
    },
    {
        "name": "台北君悅酒店",
        "url": "https://www.grandhyatttaipei.com/",
        "possible_apis": [
            "https://www.grandhyatttaipei.com/api/rooms",
            "https://www.grandhyatttaipei.com/wp-json/wp/v2/pages"
        ]
    },
    {
        "name": "寒舍艾麗酒店",
        "url": "https://www.hotel-elixir.com.tw/",
        "possible_apis": [
            "https://www.hotel-elixir.com.tw/api/rooms",
            "https://www.hotel-elixir.com.tw/wp-json/wp/v2/pages"
        ]
    },
    {
        "name": "台大醫院國際會議中心",
        "url": "https://www.ntuh.gov.tw/",
        "possible_apis": [
            "https://www.ntuh.gov.tw/api/rooms",
            "https://www.ntuh.gov.tw/wp-json/wp/v2/pages"
        ]
    }
]

print('='*80)
print('測試知名場地的 API 可用性')
print('='*80)

venues_with_api = []

for venue in test_venues:
    name = venue["name"]
    base_url = venue["url"]

    print(f'\n場地: {name}')
    print(f'URL: {base_url}')

    found_apis = []

    for api_url in venue["possible_apis"]:
        try:
            response = requests.get(api_url, timeout=5, headers={
                'Accept': 'application/json'
            })

            if response.status_code == 200:
                try:
                    data = response.json()

                    # 檢查資料內容
                    data_preview = str(data)[:100]

                    print(f'  [OK] {api_url}')
                    print(f'       {data_preview}')

                    found_apis.append({
                        'url': api_url,
                        'data': data
                    })
                except Exception as e:
                    print(f'  [{response.status_code}] {api_url} (not JSON)')
        except Exception as e:
            print(f'  [X] {api_url} - {str(e)[:50]}')

    if found_apis:
        venues_with_api.append({
            'name': name,
            'url': base_url,
            'apis': found_apis
        })

print('\n' + '='*80)
print(f'總計: {len(venues_with_api)} / {len(test_venues)} 個場地有 API')
print('='*80)

if venues_with_api:
    print('\n有 API 的場地:')
    for venue in venues_with_api:
        print(f'\n{venue["name"]}:')
        for api in venue['apis']:
            print(f'  - {api["url"]}')
