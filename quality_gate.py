#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料品質閘門 - 多層次資料驗證機制

功能：
1. 定義多層次品質規則（critical, warning, info）
2. 執行所有規則檢查
3. 計算品質分數
4. 決定是否允許更新
5. 支援嚴格模式和寬鬆模式

作者：Jobs (Global CTO)
日期：2026-03-24
版本：1.0
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Callable, Optional
import requests

# Windows UTF-8 相容
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


class QualityGate:
    """資料品質閘門"""

    # 品質規則定義
    QUALITY_RULES = {
        'critical': [
            # 必填欄位檢查
            {
                'name': '必填欄位完整性',
                'check': lambda v: QualityGate._check_required_fields(v),
                'message': '缺少必填欄位'
            },
            # URL 格式檢查
            {
                'name': 'URL 格式正確性',
                'check': lambda v: QualityGate._check_url_format(v),
                'message': 'URL 格式錯誤'
            },
            # 維度格式檢查
            {
                'name': '維度資料格式',
                'check': lambda v: QualityGate._check_dimensions_format(v),
                'message': '維度資料格式錯誤'
            },
            # 容量一致性檢查
            {
                'name': '容量資料一致性',
                'check': lambda v: QualityGate._check_capacity_consistency(v),
                'message': '容量資料不一致'
            }
        ],
        'warning': [
            # 照片 URL 檢查
            {
                'name': '照片 URL 有效性',
                'check': lambda v: QualityGate._check_photo_urls(v),
                'message': '照片 URL 無效'
            },
            # 官網可達性檢查
            {
                'name': '官網可達性',
                'check': lambda v: QualityGate._check_website_reachable(v),
                'message': '官網無法訪問'
            },
            # 價格合理性檢查
            {
                'name': '價格合理性',
                'check': lambda v: QualityGate._check_price_reasonability(v),
                'message': '價格數值異常'
            },
            # 容納人數合理性檢查
            {
                'name': '容納人數合理性',
                'check': lambda v: QualityGate._check_capacity_reasonability(v),
                'message': '容納人數異常'
            }
        ],
        'info': [
            # 資料完整度提示
            {
                'name': '資料完整度',
                'check': lambda v: QualityGate._check_data_completeness(v),
                'message': '資料完整度不足'
            }
        ]
    }

    # 必填欄位
    REQUIRED_FIELDS = ['id', 'name', 'venueType', 'city', 'address', 'contactPhone', 'url']

    def __init__(self, strict_mode: bool = False):
        """
        初始化品質閘門

        Args:
            strict_mode: 嚴格模式，任何警告都會阻擋更新
        """
        self.strict_mode = strict_mode
        self.results = []

    def should_allow_update(self, venue_data: Dict) -> Tuple[bool, Dict]:
        """
        決定是否允許更新

        Args:
            venue_data: 場地資料

        Returns:
            (allow, report) - 是否允許更新和詳細報告
        """
        report = {
            'venueId': venue_data.get('id'),
            'venueName': venue_data.get('name'),
            'timestamp': datetime.now().isoformat(),
            'qualityScore': 0,
            'qualityGrade': 'F',
            'criticalIssues': [],
            'warnings': [],
            'info': [],
            'allowUpdate': False,
            'reason': ''
        }

        # 1. 執行 Critical 規則
        for rule in self.QUALITY_RULES['critical']:
            try:
                passed, message = rule['check'](venue_data)
                if not passed:
                    report['criticalIssues'].append({
                        'rule': rule['name'],
                        'message': message or rule['message']
                    })
            except Exception as e:
                report['criticalIssues'].append({
                    'rule': rule['name'],
                    'message': f'檢查失敗: {str(e)}'
                })

        # 2. 執行 Warning 規則
        for rule in self.QUALITY_RULES['warning']:
            try:
                passed, message = rule['check'](venue_data)
                if not passed:
                    report['warnings'].append({
                        'rule': rule['name'],
                        'message': message or rule['message']
                    })
            except Exception as e:
                report['warnings'].append({
                    'rule': rule['name'],
                    'message': f'檢查失敗: {str(e)}'
                })

        # 3. 執行 Info 規則
        for rule in self.QUALITY_RULES['info']:
            try:
                passed, message = rule['check'](venue_data)
                if not passed:
                    report['info'].append({
                        'rule': rule['name'],
                        'message': message or rule['message']
                    })
            except Exception as e:
                pass  # Info 規則失敗不記錄

        # 4. 計算品質分數
        report['qualityScore'] = self._calculate_score(report)
        report['qualityGrade'] = self._get_grade(report['qualityScore'])

        # 5. 決定是否允許更新
        if len(report['criticalIssues']) > 0:
            report['allowUpdate'] = False
            report['reason'] = f'發現 {len(report["criticalIssues"])} 個嚴重問題'
        elif self.strict_mode and len(report['warnings']) > 0:
            report['allowUpdate'] = False
            report['reason'] = f'嚴格模式：發現 {len(report["warnings"])} 個警告'
        else:
            report['allowUpdate'] = True
            report['reason'] = '通過品質檢查'

        return report['allowUpdate'], report

    def batch_check(self, venues_data: List[Dict]) -> Dict:
        """
        批次檢查多個場地

        Args:
            venues_data: 場地資料列表

        Returns:
            批次檢查報告
        """
        print(f"\n{'='*70}")
        print(f"品質閘門檢查 - {len(venues_data)} 個場地")
        print(f"{'='*70}\n")

        results = []
        stats = {
            'total': len(venues_data),
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }

        for i, venue in enumerate(venues_data, 1):
            allow, report = self.should_allow_update(venue)
            results.append(report)

            # 更新統計
            if allow:
                stats['passed'] += 1
                print(f"✅ [{i}/{len(venues_data)}] {venue['name']}")
            else:
                stats['failed'] += 1
                print(f"❌ [{i}/{len(venues_data)}] {venue['name']}")
                print(f"   {report['reason']}")

            if len(report['warnings']) > 0:
                stats['warnings'] += 1

        # 輸出摘要
        print(f"\n{'='*70}")
        print(f"檢查完成")
        print(f"{'='*70}")
        print(f"總計: {stats['total']}")
        print(f"✅ 通過: {stats['passed']}")
        print(f"❌ 失敗: {stats['failed']}")
        print(f"⚠️  有警告: {stats['warnings']}")

        return {
            'results': results,
            'stats': stats,
            'checkedAt': datetime.now().isoformat()
        }

    def _calculate_score(self, report: Dict) -> float:
        """計算品質分數（0-100）"""
        score = 100

        # Critical 問題：每個 -30 分
        score -= len(report['criticalIssues']) * 30

        # Warnings：每個 -10 分
        score -= len(report['warnings']) * 10

        # Info：每個 -2 分
        score -= len(report['info']) * 2

        return max(0, score)

    def _get_grade(self, score: float) -> str:
        """根據分數取得等級"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    @staticmethod
    def _check_required_fields(venue: Dict) -> Tuple[bool, str]:
        """檢查必填欄位"""
        missing = []
        for field in QualityGate.REQUIRED_FIELDS:
            if not venue.get(field):
                missing.append(field)

        if missing:
            return False, f"缺少欄位: {', '.join(missing)}"
        return True, ''

    @staticmethod
    def _check_url_format(venue: Dict) -> Tuple[bool, str]:
        """檢查 URL 格式"""
        url = venue.get('url', '')
        if not url:
            return True, ''  # URL 可選

        if not url.startswith(('http://', 'https://')):
            return False, f"URL 格式錯誤: {url}"
        return True, ''

    @staticmethod
    def _check_dimensions_format(venue: Dict) -> Tuple[bool, str]:
        """檢查維度資料格式"""
        rooms = venue.get('rooms', [])
        errors = []

        for room in rooms:
            # 檢查 sqm 格式
            if 'sqm' in room and room['sqm'] is not None:
                if not isinstance(room['sqm'], (int, float)):
                    errors.append(f"{room.get('name', 'Unknown')}: sqm 非數字")
                elif room['sqm'] < 0 or room['sqm'] > 10000:
                    errors.append(f"{room.get('name', 'Unknown')}: sqm 數值異常")

            # 檢查 capacity 格式
            if 'capacity' in room:
                capacity = room['capacity']
                if not isinstance(capacity, dict):
                    errors.append(f"{room.get('name', 'Unknown')}: capacity 非物件")
                else:
                    for key, value in capacity.items():
                        if value is not None and not isinstance(value, int):
                            errors.append(f"{room.get('name', 'Unknown')}: capacity.{key} 非整數")

        if errors:
            return False, '; '.join(errors)
        return True, ''

    @staticmethod
    def _check_capacity_consistency(venue: Dict) -> Tuple[bool, str]:
        """檢查容量資料一致性"""
        rooms = venue.get('rooms', [])
        errors = []

        for room in rooms:
            capacity = room.get('capacity', {})
            if not capacity:
                continue

            # 檢查容量值是否合理（theater > banquet > classroom）
            theater = capacity.get('theater', 0)
            banquet = capacity.get('banquet', 0)
            classroom = capacity.get('classroom', 0)

            if theater > 0 and banquet > 0:
                # 劇院式應該大於宴會式
                if theater < banquet:
                    errors.append(f"{room.get('name', 'Unknown')}: theater < banquet")

            if banquet > 0 and classroom > 0:
                # 宴會式應該大於課堂式
                if banquet < classroom:
                    errors.append(f"{room.get('name', 'Unknown')}: banquet < classroom")

        if errors:
            return False, '; '.join(errors)
        return True, ''

    @staticmethod
    def _check_photo_urls(venue: Dict) -> Tuple[bool, str]:
        """檢查照片 URL（不實際訪問，只檢查格式）"""
        errors = []

        # 檢查場地主照片
        main_image = venue.get('images', {}).get('main')
        if main_image:
            if not main_image.startswith(('http://', 'https://')):
                errors.append('主照片 URL 格式錯誤')

        # 檢查會議室照片
        rooms = venue.get('rooms', [])
        for room in rooms:
            images = room.get('images', [])

            # images 可能是列表或字典
            if isinstance(images, list):
                for img in images:
                    if img and not img.startswith(('http://', 'https://')):
                        errors.append(f"{room.get('name', 'Unknown')}: 照片 URL 格式錯誤")
            elif isinstance(images, dict):
                main = images.get('main')
                if main and not main.startswith(('http://', 'https://')):
                    errors.append(f"{room.get('name', 'Unknown')}: 照片 URL 格式錯誤")

        if errors:
            return False, '; '.join(errors[:3])  # 只返回前3個錯誤
        return True, ''

    @staticmethod
    def _check_website_reachable(venue: Dict) -> Tuple[bool, str]:
        """檢查官網可達性（可選，因為可能較慢）"""
        url = venue.get('url', '')
        if not url:
            return True, ''  # URL 可選

        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                return False, f"HTTP {response.status_code}"
            return True, ''
        except Exception:
            # 網路問題不視為資料問題
            return True, ''

    @staticmethod
    def _check_price_reasonability(venue: Dict) -> Tuple[bool, str]:
        """檢查價格合理性"""
        warnings = []

        half_day = venue.get('priceHalfDay')
        full_day = venue.get('priceFullDay')

        if half_day is not None:
            if not isinstance(half_day, (int, float)) or half_day < 0:
                warnings.append('半日價格非數字或為負數')
            elif half_day < 500:
                warnings.append('半日價格過低 (< 500)')
            elif half_day > 500000:
                warnings.append('半日價格過高 (> 500,000)')

        if full_day is not None:
            if not isinstance(full_day, (int, float)) or full_day < 0:
                warnings.append('全日價格非數字或為負數')
            elif full_day < 1000:
                warnings.append('全日價格過低 (< 1,000)')
            elif full_day > 1000000:
                warnings.append('全日價格過高 (> 1,000,000)')

        # 檢查邏輯：全日應該大於半日
        if half_day and full_day:
            if full_day < half_day:
                warnings.append('全日價格低於半日價格')

        if warnings:
            return False, '; '.join(warnings)
        return True, ''

    @staticmethod
    def _check_capacity_reasonability(venue: Dict) -> Tuple[bool, str]:
        """檢查容納人數合理性"""
        warnings = []

        max_capacity = venue.get('maxCapacityTheater')
        if max_capacity is not None:
            if not isinstance(max_capacity, int) or max_capacity < 0:
                warnings.append('最大容納人數非整數或為負數')
            elif max_capacity < 10:
                warnings.append('最大容納人數過少 (< 10)')
            elif max_capacity > 50000:
                warnings.append('最大容納人數過多 (> 50,000)')

        if warnings:
            return False, '; '.join(warnings)
        return True, ''

    @staticmethod
    def _check_data_completeness(venue: Dict) -> Tuple[bool, str]:
        """檢查資料完整度"""
        optional_fields = [
            'contactPerson', 'contactEmail', 'priceHalfDay', 'priceFullDay',
            'maxCapacityTheater', 'maxCapacityClassroom', 'equipment'
        ]

        filled = sum(1 for field in optional_fields if venue.get(field))
        completeness = filled / len(optional_fields)

        if completeness < 0.3:
            return False, f'完整度: {completeness*100:.0f}%'

        return True, ''


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(
        description='資料品質閘門 - 驗證場地資料品質',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 檢查單一場地
  python quality_gate.py --venue venues.json --id 1086

  # 檢查所有場地
  python quality_gate.py --all venues.json

  # 嚴格模式（任何警告都會阻擋）
  python quality_gate.py --all venues.json --strict

  # 生成報告
  python quality_gate.py --all venues.json --report quality_report.json
        """
    )

    parser.add_argument(
        '--venue',
        type=str,
        default='venues.json',
        help='venues.json 路徑'
    )

    parser.add_argument(
        '--id',
        type=int,
        help='檢查單一場地 ID'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='檢查所有場地'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='嚴格模式'
    )

    parser.add_argument(
        '--report',
        type=str,
        help='生成 JSON 報告'
    )

    args = parser.parse_args()

    # 讀取資料
    with open(args.venue, 'r', encoding='utf-8') as f:
        venues_data = json.load(f)

    gate = QualityGate(strict_mode=args.strict)

    if args.id:
        # 單一場地
        venue = next((v for v in venues_data if v['id'] == args.id), None)
        if not venue:
            print(f"❌ 找不到場地 ID: {args.id}")
            sys.exit(1)

        allow, report = gate.should_allow_update(venue)

        print(f"\n{'='*70}")
        print(f"品質檢查報告: {venue['name']}")
        print(f"{'='*70}")
        print(f"品質分數: {report['qualityScore']:.0f}/100")
        print(f"品質等級: {report['qualityGrade']}")
        print(f"允許更新: {'是' if allow else '否'}")
        print(f"原因: {report['reason']}")

        if report['criticalIssues']:
            print(f"\n❌ 嚴重問題 ({len(report['criticalIssues'])}):")
            for issue in report['criticalIssues']:
                print(f"  - {issue['rule']}: {issue['message']}")

        if report['warnings']:
            print(f"\n⚠️  警告 ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  - {warning['rule']}: {warning['message']}")

        # 返回適當的退出碼
        sys.exit(0 if allow else 1)

    elif args.all:
        # 所有場地
        result = gate.batch_check(venues_data)

        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n📄 報告已保存: {args.report}")

        # 如果有任何失敗，返回非零退出碼
        sys.exit(0 if result['stats']['failed'] == 0 else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
