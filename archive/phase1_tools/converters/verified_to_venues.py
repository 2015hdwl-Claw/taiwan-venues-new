#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert verified.json to venues.json

將驗證資料轉換為最終資料庫格式，加入新架構欄位

新增欄位:
- sourceId: 來源 ID (對應 sources.json)
- qualityScore: 品質分數 (0-100)
- lastVerified: 最後驗證時間
- metadata: 擴展元數據
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import shutil


def convert_verified_to_venues(
    verified_file: str = 'data/verified.json',
    venues_file: str = 'venues.json',
    backup: bool = True
) -> List[Dict]:
    """
    Convert verified.json to venues.json format

    Args:
        verified_file: Path to verified.json
        venues_file: Path to venues.json
        backup: Whether to backup existing venues.json

    Returns:
        List of venue dictionaries
    """
    print("="*80)
    print("Converting verified.json to venues.json")
    print("="*80)
    print()

    # Backup existing venues.json
    if backup:
        venues_path = Path(venues_file)
        if venues_path.exists():
            # Calculate hash for backup name
            with open(venues_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:8]

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"venues_before_verified_{timestamp}_{file_hash}.json"
            backup_path = Path('data/backups') / backup_name
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(venues_path, backup_path)
            print(f"Backup created: {backup_path}")
            print()

    # Load verified data
    print(f"Loading {verified_file}...")
    with open(verified_file, 'r', encoding='utf-8') as f:
        verified_db = json.load(f)

    print(f"Loaded {len(verified_db['data'])} verified entries")
    print()

    # Convert to venues format
    venues = []
    updated_count = 0
    new_count = 0

    for verified_entry in verified_db['data']:
        venue = verified_entry['data'].copy()

        # Add new architecture fields
        venue['sourceId'] = verified_entry['sourceId']
        venue['qualityScore'] = verified_entry['qualityScore']
        venue['lastVerified'] = verified_db['verifiedAt']

        # Update metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}

        venue['metadata'].update({
            'verifiedAt': verified_db['verifiedAt'],
            'qualityScore': verified_entry['qualityScore'],
            'verificationPassed': verified_entry['verification']['passed'],
            'completeness': verified_entry['completeness'],
            'dataFlow': 'sources → raw → verified → venues',
            'verificationChecks': verified_entry['verification']['checks'],
            'verificationIssues': verified_entry['verification']['issues'],
            'verificationWarnings': verified_entry['verification']['warnings']
        })

        venues.append(venue)
        updated_count += 1

    # Save
    print(f"Saving to {venues_file}...")
    with open(venues_file, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print()
    print("="*80)
    print("Conversion Complete")
    print("="*80)
    print()
    print(f"Total venues: {len(venues)}")
    print(f"Updated: {updated_count}")
    print()
    print(f"Output: {venues_file}")

    return venues


def show_diff(venues_file: str = 'venues.json'):
    """
    Show differences between old and new venues.json

    Args:
        venues_file: Path to venues.json
    """
    print()
    print("="*80)
    print("New Architecture Fields")
    print("="*80)
    print()

    # Load a sample venue
    with open(venues_file, 'r', encoding='utf-8') as f:
        venues = json.load(f)

    if not venues:
        print("No venues found")
        return

    sample = venues[0]

    print(f"Sample Venue: {sample.get('name')} (ID: {sample.get('id')})")
    print()
    print("New Fields:")
    print(f"  sourceId: {sample.get('sourceId')}")
    print(f"  qualityScore: {sample.get('qualityScore')}")
    print(f"  lastVerified: {sample.get('lastVerified')}")
    print()
    print("Updated Metadata:")
    metadata = sample.get('metadata', {})
    for key in ['verifiedAt', 'qualityScore', 'verificationPassed', 'dataFlow']:
        if key in metadata:
            print(f"  {key}: {metadata[key]}")


if __name__ == '__main__':
    # Convert
    venues = convert_verified_to_venues()

    # Show new fields
    show_diff()

    print()
    print("Next steps:")
    print("  1. Review converted data")
    print("  2. Test with scrapers")
    print("  3. Update sources.json if needed")
