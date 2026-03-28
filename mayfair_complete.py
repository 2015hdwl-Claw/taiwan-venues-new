#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北美福大飯店 - 完整爬蟲（應用教訓版）
追蹤所有連結，包括動態URL和參數
"""

import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import re
import shutil
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北美福大飯店 - 完整爬蟲（應用教訓版）")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.mayfair_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1095), None)
if not venue:
    print("Venue 1095 not found!")
    sys.exit(1)

base_url = 'https://www.grandmayfull.com/'
print(f"場地: {venue['name']}")
print(f"URL: {base_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

# ========== 步驟1：從主頁提取所有連結 ==========
print("步驟1：提取主頁所有連結")
print("=" * 100)

try:
    r = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP Status: {r.status_code}")
    print(f"Content-Length: {len(r.content):,} bytes\n")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')

        # 提取所有連結
        all_links = []
        seen_urls = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if not href or href.startswith('javascript:') or href.startswith('#'):
                continue

            # 轉換為絕對URL
            if href.startswith('/'):
                full_url = base_url.rstrip('/') + href
            elif not href.startswith('http'):
                full_url = base_url + href
            else:
                full_url = href

            # 去重
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                all_links.append({
                    'text': text[:60],
                    'url': full_url
                })

        print(f"發現 {len(all_links)} 個連結\n")

        # 分類連結
        internal_links = []
        dynamic_links = []
        file_links = []

        for link in all_links:
            url = link['url']

            # 分類動態連結（有參數）
            parsed = urllib.parse.urlparse(url)
            if parsed.query:
                dynamic_links.append(link)

            # 分類檔案連結
            if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                file_links.append(link)

            # 內部連結
            if url.startswith(base_url.rstrip('/')):
                internal_links.append(link)

        print(f"內部連結: {len(internal_links)}")
        print(f"動態連結: {len(dynamic_links)}")
        print(f"檔案連結: {len(file_links)}\n")

        # 顯示動態連結（關鍵！）
        if dynamic_links:
            print("發現的動態連結（包含參數）:")
            print("-" * 100)
            for link in dynamic_links[:20]:
                print(f"  {link['text']}")
                print(f"    URL: {link['url']}")

        # 顯示PDF連結
        if file_links:
            print("\n發現的檔案連結:")
            print("-" * 100)
            for link in file_links:
                if '.pdf' in link['url'].lower():
                    print(f"  PDF: {link['url']}")

except Exception as e:
    print(f"錯誤: {e}")
    sys.exit(1)

# ========== 步驟2：訪問所有動態URL頁面 ==========
print("\n" + "=" * 100)
print("步驟2：訪問動態URL頁面")
print("=" * 100)

if dynamic_links:
    for i, link in enumerate(dynamic_links[:10]):  # 最多處理10個
        url = link['url']
        print(f"\n[{i+1}/{min(len(dynamic_links), 10)}] 訪問: {url}")
        print("-" * 100)

        try:
            r = requests.get(url, timeout=15, verify=False, headers=headers)
            print(f"  Status: {r.status_code}")

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')

                # 提取頁面文字
                text = soup.get_text()

                # 尋找會議室相關資訊
                print(f"  頁面長度: {len(text):,} 字符")

                # 提取容量
                capacities = re.findall(r'(\d+)\s*[人名桌者席位]', text)
                if capacities:
                    print(f"  容量數字: {capacities[:10]}")

                # 提取面積
                areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡])', text)
                if areas:
                    print(f"  面積數字: {areas[:10]}")

                # 提取價格
                prices = re.findall(r'(\d+,?\d*)\s*元', text)
                if prices:
                    print(f"  價格數字: {prices[:10]}")

                # 顯示前1000字
                if len(text) > 0:
                    lines = [l.strip() for l in text.split('\n') if 20 < len(l.strip()) < 150]
                    if lines:
                        print(f"  頁面內容預覽:")
                        for line in lines[:5]:
                            print(f"    {line[:100]}")

        except Exception as e:
            print(f"  錯誤: {e}")

# ========== 步驟3：嘗試常見動態參數模式 ==========
print("\n" + "=" * 100)
print("步驟3：嘗試常見動態參數模式")
print("=" * 100)

# 根據台北艾麗的經驗，嘗試類似模式
param_patterns = [
    '?cat=page&id=',  # WebSev CMS
    '?page_id=',     # WordPress
    '?p=',           # WordPress簡寫
    '?post=',        # WordPress文章
    '?id=',          # 通用ID
]

for pattern in param_patterns:
    # 嘗試常見ID範圍
    for id_num in range(100, 200):
        test_url = f"{base_url.rstrip('/')}{pattern}{id_num}"
        print(f"嘗試: {test_url}")

        try:
            r = requests.head(test_url, timeout=5, verify=False, headers=headers)
            if r.status_code == 200:
                print(f"  ✓ 200 OK - 找到頁面！")
                # 記錄這個URL供後續處理
                break
            elif r.status_code == 404:
                pass  # 繼續嘗試
            else:
                print(f"  ~ {r.status_code}")
        except:
            pass

    # 如果找到200的頁面，停止嘗試
    if r.status_code == 200:
        break

# ========== 步驟4：提取並顯示結果 ==========
print("\n" + "=" * 100)
print("爬蟲完成")
print("=" * 100)
print(f"總共發現: {len(all_links)} 個連結")
print(f"動態URL: {len(dynamic_links)} 個")
print(f"檔案連結: {len(file_links)} 個")
print(f"\n備份: {backup_file}")
print("\n下一步: 根�發現的資料更新 venues.json")
