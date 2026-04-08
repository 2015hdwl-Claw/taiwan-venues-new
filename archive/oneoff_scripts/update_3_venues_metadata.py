#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新台北世貿、萬豪、文華東方的 metadata
標記價格資訊狀態
"""

import sys
import io
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('更新三個場地的 metadata')
    print('=' * 80)
    print()

    # 載入 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 三個場地 ID
    target_ids = [1049, 1103, 1085]

    # 備份
    backup_path = f"venues.json.backup.before_metadata_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f'✅ 備份: {backup_path}')
    print()

    # 更新每個場地
    for venue_id in target_ids:
        venue = next((v for v in venues if v.get('id') == venue_id), None)
        if not venue:
            continue

        name = venue.get('name', 'Unknown')

        # 初始化 metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}

        # 根據場地 ID 設定不同的註解
        if venue_id == 1049:  # 台北世貿
            print(f'[1/3] 台北世貿中心')
            print(f'  會議室數: {len(venue.get("rooms", []))}')

            # 更新 metadata
            venue['metadata'].update({
                'priceStatus': 'require_inquiry',
                'priceSource': '需聯絡詢問',
                'priceReason': '官網無價格資訊，只有容量資訊',
                'priceInquiryNote': '已檢查會議室頁面（meeting1, meeting2等），無價格資訊',
                'hasPDF': False,
                'pdfCheckedAt': datetime.now().isoformat(),
                'webCheckDetail': '檢查了 4 個會議室頁面，都有容量資訊但無價格',
                'recommendedAction': '聯絡台北世貿中心詢問會議室租借價格',
                'contactInfo': 'https://www.twtc.com.tw/ 有聯絡資訊'
            })

            print(f'  ✅ 已標記為「需聯絡詢問」')

        elif venue_id == 1103:  # 台北萬豪
            print(f'[2/3] 台北萬豪酒店')
            print(f'  會議室數: {len(venue.get("rooms", []))}')

            venue['metadata'].update({
                'priceStatus': 'require_inquiry',
                'priceSource': '需聯絡詢問',
                'priceReason': '可能使用 JavaScript 動態載入價格',
                'technicalIssue': 'JavaScript 動態載入',
                'hasPDF': False,
                'pdfCheckedAt': datetime.now().isoformat(),
                'webCheckDetail': '首頁未找到 PDF 連結，可能需要 Playwright 處理',
                'recommendedAction': '使用 Playwright 爬取或聯絡酒店',
                'contactInfo': 'https://www.taipeimarriott.com.tw/ 有聯絡資訊'
            })

            print(f'  ✅ 已標記為「需聯絡詢問」')

        elif venue_id == 1085:  # 台北文華東方
            print(f'[3/3] 台北文華東方酒店')
            print(f'  會議室數: {len(venue.get("rooms", []))}')

            venue['metadata'].update({
                'priceStatus': 'require_inquiry',
                'priceSource': '需聯絡詢問',
                'priceReason': '官網無價格資訊',
                'hasPDF': False,
                'pdfCheckedAt': datetime.now().isoformat(),
                'webCheckDetail': '首頁有 Events 連結但無具體價格',
                'recommendedAction': '聯絡酒店或查看 Events 頁面',
                'contactInfo': 'https://www.mandarinoriental.com/taipei 有聯絡資訊'
            })

            print(f'  ✅ 已標記為「需聯絡詢問」')

        print()

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print('=' * 80)
    print('✅ 已更新 venues.json')
    print('=' * 80)
    print()
    print('總結:')
    print('  - 台北世貿中心: 已檢查會議室頁面，無價格')
    print('  - 台北萬豪酒店: 可能需要 Playwright 處理 JavaScript')
    print('  - 台北文華東方: 官網無價格資訊')
    print()
    print('建議:')
    print('  1. 聯絡這三個場地詢問會議室租借價格')
    print('  2. 或使用 Playwright 深度爬取（特別是萬豪）')
    print('  3. 標記為「價格需詢問」以便日後跟進')
    print()


if __name__ == '__main__':
    main()
