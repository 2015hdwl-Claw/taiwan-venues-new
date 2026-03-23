#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量處理管道 - Batch Processing Pipeline
整合統一更新引擎和品質檢驗系統
實現高效批量處理多個場地
"""

import json
import sys
import io
from datetime import datetime
from pathlib import Path

# 設置 UTF-8 編碼輸出（僅在直接執行時）
if __name__ == '__main__':
    if hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except:
            pass

from unified_updater import VenueUpdater
from quality_checker import QualityChecker


class BatchProcessor:
    """批量處理管道"""

    def __init__(self, venues_json_path='venues.json',
                 hotel_sources_path='hotel_sources.json',
                 max_batch_size=10):
        """
        初始化批量處理管道

        Args:
            venues_json_path: 場地資料JSON路徑
            hotel_sources_path: 飯店來源知識庫路徑
            max_batch_size: 單次批量處理最大場地數
        """
        self.venues_json_path = Path(venues_json_path)
        self.hotel_sources_path = Path(hotel_sources_path)
        self.max_batch_size = max_batch_size

        # 初始化子系統
        self.updater = VenueUpdater(venues_json_path)
        self.checker = QualityChecker(venues_json_path, hotel_sources_path)

        # 載入知識庫
        self.hotel_sources = self._load_hotel_sources()

    def _load_hotel_sources(self):
        """載入飯店來源知識庫"""
        if self.hotel_sources_path.exists():
            with open(self.hotel_sources_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _save_hotel_sources(self):
        """儲存飯店來源知識庫"""
        if self.hotel_sources:
            # 更新統計
            self._update_statistics()
            with open(self.hotel_sources_path, 'w', encoding='utf-8') as f:
                json.dump(self.hotel_sources, f, ensure_ascii=False, indent=2)

    def _update_statistics(self):
        """更新知識庫統計資料"""
        if not self.hotel_sources:
            return

        venues = self.hotel_sources.get('venues', {})
        stats = {
            'total_pending': 0,
            'total_completed': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0,
            'zero_photos': 0,
            'one_photo': 0,
            'two_photos': 0,
            'three_photos': 0
        }

        for venue_id, venue_data in venues.items():
            status = venue_data.get('status', 'pending')
            priority = venue_data.get('priority', 'low')
            photos = venue_data.get('current_photos', 0)

            if status == 'pending':
                stats['total_pending'] += 1
            elif status == 'completed':
                stats['total_completed'] += 1

            if priority == 'high':
                stats['high_priority'] += 1
            elif priority == 'medium':
                stats['medium_priority'] += 1
            elif priority == 'low':
                stats['low_priority'] += 1

            if photos == 0:
                stats['zero_photos'] += 1
            elif photos == 1:
                stats['one_photo'] += 1
            elif photos == 2:
                stats['two_photos'] += 1
            elif photos == 3:
                stats['three_photos'] += 1

        self.hotel_sources['statistics'] = stats

    def process_batch(self, venue_updates, verify_after=True, commit=True):
        """
        處理一批場地更新

        Args:
            venue_updates: {venue_id: updates, ...}
            verify_after: 更新後是否驗證 (default: True)
            commit: 是否提交到Git (default: True)

        Returns:
            dict: 處理結果
                - success_count: int
                - failed_count: int
                - results: list
                - verification_results: list (if verify_after)
                - backup_path: str
        """
        print(f'\n[批次處理] 開始處理 {len(venue_updates)} 個場地')
        print('=' * 60)

        # 1. 批量更新
        print('[1/4] 執行批量更新...')
        update_result = self.updater.update_batch(venue_updates)

        success_count = update_result['success_count']
        failed_count = update_result['failed_count']
        backup_path = update_result['backup_path']

        print(f'  ✓ 成功: {success_count}')
        print(f'  ✗ 失敗: {failed_count}')
        print(f'  備份: {backup_path}')

        # 2. 驗證更新結果
        verification_results = []
        if verify_after and success_count > 0:
            print('\n[2/4] 驗證更新結果...')
            for result in update_result['results']:
                if result['success']:
                    venue_id = result['venue_id']
                    check_result = self.checker.check_venue(venue_id)
                    verification_results.append(check_result)

                    status_icon = '✓' if check_result['score'] >= 60 else '⚠️'
                    print(f'  {status_icon} {check_result["venue_name"]}: {check_result["score"]}分')

                    # 如果有問題，顯示詳細資訊
                    if check_result['issues']:
                        print(f'    問題: {", ".join(check_result["issues"][:2])}')

        # 3. 提交到 Git
        commit_result = None
        if commit and success_count > 0:
            print('\n[3/4] 提交到 Git...')
            commit_result = self._commit_changes(update_result)
            if commit_result['success']:
                print(f'  ✓ {commit_result["message"]}')
            else:
                print(f'  ✗ 提交失敗: {commit_result["error"]}')

        # 4. 更新知識庫
        print('\n[4/4] 更新知識庫...')
        for venue_id in venue_updates.keys():
            self._update_venue_in_knowledge_base(venue_id)
        self._save_hotel_sources()
        print('  ✓ 知識庫已更新')

        print('\n[批次處理] 完成')
        print('=' * 60)

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'results': update_result['results'],
            'verification_results': verification_results,
            'backup_path': backup_path,
            'commit_result': commit_result
        }

    def _update_venue_in_knowledge_base(self, venue_id):
        """更新知識庫中的場地狀態"""
        if not self.hotel_sources:
            return

        venues = self.hotel_sources.get('venues', {})
        venue_id_str = str(venue_id)

        if venue_id_str in venues:
            venue_data = venues[venue_id_str]
            venue_data['last_attempt'] = datetime.now().strftime('%Y-%m-%d')

            # 檢查是否完成
            venue = self.updater.get_venue(venue_id)
            if venue:
                photo_count = len(venue.get('images', {}).get('gallery', []))
                venue_data['current_photos'] = photo_count

                if photo_count >= 4:
                    venue_data['status'] = 'completed'

    def _commit_changes(self, update_result):
        """提交變更到 Git"""
        try:
            import subprocess

            # 建立提交訊息
            success_venues = [r for r in update_result['results'] if r['success']]
            venue_names = [r['venue_name'] for r in success_venues[:5]]  # 最多顯示5個

            if len(success_venues) > 5:
                venue_names.append(f'等 {len(success_venues)} 個場地')

            commit_msg = f"Update {len(success_venues)} venues: {', '.join(venue_names)}\n\n"
            commit_msg += f"Batch update via unified system\n"
            commit_msg += f"Backup: {Path(update_result['backup_path']).name}\n"
            commit_msg += f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

            # 執行 Git 提交
            subprocess.run(['git', 'add', 'venues.json'], check=True,
                          capture_output=True)
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True,
                          capture_output=True)

            return {
                'success': True,
                'message': f'已提交 {len(success_venues)} 個場地更新'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_pending_venues(self, priority=None, max_photos=None):
        """
        取得待處理場地列表

        Args:
            priority: 優先級篩選 ('high', 'medium', 'low')
            max_photos: 最大照片數篩選

        Returns:
            list: 待處理場地列表
        """
        if not self.hotel_sources:
            return []

        pending_venues = []

        for venue_id_str, venue_data in self.hotel_sources.get('venues', {}).items():
            if venue_data.get('status') != 'pending':
                continue

            if priority and venue_data.get('priority') != priority:
                continue

            if max_photos is not None:
                photos = venue_data.get('current_photos', 0)
                if photos > max_photos:
                    continue

            pending_venues.append({
                'id': int(venue_id_str),
                'name': venue_data['name'],
                'priority': venue_data.get('priority', 'low'),
                'current_photos': venue_data.get('current_photos', 0),
                'base_url': venue_data.get('base_url', ''),
                'notes': venue_data.get('notes', '')
            })

        # 按優先級和照片數量排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        pending_venues.sort(key=lambda x: (
            priority_order.get(x['priority'], 99),
            x['current_photos']
        ))

        return pending_venues

    def print_summary(self):
        """印出處理摘要"""
        print('\n' + '=' * 60)
        print('批量處理管道摘要')
        print('=' * 60)

        if self.hotel_sources:
            stats = self.hotel_sources.get('statistics', {})
            print(f"待處理: {stats.get('total_pending', 0)} 個")
            print(f"已完成: {stats.get('total_completed', 0)} 個")
            print(f"  - 高優先級: {stats.get('high_priority', 0)} 個")
            print(f"  - 中優先級: {stats.get('medium_priority', 0)} 個")
            print(f"  - 低優先級: {stats.get('low_priority', 0)} 個")
            print(f"  - 無照片: {stats.get('zero_photos', 0)} 個")
        else:
            print("知識庫未載入")

        print('=' * 60)


# ========== 使用範例 ==========

if __name__ == '__main__':
    # 建立批量處理管道
    processor = BatchProcessor()

    # 印出摘要
    processor.print_summary()

    # 範例1: 取得待處理場地
    print('\n[範例1] 取得待處理場地')
    pending = processor.get_pending_venues(priority='high', max_photos=0)
    for venue in pending[:5]:
        print(f"  {venue['id']}: {venue['name']} - {venue['current_photos']}張照片")

    # 範例2: 批量處理（測試用，實際使用時移除）
    # print('\n[範例2] 批量處理')
    # batch_updates = {
    #     1122: {'images': {...}, 'lastUpdated': '2026-03-23'},
    #     1124: {'images': {...}, 'lastUpdated': '2026-03-23'}
    # }
    # result = processor.process_batch(batch_updates)
    # print(f"成功: {result['success_count']}, 失敗: {result['failed_count']}")
