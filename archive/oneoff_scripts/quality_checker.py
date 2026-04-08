#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料品質檢驗系統 - Data Quality Checker
自動化檢查場地資料的完整性和準確性
避免重複晶華飯店的錯誤（爬錯頁面、錯誤照片）
"""

import json
import sys
import io
from urllib.parse import urlparse
from pathlib import Path

# 設置 UTF-8 編碼輸出（僅在直接執行時）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class QualityChecker:
    """資料品質檢驗系統"""

    # 品質檢查項目定義
    CHECK_ITEMS = {
        'photo_source': {
            'name': '照片來源驗證',
            'weight': 5,  # 最高權重
            'description': '照片必須來自場地官網'
        },
        'photo_count': {
            'name': '照片數量',
            'weight': 2,
            'description': '至少4張照片'
        },
        'photo_accessibility': {
            'name': '照片可訪問性',
            'weight': 3,
            'description': '照片URL應該可訪問'
        },
        'room_completeness': {
            'name': '會議室完整性',
            'weight': 4,
            'description': '每個會議室應有照片和完整資料'
        },
        'data_consistency': {
            'name': '資料一致性',
            'weight': 3,
            'description': '面積、容量等資料應一致'
        },
        'verified_status': {
            'name': '驗證狀態',
            'weight': 2,
            'description': '場地應標記為已驗證'
        }
    }

    # 已知錯誤模式
    KNOWN_ERRORS = {
        'wrong_page_patterns': [
            '/uploads/news/',  # 晶華飯店錯誤
            '/accommodation/',
            '/rooms/',
            '/dining/',
            '/gallery/'
        ],
        'wrong_photo_patterns': [
            'nav-',  # 如 nav-regent-taipei-accommodation.jpg
            'logo',  # 只有 logo
            'icon'   # 圖示
        ],
        'low_quality_patterns': [
            'placeholder',
            'coming_soon',
            'under_construction'
        ]
    }

    def __init__(self, venues_json_path='venues.json', hotel_sources_path='hotel_sources.json'):
        """初始化檢驗系統"""
        self.venues_json_path = Path(venues_json_path)
        self.hotel_sources_path = Path(hotel_sources_path)
        self.venues = self._load_venues()
        self.hotel_sources = self._load_hotel_sources()

    def _load_venues(self):
        """載入場地資料"""
        with open(self.venues_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_hotel_sources(self):
        """載入飯店來源知識庫"""
        if self.hotel_sources_path.exists():
            with open(self.hotel_sources_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def check_venue(self, venue_id):
        """
        檢查單一場地的資料品質

        Args:
            venue_id: 場地ID

        Returns:
            dict: 檢查結果
                - venue_id: int
                - venue_name: str
                - score: float (0-100)
                - issues: list
                - warnings: list
                - passed_checks: list
                - failed_checks: list
        """
        # 尋找場地
        venue = None
        for v in self.venues:
            if v['id'] == venue_id:
                venue = v
                break

        if not venue:
            return {
                'venue_id': venue_id,
                'error': f'找不到場地 ID: {venue_id}'
            }

        issues = []  # 嚴重問題
        warnings = []  # 警告
        passed_checks = []
        failed_checks = []

        total_score = 0
        max_score = 0

        # 1. 檢查照片來源
        photo_source_result = self._check_photo_source(venue)
        max_score += self.CHECK_ITEMS['photo_source']['weight']
        if photo_source_result['passed']:
            total_score += self.CHECK_ITEMS['photo_source']['weight']
            passed_checks.append('照片來源')
        else:
            failed_checks.append('照片來源')
            issues.extend(photo_source_result['issues'])

        # 2. 檢查照片數量
        photo_count_result = self._check_photo_count(venue)
        max_score += self.CHECK_ITEMS['photo_count']['weight']
        if photo_count_result['passed']:
            total_score += self.CHECK_ITEMS['photo_count']['weight']
            passed_checks.append('照片數量')
        else:
            failed_checks.append('照片數量')
            warnings.extend(photo_count_result['warnings'])

        # 3. 檢查會議室完整性
        room_result = self._check_rooms(venue)
        max_score += self.CHECK_ITEMS['room_completeness']['weight']
        if room_result['passed']:
            total_score += self.CHECK_ITEMS['room_completeness']['weight']
            passed_checks.append('會議室完整性')
        else:
            failed_checks.append('會議室完整性')
            issues.extend(room_result['issues'])
            warnings.extend(room_result['warnings'])

        # 4. 檢查驗證狀態
        verified_result = self._check_verified(venue)
        max_score += self.CHECK_ITEMS['verified_status']['weight']
        if verified_result['passed']:
            total_score += self.CHECK_ITEMS['verified_status']['weight']
            passed_checks.append('驗證狀態')
        else:
            failed_checks.append('驗證狀態')
            warnings.extend(verified_result['warnings'])

        # 5. 檢查已知錯誤模式
        error_pattern_result = self._check_error_patterns(venue)
        if error_pattern_result['has_errors']:
            issues.extend(error_pattern_result['issues'])

        # 計算分數
        score = (total_score / max_score * 100) if max_score > 0 else 0

        return {
            'venue_id': venue_id,
            'venue_name': venue['name'],
            'score': round(score, 1),
            'issues': issues,
            'warnings': warnings,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'status': 'excellent' if score >= 80 else 'good' if score >= 60 else 'poor'
        }

    def _check_photo_source(self, venue):
        """檢查照片來源"""
        issues = []

        # 取得場地官網
        venue_url = venue.get('url', '')
        if not venue_url:
            return {'passed': False, 'issues': ['缺少場地官網URL']}

        # 取得照片來源
        images = venue.get('images', {})
        source = images.get('source', '')

        if not source:
            return {'passed': False, 'issues': ['缺少照片來源']}

        # 檢查來源是否為官網
        if venue_url not in source:
            issues.append(f'照片來源不是官網: {source}')

        # 檢查是否為已知錯誤頁面
        for pattern in self.KNOWN_ERRORS['wrong_page_patterns']:
            if pattern in source:
                issues.append(f'照片來自錯誤頁面模式: {pattern}')

        return {
            'passed': len(issues) == 0,
            'issues': issues
        }

    def _check_photo_count(self, venue):
        """檢查照片數量"""
        warnings = []

        gallery = venue.get('images', {}).get('gallery', [])
        photo_count = len(gallery)

        if photo_count < 4:
            warnings.append(f'照片數量不足: {photo_count} 張（建議至少4張）')

        if photo_count == 0:
            return {'passed': False, 'warnings': warnings}

        return {
            'passed': photo_count >= 4,
            'warnings': warnings
        }

    def _check_rooms(self, venue):
        """檢查會議室完整性"""
        issues = []
        warnings = []

        rooms = venue.get('rooms', [])

        if not rooms:
            issues.append('缺少會議室資料')
            return {'passed': False, 'issues': issues, 'warnings': warnings}

        # 檢查每個會議室
        rooms_without_photo = 0
        for room in rooms:
            if not room.get('photo'):
                rooms_without_photo += 1

        if rooms_without_photo > 0:
            warnings.append(f'{rooms_without_photo} 個會議室缺少照片')

        return {
            'passed': rooms_without_photo == 0,
            'issues': issues,
            'warnings': warnings
        }

    def _check_verified(self, venue):
        """檢查驗證狀態"""
        warnings = []

        verified = venue.get('verified', False)
        if not verified:
            warnings.append('場地未標記為已驗證')
            return {'passed': False, 'warnings': warnings}

        # 檢查是否有驗證時間
        images = venue.get('images', {})
        verified_at = images.get('verifiedAt', '')
        if not verified_at:
            warnings.append('缺少驗證時間戳')

        return {
            'passed': verified,
            'warnings': warnings
        }

    def _check_error_patterns(self, venue):
        """檢查已知錯誤模式"""
        issues = []

        gallery = venue.get('images', {}).get('gallery', [])

        for photo_url in gallery:
            # 檢查錯誤照片模式
            for pattern in self.KNOWN_ERRORS['wrong_photo_patterns']:
                if pattern in photo_url:
                    issues.append(f'照片URL包含錯誤模式: {pattern} 在 {photo_url}')

            # 檢查低質量照片
            for pattern in self.KNOWN_ERRORS['low_quality_patterns']:
                if pattern in photo_url:
                    issues.append(f'可能為低質量照片: {photo_url}')

        return {
            'has_errors': len(issues) > 0,
            'issues': issues
        }

    def check_batch(self, venue_ids):
        """批量檢查多個場地"""
        results = []

        for venue_id in venue_ids:
            result = self.check_venue(venue_id)
            results.append(result)

        return results

    def print_report(self, check_result):
        """印出檢查報告"""
        print('=' * 60)
        print(f"場地: {check_result['venue_name']} (ID: {check_result['venue_id']})")
        print('=' * 60)
        print(f"品質分數: {check_result['score']}/100")
        print(f"狀態: {check_result['status'].upper()}")
        print()

        if check_result.get('passed_checks'):
            print("✓ 通過檢查:")
            for check in check_result['passed_checks']:
                print(f"  - {check}")
            print()

        if check_result.get('failed_checks'):
            print("✗ 失敗檢查:")
            for check in check_result['failed_checks']:
                print(f"  - {check}")
            print()

        if check_result.get('issues'):
            print("🚨 嚴重問題:")
            for issue in check_result['issues']:
                print(f"  - {issue}")
            print()

        if check_result.get('warnings'):
            print("⚠️  警告:")
            for warning in check_result['warnings']:
                print(f"  - {warning}")
            print()

        print('=' * 60)

    def get_venues_by_quality(self, min_score=0, max_score=100):
        """根據品質分數篩選場地"""
        results = []

        for venue in self.venues:
            check_result = self.check_venue(venue['id'])
            score = check_result['score']
            if min_score <= score <= max_score:
                results.append({
                    'id': venue['id'],
                    'name': venue['name'],
                    'score': score,
                    'status': check_result['status']
                })

        # 按分數排序
        results.sort(key=lambda x: x['score'])
        return results


# ========== 使用範例 ==========

if __name__ == '__main__':
    # 建立檢驗系統
    checker = QualityChecker('venues.json', 'hotel_sources.json')

    # 範例1: 檢查單一場地
    print('[範例1] 檢查場地 1086 (晶華飯店)')
    result = checker.check_venue(1086)
    checker.print_report(result)

    # 範例2: 找出低品質場地
    print('\n[範例2] 品質分數 < 60 的場地')
    poor_venues = checker.get_venues_by_quality(0, 60)
    for venue in poor_venues:
        print(f"  {venue['id']}: {venue['name']} - {venue['score']}分")

    # 範例3: 找出有問題的場地
    print('\n[範例3] 有嚴重問題的場地')
    for venue in poor_venues:
        result = checker.check_venue(venue['id'])
        if result['issues']:
            print(f"\n{venue['name']} (ID: {venue['id']}):")
            for issue in result['issues']:
                print(f"  - {issue}")
