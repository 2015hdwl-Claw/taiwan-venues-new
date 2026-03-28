#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思竹科會議中心 - 三階段完整流程
階段1：技術檢測
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime
from urllib.parse import urljoin
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

venue_id = 1496
venue_name = "集思竹科會議中心(HSPH)"

print("=" * 100)
print(f"{venue_name} - 階段1：技術檢測")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json 獲取 URL
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v.get('id') == venue_id), None)

if not venue:
    print(f"❌ 找不到場地 (ID: {venue_id})")
    sys.exit(1)

url = venue.get('url')
if not url:
    print(f"❌ 場地沒有 URL")
    sys.exit(1)

print(f"場地 URL: {url}\n")

# 1.1 HTTP 狀態碼檢測
print("1.1 HTTP 狀態碼檢測...")
try:
    response = requests.get(url, timeout=15, verify=False)
    http_status = response.status_code
    print(f"  HTTP 狀態: {http_status}")
    print(f"  最終 URL: {response.url}")
    print(f"  重導向: {'是' if response.url != url else '否'}")
except Exception as e:
    print(f"  ❌ 錯誤: {e}")
    sys.exit(1)

# 1.2 Content-Type 檢測
print("\n1.2 Content-Type 檢測...")
content_type = response.headers.get('Content-Type', '')
print(f"  Content-Type: {content_type}")

if 'html' in content_type.lower():
    page_type = "HTML"
elif 'pdf' in content_type.lower():
    page_type = "PDF"
elif 'json' in content_type.lower():
    page_type = "JSON"
else:
    page_type = "未知"

print(f"  頁面類型: {page_type}")

# 1.3 JS 框架檢測
print("\n1.3 JavaScript 框架檢測...")
soup = BeautifulSoup(response.text, 'html.parser')

js_frameworks = []
scripts = soup.find_all('script')

script_sources = [s.get('src', '') for s in scripts if s.get('src')]
script_contents = [s.string for s in scripts if s.string]

for src in script_sources:
    if 'react' in src.lower():
        js_frameworks.append('React')
    elif 'vue' in src.lower():
        js_frameworks.append('Vue')
    elif 'angular' in src.lower():
        js_frameworks.append('Angular')
    elif 'jquery' in src.lower():
        js_frameworks.append('jQuery')

if js_frameworks:
    print(f"  檢測到的框架: {', '.join(set(js_frameworks))}")
else:
    print(f"  檢測到的框架: 無")

# 判斷載入方式
if len(js_frameworks) > 0 or 'vue' in response.text.lower() or 'react' in response.text.lower():
    loading_method = "動態渲染 (可能需要 JS)"
else:
    loading_method = "靜態/SSR"

print(f"  載入方式: {loading_method}")

# 1.4 資料位置檢測
print("\n1.4 資料位置檢測...")

# 檢查 JSON-LD
json_ld_scripts = soup.find_all('script', type='application/ld+json')
if json_ld_scripts:
    print(f"  JSON-LD: {len(json_ld_scripts)} 個")
else:
    print(f"  JSON-LD: 0 個")

# 檢查內嵌 JSON
json_pattern = r'window\.__INITIAL_STATE__|window\.INITIAL_STATE'
if re.search(json_pattern, response.text):
    print(f"  內嵌 JSON: 是")
else:
    print(f"  內嵌 JSON: 否")

# 檢查 HTML 結構
meeting_keywords = ['meeting', 'room', 'venue', 'conference', '會議', '場地', '會議室', '廳']
page_text = soup.get_text().lower()
has_meeting_info = any(kw in page_text for kw in meeting_keywords)

if has_meeting_info:
    print(f"  HTML 包含會議關鍵字: 是")
else:
    print(f"  HTML 包含會議關鍵字: 否")

# 1.5 反爬蟲機制檢測
print("\n1.5 反爬蟲機制檢測...")

server = response.headers.get('Server', '')
print(f"  Server: {server}")

if 'cloudflare' in server.lower() or 'cf-ray' in response.headers:
    anti_scraping = "Cloudflare"
elif 'incapsula' in response.headers.get('X-CDN', '').lower():
    anti_scraping = "Incapsula"
else:
    anti_scraping = "未檢測到"

print(f"  反爬蟲: {anti_scraping}")

# 檢查 Cookies
cookies_count = len(response.cookies)
print(f"  Cookies: {cookies_count} 個")

# 檢查 Session/Token
session_pattern = r'(csrf|session|token)'
has_session = bool(re.search(session_pattern, response.text.lower()))
print(f"  Session Token: {'是' if has_session else '否'}")

# 1.6 鏈結發現
print("\n1.6 鏈結發現...")

all_links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)
    all_links.append({'text': text, 'href': href})

# 分類鏈結
meeting_links = [l for l in all_links if any(kw in l['text'].lower() or kw in l['href'].lower()
               for kw in ['meeting', 'room', 'venue', '會議', '場地', '會議室'])]
pricing_links = [l for l in all_links if any(kw in l['text'].lower() or kw in l['href'].lower()
               for kw in ['price', 'pricing', 'cost', 'rate', '租金', '價格', '費用'])]
contact_links = [l for l in all_links if any(kw in l['text'].lower() or kw in l['href'].lower()
               for kw in ['contact', 'tel', 'phone', 'email', '聯絡', '電話', '信箱'])]

print(f"  總鏈結數: {len(all_links)}")
print(f"  會議相關: {len(meeting_links)}")
print(f"  價格相關: {len(pricing_links)}")
print(f"  聯絡相關: {len(contact_links)}")

# 顯示前 5 個會議相關鏈結
if meeting_links:
    print(f"\n  會議相關鏈結（前5個）:")
    for i, link in enumerate(meeting_links[:5], 1):
        print(f"    {i}. {link['text'][:60]}")
        print(f"       {link['href']}")

# 儲存階段1結果
stage1_result = {
    "venue": venue_name,
    "venue_id": venue_id,
    "url": url,
    "stage1": {
        "http_status": http_status,
        "content_type": content_type,
        "page_type": page_type,
        "js_frameworks": list(set(js_frameworks)),
        "loading_method": loading_method,
        "json_ld_count": len(json_ld_scripts) if json_ld_scripts else 0,
        "has_embedded_json": bool(re.search(json_pattern, response.text)),
        "has_meeting_keywords": has_meeting_info,
        "anti_scraping": anti_scraping,
        "cookies_count": cookies_count,
        "has_session_token": has_session,
        "links": {
            "total": len(all_links),
            "meeting": len(meeting_links),
            "pricing": len(pricing_links),
            "contact": len(contact_links)
        }
    },
    "timestamp": datetime.now().isoformat()
}

result_file = f'{venue_name}_stage1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(stage1_result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 階段1結果已儲存: {result_file}")

# 階段1 結論
print("\n" + "=" * 100)
print("階段1 結論與建議")
print("=" * 100)

print(f"\n技術檢測摘要:")
print(f"  HTTP 狀態: {http_status}")
print(f"  頁面類型: {page_type}")
print(f"  載入方式: {loading_method}")
print(f"  反爬蟲: {anti_scraping}")

print(f"\n鏈結發現:")
print(f"  會議相關鏈結: {len(meeting_links)} 個")
print(f"  價格相關鏈結: {len(pricing_links)} 個")
print(f"  聯絡相關鏈結: {len(contact_links)} 個")

print("\n建議:")

if anti_scraping != "未檢測到":
    print(f"  ⚠️  檢測到 {anti_scraping} 反爬蟲機制")
    print(f"  建議：使用模擬瀏覽器（Selenium）或手動處理")
elif loading_method == "動態渲染 (可能需要 JS)":
    print(f"  ⚠️  頁面使用動態渲染")
    print(f"  建議：使用 Selenium 或 Playwright 爬取")
elif len(meeting_links) == 0 and len(pricing_links) == 0:
    print(f"  ⚠️  未找到明顯的會議/價格鏈結")
    print(f"  建議：深度檢查頁面內容，可能需要解析複雜結構")
else:
    print(f"  ✅ 可以直接爬取")
    print(f"  建議：進入階段2，深度爬取所有相關頁面")

print("\n" + "=" * 100)
print(f"✅ {venue_name} 階段1完成")
print("=" * 100)
