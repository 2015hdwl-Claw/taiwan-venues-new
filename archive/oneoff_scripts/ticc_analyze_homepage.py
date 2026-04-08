#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC - 分析主頁尋找其他線索
"""

import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - 分析主頁")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

base_url = "https://www.ticc.com.tw/"

response = requests.get(base_url, timeout=15, verify=False)
print(f"主頁 HTTP 狀態: {response.status_code}")
print(f"最終 URL: {response.url}")
print(f"Content-Type: {response.headers.get('Content-Type')}\n")

soup = BeautifulSoup(response.text, 'html.parser')

# 儲存主頁
homepage_file = f"ticc_homepage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
with open(homepage_file, 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
print(f"✅ 主頁已儲存: {homepage_file}\n")

# 分析頁面結構
print("分析頁面結構...")
print("=" * 100)

# 檢查是否有 JavaScript 重定向
scripts = soup.find_all('script')
js_redirects = []
for script in scripts:
    if script.string:
        if 'location.href' in script.string or 'window.location' in script.string:
            js_redirects.append(script.string[:200])

if js_redirects:
    print("⚠️  發現 JavaScript 重定向:")
    for redirect in js_redirects:
        print(f"  {redirect}")

# 檢查 meta refresh
meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
if meta_refresh:
    print(f"⚠️  發現 meta refresh: {meta_refresh.get('content')}")

# 檢查 iframe
iframes = soup.find_all('iframe')
if iframes:
    print(f"⚠️  發現 {len(iframes)} 個 iframe:")
    for iframe in iframes:
        print(f"  src: {iframe.get('src')}")

# 檢查所有連結的域名
print("\n所有連結的域名分布:")
from urllib.parse import urlparse
import collections

domains = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if href.startswith('http'):
        parsed = urlparse(href)
        domains.append(parsed.netloc)

domain_counts = collections.Counter(domains)
for domain, count in domain_counts.most_common(10):
    print(f"  {domain}: {count}")

# 檢查是否有隱藏的表單或輸入
forms = soup.find_all('form')
if forms:
    print(f"\n發現 {len(forms)} 個表單:")
    for form in forms:
        print(f"  action: {form.get('action')}")
        print(f"  method: {form.get('method')}")

# 檢查頁面文字中的關鍵訊息
page_text = soup.get_text()

# 尋找可能的錯誤訊息
error_keywords = ['404', '錯誤', '找不到', 'error', 'not found', '維護中', '已搬遷', '已移除']
found_errors = []
for keyword in error_keywords:
    if keyword in page_text.lower():
        found_errors.append(keyword)

if found_errors:
    print(f"\n⚠️  頁面包含錯誤關鍵字: {', '.join(set(found_errors))}")

# 尋找新的網址資訊
new_url_patterns = [
    r'新網址[：:]\s*(https?://[^\s]+)',
    r'已搬家[到到]\s*(https?://[^\s]+)',
    r'請前往[：:]\s*(https?://[^\s]+)',
]

import re
for pattern in new_url_patterns:
    matches = re.findall(pattern, page_text)
    if matches:
        print(f"\n✅ 發現新網址訊息:")
        for match in matches:
            print(f"  {match}")

# 總結
print("\n" + "=" * 100)
print("分析總結")
print("=" * 100)

if js_redirects or meta_refresh or iframes:
    print("⚠️  頁面可能使用動態載入")
    print("建議: 使用模擬瀏覽器（Selenium）")

elif found_errors:
    print("❌ 頁面可能不存在或已搬遷")
    print("建議: 手動訪問確認正確網址")

else:
    print("✅ 頁面結構正常，但連結失效")
    print("建議: 檢查是否需要特殊認證或會話")

print(f"\n詳細內容請查看: {homepage_file}")
