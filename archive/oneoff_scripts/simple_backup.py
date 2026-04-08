#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Backup Script

每次寫入 venues.json 前備份
"""
import json
import shutil
from datetime import datetime
from pathlib import Path


def backup_venues(venues_file='venues.json', backup_dir='backups'):
    """
    Simple backup before write

    Args:
        venues_file: Path to venues.json
        backup_dir: Backup directory

    Returns:
        Path to backup file
    """
    # Ensure venues file exists
    venues_path = Path(venues_file)
    if not venues_path.exists():
        print(f"Warning: {venues_file} not found, skipping backup")
        return None

    # Create backup directory
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)

    # Create backup with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_path / f'venues_{timestamp}.json'

    # Copy file
    shutil.copy2(venues_path, backup_file)

    print(f"Backup: {backup_file}")
    return backup_file


def list_backups(backup_dir='backups'):
    """List all backups"""
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print("No backups found")
        return []

    backups = sorted(backup_path.glob('venues_*.json'), reverse=True)
    print(f"Total backups: {len(backups)}")
    print()

    for backup in backups[:10]:  # Show last 10
        stat = backup.stat()
        print(f"  {backup.name} - {stat.st_size} bytes")

    return backups


def cleanup_old_backups(backup_dir='backups', keep=10):
    """Remove old backups, keeping only N most recent"""
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        return

    backups = sorted(backup_path.glob('venues_*.json'), reverse=True)

    if len(backups) <= keep:
        print(f"Total backups: {len(backups)} (keeping all)")
        return

    # Delete old backups
    deleted = 0
    for backup in backups[keep:]:
        backup.unlink()
        deleted += 1

    print(f"Cleaned up {deleted} old backups (keeping {keep})")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'list':
            list_backups()
        elif command == 'cleanup':
            cleanup_old_backups()
        else:
            print("Usage: python simple_backup.py [list|cleanup]")
    else:
        # Create backup
        backup_venues()

        # Show backups
        print()
        list_backups()
