#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 Top 10 場地哪些需要使用 pdfplumber 重新解析
"""

import sys
import io
import json
import os
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('Top 10 場地 PDF 檢查')
    print('=' * 80)
    print()

    # Top 10 場地 ID
    top10_ids = [1049, 1122, 1448, 1053, 1103, 1128, 1042, 1125, 1129, 1085]

    # 載入 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 檢查本地 PDF 檔案
    pdf_files = list(Path('.').glob('*.pdf'))

    print('[本地 PDF 檔案]')
    print(f'找到 {len(pdf_files)} 個 PDF 檔案:')
    for pdf in sorted(pdf_files):
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f'  - {pdf.name} ({size_mb:.1f} MB)')
    print()

    # 檢查每個場地
    print('[場地分析]')
    print()

    for venue_id in top10_ids:
        venue = next((v for v in venues if v.get('id') == venue_id), None)
        if not venue:
            continue

        name = venue.get('name', 'Unknown')
        has_pdf = 'pdfParser' in venue.get('metadata', {})
        has_subspaces = venue.get('metadata', {}).get('hasSubSpaces', False)
        rooms = venue.get('rooms', [])
        total_subspaces = sum(len(r.get('subSpaces', [])) for r in rooms)

        print(f'{venue_id}. {name}')
        print(f'   使用 pdfplumber: {"✅" if has_pdf else "❌"}')
        print(f'   有 subSpaces: {"✅" if has_subspaces else "❌"}')
        print(f'   會議室數: {len(rooms)}')
        if total_subspaces > 0:
            print(f'   細分場地數: {total_subspaces}')

        # 檢查價格覆蓋
        if has_subspaces:
            with_price = sum(1 for r in rooms
                           for s in r.get('subSpaces', [])
                           if s.get('price'))
            coverage = (with_price / total_subspaces * 100) if total_subspaces else 0
            print(f'   價格覆蓋: {coverage:.0f}% ({with_price}/{total_subspaces})')
        else:
            with_price = sum(1 for r in rooms if r.get('price'))
            coverage = (with_price / len(rooms) * 100) if rooms else 0
            print(f'   價格覆蓋: {coverage:.0f}% ({with_price}/{len(rooms)})')

        # 檢查是否有相關 PDF
        related_pdfs = [pdf for pdf in pdf_files if name.replace('酒店', '').replace('會議中心', '')[:3] in pdf.name or 'victoria' in pdf.name.lower() or 'ntu' in pdf.name.lower()]
        if related_pdfs:
            print(f'   相關 PDF: {[p.name for p in related_pdfs]}')

        print()

    print('=' * 80)
    print('建議處理順序:')
    print('=' * 80)
    print()
    print('🔴 高優先級（已有 PDF，需重新解析）')
    print('  1. 維多麗亞酒店 (1122) - ✅ 已完成')
    print('  2. 集思台大會議中心 (1128) - 可能有細分場地')
    print()
    print('🟡 中優先級（可能有 PDF）')
    print('  3. 台北世貿中心 (1049) - 尋找 PDF')
    print('  4. 台北萬豪酒店 (1103) - 尋找 PDF')
    print()
    print('🟢 低優先級（連線失敗）')
    print('  5. TICC (1448) - 403 Forbidden')
    print('  6. 公務人力發展學院 (1042) - 連線失敗')
    print('  7. 華山1914 (1125) - 連線失敗')
    print()


if __name__ == '__main__':
    main()
