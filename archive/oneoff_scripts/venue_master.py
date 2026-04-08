#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
場地主控系統 - Venue Master System
整合所有更新和檢驗功能的主控腳本
一鍵處理所有場地更新工作
"""

import json
import sys
import io
from datetime import datetime

# 設置 UTF-8 編碼輸出（僅在主腳本）
if hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

from unified_updater import VenueUpdater
from quality_checker import QualityChecker
from batch_processor import BatchProcessor


class VenueMaster:
    """場地主控系統"""

    def __init__(self):
        """初始化主控系統"""
        print('=' * 70)
        print('場地主控系統 - Venue Master System')
        print('=' * 70)
        print()

        self.updater = VenueUpdater('venues.json')
        self.checker = QualityChecker('venues.json', 'hotel_sources.json')
        self.processor = BatchProcessor('venues.json', 'hotel_sources.json')

        self.show_summary()

    def show_summary(self):
        """顯示系統摘要"""
        print('[當前狀態]')
        print('-' * 70)

        # 場地統計
        self.updater.print_summary()

        # 待處理場地
        pending = self.processor.get_pending_venues()
        print(f'待處理場地: {len(pending)} 個')
        print()

    def check_single_venue(self, venue_id):
        """檢查單一場地"""
        print(f'\n[檢查場地] ID: {venue_id}')
        print('-' * 70)

        result = self.checker.check_venue(venue_id)
        self.checker.print_report(result)

        return result

    def update_single_venue(self, venue_id, updates):
        """更新單一場地"""
        print(f'\n[更新場地] ID: {venue_id}')
        print('-' * 70)

        result = self.updater.update_venue(venue_id, updates)

        if result['success']:
            print(f"✓ 更新成功: {result['venue_name']}")
            print(f"  更新欄位: {', '.join(result['updated_fields'])}")
            print(f"  備份檔案: {result['backup_path']}")

            # 驗證更新結果
            check_result = self.checker.check_venue(venue_id)
            print(f"  品質分數: {check_result['score']}/100")
        else:
            print(f"✗ 更新失敗: {result['error']}")

        return result

    def process_batch_by_priority(self, priority='high', limit=5):
        """根據優先級批量處理"""
        print(f'\n[批量處理] 優先級: {priority}, 限制: {limit} 個')
        print('=' * 70)

        # 取得待處理場地
        pending = self.processor.get_pending_venues(priority=priority)
        if not pending:
            print(f"沒有 {priority} 優先級的待處理場地")
            return

        # 限制數量
        venues_to_process = pending[:limit]
        print(f"找到 {len(venues_to_process)} 個場地待處理:")
        for venue in venues_to_process:
            print(f"  - {venue['id']}: {venue['name']} ({venue['current_photos']} 張照片)")

        print(f"\n⚠️  注意: 這些場地尚未爬取官網資料")
        print(f"    請先使用 webReader 爬取官網，再進行更新")
        print(f"\n建議流程:")
        print(f"  1. 使用 webReader 爬取場地官網")
        print(f"  2. 整理照片和會議室資料")
        print(f"  3. 使用 update_single_venue() 更新")

    def show_quality_report(self, min_score=60):
        """顯示品質報告"""
        print(f'\n[品質報告] 分數 < {min_score} 的場地')
        print('=' * 70)

        poor_venues = self.checker.get_venues_by_quality(0, min_score)

        if not poor_venues:
            print(f"沒有分數 < {min_score} 的場地")
            return

        print(f"找到 {len(poor_venues)} 個場地:\n")

        for venue in poor_venues:
            print(f"{venue['id']:4d}: {venue['name']:40s} {venue['score']:5.1f}分 ({venue['status']})")

    def export_pending_list(self, filename='pending_venues.json'):
        """匯出待處理場地列表"""
        pending = self.processor.get_pending_venues()

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_count': len(pending),
            'venues': pending
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f'\n[匯出完成] 待處理場地列表: {filename}')
        print(f'  總數: {len(pending)} 個')


# ========== 使用範例 ==========

def main():
    """主函數"""
    master = VenueMaster()

    # 顯示選項
    print('\n[可用功能]')
    print('1. 檢查單一場地: master.check_single_venue(venue_id)')
    print('2. 更新單一場地: master.update_single_venue(venue_id, updates)')
    print('3. 批量處理: master.process_batch_by_priority(priority="high")')
    print('4. 品質報告: master.show_quality_report(min_score=60)')
    print('5. 匯出待處理列表: master.export_pending_list()')
    print()

    # 範例：顯示低品質場地
    print('[範例] 品質分數 < 60 的場地（前10個）:')
    print('-' * 70)
    poor_venues = master.checker.get_venues_by_quality(0, 60)
    for venue in poor_venues[:10]:
        print(f"{venue['id']:4d}: {venue['name']:40s} {venue['score']:5.1f}分")

    if len(poor_venues) > 10:
        print(f"... 還有 {len(poor_venues) - 10} 個場地")

    print()
    print('=' * 70)
    print('系統已就緒！使用 master 物件進行操作')
    print('=' * 70)


if __name__ == '__main__':
    main()
