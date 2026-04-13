#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/audit_data_sources.py - 嚴格稽核所有場地價格資料來源

目的：
1. 審查每個場地的價格資料來源是否正確標記
2. 識別 compiled.js 等舊來源
3. 對比 venue-level metadata 和 room-level source 的一致性
4. 產出完整稽核報告

Usage:
    python tools/audit_data_sources.py              # 稽核全部場地
    python tools/audit_data_sources.py --venue 1501 # 稽核特定場地
    python tools/audit_data_sources.py --fix        # 自動修復來源標記

資料來源分類：
- official_pdf: 官方 PDF 價格表（最可信）
- official_website: 官方網站爬取（可信）
- compiled.js: 舊版 compiled.js（需要驗證）
- regex: 正則表達式解析（需要驗證）
- estimated: 估計價格（需要標註）
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, 'tools')
from constants import VENUES_FILE

# 高可信來源模式
HIGH_TRUST_PATTERNS = [
    r'tainex_official_pdf',
    r'official_pdf',
    r'官方\s*PDF',
    r'官網PDF',
    r'website_202[0-9]',
    r'官網會議.*?PDF',
    r'官網',
    r'\.pdf',
    r'\.pdf_202[0-9]',
]

# 低可信來源模式
LOW_TRUST_PATTERNS = [
    r'compiled\.js',
    r'regex',
    r'room_data_js_variable',
    r'html_card',
    r'_manual_',
]


def classify_source(source_str):
    """分類資料來源，返回 (source_type, is_high_trust, confidence)"""
    if not source_str or not isinstance(source_str, str):
        return 'unknown', False, 0

    source_lower = source_str.lower()

    # 檢查高可信來源
    for pattern in HIGH_TRUST_PATTERNS:
        if re.search(pattern, source_str, re.IGNORECASE):
            # 根據匹配模式判斷來源類型
            if 'tainex' in source_lower:
                return 'tainex_official_pdf', True, 100
            elif '官方' in source_str or '官網PDF' in source_str:
                return 'official_pdf', True, 95
            elif 'pdf' in source_lower:
                return 'pdf', True, 90
            elif 'website' in source_lower or '官網' in source_str:
                return 'website', True, 85
            return 'official', True, 80

    # 檢查低可信來源
    for pattern in LOW_TRUST_PATTERNS:
        if re.search(pattern, source_str, re.IGNORECASE):
            if 'compiled.js' in source_str:
                return 'compiled.js', False, 10
            elif 'regex' in source_str:
                return 'regex', False, 20
            return 'low_trust', False, 30

    return 'other', False, 50


def load_venues():
    """載入 venues.json"""
    with open(VENUES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def audit_venue(venue):
    """稽核單一場地的資料來源"""
    venue_id = venue.get('id', 'unknown')
    venue_name = venue.get('name', 'unknown')

    report = {
        'venue_id': venue_id,
        'venue_name': venue_name,
        'url': venue.get('url', ''),
        'venue_source': None,
        'venue_source_type': None,
        'rooms': [],
        'issues': [],
        'stats': {
            'total_rooms': 0,
            'rooms_with_pricing': 0,
            'high_trust_rooms': 0,
            'low_trust_rooms': 0,
            'no_source_rooms': 0,
            'source_mismatch': False,
        }
    }

    # 取得 venue-level metadata source
    metadata = venue.get('metadata', {})
    report['venue_source'] = metadata.get('source', '')
    report['venue_source_type'], _, _ = classify_source(report['venue_source'])

    # 稽核各會議室
    for room in venue.get('rooms', []):
        room_report = audit_room(room, venue_id, venue_name)
        report['rooms'].append(room_report)
        report['stats']['total_rooms'] += 1

        if room_report['has_pricing']:
            report['stats']['rooms_with_pricing'] += 1

        if room_report['is_high_trust']:
            report['stats']['high_trust_rooms'] += 1
        else:
            report['stats']['low_trust_rooms'] += 1

        if not room_report['source']:
            report['stats']['no_source_rooms'] += 1

        # 檢查 venue/room source 一致性
        if report['venue_source_type'] in ['tainex_official_pdf', 'official_pdf']:
            if not room_report['is_high_trust'] and room_report['has_pricing']:
                report['issues'].append({
                    'type': 'room_source_mismatch',
                    'room_id': room.get('id'),
                    'message': f'會議室 {room.get("name")} 來源為 {room_report["source"]}，與場地來源不一致'
                })
                report['stats']['source_mismatch'] = True

    return report


def audit_room(room, venue_id, venue_name):
    """稽核單一會議室的資料來源"""
    room_id = room.get('id', 'unknown')
    room_name = room.get('name', 'unknown')

    report = {
        'room_id': room_id,
        'room_name': room_name,
        'source': room.get('source', ''),
        'source_type': 'unknown',
        'is_high_trust': False,
        'confidence': 0,
        'has_pricing': False,
        'pricing_half': None,
        'pricing_full': None,
        'issues': []
    }

    # 分類來源
    source = room.get('source', '')
    report['source_type'], report['is_high_trust'], report['confidence'] = classify_source(source)

    # 檢查價格
    pricing = room.get('pricing', {})
    if isinstance(pricing, dict):
        report['pricing_half'] = pricing.get('halfDay')
        report['pricing_full'] = pricing.get('fullDay')
        report['has_pricing'] = bool(report['pricing_half'] or report['pricing_full'])

    # 識別問題
    if report['has_pricing'] and not source:
        report['issues'].append('有價格但無來源標記')

    if report['has_pricing'] and not report['is_high_trust']:
        report['issues'].append(f'價格來源可信度低：{report["source_type"]} (信心度: {report["confidence"]}%)')

    return report


def print_report(audits, verbose=False):
    """列印稽核報告"""
    total_venues = len(audits)
    total_rooms = sum(r['stats']['total_rooms'] for r in audits)
    rooms_with_pricing = sum(r['stats']['rooms_with_pricing'] for r in audits)
    high_trust_rooms = sum(r['stats']['high_trust_rooms'] for r in audits)
    low_trust_rooms = sum(r['stats']['low_trust_rooms'] for r in audits)
    venues_with_issues = sum(1 for r in audits if r['issues'])

    print("=" * 80)
    print("場地價格資料來源稽核報告")
    print("=" * 80)
    print(f"\n總計:")
    print(f"  場地數量: {total_venues}")
    print(f"  會議室總數: {total_rooms}")
    print(f"  有價格會議室: {rooms_with_pricing}")
    if rooms_with_pricing > 0:
        print(f"  高可信來源會議室: {high_trust_rooms} ({high_trust_rooms/rooms_with_pricing*100:.1f}%)")
        print(f"  低可信來源會議室: {low_trust_rooms} ({low_trust_rooms/rooms_with_pricing*100:.1f}%)")
    print(f"  有問題場地: {venues_with_issues}")

    # 來源分佈
    source_dist = defaultdict(int)
    for audit in audits:
        for room in audit['rooms']:
            if room['source_type']:
                source_dist[room['source_type']] += 1

    print(f"\n來源分佈 (按類型):")
    for source_type, count in sorted(source_dist.items(), key=lambda x: -x[1]):
        print(f"  {source_type}: {count}")

    # 詳細問題場地
    if verbose:
        print(f"\n詳細問題場地:")
        for audit in audits:
            if audit['issues']:
                print(f"\n  [{audit['venue_id']}] {audit['venue_name']}")
                print(f"    URL: {audit['url']}")
                print(f"    場地來源: {audit['venue_source']}")
                for issue in audit['issues']:
                    print(f"    ⚠️  {issue['message']}")


def print_venue_detail(audit):
    """列印單一場地詳細報告"""
    print("=" * 80)
    print(f"場地詳細報告: [{audit['venue_id']}] {audit['venue_name']}")
    print("=" * 80)
    print(f"URL: {audit['url']}")
    print(f"場地來源: {audit['venue_source']}")
    print(f"來源類型: {audit['venue_source_type']}")

    print(f"\n統計:")
    print(f"  會議室總數: {audit['stats']['total_rooms']}")
    print(f"  有價格: {audit['stats']['rooms_with_pricing']}")
    print(f"  高可信來源: {audit['stats']['high_trust_rooms']}")
    print(f"  低可信來源: {audit['stats']['low_trust_rooms']}")

    if audit['issues']:
        print(f"\n問題:")
        for issue in audit['issues']:
            print(f"  ⚠️  {issue['message']}")

    print(f"\n會議室明細:")
    for room in audit['rooms']:
        if room['has_pricing']:
            source_mark = "✓" if room['is_high_trust'] else "⚠️"
            price_info = f"${room['pricing_half'] or 'N/A'}/${room['pricing_full'] or 'N/A'}"
            print(f"  {source_mark} [{room['room_id']}] {room['room_name']}")
            print(f"      價格: {price_info}")
            print(f"      來源: {room['source']}")
            if room['issues']:
                for issue in room['issues']:
                    print(f"      ⚠️  {issue}")


def fix_sources(venues, audits, dry_run=False):
    """修復來源標記

    Rules:
    1. 如果場地來源是官方 PDF，將所有會議室來源改為對應的官方 PDF
    2. 保留原本的高可信來源
    3. 只修復低可信來源
    """
    fixed_count = 0
    fixed_rooms = []

    for audit in audits:
        venue = next((v for v in venues if v.get('id') == audit['venue_id']), None)
        if not venue:
            continue

        venue_source = audit['venue_source']
        metadata = venue.get('metadata', {})

        # 如果場地來源是官方 PDF
        if re.search(r'tainex_official_pdf|official_pdf|官方\s*PDF', venue_source, re.IGNORECASE):
            for room in venue.get('rooms', []):
                current_source = room.get('source', '')
                room_id = room.get('id')
                room_name = room.get('name')

                # 只修復低可信來源
                should_fix = (
                    not current_source or
                    re.search(r'compiled\.js|regex', current_source, re.IGNORECASE)
                )

                # 保留已經是高可信的來源
                if current_source:
                    _, is_high, _ = classify_source(current_source)
                    if is_high:
                        should_fix = False

                if should_fix:
                    new_source = f"tainex_official_pdf_2026"

                    if not dry_run:
                        room['source'] = new_source

                    fixed_count += 1
                    fixed_rooms.append({
                        'venue_id': audit['venue_id'],
                        'venue_name': audit['venue_name'],
                        'room_id': room_id,
                        'room_name': room_name,
                        'old_source': current_source,
                        'new_source': new_source
                    })

    return fixed_count, fixed_rooms


def main():
    parser = argparse.ArgumentParser(description='稽核場地價格資料來源')
    parser.add_argument('--venue', type=int, help='稽核特定場地 ID')
    parser.add_argument('--fix', action='store_true', help='自動修復來源標記')
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細輸出')
    args = parser.parse_args()

    venues = load_venues()

    if args.venue:
        target_venues = [v for v in venues if v.get('id') == args.venue]
        if not target_venues:
            print(f"錯誤: 找不到場地 ID {args.venue}")
            return 1
    else:
        target_venues = venues

    audits = [audit_venue(v) for v in target_venues]

    if args.venue:
        print_venue_detail(audits[0])
    else:
        print_report(audits, verbose=args.verbose)

    if args.fix:
        fixed_count, fixed_rooms = fix_sources(venues, audits)
        print(f"\n修復了 {fixed_count} 個會議室的來源標記")

        if fixed_rooms:
            print(f"\n修復明細 (前10個):")
            for i, fix in enumerate(fixed_rooms[:10]):
                print(f"  [{fix['venue_id']}] {fix['room_name']}")
                print(f"      舊: {fix['old_source']}")
                print(f"      新: {fix['new_source']}")
            if len(fixed_rooms) > 10:
                print(f"  ... 還有 {len(fixed_rooms) - 10} 個會議室")

        with open(VENUES_FILE, 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)
        print(f"\n已儲存到 {VENUES_FILE}")

        # 重新稽核確認修復結果
        print(f"\n重新稽核中...")
        new_audits = [audit_venue(v) for v in venues if any(a['venue_id'] == v.get('id') for a in audits)]
        new_high_trust = sum(r['stats']['high_trust_rooms'] for r in new_audits)
        new_rooms_with_pricing = sum(r['stats']['rooms_with_pricing'] for r in new_audits)
        if new_rooms_with_pricing > 0:
            print(f"修復後高可信來源: {new_high_trust}/{new_rooms_with_pricing} ({new_high_trust/new_rooms_with_pricing*100:.1f}%)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
