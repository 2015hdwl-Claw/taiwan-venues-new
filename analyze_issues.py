#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析品質問題

快速分析有問題的場地並生成報告
"""

import json
from collections import defaultdict

# 讀取資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

print("正在分析品質問題...\n")

# 統計問題類型
issue_stats = {
    '重複場地': 0,
    '缺少必填欄位': 0,
    '維度格式錯誤': 0,
    '容量不一致': 0,
    '照片問題': 0,
    'URL問題': 0,
    '價格異常': 0,
    '容量異常': 0
}

# 詳細問題清單
failed_venues = []

# 檢查每個場地
for venue in venues:
    issues = []

    # 1. 檢查必填欄位
    required = ['id', 'name', 'venueType', 'city', 'address', 'contactPhone', 'url']
    missing = [f for f in required if not venue.get(f)]
    if missing:
        issues.append(f"缺少欄位: {', '.join(missing)}")
        issue_stats['缺少必填欄位'] += 1

    # 2. 檢查 URL 格式
    url = venue.get('url', '')
    if url and not url.startswith(('http://', 'https://')):
        issues.append("URL 格式錯誤")
        issue_stats['URL問題'] += 1

    # 3. 檢查會議室資料
    rooms = venue.get('rooms', [])
    if rooms:
        for room in rooms:
            # 檢查維度
            if 'sqm' in room and room['sqm'] is not None:
                if not isinstance(room['sqm'], (int, float)):
                    issues.append(f"{room.get('name', 'Unknown')}: sqm 非數字")
                    issue_stats['維度格式錯誤'] += 1
                elif room['sqm'] < 0 or room['sqm'] > 10000:
                    issues.append(f"{room.get('name', 'Unknown')}: sqm 數值異常")
                    issue_stats['維度格式錯誤'] += 1

            # 檢查容量一致性
            capacity = room.get('capacity', {})
            if capacity and isinstance(capacity, dict):
                theater = capacity.get('theater') or 0
                banquet = capacity.get('banquet') or 0
                classroom = capacity.get('classroom') or 0

                if theater > 0 and banquet > 0 and theater < banquet:
                    issues.append(f"{room.get('name', 'Unknown')}: theater < banquet")
                    issue_stats['容量不一致'] += 1

                if banquet > 0 and classroom > 0 and banquet < classroom:
                    issues.append(f"{room.get('name', 'Unknown')}: banquet < classroom")
                    issue_stats['容量不一致'] += 1

            # 檢查照片
            images = room.get('images', [])
            if isinstance(images, list) and len(images) == 0:
                # 沒有照片
                pass
            elif isinstance(images, dict):
                main = images.get('main')
                if main and not main.startswith(('http://', 'https://')):
                    issues.append(f"{room.get('name', 'Unknown')}: 照片 URL 格式錯誤")
                    issue_stats['照片問題'] += 1

    # 4. 檢查價格
    half_day = venue.get('priceHalfDay')
    full_day = venue.get('priceFullDay')

    if half_day is not None:
        if not isinstance(half_day, (int, float)) or half_day < 0:
            issues.append("半日價格異常")
            issue_stats['價格異常'] += 1

    if full_day is not None:
        if not isinstance(full_day, (int, float)) or full_day < 0:
            issues.append("全日價格異常")
            issue_stats['價格異常'] += 1

    # 如果有問題，加入清單
    if issues:
        failed_venues.append({
            'id': venue.get('id'),
            'name': venue.get('name'),
            'issues': issues,
            'issueCount': len(issues)
        })

# 檢查重複
name_counts = defaultdict(list)
for venue in venues:
    name = venue.get('name', '')
    if name:
        name_counts[name].append(venue['id'])

duplicates = {name: ids for name, ids in name_counts.items() if len(ids) > 1}
issue_stats['重複場地'] = len(duplicates)

# 統計
total = len(venues)
failed = len(failed_venues)
passed = total - failed

# 輸出報告
print("="*70)
print("品質問題分析報告")
print("="*70)
print(f"\n總場地數: {total}")
print(f"通過檢查: {passed} ({passed/total*100:.1f}%)")
print(f"有問題: {failed} ({failed/total*100:.1f}%)")
print(f"重複場地名稱: {len(duplicates)}")

print(f"\n{'='*70}")
print("問題類型統計")
print(f"{'='*70}")

for issue, count in sorted(issue_stats.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"{issue}: {count}")

print(f"\n{'='*70}")
print("有問題的場地（前 20 個）")
print(f"{'='*70}")

# 按問題數量排序
failed_venues.sort(key=lambda x: x['issueCount'], reverse=True)

for i, venue in enumerate(failed_venues[:20], 1):
    print(f"\n{i}. {venue['name']} (ID: {venue['id']})")
    print(f"   問題數: {venue['issueCount']}")
    for issue in venue['issues'][:5]:  # 只顯示前 5 個問題
        print(f"   - {issue}")
    if len(venue['issues']) > 5:
        print(f"   ... 還有 {len(venue['issues']) - 5} 個問題")

print(f"\n{'='*70}")
print("重複場地清單")
print(f"{'='*70}")

for name, ids in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n{name}")
    print(f"  重複 {len(ids)} 次: {', '.join(map(str, ids[:5]))}")
    if len(ids) > 5:
        print(f"  ... 還有 {len(ids) - 5} 個")

# 保存報告
report = {
    'summary': {
        'total': total,
        'passed': passed,
        'failed': failed,
        'duplicates': len(duplicates)
    },
    'issueStats': issue_stats,
    'failedVenues': failed_venues,
    'duplicates': {name: ids for name, ids in duplicates.items()}
}

with open('quality_issues_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n{'='*70}")
print(f"詳細報告已保存: quality_issues_report.json")
print(f"{'='*70}")
