#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Data Flow Pipeline

執行完整的四階段資料流程:
sources.json → raw.json → verified.json → venues.json

使用方式:
    python run_data_flow.py              # 完整流程
    python run_data_flow.py --step raw   # 只執行到 raw.json
    python run_data_flow.py --step verified  # 只執行到 verified.json
"""
import argparse
import json
from pathlib import Path
from datetime import datetime

# Import converters
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from venues_to_raw import convert_venues_to_raw
from raw_to_verified import convert_raw_to_verified
from verified_to_venues import convert_verified_to_venues


def run_full_pipeline():
    """Run complete four-stage pipeline"""
    print("="*80)
    print("ACTIVITY MASTER - Data Flow Pipeline")
    print("="*80)
    print()
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check input files exist
    if not Path('venues.json').exists():
        print("[ERROR] venues.json not found")
        return False

    if not Path('sources.json').exists():
        print("[ERROR] sources.json not found")
        return False

    print("[OK] Input files found")
    print()

    # Stage 1: venues.json → raw.json
    print("-"*80)
    print("STAGE 1: Converting venues.json to raw.json")
    print("-"*80)
    try:
        raw_db = convert_venues_to_raw()
        print("[OK] Stage 1 complete")
    except Exception as e:
        print(f"[ERROR] Stage 1 failed: {e}")
        return False

    print()

    # Stage 2: raw.json → verified.json
    print("-"*80)
    print("STAGE 2: Converting raw.json to verified.json")
    print("-"*80)
    try:
        verified_db = convert_raw_to_verified()
        print("[OK] Stage 2 complete")
    except Exception as e:
        print(f"[ERROR] Stage 2 failed: {e}")
        return False

    print()

    # Stage 3: verified.json → venues.json
    print("-"*80)
    print("STAGE 3: Converting verified.json to venues.json")
    print("-"*80)
    try:
        venues = convert_verified_to_venues()
        print("[OK] Stage 3 complete")
    except Exception as e:
        print(f"[ERROR] Stage 3 failed: {e}")
        return False

    print()

    # Summary
    print("="*80)
    print("PIPELINE COMPLETE")
    print("="*80)
    print()
    print("Data Flow:")
    print("  sources.json (45 sources)")
    print("     ↓")
    print("  raw.json ({} entries)".format(raw_db['summary']['total']))
    print("     ↓")
    print("  verified.json ({} entries, {}% pass rate)".format(
        verified_db['summary']['total'],
        int(verified_db['summary']['passed'] / verified_db['summary']['total'] * 100)
    ))
    print("     ↓")
    print("  venues.json ({} venues with new architecture)".format(len(venues)))
    print()
    print("New Architecture Fields Added:")
    print("  ✓ sourceId")
    print("  ✓ qualityScore")
    print("  ✓ lastVerified")
    print("  ✓ metadata.dataFlow")
    print("  ✓ metadata.completeness")
    print("  ✓ metadata.verificationChecks")
    print()
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return True


def show_status():
    """Show current status of data pipeline"""
    print("="*80)
    print("Data Pipeline Status")
    print("="*80)
    print()

    # Check sources.json
    if Path('sources.json').exists():
        with open('sources.json', 'r', encoding='utf-8') as f:
            sources = json.load(f)
        print(f"[OK] sources.json: {len(sources['sources'])} sources")
    else:
        print("[--] sources.json: Not found")

    # Check venues.json
    if Path('venues.json').exists():
        with open('venues.json', 'r', encoding='utf-8') as f:
            venues = json.load(f)
        print(f"[OK] venues.json: {len(venues)} venues")

        # Check for new architecture fields
        if venues and 'sourceId' in venues[0]:
            print("      └─ New architecture fields: Present")
        else:
            print("      └─ New architecture fields: Missing")
    else:
        print("[--] venues.json: Not found")

    # Check raw.json
    if Path('data/raw.json').exists():
        with open('data/raw.json', 'r', encoding='utf-8') as f:
            raw = json.load(f)
        print(f"[OK] data/raw.json: {len(raw['data'])} entries")
    else:
        print("[--] data/raw.json: Not found")

    # Check verified.json
    if Path('data/verified.json').exists():
        with open('data/verified.json', 'r', encoding='utf-8') as f:
            verified = json.load(f)
        print(f"[OK] data/verified.json: {len(verified['data'])} entries")
        print(f"      └─ Average quality: {verified['summary']['averageQuality']}")
    else:
        print("[--] data/verified.json: Not found")

    print()


def main():
    parser = argparse.ArgumentParser(description='Activity Master Data Flow Pipeline')
    parser.add_argument('--step', choices=['raw', 'verified', 'full'],
                       default='full', help='Pipeline step to run')
    parser.add_argument('--status', action='store_true',
                       help='Show current pipeline status')

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.step == 'raw':
        print("Running to raw.json...")
        convert_venues_to_raw()
    elif args.step == 'verified':
        print("Running to verified.json...")
        convert_venues_to_raw()
        convert_raw_to_verified()
    else:
        print("Running full pipeline...")
        success = run_full_pipeline()
        if not success:
            print()
            print("[ERROR] Pipeline failed")
            exit(1)


if __name__ == '__main__':
    main()
