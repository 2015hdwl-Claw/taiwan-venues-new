#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載集思竹科會議中心完整場地資訊 PDF
"""

import requests
import os
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "https://www.meeting.com.tw/hsp/"

# PDF 列表
pdfs = [
    "download/竹科-場地租借申請表與注意事項-20250402.pdf",
    "download/竹科_會議室設備清單與租借費_20250214.pdf",
    "download/竹科_收費標準_202312.pdf",
    "download/竹科_詳細收費標準_202312.pdf",
    "download/竹科_取消規則_202312.pdf",
]

# 圖片列表
images = [
    "download/floorplan-2f.jpg",
    "download/floorplan-4f.jpg",
]

print("=" * 100)
print("下載集思竹科會議中心完整場地資訊")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

downloaded = []

# 下載 PDF
for pdf in pdfs:
    pdf_url = base_url + pdf
    pdf_filename = pdf.split('/')[-1]

    print(f"下載: {pdf_filename}")

    try:
        response = requests.get(pdf_url, timeout=30, verify=False)

        if response.status_code == 200:
            filepath = os.path.join('jhsi_hcph_docs', pdf_filename)
            os.makedirs('jhsi_hcph_docs', exist_ok=True)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            size_kb = len(response.content) / 1024
            print(f"  ✅ 已儲存: {filepath} ({size_kb:.1f} KB)")
            downloaded.append(filepath)
        else:
            print(f"  ❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

# 下載圖片
for img in images:
    img_url = base_url + img
    img_filename = img.split('/')[-1]

    print(f"下載: {img_filename}")

    try:
        response = requests.get(img_url, timeout=30, verify=False)

        if response.status_code == 200:
            filepath = os.path.join('jhsi_hcph_docs', img_filename)
            os.makedirs('jhsi_hcph_docs', exist_ok=True)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            size_kb = len(response.content) / 1024
            print(f"  ✅ 已儲存: {filepath} ({size_kb:.1f} KB)")
            downloaded.append(filepath)
        else:
            print(f"  ❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

print(f"\n✅ 下載完成: {len(downloaded)} 個檔案")
print(f"   儲存位置: jhsi_hcph_docs/")

print("\n" + "=" * 100)
print("✅ 下載完成")
print("=" * 100)
