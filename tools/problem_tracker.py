#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/problem_tracker.py - 問題追蹤系統

記錄、查詢、管理場地資料問題
避免重複診斷已確認的問題
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Windows 控制台編碼修復
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 專案路徑
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_FILE = os.path.join(PROJECT_ROOT, 'data', 'problems.json')
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')


# 問題類型定義
PROBLEM_TYPES = {
    'missing_rooms': '缺少會議室資料',
    'missing_pricing': '缺少價格資料',
    'missing_capacity': '缺少容量資料',
    'missing_images': '缺少圖片資料',
    'missing_description': '缺少場地描述',
    'invalid_schema': 'Schema 格式錯誤',
    'low_quality_source': '資料來源品質低',
    'website_changed': '官網結構變更',
    'website_404': '官網無法存取',
}

# 嚴重程度定義
SEVERITY_LEVELS = {
    'critical': '嚴重 - 影響核心功能',
    'high': '高 - 重要資料缺失',
    'medium': '中 - 部分資料缺失',
    'low': '低 - 次要資料缺失',
}

# 問題狀態定義
STATUS_TYPES = {
    'open': '待處理',
    'diagnosing': '診斷中',
    'fixing': '修復中',
    'fixed': '已修復',
    'wontfix': '無法修復',
    'confirmed_absent': '確認官網無此資料',
}


class ProblemTracker:
    """問題追蹤器"""

    def __init__(self, problems_file: str = None):
        """初始化問題追蹤器

        Args:
            problems_file: 問題資料檔案路徑，預設為 data/problems.json
        """
        self.problems_file = problems_file or PROBLEMS_FILE
        self._ensure_data_dir()
        self.problems = self._load_problems()

    def _ensure_data_dir(self):
        """確保 data 目錄存在"""
        data_dir = os.path.dirname(self.problems_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load_problems(self) -> List[Dict]:
        """載入問題記錄"""
        if os.path.exists(self.problems_file):
            try:
                with open(self.problems_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[警告] 載入問題記錄失敗: {e}")
                return []
        return []

    def _save_problems(self):
        """儲存問題記錄"""
        with open(self.problems_file, 'w', encoding='utf-8') as f:
            json.dump(self.problems, f, ensure_ascii=False, indent=2)

    def _load_venues(self) -> List[Dict]:
        """載入場地資料"""
        if os.path.exists(VENUES_FILE):
            with open(VENUES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else data.get('venues', [])
        return []

    def _find_problem(self, venue_id: int, field: str) -> Optional[Dict]:
        """尋找已存在的問題記錄"""
        for problem in self.problems:
            if (problem.get('venueId') == venue_id and
                problem.get('field') == field and
                problem.get('status') not in ['fixed', 'confirmed_absent']):
                return problem
        return None

    def record_problem(
        self,
        venue_id: int,
        problem_type: str,
        field: str,
        severity: str = 'medium',
        diagnosis: str = None,
        can_fix: bool = None,
        fix_action: str = None,
        source: str = 'validator',
        notes: str = None
    ) -> Dict:
        """記錄問題

        Args:
            venue_id: 場地 ID
            problem_type: 問題類型
            field: 欄位名稱
            severity: 嚴重程度
            diagnosis: LLM 診斷結果
            can_fix: 是否可修復
            fix_action: 修復建議
            source: 問題來源
            notes: 備註

        Returns:
            問題記錄
        """
        # 載入場地資料以取得場地名稱
        venues = self._load_venues()
        venue = next((v for v in venues if v.get('id') == venue_id), None)
        venue_name = venue.get('name', 'Unknown') if venue else 'Unknown'

        # 檢查是否已有相同問題
        existing = self._find_problem(venue_id, field)
        now = datetime.now().isoformat()

        if existing:
            # 更新已有問題
            existing['lastSeen'] = now
            existing['occurrences'] = existing.get('occurrences', 1) + 1
            if severity != existing.get('severity'):
                existing['severity'] = severity
            if diagnosis:
                existing['diagnosis'] = diagnosis
            if can_fix is not None:
                existing['canFix'] = can_fix
            if fix_action:
                existing['fixAction'] = fix_action
            if notes:
                old_notes = existing.get('notes', '')
                existing['notes'] = f"{old_notes}\n{now}: {notes}" if old_notes else notes
            self._save_problems()
            return existing
        else:
            # 建立新問題
            problem = {
                'id': f"{venue_id}-{field}-{int(datetime.now().timestamp())}",
                'venueId': venue_id,
                'venueName': venue_name,
                'problemType': problem_type,
                'severity': severity,
                'field': field,
                'diagnosis': diagnosis,
                'canFix': can_fix,
                'fixAction': fix_action,
                'source': source,
                'firstSeen': now,
                'lastSeen': now,
                'occurrences': 1,
                'status': 'open',
                'notes': notes or '',
            }
            self.problems.append(problem)
            self._save_problems()
            return problem

    def get_problems(
        self,
        venue_id: int = None,
        status: str = None,
        problem_type: str = None,
        severity: str = None
    ) -> List[Dict]:
        """查詢問題

        Args:
            venue_id: 場地 ID 過濾
            status: 狀態過濾
            problem_type: 問題類型過濾
            severity: 嚴重程度過濾

        Returns:
            問題列表
        """
        results = self.problems

        if venue_id is not None:
            results = [p for p in results if p.get('venueId') == venue_id]

        if status is not None:
            results = [p for p in results if p.get('status') == status]

        if problem_type is not None:
            results = [p for p in results if p.get('problemType') == problem_type]

        if severity is not None:
            results = [p for p in results if p.get('severity') == severity]

        # 按更新時間排序
        results.sort(key=lambda x: x.get('lastSeen', ''), reverse=True)

        return results

    def get_problem(self, problem_id: str) -> Optional[Dict]:
        """取得單一問題"""
        for problem in self.problems:
            if problem.get('id') == problem_id:
                return problem
        return None

    def mark_fixed(self, problem_id: str, fix_notes: str = None) -> bool:
        """標記問題已修復

        Args:
            problem_id: 問題 ID
            fix_notes: 修復說明

        Returns:
            是否成功
        """
        problem = self.get_problem(problem_id)
        if not problem:
            return False

        problem['status'] = 'fixed'
        problem['fixedAt'] = datetime.now().isoformat()
        if fix_notes:
            old_notes = problem.get('notes', '')
            problem['notes'] = f"{old_notes}\n{datetime.now().isoformat()}: 修復: {fix_notes}"

        self._save_problems()
        return True

    def mark_wontfix(self, problem_id: str, reason: str) -> bool:
        """標記問題不可修復

        Args:
            problem_id: 問題 ID
            reason: 原因說明

        Returns:
            是否成功
        """
        problem = self.get_problem(problem_id)
        if not problem:
            return False

        problem['status'] = 'wontfix'
        problem['wontfixReason'] = reason
        problem['wontfixAt'] = datetime.now().isoformat()

        old_notes = problem.get('notes', '')
        problem['notes'] = f"{old_notes}\n{datetime.now().isoformat()}: 無法修復: {reason}"

        self._save_problems()
        return True

    def mark_confirmed_absent(self, problem_id: str, reason: str) -> bool:
        """標記確認官網無此資料

        Args:
            problem_id: 問題 ID
            reason: 確認說明

        Returns:
            是否成功
        """
        problem = self.get_problem(problem_id)
        if not problem:
            return False

        problem['status'] = 'confirmed_absent'
        problem['confirmedAt'] = datetime.now().isoformat()
        problem['canFix'] = False

        old_notes = problem.get('notes', '')
        problem['notes'] = f"{old_notes}\n{datetime.now().isoformat()}: 確認官網無此資料: {reason}"

        self._save_problems()
        return True

    def should_skip_diagnosis(self, venue_id: int, field: str) -> bool:
        """檢查是否應跳過診斷

        如果問題已確認為官網無此資料，或已診斷過且未變化，則跳過

        Args:
            venue_id: 場地 ID
            field: 欄位名稱

        Returns:
            是否應跳過診斷
        """
        problem = self._find_problem(venue_id, field)

        if not problem:
            return False

        # 已確認官網無此資料 → 跳過
        if problem.get('status') == 'confirmed_absent':
            return True

        # 已診斷過且有明確結論 → 跳過
        if problem.get('diagnosis') and problem.get('canFix') is not None:
            return True

        return False

    def get_statistics(self) -> Dict:
        """取得問題統計資料"""
        total = len(self.problems)
        by_status = {}
        by_type = {}
        by_severity = {}

        for problem in self.problems:
            status = problem.get('status', 'unknown')
            ptype = problem.get('problemType', 'unknown')
            severity = problem.get('severity', 'unknown')

            by_status[status] = by_status.get(status, 0) + 1
            by_type[ptype] = by_type.get(ptype, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # 計算有問題的場地數量
        venues_with_problems = len(set(p.get('venueId') for p in self.problems))

        return {
            'totalProblems': total,
            'venuesWithProblems': venues_with_problems,
            'byStatus': by_status,
            'byType': by_type,
            'bySeverity': by_severity,
        }

    def get_venue_history(self, venue_id: int) -> List[Dict]:
        """取得場地的問題歷史

        Args:
            venue_id: 場地 ID

        Returns:
            問題列表（按時間排序）
        """
        problems = [p for p in self.problems if p.get('venueId') == venue_id]
        problems.sort(key=lambda x: x.get('firstSeen', ''), reverse=True)
        return problems


# CLI 介面
def main():
    """命令列介面"""
    import argparse

    parser = argparse.ArgumentParser(description='問題追蹤系統')
    subparsers = parser.add_subparsers(dest='command', help='指令')

    # list 指令
    list_parser = subparsers.add_parser('list', help='列出問題')
    list_parser.add_argument('--venue', type=int, help='場地 ID')
    list_parser.add_argument('--status', help='狀態過濾')
    list_parser.add_argument('--type', help='問題類型過濾')
    list_parser.add_argument('--severity', help='嚴重程度過濾')

    # stats 指令
    subparsers.add_parser('stats', help='統計資料')

    # history 指令
    history_parser = subparsers.add_parser('history', help='場地問題歷史')
    history_parser.add_argument('venue', type=int, help='場地 ID')

    # mark 指令
    mark_parser = subparsers.add_parser('mark', help='標記問題狀態')
    mark_parser.add_argument('problem_id', help='問題 ID')
    mark_parser.add_argument('--status', required=True, choices=['fixed', 'wontfix', 'absent'], help='新狀態')
    mark_parser.add_argument('--reason', help='原因/說明')

    args = parser.parse_args()

    tracker = ProblemTracker()

    if args.command == 'list':
        problems = tracker.get_problems(
            venue_id=args.venue,
            status=args.status,
            problem_type=args.type,
            severity=args.severity
        )

        if not problems:
            print("沒有符合條件的問題")
            return

        print(f"\n找到 {len(problems)} 個問題:\n")
        for p in problems[:20]:  # 最多顯示 20 個
            status_mark = {
                'open': '⚠️',
                'diagnosing': '🔍',
                'fixing': '🔧',
                'fixed': '✅',
                'wontfix': '❌',
                'confirmed_absent': '⭕',
            }.get(p.get('status'), '?')

            print(f"{status_mark} [{p['id']}] {p['venueName']} (ID: {p['venueId']})")
            print(f"    類型: {p.get('problemType')} | 欄位: {p.get('field')}")
            print(f"    狀態: {p.get('status')} | 嚴重: {p.get('severity')}")
            print(f"    發生次數: {p.get('occurrences', 1)} | 最後: {p.get('lastSeen', '')[:10]}")
            if p.get('diagnosis'):
                print(f"    診斷: {p['diagnosis'][:100]}...")
            print()

        if len(problems) > 20:
            print(f"... 還有 {len(problems) - 20} 個問題")

    elif args.command == 'stats':
        stats = tracker.get_statistics()
        print("\n問題統計:")
        print(f"  總問題數: {stats['totalProblems']}")
        print(f"  有問題場地: {stats['venuesWithProblems']}")
        print(f"\n  按狀態:")
        for status, count in stats['byStatus'].items():
            print(f"    {status}: {count}")
        print(f"\n  按類型:")
        for ptype, count in stats['byType'].items():
            print(f"    {ptype}: {count}")
        print(f"\n  按嚴重程度:")
        for severity, count in stats['bySeverity'].items():
            print(f"    {severity}: {count}")

    elif args.command == 'history':
        problems = tracker.get_venue_history(args.venue)
        if not problems:
            print(f"場地 {args.venue} 沒有問題記錄")
            return

        venue_name = problems[0].get('venueName', 'Unknown')
        print(f"\n場地 {venue_name} (ID: {args.venue}) 的問題歷史:\n")

        for p in problems:
            print(f"  [{p.get('firstSeen', '')[:10]}] {p.get('problemType')} - {p.get('field')}")
            print(f"    狀態: {p.get('status')} | 發生次數: {p.get('occurrences', 1)}")
            if p.get('notes'):
                print(f"    備註: {p['notes'][:100]}...")
            print()

    elif args.command == 'mark':
        success = False
        if args.status == 'fixed':
            success = tracker.mark_fixed(args.problem_id, args.reason)
        elif args.status == 'wontfix':
            success = tracker.mark_wontfix(args.problem_id, args.reason)
        elif args.status == 'absent':
            success = tracker.mark_confirmed_absent(args.problem_id, args.reason)

        if success:
            print(f"問題 {args.problem_id} 已標記為 {args.status}")
        else:
            print(f"找不到問題 {args.problem_id}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
