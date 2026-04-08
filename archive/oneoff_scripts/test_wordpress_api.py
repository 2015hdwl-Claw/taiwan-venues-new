#!/usr/bin/env python3
import requests
import json

# 具體測試幾個知名場地是否有 WordPress API
test_venues = [
    {"name": "集思台大會議中心", "url": "https://www.meeting.com.tw/"},
    {"name": "台北君悅酒店", "url": "https://www.grandhyatttaipei.com/"},
    {"name": "台北國際會議中心", "url": "https://www.ticc.com.tw/"},
    {"name": "寒舍艾麗酒店", "url": "https://www.hotel-elixir.com.tw/"},
    {"name": "麗緻酒店", "url": "https://taipei.landishotelsresorts.com/"},
]

print("測試場地的 WordPress API 可用性\n")
print("="*80)

for venue in test_venues:
    name = venue["name"]
    base_url = venue["url"].rstrip('/')

    # 測試 WordPress API
    api_url = f"{base_url}/wp-json/wp/v2/pages"

    try:
        response = requests.get(api_url, timeout=5, headers={
            'Accept': 'application/json'
        })

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n{name}:")
                print(f"  URL: {base_url}")
                print(f"  [OK] 有 WordPress API")
                print(f"  端點: /wp-json/wp/v2/pages")
                print(f"  頁面數: {len(data) if isinstance(data, list) else 'N/A'}")

                # 顯示前3個頁面標題
                if isinstance(data, list) and len(data) > 0:
                    print(f"  頁面範例:")
                    for page in data[:3]:
                        title = page.get('title', {}).get('rendered', 'N/A')
                        # 清理 HTML 標籤
                        import re
                        title_clean = re.sub('<[^<]+?>', '', title)
                        print(f"    - {title_clean[:50]}")
            except:
                print(f"\n{name}: [X] API 回應但不是 JSON")
        else:
            print(f"\n{name}: [X] 無 WordPress API (狀態碼: {response.status_code})")
    except requests.exceptions.Timeout:
        print(f"\n{name}: [X] 逾時")
    except requests.exceptions.ConnectionError:
        print(f"\n{name}: [X] 無法連線")
    except Exception as e:
        print(f"\n{name}: [X] 錯誤: {str(e)[:50]}")

print("\n" + "="*80)
print("\n結論:")
print("如果場地使用 WordPress，通常會有 /wp-json/wp/v2/pages API")
print("這個 API 可以取得所有頁面的 JSON 資料")
