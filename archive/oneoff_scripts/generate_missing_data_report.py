#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北市場地資料完整性檢測報告

依據新的三階段流程檢測所有台北市場地
找出缺失的欄位與資料
"""

import sys
import io
import json
from datetime import datetime
from collections import defaultdict

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 篩選台北市場地
    taipei_venues = [
        v for v in venues
        if v.get('city') == '台北市' and v.get('status') != 'discontinued'
    ]

    print('=' * 80)
    print('台北市場地資料完整性檢測報告')
    print('=' * 80)
    print(f'檢測時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'場地總數: {len(taipei_venues)}')
    print()

    # 統計變數
    stats = {
        'phone': 0,
        'email': 0,
        'address': 0,
        'capacity': 0,
        'area': 0,
        'price': 0,
        'equipment': 0,
        'traffic': 0,
        'pdf': 0
    }

    total_rooms = 0
    rooms_with_capacity = 0
    rooms_with_area = 0
    rooms_with_price = 0

    # 詳細缺失記錄
    by_category = defaultdict(list)

    for venue in taipei_venues:
        vid = venue.get('id')
        name = venue.get('name', 'Unknown')
        url = venue.get('url', 'N/A')
        rooms = venue.get('rooms', [])

        # 檢查基本欄位
        contact = venue.get('contact', {})
        has_phone = bool(contact.get('phone'))
        has_email = bool(contact.get('email'))
        has_address = bool(venue.get('address'))

        if has_phone:
            stats['phone'] += 1
        if has_email:
            stats['email'] += 1
        if has_address:
            stats['address'] += 1

        # 檢查會議室欄位
        rooms_cap = sum(1 for r in rooms if r.get('capacity'))
        rooms_area = sum(1 for r in rooms if r.get('area'))
        rooms_price = sum(1 for r in rooms if r.get('price'))
        rooms_equipment = sum(1 for r in rooms if r.get('equipment'))

        total_rooms += len(rooms)
        rooms_with_capacity += rooms_cap
        rooms_with_area += rooms_area
        rooms_with_price += rooms_price

        if rooms_cap > 0:
            stats['capacity'] += 1
        if rooms_area > 0:
            stats['area'] += 1
        if rooms_price > 0:
            stats['price'] += 1
        if rooms_equipment > 0:
            stats['equipment'] += 1

        # 檢查交通資訊
        traffic = venue.get('traffic')
        has_traffic = False
        if traffic:
            if isinstance(traffic, dict):
                has_traffic = any(traffic.values())
            elif isinstance(traffic, str):
                has_traffic = len(traffic) > 10

        if has_traffic:
            stats['traffic'] += 1

        # 檢查 PDF
        metadata = venue.get('metadata', {})
        has_pdf = bool(metadata.get('pdfUrls'))
        if has_pdf:
            stats['pdf'] += 1

        # 記錄缺失（只記錄有問題的場地）
        missing_critical = []
        missing_important = []
        missing_optional = []

        # 關鍵欄位（聯絡資訊）
        if not has_phone:
            missing_critical.append('電話')
        if not has_email:
            missing_critical.append('Email')
        if not has_address:
            missing_critical.append('地址')

        # 重要欄位（會議室資料）
        if len(rooms) > 0:
            if rooms_cap == 0:
                missing_important.append(f'容量 (0/{len(rooms)})')
            if rooms_area == 0:
                missing_important.append(f'面積 (0/{len(rooms)})')
            if rooms_price == 0:
                missing_important.append(f'價格 (0/{len(rooms)})')

        # 次要欄位
        if not has_traffic:
            missing_optional.append('交通資訊')
        if not has_pdf:
            missing_optional.append('PDF URL')

        # 分類記錄
        all_missing = missing_critical + missing_important + missing_optional

        if all_missing:
            category = 'critical' if missing_critical else ('important' if missing_important else 'optional')
            by_category[category].append({
                'id': vid,
                'name': name,
                'url': url,
                'rooms': len(rooms),
                'capacity_coverage': f'{rooms_cap}/{len(rooms)}' if len(rooms) > 0 else 'N/A',
                'area_coverage': f'{rooms_area}/{len(rooms)}' if len(rooms) > 0 else 'N/A',
                'price_coverage': f'{rooms_price}/{len(rooms)}' if len(rooms) > 0 else 'N/A',
                'missing_critical': missing_critical,
                'missing_important': missing_important,
                'missing_optional': missing_optional
            })

    # 輸出統計報告
    print('=' * 80)
    print('📊 整體覆蓋率統計')
    print('=' * 80)
    print()

    print('【基本資訊】')
    print(f'  電話:   {stats["phone"]:2}/{len(taipei_venues)} ({stats["phone"]/len(taipei_venues)*100:5.1f}%) {"✅" if stats["phone"] == len(taipei_venues) else "❌"}')
    print(f'  Email:  {stats["email"]:2}/{len(taipei_venues)} ({stats["email"]/len(taipei_venues)*100:5.1f}%) {"✅" if stats["email"] == len(taipei_venues) else "❌"}')
    print(f'  地址:   {stats["address"]:2}/{len(taipei_venues)} ({stats["address"]/len(taipei_venues)*100:5.1f}%) {"✅" if stats["address"] == len(taipei_venues) else "❌"}')
    print()

    print('【會議室資料 - 場地層級】')
    print(f'  有容量資料: {stats["capacity"]:2}/{len(taipei_venues)} ({stats["capacity"]/len(taipei_venues)*100:5.1f}%)')
    print(f'  有面積資料: {stats["area"]:2}/{len(taipei_venues)} ({stats["area"]/len(taipei_venues)*100:5.1f}%)')
    print(f'  有價格資料: {stats["price"]:2}/{len(taipei_venues)} ({stats["price"]/len(taipei_venues)*100:5.1f}%)')
    print(f'  有設備資料: {stats["equipment"]:2}/{len(taipei_venues)} ({stats["equipment"]/len(taipei_venues)*100:5.1f}%)')
    print()

    print('【會議室資料 - 會議室層級】')
    if total_rooms > 0:
        print(f'  總會議室數: {total_rooms}')
        print(f'  有容量: {rooms_with_capacity:3}/{total_rooms} ({rooms_with_capacity/total_rooms*100:5.1f}%)')
        print(f'  有面積: {rooms_with_area:3}/{total_rooms} ({rooms_with_area/total_rooms*100:5.1f}%)')
        print(f'  有價格: {rooms_with_price:3}/{total_rooms} ({rooms_with_price/total_rooms*100:5.1f}%)')
    print()

    print('【其他資訊】')
    print(f'  有交通資訊: {stats["traffic"]:2}/{len(taipei_venues)}')
    print(f'  有 PDF URL: {stats["pdf"]:2}/{len(taipei_venues)}')
    print()

    # 輸出缺失場地明細
    print('=' * 80)
    print('🔍 缺失資料場地明細')
    print('=' * 80)
    print()

    if by_category['critical']:
        print('【🚨 關鍵欄位缺失 - 聯絡資訊】')
        print()
        for item in sorted(by_category['critical'], key=lambda x: x['id']):
            print(f"  [{item['id']}] {item['name'][:50]}")
            print(f"    URL: {item['url']}")
            print(f"    缺失關鍵: {', '.join(item['missing_critical'])}")
            if item['missing_important']:
                print(f"    缺失重要: {', '.join(item['missing_important'])}")
            print()

    if by_category['important']:
        print('【⚠️  重要欄位缺失 - 會議室資料】')
        print()
        for item in sorted(by_category['important'], key=lambda x: x['id']):
            print(f"  [{item['id']}] {item['name'][:50]}")
            print(f"    會議室數: {item['rooms']}")
            print(f"    容量覆蓋: {item['capacity_coverage']}")
            print(f"    面積覆蓋: {item['area_coverage']}")
            print(f"    價格覆蓋: {item['price_coverage']}")
            print(f"    缺失重要: {', '.join(item['missing_important'])}")
            if item['missing_optional']:
                print(f"    缺失信次: {', '.join(item['missing_optional'])}")
            print()

    if by_category['optional']:
        print('【ℹ️  次要欄位缺失 - 交通與 PDF】')
        print()
        for item in sorted(by_category['optional'], key=lambda x: x['id']):
            print(f"  [{item['id']}] {item['name'][:50]}")
            print(f"    缺失信次: {', '.join(item['missing_optional'])}")
            print()

    # 總結建議
    print('=' * 80)
    print('🎯 總結與建議')
    print('=' * 80)
    print()

    critical_count = len(by_category['critical'])
    important_count = len(by_category['important'])
    optional_count = len(by_category['optional'])

    print(f'關鍵問題場地: {critical_count} 個')
    print(f'重要問題場地: {important_count} 個')
    print(f'次要問題場地: {optional_count} 個')
    print()

    if critical_count > 0:
        print('⚠️  優先處理:')
        print('   1. 手動確認並補充聯絡資訊')
        print('   2. 檢查 URL 是否正確')
        print()

    if important_count > 0:
        print('⭐ 主要任務:')
        print('   1. 實作三級爬取（主頁→會議頁→詳情頁）')
        print('   2. 處理 PDF 價格表')
        print(f'   3. 預期改善: 容量 {stats["capacity"]}/{len(taipei_venues)} → 60-70%')
        print()

    if optional_count > 0:
        print('📝 次要任務:')
        print('   1. 補充交通資訊')
        print('   2. 發現並記錄 PDF URL')
        print()

    # 優先處理清單
    if important_count > 0:
        print('=' * 80)
        print('📋 優先處理清單（前 10 個最多會議室的場地）')
        print('=' * 80)
        print()

        top_venues = sorted(
            [v for v in by_category['important']],
            key=lambda x: x['rooms'],
            reverse=True
        )[:10]

        for i, item in enumerate(top_venues, 1):
            print(f"{i}. [{item['id']}] {item['name'][:40]}")
            print(f"   會議室: {item['rooms']} 個 | 缺失: {', '.join(item['missing_important'][:2])}")
            print()

if __name__ == '__main__':
    main()
