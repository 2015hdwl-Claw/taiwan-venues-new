#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豪景大酒店 - 階段1：技術檢測與網站結構分析
完整嚴謹版本
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys
import warnings
import re
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("豪景大酒店 - 階段1：技術檢測（完整版）")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1126), None)

if not venue:
    print("Venue 1126 not found!")
    sys.exit(1)

base_url = venue['url']
print(f"目標URL: {base_url}\n")

# 1.1 HTTP狀態檢測
print("1.1 HTTP狀態檢測")
print("-" * 100)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

try:
    response = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"✓ HTTP Status: {response.status_code}")
    print(f"✓ Content-Type: {response.headers.get('Content-Type')}")
    print(f"✓ Content-Length: {len(response.content):,} bytes")
    print(f"✓ Server: {response.headers.get('Server', 'Unknown')}")
    print(f"✓ 最後修改: {response.headers.get('Last-Modified', 'Unknown')}")
except Exception as e:
    print(f"✗ 錯誤: {e}")
    sys.exit(1)

if response.status_code != 200:
    print("✗ 無法訪問主頁")
    sys.exit(1)

# 1.2 網頁載入方式檢測
print("\n1.2 網頁載入方式檢測")
print("-" * 100)

soup = BeautifulSoup(response.text, 'html.parser')

# 檢測Script標籤
scripts = soup.find_all('script')
print(f"Script標籤數量: {len(scripts)}")

# 檢測JS框架
js_frameworks = []
framework_patterns = {
    'react': ['react', 'reactdom', '__react'],
    'vue': ['vue', 'vuerouter', 'vuex'],
    'angular': ['angular', 'ng-app', 'ng-controller'],
    'jquery': ['jquery', '$.fn', 'jquery.min'],
    'bootstrap': ['bootstrap', 'btn-', 'navbar']
}

script_text = ' '.join([s.string or '' for s in scripts])
for framework, patterns in framework_patterns.items():
    if any(pattern in script_text.lower() for pattern in patterns):
        js_frameworks.append(framework)

if js_frameworks:
    print(f"✓ 檢測到JS框架: {', '.join(js_frameworks)}")
else:
    print("✓ 未檢測到主要JS框架（靜態HTML）")

# 檢測AJAX/API調用
ajax_patterns = ['fetch(', 'axios.', 'xmlhttprequest', '$.ajax', '$.get', '$.post']
has_ajax = any(pattern in script_text.lower() for pattern in ajax_patterns)
print(f"✓ AJAX動態載入: {'是' if has_ajax else '否'}")

# 1.3 資料位置檢測
print("\n1.3 資料位置檢測")
print("-" * 100)

# 檢測JSON-LD
json_ld_scripts = soup.find_all('script', type='application/ld+json')
if json_ld_scripts:
    print(f"✓ 發現 {len(json_ld_scripts)} 個JSON-LD腳本")
    for i, script in enumerate(json_ld_scripts[:3]):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and '@type' in data:
                print(f"  類型: {data.get('@type')}")
        except:
            pass
else:
    print("✓ 未發現JSON-LD")

# 檢測內嵌JSON
inline_json = re.findall(r'\{[\s\S]*?"name"[\s\S]*?\}', str(soup))
if inline_json:
    print(f"✓ 發現 {len(inline_json)} 個可能的JSON對象")

# 1.4 反爬蟲機制檢測
print("\n1.4 反爬蟲機制檢測")
print("-" * 100)

# 檢測Cloudflare
cloudflare_indicators = ['cloudflare', '__cf', 'cf-challenge', 'cf-ray']
has_cloudflare = any(indicator in response.text.lower() for indicator in cloudflare_indicators)
print(f"✓ Cloudflare保護: {'是' if has_cloudflare else '否'}")

# 檢測Cookies
print(f"✓ Cookies數量: {len(response.cookies)}")
if response.cookies:
    for cookie in response.cookies:
        print(f"  - {cookie.name}: {cookie.value[:20]}...")

# 檢測Rate Limiting
rate_limit_headers = ['x-rate-limit', 'x-ratelimit', 'retry-after']
has_rate_limit = any(header in response.headers for header in rate_limit_headers)
print(f"✓ Rate Limiting: {'是' if has_rate_limit else '否'}")

# 1.5 會議/宴會連結發現
print("\n1.5 會議/宴會連結發現")
print("-" * 100)

meeting_links = []

for link in soup.find_all('a', href=True):
    href = link['href'].lower()
    text = link.get_text().lower()

    keywords = ['meeting', 'banquet', 'conference', 'event', 'mice', 'wedding',
                '會議', '宴會', '會議室', '婚宴', '活動', '場地']

    if any(keyword in href or keyword in text for keyword in keywords):
        full_url = link['href'] if link['href'].startswith('http') else base_url.rstrip('/') + '/' + link['href'].lstrip('/')
        meeting_links.append({
            'text': link.get_text(strip=True),
            'url': full_url,
            'type': 'internal' if not link['href'].startswith('http') else 'external'
        })

# 去重
seen = set()
unique_links = []
for link in meeting_links:
    if link['url'] not in seen:
        seen.add(link['url'])
        unique_links.append(link)

print(f"✓ 發現 {len(unique_links)} 個會議/宴會相關連結:")
for link in unique_links[:20]:
    print(f"  [{link['type']}] {link['text'][:50]:50s} | {link['url']}")

# 1.6 PDF連結發現
print("\n1.6 PDF連結發現")
print("-" * 100)

pdf_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if '.pdf' in href.lower():
        if not href.startswith('http'):
            href = href if href.startswith('/') else base_url + href
        pdf_links.append({
            'text': link.get_text(strip=True),
            'url': href
        })

print(f"✓ 發現 {len(pdf_links)} 個PDF連結:")
for pdf in pdf_links:
    print(f"  - {pdf['text'][:40]:40s} | {pdf['url']}")

# 1.7 URL模式猜測
print("\n1.7 URL模式猜測")
print("-" * 100)

url_patterns = [
    '/meeting',
    '/meetings',
    '/banquet',
    '/banquets',
    '/conference',
    '/event',
    '/events',
    '/wedding',
    '/facilities',
    '/會議',
    '/宴會',
    '/會議室',
    '/婚宴'
]

print("測試常見會議頁面URL模式:")
for pattern in url_patterns:
    test_url = base_url.rstrip('/') + pattern
    try:
        r = requests.head(test_url, timeout=10, verify=False, headers=headers)
        if r.status_code == 200:
            print(f"  ✓ {pattern}: 200 OK")
        elif r.status_code == 404:
            print(f"  ✗ {pattern}: 404 Not Found")
        else:
            print(f"  ~ {pattern}: {r.status_code}")
    except:
        print(f"  ✗ {pattern}: 錯誤")

# 1.8 檢查現有資料
print("\n1.8 檢查現有資料")
print("-" * 100)

print(f"場地名稱: {venue.get('name')}")
print(f"當前品質分數: {venue.get('metadata', {}).get('qualityScore', 'N/A')}")
print(f"會議室數量: {len(venue.get('rooms', []))}")

rooms = venue.get('rooms', [])
if rooms:
    print(f"\n現有會議室:")
    for room in rooms:
        name = room.get('name', 'N/A')
        area = room.get('areaSqm') or room.get('area')
        cap = room.get('capacity')
        cap_str = str(cap.get('theater', 'N/A')) if isinstance(cap, dict) else str(cap) if cap else 'N/A'
        print(f"  - {name}: 面積={area}㎡, 容量={cap_str}人")
else:
    print("  ⚠️  無會議室資料")

# 儲存階段1結果
stage1_result = {
    "venue": "豪景大酒店",
    "venue_id": 1126,
    "timestamp": datetime.now().isoformat(),
    "http_status": response.status_code,
    "content_type": response.headers.get('Content-Type'),
    "content_size": len(response.content),
    "js_frameworks": js_frameworks,
    "has_ajax": has_ajax,
    "has_cloudflare": has_cloudflare,
    "cookies_count": len(response.cookies),
    "meeting_links": unique_links,
    "pdf_links": pdf_links
}

with open('riverview_stage1_results.json', 'w', encoding='utf-8') as f:
    json.dump(stage1_result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("階段1完成")
print("=" * 100)
print(f"會議連結: {len(unique_links)}")
print(f"PDF連結: {len(pdf_links)}")
print(f"結果已儲存: riverview_stage1_results.json")
