#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/inquiry_generator.py - 場地詢問信生成器

輸入：場地 ID + 活動情境
輸出：email 範本（自動排除已有資料的問題）

用法：
    python tools/inquiry_generator.py --venue 1072 --scenario 研討會
    python tools/inquiry_generator.py --venue 1072 --scenario 研討會 --output email.txt
    python tools/inquiry_generator.py --list-scenarios
"""

import argparse
import json
import os
import sys
import io
from datetime import datetime

# Windows UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')
AI_KB_DIR = os.path.join(PROJECT_ROOT, 'ai_knowledge_base', 'venues')

sys.path.insert(0, PROJECT_ROOT)

from scraper.knowledge_config import (
    EVENT_SCENARIOS,
    QUESTION_CATEGORIES,
    FIELD_CHECKERS,
    get_all_questions,
    get_scenarios_list,
)


def load_venue(venue_id: int) -> dict:
    """從 venues.json 載入場地基本資料"""
    if not os.path.exists(VENUES_FILE):
        return None

    with open(VENUES_FILE, 'r', encoding='utf-8') as f:
        venues = json.load(f)

    for v in venues:
        if v.get('id') == venue_id:
            return v
    return None


def load_venue_ai_data(venue_id: int) -> dict:
    """載入 AI 知識庫資料"""
    path = os.path.join(AI_KB_DIR, f'{venue_id}.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def filter_answered_questions(questions: list, ai_data: dict) -> tuple:
    """
    過濾已有答案的問題
    返回 (pending_questions, answered_questions)
    """
    pending = []
    answered = []

    for q in questions:
        target_fields = q.get("targetFields", [])
        has_answer = False

        for field in target_fields:
            checker = FIELD_CHECKERS.get(field)
            if checker and checker(ai_data):
                has_answer = True
                break

        if has_answer:
            answered.append(q)
        else:
            pending.append(q)

    return pending, answered


def summarize_existing_knowledge(ai_data: dict) -> dict:
    """摘要已有知識（用於 email 開頭）"""
    summary = {}
    if not ai_data or not isinstance(ai_data, dict):
        return summary

    risks = ai_data.get("risks") or {}
    if risks.get("bookingLeadTime"):
        summary["bookingLeadTime"] = risks["bookingLeadTime"]

    rules_data = ai_data.get("rules") or {}
    if rules_data.get("catering"):
        rules = rules_data["catering"]
        if isinstance(rules, list) and rules:
            summary["catering"] = rules[0].get("rule", str(rules[0]))
        elif isinstance(rules, str):
            summary["catering"] = rules

    rooms_with_limitations = [
        r for r in ai_data.get("rooms", [])
        if r.get("limitations")
    ]
    if rooms_with_limitations:
        summary["limitationsCount"] = len(rooms_with_limitations)

    return summary


def build_email(
    venue: dict,
    scenario_config: dict,
    pending_questions: list,
    answered_questions: list,
    ai_data: dict,
) -> str:
    """組裝詢問信 email"""
    venue_name = venue.get("name", "貴場地")
    contact_email = venue.get("contactEmail", "")
    phone = venue.get("contactPhone") or venue.get("phone", "")
    capacity = scenario_config.get("defaultCapacity", {})

    lines = []

    # 主旨
    lines.append(f"主旨：關於在 貴場地舉辦{scenario_config['label']}的場地詢問")
    lines.append("")

    # 收件人
    if contact_email:
        lines.append(f"收件人：{contact_email}")
    elif phone:
        lines.append(f"電話洽詢：{phone}")
    lines.append("")

    # 開頭
    lines.append("您好，")
    lines.append("")
    cap_text = ""
    if capacity:
        cap_text = f"（約 {capacity['min']}-{capacity['max']} 人）"
    lines.append(
        f"我是活動企劃，正在評估在 貴場地（{venue_name}）"
        f"舉辦一場{scenario_config['label']}{cap_text}，"
        "有幾個問題想請教："
    )
    lines.append("")

    # 已知情識（簡短帶過）
    existing = summarize_existing_knowledge(ai_data)
    if existing:
        lines.append("【已知情識（請確認是否仍正確）】")
        for key, value in existing.items():
            if isinstance(value, str):
                lines.append(f"  - 我們了解：{value}")
        lines.append("")

    # 按分類群組問題
    categorized = {}
    for q in pending_questions:
        cat = q.get("category", "other")
        cat_label = QUESTION_CATEGORIES.get(cat, cat)
        categorized.setdefault(cat_label, []).append(q)

    for cat_label, questions in categorized.items():
        lines.append(f"【{cat_label}】")
        for i, q in enumerate(questions, 1):
            lines.append(f"  {i}. {q['text']}")
        lines.append("")

    # 結尾
    lines.append("期待您的回覆，謝謝！")
    lines.append("")
    lines.append("此致")
    lines.append("活動大師 場地研究團隊")
    lines.append(f"日期：{datetime.now().strftime('%Y-%m-%d')}")

    # 附件說明
    if answered_questions:
        lines.append("")
        lines.append("---")
        lines.append(f"（註：另有 {len(answered_questions)} 個問題我們已有資料，未列入詢問）")

    return '\n'.join(lines)


def generate_inquiry(venue_id: int, scenario: str) -> dict:
    """
    生成詢問信
    返回 dict 含所有生成資訊
    """
    # 載入場地資料
    venue = load_venue(venue_id)
    if not venue:
        return {"error": f"找不到場地 ID: {venue_id}"}

    # 載入情境
    scenario_config = EVENT_SCENARIOS.get(scenario)
    if not scenario_config:
        return {"error": f"找不到情境: {scenario}。可選: {get_scenarios_list()}"}

    # 載入 AI 知識庫
    ai_data = load_venue_ai_data(venue_id)

    # 過濾已回答的問題
    questions = scenario_config.get("questions", [])
    pending, answered = filter_answered_questions(questions, ai_data)

    # 生成 email
    email_draft = build_email(venue, scenario_config, pending, answered, ai_data)

    return {
        "venueId": venue_id,
        "venueName": venue.get("name", ""),
        "scenario": scenario,
        "totalQuestions": len(questions),
        "pendingCount": len(pending),
        "answeredCount": len(answered),
        "existingKnowledge": summarize_existing_knowledge(ai_data),
        "pendingQuestions": pending,
        "answeredQuestions": answered,
        "emailDraft": email_draft,
    }


def main():
    parser = argparse.ArgumentParser(description='場地詢問信生成器')
    parser.add_argument('--venue', type=int, default=None, help='場地 ID')
    parser.add_argument('--scenario', type=str, default=None, help='活動情境')
    parser.add_argument('--output', '-o', type=str, help='輸出檔案路徑')
    parser.add_argument('--list-scenarios', action='store_true', help='列出所有情境（不需 --venue/--scenario）')
    parser.add_argument('--json', action='store_true', help='輸出 JSON 格式')

    args = parser.parse_args()

    if args.list_scenarios:
        print("可用情境：")
        for name, config in EVENT_SCENARIOS.items():
            q_count = len(config.get("questions", []))
            print(f"  {name}: {config['description']} ({q_count} 題)")
        return

    if not args.venue or not args.scenario:
        parser.error("--venue 和 --scenario 為必填（除非使用 --list-scenarios）")

    result = generate_inquiry(args.venue, args.scenario)

    if "error" in result:
        print(f"[錯誤] {result['error']}")
        sys.exit(1)

    # 輸出
    if args.json:
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        # 人類可讀格式
        lines = [
            f"場地：{result['venueName']} (ID: {result['venueId']})",
            f"情境：{result['scenario']}",
            f"問題統計：{result['pendingCount']} 待問 / "
            f"{result['answeredCount']} 已有資料 / "
            f"{result['totalQuestions']} 總計",
            "",
            "=" * 60,
            "詢問信內容",
            "=" * 60,
            "",
            result["emailDraft"],
        ]
        output = '\n'.join(lines)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已寫入: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
