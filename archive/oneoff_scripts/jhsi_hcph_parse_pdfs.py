#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析集思竹科 PDF - 提取價格與場地資訊
"""

import pdfplumber
import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("解析集思竹科 PDF 資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# PDF 列表
pdfs = [
    'jhsi_hcph_docs/竹科_租借辦法_202312.pdf',
    'jhsi_hcph_docs/竹科_管理規則_202312.pdf',
    'jhsi_hcph_docs/竹科_餐飲管理規則_202312.pdf',
]

all_data = {}

for pdf_path in pdfs:
    print(f"\n{'=' * 100}")
    print(f"解析: {pdf_path.split('/')[-1]}")
    print('=' * 100)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"總頁數: {len(pdf.pages)}\n")

            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    print(f"--- 第 {i} 頁 ---")
                    # 只顯示前 1500 字元
                    print(text[:1500])
                    print("...\n")

                    # 儲存到 all_data
                    pdf_name = pdf_path.split('/')[-1]
                    if pdf_name not in all_data:
                        all_data[pdf_name] = []

                    all_data[pdf_name].append({
                        'page': i,
                        'text': text
                    })

    except Exception as e:
        print(f"❌ 錯誤: {e}")

# 儲存完整資料
output_file = 'jhsi_hcph_pdf_parsed.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 完整資料已儲存: {output_file}")

print("\n" + "=" * 100)
print("✅ PDF 解析完成")
print("=" * 100)
