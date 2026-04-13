#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/llm_diagnostic.py - LLM 診斷器

使用 LLM 分析資料不完整的原因，
判斷是否可修復並提供修復建議
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI

# 專案路徑
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')


class LLMDiagnostic:
    """LLM 診斷器"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """初始化 LLM 客戶端

        Args:
            api_key: API Key，預設從環境變數 CLASSIFIER_API_KEY 讀取
            base_url: API 端點，預設從環境變數 CLASSIFIER_BASE_URL 讀取
            model: 模型名稱，預設為 glm-4.7-flash
        """
        # 從環境變數讀取配置
        api_key = api_key or os.getenv('CLASSIFIER_API_KEY')
        base_url = base_url or os.getenv('CLASSIFIER_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/')
        model = model or os.getenv('CLASSIFIER_MODEL', 'glm-4.7-flash')

        if not api_key:
            raise ValueError("缺少 API Key，請設定 CLASSIFIER_API_KEY 環境變數")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def _load_venue(self, venue_id: int) -> Optional[Dict]:
        """載入場地資料"""
        if not os.path.exists(VENUES_FILE):
            return None

        with open(VENUES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            venues = data if isinstance(data, list) else data.get('venues', [])
            return next((v for v in venues if v.get('id') == venue_id), None)

    def _build_prompt(
        self,
        venue: Dict,
        problem_type: str,
        field: str,
        scrape_report: Dict = None
    ) -> str:
        """建立診斷 Prompt"""

        venue_name = venue.get('name', 'Unknown')
        venue_id = venue.get('id')
        venue_url = venue.get('url', '')

        prompt = f"""你是場地資料爬蟲專家。請分析以下資料不完整問題並給出診斷。

場地：{venue_name} (ID: {venue_id})
官網：{venue_url}
問題：{field} 資料缺失

"""

        # 加入爬蟲報告（如果有）
        if scrape_report:
            prompt += f"""爬蟲報告：
- HTTP 狀態：{scrape_report.get('httpStatus', 'N/A')}
- 提取策略：{scrape_report.get('extractionStrategy', 'N/A')}
- 是否動態網站：{scrape_report.get('isDynamic', 'N/A')}
- JS 框架：{scrape_report.get('jsFrameworks', 'N/A')}
- 發現頁面數：{len(scrape_report.get('discoveredPages', []))}
- 提取會議室數：{scrape_report.get('rooms', 0)}

"""

        prompt += """請分析並回答以下問題：

1. 為什麼沒有提取到此資料？
2. 這個資料是否可能存在於官網的其他位置？
3. 如果存在，爬蟲應該如何改進才能提取到？
4. 如果不存在，請說明為什麼確定官網沒有此資料

請以 JSON 格式回答：
{
  "reason": "原因說明",
  "canFix": true/false,
  "fixAction": "具體修復建議（如果可以修復）",
  "confidence": 0-100（判斷信心度）
}

注意：
- canFix = true 表示問題可以透過改進爬蟲來解決
- canFix = false 表示官網確實沒有此資料，無法透過爬蟲取得
- confidence >= 80 表示高信心判斷，< 80 表示不確定
"""

        return prompt

    def diagnose(
        self,
        venue_id: int,
        problem_type: str,
        field: str,
        scrape_report: Dict = None
    ) -> Dict:
        """執行單一問題診斷

        Args:
            venue_id: 場地 ID
            problem_type: 問題類型
            field: 欄位名稱
            scrape_report: 爬蟲報告（可選）

        Returns:
            診斷結果
        """
        venue = self._load_venue(venue_id)
        if not venue:
            return {
                'error': f'找不到場地 {venue_id}',
                'reason': '場地不存在',
                'canFix': False,
                'confidence': 0
            }

        prompt = self._build_prompt(venue, problem_type, field, scrape_report)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是場地資料爬蟲專家，負責診斷資料缺失問題。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # 加入診斷元資料
            result['diagnosedAt'] = datetime.now().isoformat()
            result['venueId'] = venue_id
            result['field'] = field
            result['problemType'] = problem_type

            return result

        except Exception as e:
            return {
                'error': str(e),
                'reason': f'LLM 診斷失敗: {e}',
                'canFix': None,
                'confidence': 0
            }

    def batch_diagnose(
        self,
        problems: List[Dict],
        max_concurrent: int = 3
    ) -> List[Dict]:
        """批次診斷多個問題

        Args:
            problems: 問題列表，每個問題包含 venueId, problemType, field
            max_concurrent: 最大並發數

        Returns:
            診斷結果列表
        """
        results = []

        for i, problem in enumerate(problems):
            venue_id = problem.get('venueId')
            problem_type = problem.get('problemType')
            field = problem.get('field')

            print(f"[{i+1}/{len(problems)}] 診斷場地 {venue_id} 的 {field} 問題...")

            result = self.diagnose(venue_id, problem_type, field)
            results.append(result)

        return results

    def diagnose_from_tracker(
        self,
        tracker,
        status: str = 'open',
        limit: int = 10
    ) -> List[Dict]:
        """從問題追蹤器取得問題並診斷

        Args:
            tracker: ProblemTracker 實例
            status: 問題狀態過濾
            limit: 最多診斷數量

        Returns:
            診斷結果列表
        """
        # 取得待診斷的問題
        problems = tracker.get_problems(status=status, limit=limit)

        # 過濾已診斷過的問題
        needs_diagnosis = [
            p for p in problems
            if not p.get('diagnosis') or p.get('canFix') is None
        ]

        if not needs_diagnosis:
            print("沒有需要診斷的問題")
            return []

        print(f"找到 {len(needs_diagnosis)} 個需要診斷的問題")

        # 執行批次診斷
        results = []
        for problem in needs_diagnosis:
            venue_id = problem.get('venueId')
            problem_type = problem.get('problemType')
            field = problem.get('field')

            print(f"診斷場地 {venue_id} 的 {field} 問題...")

            result = self.diagnose(venue_id, problem_type, field)

            # 更新問題追蹤器
            if not result.get('error'):
                tracker.record_problem(
                    venue_id=venue_id,
                    problem_type=problem_type,
                    field=field,
                    diagnosis=result.get('reason'),
                    can_fix=result.get('canFix'),
                    fix_action=result.get('fixAction'),
                    source='llm_diagnostic'
                )

            results.append({
                'problem': problem,
                'diagnosis': result
            })

        return results


# CLI 介面
def main():
    """命令列介面"""
    import argparse

    parser = argparse.ArgumentParser(description='LLM 診斷器')
    subparsers = parser.add_subparsers(dest='command', help='指令')

    # diagnose 指令
    diag_parser = subparsers.add_parser('diagnose', help='診斷單一問題')
    diag_parser.add_argument('--venue', type=int, required=True, help='場地 ID')
    diag_parser.add_argument('--field', required=True, help='欄位名稱')
    diag_parser.add_argument('--type', default='missing', help='問題類型')

    # batch 指令
    batch_parser = subparsers.add_parser('batch', help='批次診斷')
    batch_parser.add_argument('--status', default='open', help='問題狀態過濾')
    batch_parser.add_argument('--limit', type=int, default=10, help='最多診斷數量')

    # from-tracker 指令
    tracker_parser = subparsers.add_parser('from-tracker', help='從問題追蹤器診斷')
    tracker_parser.add_argument('--status', default='open', help='問題狀態過濾')
    tracker_parser.add_argument('--limit', type=int, default=10, help='最多診斷數量')

    args = parser.parse_args()

    try:
        diagnostic = LLMDiagnostic()
    except ValueError as e:
        print(f"錯誤: {e}")
        print("\n請設定環境變數：")
        print("  export CLASSIFIER_API_KEY=your_api_key")
        print("  export CLASSIFIER_BASE_URL=https://open.bigmodel.cn/api/paas/v4/")
        return 1

    if args.command == 'diagnose':
        result = diagnostic.diagnose(
            venue_id=args.venue,
            problem_type=args.type,
            field=args.field
        )

        print("\n診斷結果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'from-tracker':
        from problem_tracker import ProblemTracker

        tracker = ProblemTracker()
        results = diagnostic.diagnose_from_tracker(
            tracker=tracker,
            status=args.status,
            limit=args.limit
        )

        print(f"\n完成 {len(results)} 個問題的診斷:\n")
        for r in results:
            problem = r['problem']
            diagnosis = r['diagnosis']

            if diagnosis.get('error'):
                print(f"❌ [{problem['venueName']}] {problem['field']}")
                print(f"   錯誤: {diagnosis.get('error')}")
            else:
                can_fix_mark = "✅ 可修復" if diagnosis.get('canFix') else "⭕ 不可修復"
                print(f"✓ [{problem['venueName']}] {problem['field']}")
                print(f"   {can_fix_mark} | 信心度: {diagnosis.get('confidence', 0)}%")
                print(f"   原因: {diagnosis.get('reason', 'N/A')[:100]}...")
                if diagnosis.get('fixAction'):
                    print(f"   建議: {diagnosis['fixAction'][:100]}...")
            print()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
