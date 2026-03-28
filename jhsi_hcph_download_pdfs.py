#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載集思竹科會議中心 PDF (使用正確的 URL 編碼)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "https://www.meeting.com.tw/hsp/download.php"

print("=" * 100)
print("下載集思竹科會議中心完整場地資訊 PDF")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 獲取下載頁面
response = requests.get(base_url, timeout=15, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# 找到所有 PDF 連結
pdf_links = [a.get('href') for a in soup.find_all('a', href=True) if '.pdf' in a.get('href', '') and '竹科' in a.get('href', '')]

print(f"找到 {len(pdf_links)} 個竹科相關 PDF\n")

os.makedirs('jhsi_hcph_docs', exist_ok=True)
downloaded = []

for pdf_href in pdf_links:
    # 轉換為完整 URL
    if pdf_href.startswith('http'):
        pdf_url = pdf_href
    else:
        pdf_url = urljoin(base_url, pdf_href)

    # 從 URL 提取檔名
    pdf_filename = pdf_href.split('/')[-1]
    if not pdf_filename.endswith('.pdf'):
        continue

    print(f"下載: {pdf_filename}")
    print(f"  URL: {pdf_url}")

    try:
        response = requests.get(pdf_url, timeout=30, verify=False)

        if response.status_code == 200:
            filepath = os.path.join('jhsi_hcph_docs', pdf_filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            size_kb = len(response.content) / 1024
            print(f"  ✅ 已儲存: {filepath} ({size_kb:.1f} KB)")
            downloaded.append(filepath)
        else:
            print(f"  ❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

    print()

print(f"✅ 下載完成: {len(downloaded)} 個 PDF")
print(f"   儲存位置: jhsi_hcph_docs/")

print("\n" + "=" * 100)
print("✅ PDF 下載完成")
print("=" * 100)
