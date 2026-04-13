#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/pipeline.py - Unified venue data pipeline CLI

Usage:
    python tools/pipeline.py audit [--venue ID]        # Check data quality
    python tools/pipeline.py sources [--venue ID]      # Audit data sources (new)
    python tools/pipeline.py estimate [--venue ID]     # Fill missing area/price
    python tools/pipeline.py validate [--venue ID]     # Check schema compliance
    python tools/pipeline.py fix [--venue ID]          # estimate + validate + sync
    python tools/pipeline.py sync                      # Sync taipei.json + bump DATA_VERSION
    python tools/pipeline.py deploy                    # Deploy to Vercel
    python tools/pipeline.py crawl ID                  # Crawl official website (LLM)
    python tools/pipeline.py images ID                # Download images (LLM)
    python tools/pipeline.py knowledge [--venue ID]    # Extract knowledge (no LLM)
    python tools/pipeline.py verify ID [--update]      # Verify data against official website

LLM role boundary:
    audit/estimate/validate/sync/deploy/knowledge = NO LLM needed (deterministic rules)
    crawl/images = NEEDS LLM (web understanding, image judgment)
    knowledge = NO LLM needed -- keyword-based extraction from PDFs/HTML
"""

import argparse
import json
import os
import sys
import io
import subprocess
from shutil import copy2
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.constants import VENUES_FILE, VENUES_TAIPEI_FILE
from tools.estimators import estimate_venue, estimate_room
from tools.validators import audit_venue, validate_venue, validate_room, fix_room
from tools.sync import sync_all, bump_version, check_consistency
from tools.problem_tracker import ProblemTracker
from tools.llm_diagnostic import LLMDiagnostic


# ========== Helpers ==========

def load_venues():
    """Load venues.json, return (data_list, raw_json)"""
    with open(VENUES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    venues = data if isinstance(data, list) else data.get('venues', [])
    return venues, data


def save_venues(venues, raw_data):
    """Save venues back to venues.json"""
    if raw_data and isinstance(raw_data, dict):
        raw_data['venues'] = venues
        out = raw_data
    else:
        out = venues
    with open(VENUES_FILE, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


def find_venue(venues, venue_id):
    """Find venue by ID (int or str)"""
    vid = int(venue_id) if isinstance(venue_id, str) else venue_id
    for v in venues:
        if v.get('id') == vid:
            return v
    return None


def backup_venues():
    """Create timestamped backup"""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{VENUES_FILE}.backup.{ts}"
    copy2(VENUES_FILE, backup_path)
    print(f"[backup] {backup_path}")


# ========== Commands ==========

def cmd_audit(args):
    """Audit data quality for all or specific venues"""
    venues, _ = load_venues()

    targets = venues
    if args.venue:
        v = find_venue(venues, args.venue)
        if not v:
            print(f"[error] Venue {args.venue} not found")
            return 1
        targets = [v]

    print(f"\n{'='*70}")
    print(f"AUDIT: {len(targets)} venues")
    print(f"{'='*70}\n")

    total_missing_area = 0
    total_missing_price = 0
    total_missing_img = 0
    total_schema = 0
    ok_count = 0
    issues_list = []

    for venue in targets:
        report = audit_venue(venue)
        is_ok = (report['missing_area'] == 0 and
                 report['missing_price'] == 0 and
                 report['missing_img'] == 0 and
                 report['schema_issues'] == 0)
        status = "OK" if is_ok else "!!"

        if is_ok:
            ok_count += 1
        else:
            issues_list.append(report)

        print(f"  {status:6s} | {venue.get('id', '?'):>5} | "
              f"{venue.get('name', '?'):20s} | "
              f"area={report['missing_area']:>2} price={report['missing_price']:>2} "
              f"img={report['missing_img']:>2} schema={report['schema_issues']:>2}")

    # Save report
    report_file = os.path.join(os.path.dirname(VENUES_FILE), 'audit_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'ok_count': ok_count,
            'total': len(targets),
            'total_missing_area': total_missing_area,
            'total_missing_price': total_missing_price,
            'total_missing_img': total_missing_img,
            'total_schema_issues': total_schema,
            'venues_with_issues': issues_list,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n[report] Saved to {report_file}")

    return 0


def cmd_sources(args):
    """Audit data sources for pricing"""
    import subprocess
    cmd = [sys.executable, 'tools/audit_data_sources.py']
    if args.venue:
        cmd.extend(['--venue', str(args.venue)])
    if args.verbose:
        cmd.append('-v')
    if args.fix:
        cmd.append('--fix')
    return subprocess.call(cmd)


def cmd_estimate(args):
    """Estimate missing area and pricing"""
    venues, raw = load_venues()
    backup_venues()

    targets = venues
    if args.venue:
        v = find_venue(venues, args.venue)
        if not v:
            print(f"[error] Venue {args.venue} not found")
            return 1
        targets = [v]

    print(f"\n{'='*50}")
    print(f"ESTIMATE: {len(targets)} venues")
    print(f"{'='*50}")
    total_fixed = 0

    for venue in targets:
        stats = estimate_venue(venue)
        if stats['rooms_fixed'] > 0:
            total_fixed += stats['rooms_fixed']
            print(f"  {venue.get('id')} {venue.get('name')}: "
                  f"area+{stats['area_added']} price+{stats['pricing_added']}")

    save_venues(venues, raw)
    print(f"\n[estimate] Fixed {total_fixed} rooms across {len(targets)} venues")

    return 0


def cmd_validate(args):
    """Validate schema compliance"""
    venues, _ = load_venues()

    targets = venues
    if args.venue:
        v = find_venue(venues, args.venue)
        if not v:
            print(f"[error] Venue {args.venue} not found")
            return 1
        targets = [v]

    print(f"\n{'='*70}")
    print(f"VALIDATE: {len(targets)} venues")
    print(f"{'='*70}")
    total_issues = 0

    for venue in targets:
        result = validate_venue(venue)
        if result['total_issues'] > 0:
            total_issues += result['total_issues']
            for issue in result['issues']:
                print(f"  {issue}")

    if total_issues == 0:
        print(f"[validate] All {len(targets)} venues pass validation")
        return 0
    else:
        print(f"\n[validate] {total_issues} issues found")
        return 1


def cmd_fix(args):
    """fix = estimate + validate + sync"""
    print("=" * 50)
    print("FIX: estimate + validate + sync")
    print("=" * 50)

    # Step 1: Estimate
    venues, raw = load_venues()
    backup_venues()

    targets = venues
    if args.venue:
        v = find_venue(venues, args.venue)
        if not v:
            print(f"[error] Venue {args.venue} not found")
            return 1
        targets = [v]

    print(f"\n--- Step 1: Estimate ---")
    print(f"FIX: {len(targets)} venues")

    total_fixed = 0
    for venue in targets:
        stats = estimate_venue(venue)
        if stats['rooms_fixed'] > 0:
            total_fixed += stats['rooms_fixed']
            print(f"  {venue.get('id')} {venue.get('name')}: "
                  f"area+{stats['area_added']} price+{stats['pricing_added']}")

    # Step 2: Auto-fix schema issues
    print("\n--- Step 2: Schema fixes ---")
    schema_fixed = 0
    for venue in targets:
        vid = venue.get('id', 0)
        for room in venue.get('rooms', []):
            fixes = fix_room(room, venue_id=vid)
            if fixes:
                schema_fixed += len(fixes)
                for fix in fixes:
                    print(f"  {room.get('id')}: {fix}")

    # Step 3: Validate
    print("\n--- Step 3: Validate ---")
    total_issues = 0
    for venue in targets:
        result = validate_venue(venue)
        total_issues += result['total_issues']

    if total_issues > 0:
        print(f"  [WARN] {total_issues} issues remain (manual fix needed)")
    else:
        print(f"  All clear")

    # Step 4: Save + Sync
    print("\n--- Step 4: Save + Sync ---")
    save_venues(venues, raw)
    sync_result = sync_all()

    print(f"\n{'='*50}")
    print(f"FIX COMPLETE")
    print(f"  Rooms estimated: {total_fixed}")
    print(f"  Schema fixes: {schema_fixed}")
    print(f"  Remaining issues: {total_issues}")
    print(f"  Version: {sync_result['version']}")
    print(f"{'='*50}")

    return 0 if total_issues == 0 else 1


def cmd_sync(args):
    """Bump DATA_VERSION + consistency check"""
    result = sync_all()
    issues = result.get('issues', [])
    print(f"\n[sync] Done. Version: {result['version']}")
    if issues:
        print(f"[sync] WARNING: {len(issues)} issues found")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    return 0


# ========== Scan command (爬蟲 + 查核 + 診斷) ==========

def cmd_scan(args):
    """
    完整掃描：爬蟲 → 查核 → 診斷

    整合爬蟲、驗證、來源稽核和 LLM 診斷的完整流程
    """
    from scraper.scraper import UnifiedScraper

    venues, raw = load_venues()

    if args.venue:
        v = find_venue(venues, args.venue)
        if not v:
            print(f"[error] Venue {args.venue} not found")
            return 1
        targets = [v]
    else:
        targets = venues

    tracker = ProblemTracker()
    diagnostic = None

    if args.use_llm:
        try:
            diagnostic = LLMDiagnostic()
        except ValueError as e:
            print(f"[警告] LLM 不可用: {e}")
            print("[scan] 將跳過 LLM 診斷步驟")

    print(f"\n{'='*60}")
    print(f"SCAN: {len(targets)} 個場地")
    print(f"{'='*60}\n")

    total_problems = 0
    new_problems = 0
    diagnosed = 0

    for venue in targets:
        venue_id = venue.get('id')
        venue_name = venue.get('name')

        print(f"\n--- {venue_name} (ID: {venue_id}) ---")

        # Step 1: Schema 驗證
        venue_result = validate_venue(venue)
        schema_issues = venue_result['total_issues']

        # Step 2: 來源稽核
        source_issues = 0
        for room in venue.get('rooms', []):
            source = room.get('source', '')
            if not source or 'regex' in source or 'compiled.js' in source:
                source_issues += 1

        # Step 3: 完整性檢查
        completeness_issues = 0
        if not venue.get('rooms'):
            tracker.record_problem(
                venue_id=venue_id,
                problem_type='missing_rooms',
                field='rooms',
                severity='critical',
                source='scan'
            )
            completeness_issues += 1
            total_problems += 1

        for room in venue.get('rooms', []):
            if not room.get('pricing') or not room.get('pricing').get('halfDay'):
                if not tracker.should_skip_diagnosis(venue_id, f"room.{room.get('id')}.pricing"):
                    tracker.record_problem(
                        venue_id=venue_id,
                        problem_type='missing_pricing',
                        field=f"room.{room.get('id')}.pricing",
                        severity='high',
                        source='scan'
                    )
                    completeness_issues += 1
                    total_problems += 1
                    new_problems += 1

        # Step 4: LLM 診斷新問題
        if diagnostic and new_problems > 0:
            print(f"  [LLM] 診斷 {new_problems} 個新問題...")
            problems = tracker.get_problems(venue_id=venue_id, status='open')
            for problem in problems[:5]:  # 最多診斷 5 個
                result = diagnostic.diagnose(
                    venue_id=venue_id,
                    problem_type=problem.get('problemType'),
                    field=problem.get('field')
                )
                if not result.get('error'):
                    tracker.record_problem(
                        venue_id=venue_id,
                        problem_type=problem.get('problemType'),
                        field=problem.get('field'),
                        diagnosis=result.get('reason'),
                        can_fix=result.get('canFix'),
                        fix_action=result.get('fixAction'),
                        source='llm_diagnostic'
                    )
                    diagnosed += 1

        # 總結
        venue_total = schema_issues + source_issues + completeness_issues
        if venue_total > 0:
            print(f"  Schema: {schema_issues}, 來源: {source_issues}, 完整性: {completeness_issues}")
        else:
            print(f"  ✓ 無問題")

    # 統計
    stats = tracker.get_statistics()
    print(f"\n{'='*60}")
    print(f"SCAN 完成")
    print(f"{'='*60}")
    print(f"  總問題: {total_problems}")
    print(f"  新問題: {new_problems}")
    print(f"  已診斷: {diagnosed}")
    print(f"  問題記錄: {stats['totalProblems']}")
    print(f"  有問題場地: {stats['venuesWithProblems']}")
    print(f"{'='*60}\n")

    return 0


# ========== Diagnose command ==========

def cmd_diagnose(args):
    """
    對已有問題執行 LLM 診斷

    使用問題追蹤器中的問題，執行 LLM 診斷
    """
    tracker = ProblemTracker()

    try:
        diagnostic = LLMDiagnostic()
    except ValueError as e:
        print(f"[錯誤] {e}")
        return 1

    if args.venue:
        # 診斷特定場地
        problems = tracker.get_problems(venue_id=args.venue, status=args.status)
    else:
        # 診斷所有問題
        problems = tracker.get_problems(status=args.status)

    if not problems:
        print("沒有需要診斷的問題")
        return 0

    # 過濾已診斷過的
    needs_diagnosis = [
        p for p in problems
        if not p.get('diagnosis') or p.get('canFix') is None
    ]

    if not needs_diagnosis:
        print("所有問題已診斷過")
        return 0

    if args.limit:
        needs_diagnosis = needs_diagnosis[:args.limit]

    print(f"診斷 {len(needs_diagnosis)} 個問題...\n")

    for problem in needs_diagnosis:
        venue_id = problem.get('venueId')
        problem_type = problem.get('problemType')
        field = problem.get('field')

        print(f"[{venue_id}] {field}...")

        result = diagnostic.diagnose(venue_id, problem_type, field)

        if result.get('error'):
            print(f"  ❌ {result.get('error')}")
        else:
            can_fix_mark = "✅ 可修復" if result.get('canFix') else "⭕ 不可修復"
            print(f"  {can_fix_mark} | 信心: {result.get('confidence', 0)}%")
            print(f"  原因: {result.get('reason', 'N/A')[:80]}...")

            # 更新問題追蹤器
            tracker.record_problem(
                venue_id=venue_id,
                problem_type=problem_type,
                field=field,
                diagnosis=result.get('reason'),
                can_fix=result.get('canFix'),
                fix_action=result.get('fixAction'),
                source='llm_diagnostic'
            )
        print()

    return 0


# ========== Problems command ==========

def cmd_problems(args):
    """
    查看/管理問題追蹤記錄

    列出問題、顯示統計、標記狀態
    """
    tracker = ProblemTracker()

    if args.stats:
        # 顯示統計
        stats = tracker.get_statistics()
        print("\n問題統計:")
        print(f"  總問題數: {stats['totalProblems']}")
        print(f"  有問題場地: {stats['venuesWithProblems']}")
        print(f"\n  按狀態:")
        for status, count in stats['byStatus'].items():
            status_name = STATUS_TYPES.get(status, status)
            print(f"    {status_name}: {count}")
        print(f"\n  按類型:")
        for ptype, count in stats['byType'].items():
            type_name = PROBLEM_TYPES.get(ptype, ptype)
            print(f"    {type_name}: {count}")
        return 0

    if args.history:
        # 顯示場地歷史
        problems = tracker.get_venue_history(args.history)
        if not problems:
            print(f"場地 {args.history} 沒有問題記錄")
            return 0

        venue_name = problems[0].get('venueName', 'Unknown')
        print(f"\n場地 {venue_name} (ID: {args.history}) 的問題歷史:\n")

        for p in problems:
            status_mark = {
                'open': '⚠️',
                'diagnosing': '🔍',
                'fixing': '🔧',
                'fixed': '✅',
                'wontfix': '❌',
                'confirmed_absent': '⭕',
            }.get(p.get('status'), '?')

            print(f"{status_mark} [{p.get('firstSeen', '')[:10]}] {p.get('problemType')} - {p.get('field')}")
            print(f"    狀態: {p.get('status')} | 發生: {p.get('occurrences', 1)} 次")
            if p.get('diagnosis'):
                print(f"    診斷: {p['diagnosis'][:100]}...")
            print()
        return 0

    # 標記問題狀態
    if args.mark:
        success = False
        if args.mark == 'fixed':
            success = tracker.mark_fixed(args.problem_id, args.reason)
        elif args.mark == 'wontfix':
            success = tracker.mark_wontfix(args.problem_id, args.reason)
        elif args.mark == 'absent':
            success = tracker.mark_confirmed_absent(args.problem_id, args.reason)

        if success:
            print(f"問題 {args.problem_id} 已標記為 {args.mark}")
        else:
            print(f"找不到問題 {args.problem_id}")
        return 0 if success else 1

    # 列出問題
    problems = tracker.get_problems(
        venue_id=args.venue,
        status=args.status,
        problem_type=args.type,
        severity=args.severity
    )

    if not problems:
        print("沒有符合條件的問題")
        return 0

    print(f"\n找到 {len(problems)} 個問題:\n")

    for p in problems[:30]:  # 最多顯示 30 個
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

        if p.get('diagnosis'):
            can_fix = "可修復" if p.get('canFix') else "不可修復"
            print(f"    診斷: {can_fix} | {p['diagnosis'][:80]}...")
        print()

    if len(problems) > 30:
        print(f"... 還有 {len(problems) - 30} 個問題")

    return 0


def cmd_deploy(args):
    """Deploy to Vercel"""
    print("[deploy] Running vercel --prod --yes...")
    result = subprocess.run(
        ['vercel', '--prod', '--yes'],
        cwd=os.path.dirname(VENUES_FILE),
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode


def cmd_crawl(args):
    """Crawl official website for precise data (placeholder for LLM)"""
    print(f"[crawl] Venue ID: {args.venue}")
    print("[crawl] This step requires LLM to:")
    print("  1. Visit the venue's official website")
    print("  2. Find meeting room data (PDF preferred)")
    print("  3. Extract structured data")
    print("  4. Run: python tools/pipeline.py fix <id>")
    print()
    print("Recommended: Use gstack to browse the website,")
    print("then update venues.json manually or via fix command.")
    return 0


def cmd_images(args):
    """Download venue images (placeholder for LLM)"""
    print(f"[images] Venue ID: {args.venue}")
    print("[images] This step requires LLM to:")
    print("  1. Find official images from venue website")
    print("  2. Download using python urllib")
    print("  3. Judge if images show meeting rooms (not guest rooms)")
    print("  4. Update venues.json with image URLs")
    return 0


# ========== Knowledge command ==========

def cmd_knowledge(args):
    """
    Extract knowledge (rules, limitations, loadIn, equipment specs)
    from PDFs and official websites.

    Default: output JSON to stdout (does NOT modify venues.json).
    Use --save to actually write results into venues.json.

    No LLM needed -- uses keyword-based KnowledgeExtractor.

    Modes:
      --venue ID          Extract from venue's website + known PDFs
      --venue ID --pdf F  Extract from a specific local PDF file
      (no args)           Extract from all venues that lack knowledge
      --save              Actually write to venues.json (default: stdout only)
    """
    from scraper.extractors import KnowledgeExtractor

    kx = KnowledgeExtractor()
    should_save = getattr(args, 'save', False)

    # --- Specific PDF file mode ---
    if args.pdf:
        if not args.venue:
            print("[error] --pdf requires --venue to know where to save results")
            return 1

        venues, raw = load_venues()
        venue = find_venue(venues, args.venue)
        if not venue:
            print(f"[error] Venue {args.venue} not found")
            return 1

        print(f"\n{'='*60}")
        print(f"KNOWLEDGE (PDF): {venue.get('name')} (ID: {venue['id']})")
        print(f"{'='*60}")

        try:
            import pdfplumber
            pdf = pdfplumber.open(args.pdf)
            full_text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
            pdf.close()
        except ImportError:
            print("[error] pdfplumber not installed: pip install pdfplumber")
            return 1
        except Exception as e:
            print(f"[error] Cannot read PDF: {e}")
            return 1

        knowledge = kx.extract_from_text(full_text)

        if should_save:
            _merge_knowledge_to_venue(venue, knowledge)
            save_venues(venues, raw)
            print(f"\n[knowledge] Done. Saved to venues.json")
        else:
            _print_knowledge_json(venue['id'], knowledge)

        return 0

    # --- Specific venue mode ---
    if args.venue:
        venues, raw = load_venues()
        venue = find_venue(venues, args.venue)
        if not venue:
            print(f"[error] Venue {args.venue} not found")
            return 1

        print(f"\n{'='*60}")
        print(f"KNOWLEDGE: {venue.get('name')} (ID: {venue['id']})")
        print(f"{'='*60}")

        knowledge = _collect_knowledge_for_venue(venue, kx)

        if should_save:
            _merge_knowledge_to_venue(venue, knowledge)
            save_venues(venues, raw)
            print(f"\n[knowledge] Done. Saved to venues.json")
        else:
            _print_knowledge_json(venue['id'], knowledge)

        return 0

    # --- Batch mode: extract from all venues that lack knowledge ---
    venues, raw = load_venues()
    results = []
    processed = 0

    for venue in venues:
        if not venue.get('active', True):
            continue

        has_rules = bool(venue.get('rules'))
        has_limitations = any(
            r.get('limitations') for r in venue.get('rooms', [])
        )
        if has_rules and has_limitations:
            continue

        print(f"\n{'='*60}")
        print(f"KNOWLEDGE: {venue.get('name', '?')} (ID: {venue.get('id')})")
        print(f"{'='*60}")

        knowledge = _collect_knowledge_for_venue(venue, kx)

        if should_save:
            _merge_knowledge_to_venue(venue, knowledge)

        results.append({
            'venueId': venue.get('id'),
            'venueName': venue.get('name', ''),
            'knowledge': knowledge,
        })
        processed += 1

    if should_save:
        save_venues(venues, raw)
        print(f"\n[knowledge] Processed {processed} venues. Saved to venues.json")
    else:
        print(f"\n{'='*60}")
        print(f"KNOWLEDGE EXTRACTION RESULTS ({processed} venues)")
        print(f"(dry-run mode: use --save to write to venues.json)")
        print(f"{'='*60}")
        for r in results:
            rules_count = sum(len(v) for v in r['knowledge'].get('rules', {}).values() if isinstance(v, list))
            lim_count = len(r['knowledge'].get('limitations', []))
            print(f"  {r['venueId']:>5} {r['venueName'][:30]:30s} rules={rules_count} limitations={lim_count}")

    return 0


def _print_knowledge_json(venue_id, knowledge):
    """Print extracted knowledge as JSON to stdout"""
    output = {
        "venueId": venue_id,
        "knowledge": knowledge,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def _collect_knowledge_for_venue(venue, kx):
    """Extract knowledge for a single venue from all available sources"""
    from scraper.knowledge_config import get_venue_pdfs
    from datetime import datetime

    url = venue.get('url', '')
    venue_name = venue.get('name', '')
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_knowledge = {
        "rules": {},
        "limitations": [],
        "loadIn": {},
        "equipmentDetails": [],
    }

    # Source 1: Local PDFs from LOCAL_PDF_MAP
    local_pdfs = get_venue_pdfs(venue.get('id'), project_root)
    for pdf_path in local_pdfs:
        print(f"  [PDF] Reading {os.path.basename(pdf_path)}...")
        try:
            import pdfplumber
            pdf = pdfplumber.open(pdf_path)
            full_text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
            pdf.close()
            if full_text.strip():
                source = {
                    "type": "pdf",
                    "file": os.path.basename(pdf_path),
                    "venue_url": url,
                    "extractedAt": datetime.now().strftime("%Y-%m-%d")
                }
                pdf_knowledge = kx.extract_from_text(full_text, source)
                _merge_knowledge_dicts(all_knowledge, pdf_knowledge)
                rules_count = sum(len(v) for v in pdf_knowledge.get('rules', {}).values())
                lim_count = len(pdf_knowledge.get('limitations', []))
                print(f"  [PDF] Got {rules_count} rules, {lim_count} limitations")
        except Exception as e:
            print(f"  [PDF] Error: {e}")

    # Source 2: Official website
    if url and url != 'TBD':
        print(f"  [HTML] Fetching {url}...")
        try:
            html_knowledge = kx.extract_from_html(url, venue_url=url)
            if html_knowledge:
                _merge_knowledge_dicts(all_knowledge, html_knowledge)
                print(f"  [HTML] Got: "
                      f"{sum(len(v) for v in html_knowledge.get('rules', {}).values())} rules, "
                      f"{len(html_knowledge.get('limitations', []))} limitations")
        except Exception as e:
            print(f"  [HTML] Error: {e}")

    # Source 3: Remote PDF links from venue data
    floor_plan = venue.get('floorPlan')
    if floor_plan and isinstance(floor_plan, str) and floor_plan.startswith('http'):
        print(f"  [PDF] Fetching floorPlan: {floor_plan}")
        try:
            pdf_knowledge = kx.extract_from_pdf(floor_plan, venue_url=url)
            if pdf_knowledge:
                _merge_knowledge_dicts(all_knowledge, pdf_knowledge)
                print(f"  [PDF] Got: "
                      f"{sum(len(v) for v in pdf_knowledge.get('rules', {}).values())} rules")
        except Exception as e:
            print(f"  [PDF] Error: {e}")

    # Source 4: Try common knowledge page URLs
    knowledge_paths = [
        '/meeting/notice', '/meeting/rules', '/meeting/faq',
        '/venue/rules', '/venue/notice', '/venue/faq',
        '/banquet/rules', '/banquet/notice',
        '/faq', '/notice', '/terms',
    ]
    if url and url != 'TBD':
        from urllib.parse import urlparse, urljoin
        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        for path in knowledge_paths:
            try_url = urljoin(base, path)
            print(f"  [PROBE] {try_url}...", end=' ')
            try:
                import requests as req
                r = req.get(try_url, timeout=8, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }, verify=False, allow_redirects=True)
                if r.status_code == 200 and len(r.text) > 500:
                    page_knowledge = kx.extract_from_html(try_url, venue_url=url)
                    if page_knowledge and (page_knowledge.get('rules') or page_knowledge.get('limitations')):
                        _merge_knowledge_dicts(all_knowledge, page_knowledge)
                        print(f"HIT - {sum(len(v) for v in page_knowledge.get('rules', {}).values())} rules")
                    else:
                        print("no knowledge")
                else:
                    print(f"{r.status_code}")
            except Exception:
                print("timeout")

    # Return collected knowledge (caller decides whether to save)
    if any(all_knowledge.values()):
        return all_knowledge
    else:
        print(f"  [RESULT] No knowledge extracted")
        return all_knowledge


def _merge_knowledge_dicts(target, source):
    """Merge source knowledge into target (non-destructive, add-only)"""
    # Rules: merge by category
    for cat, rules in source.get("rules", {}).items():
        if cat not in target["rules"]:
            target["rules"][cat] = []
        existing_texts = [
            r.get("rule", "") if isinstance(r, dict) else str(r)
            for r in target["rules"][cat]
        ]
        for rule in rules:
            rule_text = rule.get("rule", "") if isinstance(rule, dict) else str(rule)
            if rule_text and rule_text not in existing_texts:
                target["rules"][cat].append(rule)

    # Limitations: append unique
    for lim in source.get("limitations", []):
        if lim not in target["limitations"]:
            target["limitations"].append(lim)

    # LoadIn: merge keys
    for key, val in source.get("loadIn", {}).items():
        if val and key not in target["loadIn"]:
            target["loadIn"][key] = val

    # Equipment: append unique by name
    existing_names = [e.get("name") for e in target.get("equipmentDetails", [])]
    for eq in source.get("equipmentDetails", []):
        if eq.get("name") not in existing_names:
            target.setdefault("equipmentDetails", []).append(eq)


def _merge_knowledge_to_venue(venue, knowledge):
    """Merge extracted knowledge into a venue record in venues.json format"""

    # Venue-level rules
    if knowledge.get("rules"):
        existing_rules = venue.get("rules") or {}
        if not isinstance(existing_rules, dict):
            existing_rules = {}

        for cat, rules in knowledge["rules"].items():
            if cat not in existing_rules:
                existing_rules[cat] = []
            elif isinstance(existing_rules[cat], str):
                existing_rules[cat] = [{"rule": existing_rules[cat]}]

            existing_texts = [
                r.get("rule", "") if isinstance(r, dict) else str(r)
                for r in existing_rules[cat]
            ]
            for rule in rules:
                rule_text = rule.get("rule", "") if isinstance(rule, dict) else str(rule)
                if rule_text and rule_text not in existing_texts:
                    existing_rules[cat].append(rule)

        venue["rules"] = existing_rules

    # Venue-level limitations
    if knowledge.get("limitations"):
        existing = venue.get("limitations", [])
        if not isinstance(existing, list):
            existing = []
        for lim in knowledge["limitations"]:
            if lim not in existing:
                existing.append(lim)
        venue["limitations"] = existing

    # Venue-level loadIn
    if knowledge.get("loadIn"):
        existing = venue.get("loadIn", {})
        if not isinstance(existing, dict):
            existing = {}
        for key, val in knowledge["loadIn"].items():
            if val and key not in existing:
                existing[key] = val
        venue["loadIn"] = existing

    # Merge into rooms
    global_limitations = knowledge.get("limitations", [])
    global_loadin = knowledge.get("loadIn", {})
    global_equipment = knowledge.get("equipmentDetails", [])

    for room in venue.get("rooms", []):
        # Limitations
        if global_limitations:
            existing = room.get("limitations", [])
            if not isinstance(existing, list):
                existing = []
            for lim in global_limitations:
                if lim not in existing:
                    existing.append(lim)
            room["limitations"] = existing

        # LoadIn
        if global_loadin:
            existing_li = room.get("loadIn", {})
            if not isinstance(existing_li, dict) or not existing_li:
                room["loadIn"] = {
                    "elevator": global_loadin.get("elevatorCapacity", ""),
                    "vehicleAccess": None,
                    "loadingDock": global_loadin.get("loadingDock", ""),
                }
                if global_loadin.get("loadInTime"):
                    room["loadIn"]["loadInTime"] = global_loadin["loadInTime"]
                if global_loadin.get("loadOutTime"):
                    room["loadIn"]["loadOutTime"] = global_loadin["loadOutTime"]

        # Equipment details
        if global_equipment and room.get("equipment"):
            if isinstance(room["equipment"], list):
                name_map = {
                    "projector": "投影",
                    "screen": "投影",
                    "microphone": "麥克風",
                    "sound_system": "音響",
                    "lighting": "燈光",
                    "network": "網路",
                }
                for eq_detail in global_equipment:
                    eq_name = eq_detail.get("name", "")
                    spec = eq_detail.get("spec", "")
                    common_name = name_map.get(eq_name)
                    if common_name and spec:
                        for i, e in enumerate(room["equipment"]):
                            if common_name in str(e) and spec not in str(e):
                                room["equipment"][i] = f"{e}（{spec}）"
                                break


# ========== Verify command ==========

def cmd_verify(args):
    """
    Verify venue data against official website.

    Downloads and parses official website data, then compares
    with stored data to identify:
    - Data without official source
    - Data that doesn't match official info
    - Missing official data

    Use --file to test a specific venue file (e.g., corrected version).
    Use --update to replace stored data with official data.
    """
    venue_id = args.venue

    # If --file is specified, load from that file directly
    if args.file:
        import os
        file_path = args.file
        if not os.path.exists(file_path):
            print(f"[error] File not found: {file_path}")
            return 1
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Handle both direct venue object and {"venues": [...]} format
        if isinstance(data, list):
            venue = find_venue(data, venue_id)
        elif isinstance(data, dict) and 'venues' in data:
            venue = find_venue(data['venues'], venue_id)
        else:
            venue = data
        if not venue or venue.get('id') != int(venue_id):
            print(f"[error] File does not contain venue {venue_id}")
            return 1
    else:
        venues, raw = load_venues()
        venue = find_venue(venues, venue_id)

    if not venue:
        print(f"[error] Venue {venue_id} not found")
        return 1

    print(f"\n{'='*70}")
    print(f"VERIFY: {venue.get('name')} (ID: {venue_id})")
    print(f"{'='*70}\n")

    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime

    url = venue.get('url', '')
    if not url or url == 'TBD':
        print("[error] No website URL configured")
        return 1

    official_data = {
        'address': None,
        'phone': None,
        'email': None,
        'rooms': [],
        'rules': [],
        'pricing': [],
    }

    # Step 1: Scrape official website
    print("[Step 1] Downloading official data...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Try to find common venue pages
        pages_to_try = [
            url,
            url.replace('http://', 'https://'),
            url.rstrip('/') + '/meeting',
            url.rstrip('/') + '/conference',
            url.rstrip('/') + '/banquet',
            url.rstrip('/') + '/venue',
            url.rstrip('/') + '/about',
            url.rstrip('/') + '/contact',
        ]

        found_content = False
        for try_url in pages_to_try:
            try:
                page.goto(try_url, wait_until='domcontentloaded', timeout=15000)
                page.wait_for_timeout(2000)
                text = page.evaluate('() => document.body.innerText')

                if len(text) > 500:
                    print(f"  [OK] Fetched: {try_url}")

                    # Extract contact info - better phone pattern
                    phones = re.findall(r'0[2-9]-?\d{7,8}[\s#]*\d*', text)
                    if phones:
                        # Clean up phone numbers
                        clean_phones = []
                        for ph in phones:
                            ph = re.sub(r'[#\s].*', '', ph)  # Remove extension
                            if len(ph) >= 9:
                                clean_phones.append(ph)
                        if clean_phones:
                            official_data['phone'] = clean_phones[0]
                            print(f"  [Phone] {clean_phones[0]}")

                    # Look for address - better pattern matching
                    for line in text.split('\n'):
                        line = line.strip()
                        # Look for lines with address indicators but exclude announcements
                        if any(kw in line for kw in ['地址', 'Address']):
                            if len(line) > 10 and len(line) < 80:
                                # Must have typical address format
                                if re.search(r'[市縣].*[區鄉鎮市].*路', line):
                                    official_data['address'] = line
                                    print(f"  [Address] {line}")
                                    break

                    found_content = True
                    break
            except Exception as e:
                continue

        browser.close()

    if not found_content:
        print("[warn] Could not fetch official website")

    # Step 2: Compare with stored data
    print(f"\n[Step 2] Comparing with stored data...\n")

    issues = []

    # Compare address (normalize for comparison)
    stored_addr = venue.get('address', '')
    if official_data['address'] and stored_addr:
        # Remove postal code, normalize Chinese numbers
        def normalize_addr(addr):
            addr = addr.replace('地址', '').strip()  # Remove label first
            addr = re.sub(r'^\d{3,5}\s*', '', addr)  # Then remove postal code
            addr = addr.replace('一號', '1號').replace('二號', '2號').replace('三號', '3號')
            addr = re.sub(r'\s+', '', addr)  # Remove all spaces
            return addr

        if normalize_addr(stored_addr) != normalize_addr(official_data['address']):
            issues.append({
                'field': 'address',
                'stored': stored_addr,
                'official': official_data['address'],
                'match': False
            })

    # Compare phone
    stored_phone = venue.get('contact', {}).get('phone', '')
    if official_data['phone'] and stored_phone:
        # Normalize phone numbers
        def normalize_phone(phone):
            phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            return phone

        if normalize_phone(stored_phone) != normalize_phone(official_data['phone']):
            issues.append({
                'field': 'contact.phone',
                'stored': stored_phone,
                'official': official_data['phone'],
                'match': False
            })

    # Check for legacy rules
    legacy_rules = []
    for cat, rules in venue.get('rules', {}).items():
        for rule in rules if isinstance(rules, list) else []:
            if isinstance(rule, dict) and rule.get('source', {}).get('type') == 'legacy':
                legacy_rules.append({'category': cat, 'rule': rule.get('rule', '')})

    if legacy_rules:
        issues.append({
            'field': 'rules',
            'issue': 'legacy_source',
            'count': len(legacy_rules),
            'details': legacy_rules[:5]  # Show first 5
        })

    # Check for data without source
    no_source_fields = []
    if venue.get('risks') and not venue.get('risks', {}).get('source'):
        no_source_fields.append('risks')
    if venue.get('pricingTips'):
        no_source_fields.append('pricingTips')

    if no_source_fields:
        issues.append({
            'field': 'no_source',
            'fields': no_source_fields
        })

    # Step 3: Print report
    print(f"{'='*70}")
    print(f"VERIFICATION REPORT")
    print(f"{'='*70}\n")

    if issues:
        print(f"[ISSUES FOUND: {len(issues)}]\n")

        for i, issue in enumerate(issues, 1):
            if issue['field'] == 'address':
                print(f"{i}. Address mismatch:")
                print(f"   Stored: {issue['stored']}")
                print(f"   Official: {issue['official']}")
            elif issue['field'] == 'contact.phone':
                print(f"{i}. Phone mismatch:")
                print(f"   Stored: {issue['stored']}")
                print(f"   Official: {issue['official']}")
            elif issue['field'] == 'rules':
                print(f"{i}. Rules with 'legacy' source: {issue['count']} rules")
                for detail in issue['details']:
                    print(f"   - [{detail['category']}] {detail['rule'][:50]}...")
            elif issue['field'] == 'no_source':
                print(f"{i}. Fields without source: {', '.join(issue['fields'])}")
            print()

        if args.update:
            print(f"[--update flag: NOT IMPLEMENTED]")
            print(f"Please manually review and update data/venues/{venue_id}.json")
    else:
        print("[OK] All verified data matches official website")

    return 0


# ========== CLI ==========

def main():
    parser = argparse.ArgumentParser(description='Venue data pipeline')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # audit
    p_audit = subparsers.add_parser('audit', help='Audit data quality')
    p_audit.add_argument('--venue', type=int, default=None, help='Specific venue ID')

    # sources
    p_src = subparsers.add_parser('sources', help='Audit data sources')
    p_src.add_argument('--venue', type=int, default=None, help='Specific venue ID')
    p_src.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    p_src.add_argument('--fix', action='store_true', help='Auto-fix source tags')

    # estimate
    p_est = subparsers.add_parser('estimate', help='Estimate missing area/price')
    p_est.add_argument('--venue', type=int, default=None, help='Specific venue ID')

    # validate
    p_val = subparsers.add_parser('validate', help='Validate schema compliance')
    p_val.add_argument('--venue', type=int, default=None, help='Specific venue ID')

    # fix
    p_fix = subparsers.add_parser('fix', help='estimate + validate + sync')
    p_fix.add_argument('--venue', type=int, default=None, help='Specific venue ID')

    # sync
    subparsers.add_parser('sync', help='Sync taipei.json + bump DATA_VERSION')

    # deploy
    subparsers.add_parser('deploy', help='Deploy to Vercel')

    # crawl
    p_crawl = subparsers.add_parser('crawl', help='Crawl official website (LLM)')
    p_crawl.add_argument('venue', type=int, help='Venue ID')

    # images
    p_img = subparsers.add_parser('images', help='Download images (LLM)')
    p_img.add_argument('venue', type=int, help='Venue ID')

    # knowledge
    p_know = subparsers.add_parser('knowledge', help='Extract knowledge from PDFs/HTML')
    p_know.add_argument('--venue', type=int, default=None, help='Specific venue ID')
    p_know.add_argument('--pdf', type=str, default=None, help='Specific PDF file path')
    p_know.add_argument('--save', action='store_true', default=False,
                        help='Actually write to venues.json (default: stdout only)')

    # verify
    p_verify = subparsers.add_parser('verify', help='Verify data against official website')
    p_verify.add_argument('venue', type=int, help='Venue ID')
    p_verify.add_argument('--file', type=str, default=None,
                          help='Test specific venue file instead of venues.json')
    p_verify.add_argument('--update', action='store_true', default=False,
                          help='Update stored data with official data')

    # scan
    p_scan = subparsers.add_parser('scan', help='完整掃描：爬蟲 + 查核 + 診斷')
    p_scan.add_argument('--venue', type=int, default=None, help='Specific venue ID')
    p_scan.add_argument('--use-llm', action='store_true', default=False, help='使用 LLM 診斷')

    # diagnose
    p_diag = subparsers.add_parser('diagnose', help='對已有問題執行 LLM 診斷')
    p_diag.add_argument('--venue', type=int, default=None, help='Specific venue ID')
    p_diag.add_argument('--status', default='open', help='Problem status filter')
    p_diag.add_argument('--limit', type=int, default=10, help='Max problems to diagnose')

    # problems
    p_probs = subparsers.add_parser('problems', help='查看/管理問題追蹤記錄')
    p_probs.add_argument('--venue', type=int, default=None, help='Filter by venue ID')
    p_probs.add_argument('--status', help='Filter by status')
    p_probs.add_argument('--type', help='Filter by problem type')
    p_probs.add_argument('--severity', help='Filter by severity')
    p_probs.add_argument('--stats', action='store_true', help='Show statistics')
    p_probs.add_argument('--history', type=int, help='Show venue problem history')
    p_probs.add_argument('--mark', choices=['fixed', 'wontfix', 'absent'], help='Mark problem status')
    p_probs.add_argument('--problem-id', help='Problem ID (for --mark)')
    p_probs.add_argument('--reason', help='Reason/notes (for --mark)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        'audit': cmd_audit,
        'sources': cmd_sources,
        'estimate': cmd_estimate,
        'validate': cmd_validate,
        'fix': cmd_fix,
        'sync': cmd_sync,
        'deploy': cmd_deploy,
        'crawl': cmd_crawl,
        'images': cmd_images,
        'knowledge': cmd_knowledge,
        'verify': cmd_verify,
        'scan': cmd_scan,
        'diagnose': cmd_diagnose,
        'problems': cmd_problems,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
