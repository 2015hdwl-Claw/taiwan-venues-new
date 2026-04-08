#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Source Database Manager
管理來源資料庫
"""
import json
import argparse
from datetime import datetime

SOURCES_FILE = 'sources.json'

def load_sources():
    """Load sources database"""
    with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_sources(data):
    """Save sources database"""
    # Backup
    from datetime import datetime as dt
    timestamp = dt.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{SOURCES_FILE}.backup.{timestamp}"

    import shutil
    shutil.copy(SOURCES_FILE, backup_name)
    print(f"Backup: {backup_name}")

    # Save
    with open(SOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {SOURCES_FILE}")

def list_sources(args):
    """List sources"""
    data = load_sources()
    sources = data['sources']

    print("="*80)
    print("Source Database List")
    print("="*80)
    print()

    # Filter
    if args.status:
        sources = [s for s in sources if s['status'] == args.status]

    if args.priority:
        sources = [s for s in sources if s['priority'] == args.priority]

    if args.venue_type:
        sources = [s for s in sources if s['venueTypeId'] == args.venue_type]

    # Sort
    sort_key = args.sort or 'id'
    reverse = args.reverse

    if sort_key in ['id', 'priority', 'status']:
        sources.sort(key=lambda x: x[sort_key], reverse=reverse)

    # Display
    print(f"Total: {len(sources)} sources")
    print()

    for s in sources:
        status_mark = "[OK]" if s['status'] == 'active' else "[PENDING]" if s['status'] == 'pending' else "[INACTIVE]"
        print(f"{status_mark} ID {s['id']}: {s['name']}")
        print(f"   Type: {s['venueTypeId']} | Priority: {s['priority']} | Tech: {s['webTech']}")
        print(f"   URL: {s['url']}")
        print(f"   Status: {s['status']} | Last Scrape: {s.get('lastScraped', 'Never')}")
        if s.get('notes'):
            print(f"   Notes: {s['notes']}")
        print()

def add_source(args):
    """Add new source"""
    data = load_sources()

    # Generate new ID
    max_id = max([s['id'] for s in data['sources']] + [1000])
    new_id = max_id + 1

    # Detect web tech
    if args.detect:
        print(f"Detecting web tech for {args.url}...")
        # TODO: Implement detection
        web_tech = "unknown"
    else:
        web_tech = args.tech or "unknown"

    new_source = {
        "id": new_id,
        "name": args.name,
        "nameEn": args.name_en or "",
        "regionId": args.region or "TW-TPE",
        "venueTypeId": args.venue_type or "conference_center",
        "url": args.url,
        "webTech": web_tech,
        "priority": args.priority or 3,
        "status": "pending",
        "notes": args.notes or "",
        "lastChecked": datetime.now().isoformat(),
        "lastScraped": None,
        "scrapeVersion": None,
        "scrapeResult": None
    }

    data['sources'].append(new_source)
    data['lastUpdated'] = datetime.now().isoformat()

    save_sources(data)

    print()
    print(f"[OK] Added source {new_id}: {args.name}")

def update_source(args):
    """Update existing source"""
    data = load_sources()

    # Find source
    source = None
    for s in data['sources']:
        if s['id'] == args.id:
            source = s
            break

    if not source:
        print(f"[ERROR] Source {args.id} not found")
        return

    # Update fields
    if args.status:
        source['status'] = args.status
        source['lastChecked'] = datetime.now().isoformat()

    if args.priority:
        source['priority'] = args.priority

    if args.notes:
        source['notes'] = args.notes

    if args.url:
        source['url'] = args.url

    data['lastUpdated'] = datetime.now().isoformat()

    save_sources(data)

    print()
    print(f"[OK] Updated source {args.id}")

def show_stats(args):
    """Show statistics"""
    data = load_sources()
    sources = data['sources']

    print("="*80)
    print("Source Database Statistics")
    print("="*80)
    print()

    # Total
    print(f"Total Sources: {len(sources)}")
    print()

    # By status
    print("By Status:")
    status_count = {}
    for s in sources:
        status = s['status']
        status_count[status] = status_count.get(status, 0) + 1

    for status in ['active', 'pending', 'inactive', 'removed']:
        count = status_count.get(status, 0)
        percentage = (count / len(sources) * 100) if sources else 0
        print(f"  {status}: {count} ({percentage:.1f}%)")
    print()

    # By venue type
    print("By Venue Type:")
    type_count = {}
    for s in sources:
        vtype = s['venueTypeId']
        type_count[vtype] = type_count.get(vtype, 0) + 1

    for vtype in data['venueTypes']:
        count = type_count.get(vtype['id'], 0)
        print(f"  {vtype['name']}: {count}")
    print()

    # By priority
    print("By Priority:")
    priority_count = {}
    for s in sources:
        priority = s['priority']
        priority_count[priority] = priority_count.get(priority, 0) + 1

    for priority in sorted(priority_count.keys()):
        count = priority_count[priority]
        print(f"  Priority {priority}: {count}")
    print()

    # By region
    print("By Region:")
    region_count = {}
    for s in sources:
        region = s['regionId']
        region_count[region] = region_count.get(region, 0) + 1

    for region in data['regions']:
        count = region_count.get(region['id'], 0)
        if count > 0:
            print(f"  {region['name']}: {count}")
    print()

    # Scrape status
    scraped = [s for s in sources if s.get('lastScraped')]
    print(f"Scraped: {len(scraped)}/{len(sources)} ({len(scraped)/len(sources)*100:.1f}%)")

    not_scraped = [s for s in sources if not s.get('lastScraped')]
    print(f"Not Scraped: {len(not_scraped)}/{len(sources)} ({len(not_scraped)/len(sources)*100:.1f}%)")

def export_sources(args):
    """Export sources to different format"""
    data = load_sources()

    if args.format == 'csv':
        import csv

        filename = f"sources_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'ID', 'Name', 'Type', 'Region', 'URL',
                'Web Tech', 'Priority', 'Status', 'Last Scraped'
            ])

            # Data
            for s in data['sources']:
                # Get type name
                type_name = ""
                for vt in data['venueTypes']:
                    if vt['id'] == s['venueTypeId']:
                        type_name = vt['name']
                        break

                # Get region name
                region_name = ""
                for r in data['regions']:
                    if r['id'] == s['regionId']:
                        region_name = r['name']
                        break

                writer.writerow([
                    s['id'],
                    s['name'],
                    type_name,
                    region_name,
                    s['url'],
                    s['webTech'],
                    s['priority'],
                    s['status'],
                    s.get('lastScraped', 'Never')
                ])

        print(f"[OK] Exported to {filename}")

    elif args.format == 'json':
        filename = f"sources_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[OK] Exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Source Database Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List sources')
    list_parser.add_argument('--status', choices=['active', 'pending', 'inactive', 'removed'])
    list_parser.add_argument('--priority', type=int, choices=[1, 2, 3, 4, 5])
    list_parser.add_argument('--venue-type', choices=['conference_center', 'hotel', 'wedding', 'exhibition', 'sports'])
    list_parser.add_argument('--sort', choices=['id', 'name', 'priority', 'status'], default='id')
    list_parser.add_argument('--reverse', action='store_true')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add new source')
    add_parser.add_argument('--name', required=True, help='Venue name')
    add_parser.add_argument('--name-en', help='Venue English name')
    add_parser.add_argument('--url', required=True, help='Official website URL')
    add_parser.add_argument('--region', default='TW-TPE', help='Region ID')
    add_parser.add_argument('--venue-type', default='conference_center', help='Venue type ID')
    add_parser.add_argument('--tech', choices=['static', 'wordpress', 'javascript', 'unknown'], help='Web tech type')
    add_parser.add_argument('--priority', type=int, choices=[1, 2, 3, 4, 5], default=3, help='Priority')
    add_parser.add_argument('--notes', help='Notes')
    add_parser.add_argument('--detect', action='store_true', help='Auto-detect web tech')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update source')
    update_parser.add_argument('--id', type=int, required=True, help='Source ID')
    update_parser.add_argument('--status', choices=['active', 'pending', 'inactive', 'removed'])
    update_parser.add_argument('--priority', type=int, choices=[1, 2, 3, 4, 5])
    update_parser.add_argument('--url', help='Update URL')
    update_parser.add_argument('--notes', help='Update notes')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export sources')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Export format')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'list':
        list_sources(args)
    elif args.command == 'add':
        add_source(args)
    elif args.command == 'update':
        update_source(args)
    elif args.command == 'stats':
        show_stats(args)
    elif args.command == 'export':
        export_sources(args)

if __name__ == '__main__':
    main()
