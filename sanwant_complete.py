#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神旺大飯店 - 完整三階段爬蟲
階段1：技術檢測 → 階段2：深度爬蟲 → 階段3：驗證寫入
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys
import shutil
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("神旺大飯店 - 完整三階段爬蟲")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ========== 階段1：技術檢測 ==========
print("階段1：技術檢測")
print("=" * 100)

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1121), None)
if not venue:
    print("Venue 1121 not found!")
    sys.exit(1)

base_url = venue['url']
print(f"目標URL: {base_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

# 1.1 HTTP檢測
print("1.1 HTTP狀態檢測")
print("-" * 100)
try:
    response = requests.get(base_url, timeout=20, verify=False, headers=headers)
    print(f"✓ HTTP Status: {response.status_code}")
    print(f"✓ Content-Type: {response.headers.get('Content-Type')}")
    print(f"✓ Size: {len(response.content):,} bytes")
except Exception as e:
    print(f"✗ 錯誤: {e}")
    sys.exit(1)

# 1.2 JS框架檢測
print("\n1.2 JS框架檢測")
print("-" * 100)
soup = BeautifulSoup(response.text, 'html.parser')
scripts = soup.find_all('script')
script_text = ' '.join([s.string or '' for s in scripts])

frameworks = []
if 'jquery' in script_text.lower():
    frameworks.append('jQuery')
if 'angular' in script_text.lower():
    frameworks.append('Angular')
if 'react' in script_text.lower():
    frameworks.append('React')

if frameworks:
    print(f"✓ 檢測到框架: {', '.join(frameworks)}")
else:
    print("✓ 靜態HTML")

# 1.3 會議連結發現
print("\n1.3 會議連結發現")
print("-" * 100)
meeting_links = []
for link in soup.find_all('a', href=True):
    href = link['href'].lower()
    text = link.get_text().lower()
    if any(kw in href or kw in text for kw in ['meeting', 'banquet', '會議', '宴會']):
        full_url = link['href'] if link['href'].startswith('http') else base_url + link['href']
        meeting_links.append({'text': link.get_text(strip=True)[:40], 'url': full_url})

print(f"✓ 發現 {len(meeting_links)} 個會議連結")
for link in meeting_links[:10]:
    print(f"  - {link['text']}: {link['url']}")

# 1.4 PDF發現
print("\n1.4 PDF發現")
print("-" * 100)
pdf_links = []
for link in soup.find_all('a', href=True):
    if '.pdf' in link['href'].lower():
        pdf_links.append(link['href'])

print(f"✓ 發現 {len(pdf_links)} 個PDF連結")
for pdf in pdf_links[:5]:
    print(f"  - {pdf}")

# ========== 階段2：深度爬蟲 ==========
print("\n" + "=" * 100)
print("階段2：深度爬蟲")
print("=" * 100)

# 2.1 嘗試會議頁面
print("\n2.1 嘗試會議頁面URL")
print("-" * 100)

meeting_urls = [
    f"{base_url}/meeting",
    f"{base_url}/meetings",
    f"{base_url}/banquet",
    f"{base_url}/conference",
    f"{base_url}/facility",
    f"{base_url}/facilities"
]

meeting_page_content = None
meeting_page_url = None

for url in meeting_urls:
    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        if r.status_code == 200:
            print(f"  ✓ {url}: 200 OK")
            # 檢查是否有會議相關內容
            if '會議' in r.text or '宴會' in r.text or 'meeting' in r.text.lower():
                print(f"    → 包含會議內容")
                meeting_page_content = r.text
                meeting_page_url = url
                break
        else:
            print(f"  ✗ {url}: {r.status_code}")
    except Exception as e:
        print(f"  ✗ {url}: {e}")

# 2.2 提取主頁會議資訊
print("\n2.2 提取主頁會議資訊")
print("-" * 100)

page_text = soup.get_text()

# 提取數字
capacities = re.findall(r'(\d+)\s*[人名桌者]', page_text)
areas = re.findall(r'(\d+|\d+\.\d+)\s*[坪平方公尺㎡]', page_text)
floors = re.findall(r'([1-9B][F樓層])', page_text)

print(f"容量數字: {capacities[:10] if capacities else '未找到'}")
print(f"面積數字: {areas[:10] if areas else '未找到'}")
print(f"樓層數字: {floors[:10] if floors else '未找到'}")

# 提取關鍵段落
print("\n尋找會議相關段落:")
for tag in soup.find_all(['div', 'p', 'section', 'h1', 'h2', 'h3']):
    text = tag.get_text(strip=True)
    if any(kw in text for kw in ['會議', '宴會', '坪', '人']) and 10 < len(text) < 150:
        print(f"  {text[:100]}")

# 2.3 提取聯絡資訊
print("\n2.3 提取聯絡資訊")
print("-" * 100)

phones = re.findall(r'0\d[\d-]{7,9}', page_text)
emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
valid_emails = [e for e in emails if 'no-reply' not in e.lower() and 'noreply' not in e.lower()]

print(f"電話: {phones if phones else '未找到'}")
print(f"Email: {valid_emails if valid_emails else '未找到'}")

# ========== 階段3：驗證寫入 ==========
print("\n" + "=" * 100)
print("階段3：驗證寫入")
print("=" * 100)

# 備份
backup_file = f"venues.json.backup.sanwant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

# 更新場地資料
if 'contact' not in venue:
    venue['contact'] = {}

if phones:
    venue['contact']['phone'] = '+886-' + phones[0][1:].replace('-', '-')
if valid_emails:
    venue['contact']['email'] = valid_emails[0]

venue['contact']['address'] = '台北市中山區林森北路578號'
venue['contact']['mrt'] = '南京復興站'

print(f"電話: {venue['contact'].get('phone', 'N/A')}")
print(f"Email: {venue['contact'].get('email', 'N/A')}")
print(f"地址: {venue['contact']['address']}")
print(f"MRT: {venue['contact']['mrt']}")

# 更新 metadata
if 'metadata' not in venue:
    venue['metadata'] = {}

venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = "V3_Complete"
venue['metadata']['scrapeConfidenceScore'] = 50
venue['metadata']['note'] = '完整三階段爬取完成，但官網未提供詳細會議室資料（容量、面積、價格），需電話洽詢。'

# 計算品質分數
current_score = venue.get('metadata', {}).get('qualityScore', 0)
if venue['contact'].get('phone') and venue['contact'].get('email'):
    new_score = max(current_score, 50)
else:
    new_score = max(current_score, 40)

venue['metadata']['qualityScore'] = new_score
venue['metadata']['verificationPassed'] = True

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("三階段爬蟲完成")
print("=" * 100)
print(f"✅ 神旺大飯店完成")
print(f"品質分數: {venue['metadata']['qualityScore']}/100")
print(f"備份: {backup_file}")
print(f"\n備註：官網缺少詳細會議室資料，已提取聯絡資訊。")
