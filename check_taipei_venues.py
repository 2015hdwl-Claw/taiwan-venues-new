#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查台北市場地資料完整性"""

import json
from datetime import datetime

def check_venue_completeness(venue):
    """檢查單一場地的資料完整性"""
    issues = []
    
    # 基本資訊檢查
    if not venue.get('name'):
        issues.append("❌ 缺少場地名稱")
    if not venue.get('address'):
        issues.append("❌ 缺少地址")
    if not venue.get('contactPhone'):
        issues.append("❌ 缺少聯絡電話")
    if not venue.get('url'):
        issues.append("❌ 缺少官網 URL")
    
    # 照片檢查
    images = venue.get('images', {})
    if not images.get('main'):
        issues.append("❌ 缺少場地主照片")
    elif 'unsplash.com' in images.get('main', ''):
        issues.append("⚠️ 使用 Unsplash 佔位圖")
    
    # 會議室檢查
    rooms = venue.get('rooms', [])
    if not rooms:
        issues.append("⚠️ 缺少會議室資訊（rooms）")
    else:
        for i, room in enumerate(rooms):
            if not room.get('id'):
                issues.append(f"⚠️ 會議室 {i+1} 缺少 ID")
            if not room.get('images', {}).get('main'):
                issues.append(f"⚠️ 會議室 {room.get('name', i+1)} 缺少照片")
    
    # 價格檢查
    if not venue.get('priceHalfDay') and not venue.get('priceFullDay'):
        issues.append("⚠️ 缺少價格資訊")
    
    # 容納人數檢查
    if not venue.get('maxCapacityTheater') and not venue.get('maxCapacityClassroom'):
        issues.append("⚠️ 缺少容納人數資訊")
    
    return issues

def main():
    # 讀取資料
    with open('/root/.openclaw/workspace/taiwan-venues-new/venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)
    
    # 篩選台北市場地
    taipei_venues = [v for v in venues if v.get('city') == '台北市']
    
    print("=" * 80)
    print(f"台北市場地檢查報告")
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"\n總計台北市場地數量: {len(taipei_venues)}")
    
    # 分類場地
    large_venues = []  # 容納人數 > 200
    medium_venues = []  # 容納人數 100-200
    small_venues = []  # 容納人數 < 100
    needs_update = []  # 需要更新的場地
    
    # 分析每個場地
    for venue in taipei_venues:
        capacity = venue.get('maxCapacityTheater', 0) or venue.get('maxCapacityClassroom', 0) or 0
        issues = check_venue_completeness(venue)
        
        venue_info = {
            'id': venue.get('id'),
            'name': venue.get('name'),
            'capacity': capacity,
            'issues': issues,
            'verified': venue.get('verified', False),
            'url': venue.get('url')
        }
        
        if issues:
            needs_update.append(venue_info)
        
        if capacity > 200:
            large_venues.append(venue_info)
        elif capacity >= 100:
            medium_venues.append(venue_info)
        else:
            small_venues.append(venue_info)
    
    # 輸出報告
    print("\n" + "=" * 80)
    print("📊 依照容納人數分類:")
    print("=" * 80)
    print(f"  大型場地（>200人）: {len(large_venues)} 個")
    print(f"  中型場地（100-200人）: {len(medium_venues)} 個")
    print(f"  小型場地（<100人）: {len(small_venues)} 個")
    
    # 優先處理：大型場地且需要更新
    print("\n" + "=" * 80)
    print("🔴 優先處理：大型場地（>200人）需要更新:")
    print("=" * 80)
    
    large_needs_update = [v for v in large_venues if v['issues']]
    if large_needs_update:
        for i, v in enumerate(large_needs_update, 1):
            print(f"\n{i}. {v['name']} (ID: {v['id']})")
            print(f"   容納人數: {v['capacity']}人")
            print(f"   官網: {v['url']}")
            print(f"   問題:")
            for issue in v['issues']:
                print(f"     {issue}")
    else:
        print("  ✅ 所有大型場地資料完整！")
    
    # 其他需要更新的場地
    print("\n" + "=" * 80)
    print("🟡 其他需要更新的場地:")
    print("=" * 80)
    
    other_needs_update = [v for v in needs_update if v not in large_needs_update]
    if other_needs_update:
        for i, v in enumerate(other_needs_update, 1):
            print(f"\n{i}. {v['name']} (ID: {v['id']})")
            print(f"   容納人數: {v['capacity']}人")
            print(f"   官網: {v['url']}")
            print(f"   問題:")
            for issue in v['issues']:
                print(f"     {issue}")
    else:
        print("  ✅ 所有場地資料完整！")
    
    # 統計總結
    print("\n" + "=" * 80)
    print("📈 統計總結:")
    print("=" * 80)
    print(f"  需要更新的場地: {len(needs_update)} / {len(taipei_venues)}")
    print(f"  資料完整率: {((len(taipei_venues) - len(needs_update)) / len(taipei_venues) * 100):.1f}%")
    print(f"  其中大型場地需更新: {len(large_needs_update)} 個")
    
    # 輸出更新清單（JSON 格式）
    update_list = {
        'timestamp': datetime.now().isoformat(),
        'total_venues': len(taipei_venues),
        'needs_update_count': len(needs_update),
        'large_venues_count': len(large_venues),
        'large_needs_update': large_needs_update,
        'other_needs_update': other_needs_update
    }
    
    with open('/root/.openclaw/workspace/taiwan-venues-new/update_list.json', 'w', encoding='utf-8') as f:
        json.dump(update_list, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 更新清單已儲存至: update_list.json")

if __name__ == '__main__':
    main()
