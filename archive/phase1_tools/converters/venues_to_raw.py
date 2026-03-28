#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert venues.json to raw.json

將現有 venues.json 轉換為新架構的初步資料庫 (raw.json)

Raw 格式:
{
  "version": "1.0",
  "generatedAt": "2026-03-26T10:30:00",
  "generator": "venues_to_raw.py",
  "sources": {...},
  "data": [
    {
      "sourceId": 1128,
      "scrapedAt": "2026-03-25T10:30:00",
      "scraper": "unknown",
      "success": true,
      "data": {venue data},
      "errors": [],
      "warnings": []
    }
  ]
}
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def convert_venues_to_raw(
    venues_file: str = 'venues.json',
    output_file: str = 'data/raw.json'
) -> Dict:
    """
    Convert venues.json to raw.json format

    Args:
        venues_file: Path to venues.json
        output_file: Path to output raw.json

    Returns:
        Raw database dictionary
    """
    print("="*80)
    print("Converting venues.json to raw.json")
    print("="*80)
    print()

    # Load venues
    print(f"Loading {venues_file}...")
    with open(venues_file, 'r', encoding='utf-8') as f:
        venues = json.load(f)

    print(f"Loaded {len(venues)} venues")
    print()

    # Convert to raw format
    raw_entries = []
    success_count = 0
    warning_count = 0

    for venue in venues:
        venue_id = venue.get('id')
        venue_name = venue.get('name', 'Unknown')

        # Extract metadata
        metadata = venue.get('metadata', {})
        last_scraped = metadata.get('lastScrapedAt')
        scrape_version = metadata.get('scrapeVersion', 'unknown')
        scrape_confidence = metadata.get('scrapeConfidenceScore', 0)

        # Determine scraper from version
        if 'V4_PDF' in scrape_version:
            scraper = 'full_site_scraper_v4_enhanced.py'
        elif 'V4' in scrape_version:
            scraper = 'full_site_scraper_v4.py'
        elif 'V3' in scrape_version:
            scraper = 'intelligent_scraper_v3.py'
        else:
            scraper = 'unknown'

        # Build raw entry
        raw_entry = {
            "sourceId": venue_id,
            "scrapedAt": last_scraped or datetime.now().isoformat(),
            "scraper": scraper,
            "success": True,
            "data": venue,
            "errors": [],
            "warnings": []
        }

        # Add warnings for incomplete data
        if not venue.get('contact', {}).get('phone'):
            raw_entry['warnings'].append('Missing phone number')
            warning_count += 1

        if not venue.get('contact', {}).get('email'):
            raw_entry['warnings'].append('Missing email')
            warning_count += 1

        if not venue.get('rooms'):
            raw_entry['warnings'].append('No rooms data')
            warning_count += 1

        if scrape_confidence < 70:
            raw_entry['warnings'].append(f'Low confidence score: {scrape_confidence}')
            warning_count += 1

        raw_entries.append(raw_entry)
        success_count += 1

    # Build raw database
    raw_db = {
        "version": "1.0",
        "generatedAt": datetime.now().isoformat(),
        "generator": "venues_to_raw.py",
        "sources": {
            "sourceFile": "venues.json",
            "conversionDate": datetime.now().isoformat()
        },
        "data": raw_entries,
        "summary": {
            "total": len(raw_entries),
            "success": success_count,
            "failed": 0,
            "withWarnings": warning_count
        }
    }

    # Create output directory
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(raw_db, f, ensure_ascii=False, indent=2)

    print()
    print("="*80)
    print("Conversion Complete")
    print("="*80)
    print()
    print(f"Total venues: {raw_db['summary']['total']}")
    print(f"Success: {raw_db['summary']['success']}")
    print(f"With warnings: {raw_db['summary']['withWarnings']}")
    print()
    print(f"Output: {output_file}")

    return raw_db


if __name__ == '__main__':
    # Convert
    raw_db = convert_venues_to_raw()

    print()
    print("Sample raw entry:")
    print(json.dumps(raw_db['data'][0], indent=2, ensure_ascii=False))
