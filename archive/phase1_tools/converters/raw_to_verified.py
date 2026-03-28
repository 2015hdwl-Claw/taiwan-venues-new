#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert raw.json to verified.json

驗證初步資料並建立驗證資料庫 (verified.json)

Verified 格式:
{
  "version": "1.0",
  "verifiedAt": "2026-03-26T11:00:00",
  "verifier": "raw_to_verified.py",
  "data": [
    {
      "id": 1128,
      "sourceId": 1128,
      "name": "集思台大會議中心",
      "qualityScore": 85,
      "completeness": {
        "basicInfo": true,
        "rooms": true,
        "capacity": true,
        "area": true,
        "price": false,
        "transportation": true,
        "images": false
      },
      "verification": {
        "passed": true,
        "checks": [...],
        "issues": [],
        "warnings": [...]
      },
      "data": {...}
    }
  ]
}
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import sys
import os

# Add parent directory to path to import validator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_validator import DataValidator


def calculate_completeness(venue: Dict) -> Dict[str, bool]:
    """
    Calculate venue completeness

    Args:
        venue: Venue dictionary

    Returns:
        Completeness dictionary
    """
    completeness = {}

    # Basic info
    completeness['basicInfo'] = all([
        venue.get('name'),
        venue.get('venueType'),
        venue.get('address'),
        venue.get('url')
    ])

    # Rooms
    rooms = venue.get('rooms', [])
    completeness['rooms'] = len(rooms) > 0

    # Capacity
    has_capacity = False
    if venue.get('capacity'):
        has_capacity = True
    else:
        for room in rooms:
            if room.get('capacity'):
                has_capacity = True
                break
    completeness['capacity'] = has_capacity

    # Area
    has_area = False
    for room in rooms:
        if room.get('area'):
            has_area = True
            break
    completeness['area'] = has_area

    # Price
    has_price = False
    for room in rooms:
        if room.get('price'):
            has_price = True
            break
    completeness['price'] = has_price

    # Transportation
    completeness['transportation'] = bool(venue.get('traffic'))

    # Images
    completeness['images'] = bool(venue.get('images'))

    return completeness


def calculate_quality_score(completeness: Dict[str, bool], warnings: List[str]) -> int:
    """
    Calculate quality score (0-100)

    Args:
        completeness: Completeness dictionary
        warnings: List of warnings

    Returns:
        Quality score
    """
    # Base score from completeness
    weights = {
        'basicInfo': 20,
        'rooms': 20,
        'capacity': 15,
        'area': 10,
        'price': 15,
        'transportation': 10,
        'images': 10
    }

    score = 0
    for key, present in completeness.items():
        if present:
            score += weights[key]

    # Deduct for warnings
    score -= min(len(warnings) * 5, 20)

    return max(0, min(100, score))


def convert_raw_to_verified(
    raw_file: str = 'data/raw.json',
    output_file: str = 'data/verified.json'
) -> Dict:
    """
    Convert raw.json to verified.json with validation

    Args:
        raw_file: Path to raw.json
        output_file: Path to output verified.json

    Returns:
        Verified database dictionary
    """
    print("="*80)
    print("Converting raw.json to verified.json")
    print("="*80)
    print()

    # Load raw data
    print(f"Loading {raw_file}...")
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_db = json.load(f)

    print(f"Loaded {len(raw_db['data'])} entries")
    print()

    # Initialize validator
    validator = DataValidator(strict=False)

    # Verify each entry
    verified_entries = []
    passed_count = 0
    failed_count = 0
    warning_count = 0

    for raw_entry in raw_db['data']:
        venue = raw_entry['data']
        venue_id = venue.get('id')
        venue_name = venue.get('name', 'Unknown')

        # Don't print venue name to avoid encoding issues
        print(f"Verifying venue {venue_id}...")

        # Validate venue
        is_valid, errors, warnings = validator.validate_venue(venue)

        # Calculate completeness
        completeness = calculate_completeness(venue)

        # Calculate quality score
        entry_warnings = raw_entry.get('warnings', [])
        all_warnings = warnings + entry_warnings
        quality_score = calculate_quality_score(completeness, all_warnings)

        # Build verification record
        checks = []
        if completeness['basicInfo']:
            checks.append('has_basic_info')
        if venue.get('contact', {}).get('phone'):
            checks.append('has_phone')
        if venue.get('contact', {}).get('email'):
            checks.append('has_email')
        if completeness['rooms']:
            checks.append('has_rooms')
        if completeness['capacity']:
            checks.append('has_capacity')

        verified_entry = {
            "id": venue_id,
            "sourceId": raw_entry['sourceId'],
            "name": venue_name,
            "qualityScore": quality_score,
            "completeness": completeness,
            "verification": {
                "passed": is_valid,
                "checks": checks,
                "issues": errors,
                "warnings": all_warnings
            },
            "data": venue
        }

        verified_entries.append(verified_entry)

        if is_valid:
            passed_count += 1
            print(f"  [PASS] Score: {quality_score}")
        else:
            failed_count += 1
            # Don't print error details to avoid encoding issues
            print(f"  [FAIL] {len(errors)} error(s)")

        if all_warnings:
            warning_count += 1
            # Don't print warning details
            print(f"  [WARN] {len(all_warnings)} warning(s)")

        # Only print progress every 10 venues
        if venue_id % 10 == 0:
            print()

    # Build verified database
    verified_db = {
        "version": "1.0",
        "verifiedAt": datetime.now().isoformat(),
        "verifier": "raw_to_verified.py",
        "data": verified_entries,
        "summary": {
            "total": len(verified_entries),
            "passed": passed_count,
            "failed": failed_count,
            "withWarnings": warning_count,
            "averageQuality": sum(e['qualityScore'] for e in verified_entries) // len(verified_entries) if verified_entries else 0
        }
    }

    # Create output directory
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verified_db, f, ensure_ascii=False, indent=2)

    print()
    print("="*80)
    print("Verification Complete")
    print("="*80)
    print()
    print(f"Total venues: {verified_db['summary']['total']}")
    print(f"Passed: {verified_db['summary']['passed']}")
    print(f"Failed: {verified_db['summary']['failed']}")
    print(f"With warnings: {verified_db['summary']['withWarnings']}")
    print(f"Average quality: {verified_db['summary']['averageQuality']}")
    print()
    print(f"Output: {output_file}")

    return verified_db


if __name__ == '__main__':
    # Convert
    verified_db = convert_raw_to_verified()

    print()
    print("Sample verified entry:")
    print(json.dumps(verified_db['data'][0], indent=2, ensure_ascii=False))
