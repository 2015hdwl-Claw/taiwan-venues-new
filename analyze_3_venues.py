#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析台北世貿、萬豪、文華東方的現有資料
"""

import sys
import io
import json
import requests
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('分析三個場地：台北世貿、萬豪、文華東方')
    print('=' * 80)
    print()

    # 載入 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 三個場地 ID
    target_ids = [1049, 1103, 1085]
    target_names = {
        1049: '台北世貿中心',
        1103: '台北萬豪酒店',
        1085: '台北文華東方酒店'
    }

    for venue_id in target_ids:
        venue = next((v for v in venues if v.get('id') == venue_id), None)
        if not venue:
            continue

        name = venue.get('name', 'Unknown')
        url = venue.get('url', '')
        rooms = venue.get('rooms', [])

        print(f'[{venue_id}] {name}')
        print(f'URL: {url}')
        print(f'會議室數: {len(rooms)}')

        # 檢查是否有 PDF 連結
        print(f'檢查 PDF 連結...')
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            # 尋找 PDF 連結
            pdf_links = []
            if 'pdf' in response.text.lower():
                # 簡單搜尋 PDF 連結
                import re
                pdf_pattern = r'href=["\']([^"\']*\.pdf)["\']'
                pdf_matches = re.findall(pdf_pattern, response.text, re.IGNORECASE)
                pdf_links = pdf_matches[:5]  # 只取前 5 個

            if pdf_links:
                print(f'  ✅ 找到 {len(pdf_links)} 個 PDF 連結:')
                for i, pdf_url in enumerate(pdf_links, 1):
                    print(f'    {i}. {pdf_url}')
            else:
                print(f'  ⚠️  未找到 PDF 連結')

            # 儲存連結資訊
            venue['pdf_links'] = pdf_links

        except Exception as e:
            print(f'  ❌ 無法訪問: {e}')

        # 顯示現有會議室
        if rooms:
            print(f'現有會議室:')
            for i, room in enumerate(rooms[:3], 1):  # 只顯示前 3 個
                room_name = room.get('name', 'Unknown')
                has_price = room.get('price') is not None
                print(f'  {i}. {room_name} - 價格: {"✅" if has_price else "❌"}')
            if len(rooms) > 3:
                print(f'  ... 還有 {len(rooms) - 3} 個會議室')

        print()

    # 儲存分析結果
    print('[儲存分析結果]')

    # 備份
    backup_path = f"venues.json.backup.before_3venues_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'✅ 備份: {backup_path}')

    # 更新 venues.json（儲存 PDF 連結）
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'✅ 已更新 venues.json')

    print()
    print('=' * 80)
    print('下一步:')
    print('=' * 80)
    print()
    print('1. 檢查找到的 PDF 連結')
    print('2. 下載並使用 pdfplumber 解析')
    print('3. 建立細分場地結構（如需要）')
    print()


if __name__ == '__main__':
    main()
