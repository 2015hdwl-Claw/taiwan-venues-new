#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 1: 照片品質檢查和場地篩選
自動化執行 MVP 執行計畫的 Day 1 任務
"""

import json
import sys
from urllib.parse import urlparse
from typing import List, Dict, Tuple

def load_venues(filepath: str) -> List[Dict]:
    """載入 venues.json"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_url_quality(url: str) -> Tuple[bool, List[str]]:
    """
    檢查照片 URL 品質
    Returns: (is_good, issues)
    """
    issues = []

    if not url:
        return False, ["Empty URL"]

    url_lower = url.lower()

    # 檢查禁止的關鍵字
    forbidden = ['placeholder', 'default', 'wiki', 'wikipedia',
                 'external', 'generic', 'sample']
    for keyword in forbidden:
        if keyword in url_lower:
            issues.append(f"Contains forbidden keyword: {keyword}")

    # 檢查是否是 Wiki 或外部圖片
    parsed = urlparse(url)
    if 'wikipedia.org' in parsed.netloc or 'wikimedia.org' in parsed.netloc:
        issues.append("Wiki domain")

    return len(issues) == 0, issues

def check_venue_photos(venue: Dict) -> Tuple[bool, List[str]]:
    """
    檢查單一場地的照片品質
    Returns: (is_good, issues)
    """
    issues = []

    # 檢查城市
    if venue.get('city') != '台北市':
        issues.append(f"Not in Taipei: {venue.get('city')}")
        return False, issues

    # 檢查 main photo
    images = venue.get('images', {})
    if not images or not isinstance(images, dict):
        issues.append("No images field")
        return False, issues

    main_photo = images.get('main', '')

    if not main_photo:
        issues.append("No main photo")
        return False, issues

    is_main_good, main_issues = check_url_quality(main_photo)
    if not is_main_good:
        issues.extend([f"Main photo: {issue}" for issue in main_issues])

    # 檢查 gallery photos
    gallery = images.get('gallery', [])
    if len(gallery) < 3:
        issues.append(f"Only {len(gallery)} gallery photos (need >= 3)")
        return False, issues

    # 檢查前 3 張 gallery photos
    for i, photo_url in enumerate(gallery[:3]):
        is_good, photo_issues = check_url_quality(photo_url)
        if not is_good:
            issues.extend([f"Gallery[{i}]: {issue}" for issue in photo_issues])

    return len(issues) == 0, issues

def filter_venues(venues: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    篩選符合標準的場地
    Returns: (filtered_venues, report)
    """
    filtered = []
    rejected = []
    report = {
        'total': len(venues),
        'filtered': 0,
        'rejected': 0,
        'reject_reasons': {}
    }

    for venue in venues:
        is_good, issues = check_venue_photos(venue)

        if is_good:
            filtered.append(venue)
            report['filtered'] += 1
        else:
            rejected.append({
                'id': venue.get('id'),
                'name': venue.get('name'),
                'issues': issues
            })
            report['rejected'] += 1

            # 統計拒絕原因
            for issue in issues:
                reason = issue.split(':')[0]
                report['reject_reasons'][reason] = \
                    report['reject_reasons'].get(reason, 0) + 1

    return filtered, report

def save_results(filtered_venues: List[Dict], report: Dict):
    """儲存結果"""
    # 儲存過濾後的場地
    with open('mvp_venues_day1.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_venues, f, ensure_ascii=False, indent=2)

    # 儲存報告
    with open('day1_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

def main():
    print("Day 1: Photo Quality Check and Venue Filtering")
    print("=" * 50)

    # 1. 載入 venues.json
    try:
        venues = load_venues('venues.json')
        print(f"Loaded {len(venues)} venues")
    except FileNotFoundError:
        print("ERROR: venues.json not found")
        sys.exit(1)

    # 2. 篩選場地
    print("\nFiltering criteria:")
    print("  - City: Taipei")
    print("  - Main photo: Must exist and good quality")
    print("  - Gallery photos: At least 3 with good quality")
    print("  - URL: Cannot contain placeholder, wiki, etc.")

    filtered, report = filter_venues(venues)

    # 3. 顯示結果
    print(f"\nFiltering results:")
    print(f"  Total venues: {report['total']}")
    print(f"  Passed: {report['filtered']}")
    print(f"  Rejected: {report['rejected']}")

    if report['reject_reasons']:
        print(f"\nRejection reasons:")
        for reason, count in sorted(report['reject_reasons'].items(),
                                     key=lambda x: x[1], reverse=True):
            print(f"  - {reason}: {count}")

    # 4. 儲存結果
    save_results(filtered, report)
    print(f"\nResults saved:")
    print(f"  - mvp_venues_day1.json ({len(filtered)} venues)")
    print(f"  - day1_report.json")

    # 5. Go/No Go 決策
    print(f"\nGo/No Go decision:")
    if len(filtered) >= 10:
        print(f"  GO! {len(filtered)} venues meet criteria")
        print(f"  Next: Day 2 - Photo Standardization")
        return 0
    elif len(filtered) >= 5:
        print(f"  CAUTION: Only {len(filtered)} venues")
        print(f"  Suggestion: Expand to New Taipei City or manually add photos")
        return 0
    else:
        print(f"  NO GO: Only {len(filtered)} venues")
        print(f"  Required: Expand to all Taiwan or manually add photos")
        return 1

if __name__ == '__main__':
    sys.exit(main())
