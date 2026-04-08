#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一更新引擎 - Unified Venue Updater
取代所有重複的 update_xxx.py 腳本
支援單一場地更新和批量更新
"""

import json
import sys
import io
import shutil
from datetime import datetime
from pathlib import Path

# 設置 UTF-8 編碼輸出（僅在直接執行時）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class VenueUpdater:
    """統一場地更新引擎"""

    def __init__(self, venues_json_path='venues.json'):
        """初始化更新引擎"""
        self.venues_json_path = Path(venues_json_path)
        self.venues = self._load_venues()
        self.backup_path = None

    def _load_venues(self):
        """載入場地資料"""
        with open(self.venues_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_venues(self):
        """儲存場地資料"""
        with open(self.venues_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.venues, f, ensure_ascii=False, indent=2)

    def _create_backup(self):
        """建立備份檔案"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f'{self.venues_json_path.name}.backup.unified_{timestamp}'
        backup_path = self.venues_json_path.parent / backup_name
        shutil.copy(self.venues_json_path, backup_path)
        self.backup_path = backup_path
        return backup_path

    def update_venue(self, venue_id, updates, create_backup=True):
        """
        更新單一場地

        Args:
            venue_id: 場地ID (int)
            updates: 更新資料 (dict)
                - images: 照片資料
                - rooms: 會議室資料
                - verified: 驗證狀態
                - 等
            create_backup: 是否建立備份 (default: True)

        Returns:
            dict: 更新結果
                - success: bool
                - venue_name: str
                - updated_fields: list
                - backup_path: str
        """
        if create_backup:
            backup_path = self._create_backup()
        else:
            backup_path = None

        # 尋找場地
        venue = None
        venue_index = None
        for i, v in enumerate(self.venues):
            if v['id'] == venue_id:
                venue = v
                venue_index = i
                break

        if not venue:
            return {
                'success': False,
                'error': f'找不到場地 ID: {venue_id}'
            }

        # 記錄更新前的欄位
        venue_name = venue['name']
        updated_fields = []

        # 執行更新
        for key, value in updates.items():
            if key == 'images':
                # 更新照片資料
                if 'images' not in venue:
                    venue['images'] = {}
                for img_key, img_value in value.items():
                    venue['images'][img_key] = img_value
                    updated_fields.append(f'images.{img_key}')

            elif key == 'rooms':
                # 完全取代會議室資料
                old_room_count = len(venue.get('rooms', []))
                venue['rooms'] = value
                new_room_count = len(value)
                updated_fields.append(f'rooms: {old_room_count}→{new_room_count}')

            elif key == 'verified':
                # 更新驗證狀態
                venue['verified'] = value
                updated_fields.append('verified')

            elif key == 'lastUpdated':
                # 更新時間戳
                venue[key] = value
                updated_fields.append('lastUpdated')

            else:
                # 其他欄位直接更新
                venue[key] = value
                updated_fields.append(key)

        # 儲存變更
        self._save_venues()

        return {
            'success': True,
            'venue_id': venue_id,
            'venue_name': venue_name,
            'updated_fields': updated_fields,
            'backup_path': str(backup_path) if backup_path else None
        }

    def update_batch(self, updates_dict, create_backup=True):
        """
        批量更新多個場地

        Args:
            updates_dict: {venue_id: updates, ...}
            create_backup: 是否建立備份 (default: True)

        Returns:
            dict: 批量更新結果
                - success_count: int
                - failed_count: int
                - results: list
                - backup_path: str
        """
        if create_backup:
            backup_path = self._create_backup()
        else:
            backup_path = None

        results = []
        success_count = 0
        failed_count = 0

        for venue_id, updates in updates_dict.items():
            result = self.update_venue(venue_id, updates, create_backup=False)
            results.append(result)
            if result['success']:
                success_count += 1
            else:
                failed_count += 1

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results,
            'backup_path': str(backup_path) if backup_path else None
        }

    def add_photos(self, venue_id, main_photo, gallery_photos, source_url,
                   verified=True, note=''):
        """
        添加照片資料（便捷方法）

        Args:
            venue_id: 場地ID
            main_photo: 主要照片URL
            gallery_photos: 相簿照片URL列表
            source_url: 照片來源URL
            verified: 是否驗證
            note: 備註

        Returns:
            dict: 更新結果
        """
        updates = {
            'images': {
                'main': main_photo,
                'gallery': gallery_photos,
                'source': source_url,
                'verified': verified,
                'verifiedAt': datetime.now().isoformat() + 'Z',
                'note': note,
                'lastUpdated': datetime.now().strftime('%Y-%m-%d')
            },
            'lastUpdated': datetime.now().strftime('%Y-%m-%d')
        }

        return self.update_venue(venue_id, updates)

    def add_rooms(self, venue_id, rooms_data):
        """
        添加會議室資料（便捷方法）

        Args:
            venue_id: 場地ID
            rooms_data: 會議室資料列表

        Returns:
            dict: 更新結果
        """
        updates = {
            'rooms': rooms_data,
            'lastUpdated': datetime.now().strftime('%Y-%m-%d')
        }

        return self.update_venue(venue_id, updates)

    def get_venue(self, venue_id):
        """取得場地資料"""
        for venue in self.venues:
            if venue['id'] == venue_id:
                return venue
        return None

    def get_venues_by_photo_count(self, min_photos, max_photos=None):
        """根據照片數量篩選場地"""
        results = []
        for venue in self.venues:
            photo_count = len(venue.get('images', {}).get('gallery', []))
            if photo_count >= min_photos:
                if max_photos is None or photo_count <= max_photos:
                    results.append({
                        'id': venue['id'],
                        'name': venue['name'],
                        'photo_count': photo_count
                    })
        return results

    def print_summary(self):
        """印出場地統計摘要"""
        total = len(self.venues)
        zero_photos = self.get_venues_by_photo_count(0, 0)
        one_photo = self.get_venues_by_photo_count(1, 1)
        two_photos = self.get_venues_by_photo_count(2, 2)
        three_photos = self.get_venues_by_photo_count(3, 3)
        completed = self.get_venues_by_photo_count(4)

        print('=' * 60)
        print('場地統計摘要')
        print('=' * 60)
        print(f'總場地數: {total}')
        print(f'0張照片: {len(zero_photos)} 個')
        print(f'1張照片: {len(one_photo)} 個')
        print(f'2張照片: {len(two_photos)} 個')
        print(f'3張照片: {len(three_photos)} 個')
        print(f'已完成(4+): {len(completed)} 個')
        print('=' * 60)


# ========== 使用範例 ==========

if __name__ == '__main__':
    # 建立更新引擎
    updater = VenueUpdater('venues.json')

    # 印出統計摘要
    updater.print_summary()
    print()

    # 範例1: 更新單一場地的照片
    print('[範例1] 更新單一場地照片')
    result = updater.add_photos(
        venue_id=1126,  # 豪景大酒店
        main_photo='https://example.com/main.jpg',
        gallery_photos=[
            'https://example.com/photo1.jpg',
            'https://example.com/photo2.jpg'
        ],
        source_url='https://example.com',
        note='測試更新'
    )

    if result['success']:
        print(f"✓ 更新成功: {result['venue_name']}")
        print(f"  更新欄位: {', '.join(result['updated_fields'])}")
        print(f"  備份檔案: {result['backup_path']}")
    else:
        print(f"✗ 更新失敗: {result['error']}")

    print()

    # 範例2: 批量更新多個場地
    print('[範例2] 批量更新多個場地')
    batch_updates = {
        1122: {
            'images': {
                'main': 'https://example.com/1122_main.jpg',
                'gallery': ['https://example.com/1122_1.jpg'],
                'source': 'https://example.com',
                'verified': True,
                'verifiedAt': datetime.now().isoformat() + 'Z',
                'lastUpdated': datetime.now().strftime('%Y-%m-%d')
            },
            'lastUpdated': datetime.now().strftime('%Y-%m-%d')
        },
        1124: {
            'images': {
                'main': 'https://example.com/1124_main.jpg',
                'gallery': ['https://example.com/1124_1.jpg'],
                'source': 'https://example.com',
                'verified': True,
                'verifiedAt': datetime.now().isoformat() + 'Z',
                'lastUpdated': datetime.now().strftime('%Y-%m-%d')
            },
            'lastUpdated': datetime.now().strftime('%Y-%m-%d')
        }
    }

    # 注意：實際使用時移除這個測試範例的執行
    # batch_result = updater.update_batch(batch_updates)
    # print(f"批量更新完成: {batch_result['success_count']} 成功, {batch_result['failed_count']} 失敗")
