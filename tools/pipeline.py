#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/pipeline.py - Unified venue data pipeline CLI

Usage:
    python tools/pipeline.py audit [--venue ID]     # Check data quality
    python tools/pipeline.py estimate [--venue ID]   # Fill missing area/price
    python tools/pipeline.py validate [--venue ID]   # Check schema compliance
    python tools/pipeline.py fix [--venue ID]        # estimate + validate + sync
    python tools/pipeline.py sync                    # Sync taipei.json + bump DATA_VERSION
    python tools/pipeline.py deploy                  # Deploy to Vercel
    python tools/pipeline.py crawl ID                # Crawl official website (LLM)
    python tools/pipeline.py images ID              # Download images (LLM)
    python tools/pipeline.py knowledge [--venue ID]  # Extract knowledge (no LLM)

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


# ========== CLI ==========

def main():
    parser = argparse.ArgumentParser(description='Venue data pipeline')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # audit
    p_audit = subparsers.add_parser('audit', help='Audit data quality')
    p_audit.add_argument('--venue', type=int, default=None, help='Specific venue ID')

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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        'audit': cmd_audit,
        'estimate': cmd_estimate,
        'validate': cmd_validate,
        'fix': cmd_fix,
        'sync': cmd_sync,
        'deploy': cmd_deploy,
        'crawl': cmd_crawl,
        'images': cmd_images,
        'knowledge': cmd_knowledge,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
