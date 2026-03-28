#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Manager - Thread-safe data access with file locking

Provides centralized data access with:
- File locking for concurrent access control
- Automatic backup before writes
- Data validation integration
- Atomic write operations

Platform Support:
- Unix/Linux: Uses fcntl for file locking
- Windows: Uses msvcrt.locking (fallback to no locking)
"""
import json
import hashlib
import shutil
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any, Tuple

# Platform-specific locking
if sys.platform == 'win32':
    # Windows: use msvcrt.locking or fallback to no locking
    try:
        import msvcrt
        import os

        def _lock_file(file):
            """Lock file on Windows"""
            file.seek(0)
            msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)

        def _unlock_file(file):
            """Unlock file on Windows"""
            file.seek(0)
            msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)

    except ImportError:
        # Fallback: no locking on Windows
        def _lock_file(file):
            pass

        def _unlock_file(file):
            pass

else:
    # Unix/Linux: use fcntl
    import fcntl

    def _lock_file(file):
        """Lock file on Unix (shared lock)"""
        fcntl.flock(file.fileno(), fcntl.LOCK_SH)

    def _unlock_file(file):
        """Unlock file on Unix"""
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)


class DataManager:
    """
    Thread-safe data manager with file locking and transaction support
    """

    def __init__(self, data_file: str, backup_dir: str = "./data/backups"):
        """
        Initialize DataManager

        Args:
            data_file: Path to main data file (venues.json)
            backup_dir: Directory for backups
        """
        self.data_file = Path(data_file)
        self.backup_dir = Path(backup_dir)

        # Create backup directory if not exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Lock file path
        self.lock_file = self.data_file.parent / f".{self.data_file.name}.lock"

    def read_venues(self) -> List[Dict]:
        """
        Read venues data with shared lock (LOCK_SH)

        Returns:
            List of venue dictionaries

        Raises:
            FileNotFoundError: If data file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        if not self.data_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        with open(self.data_file, 'r', encoding='utf-8') as f:
            # Acquire shared lock (multiple readers allowed)
            _lock_file(f)

            try:
                data = json.load(f)
                # Ensure data is a list
                if isinstance(data, dict):
                    data = data.get('venues', [])
            finally:
                # Release lock
                _unlock_file(f)

        return data

    def write_venues(
        self,
        data: List[Dict],
        backup: bool = True,
        validator: Optional[Any] = None
    ) -> bool:
        """
        Write venues data with transaction support

        Process:
        1. Validate data (if validator provided)
        2. Create backup (if backup=True)
        3. Write to temporary file
        4. Verify temporary file
        5. Atomically replace main file

        Args:
            data: List of venue dictionaries
            backup: Whether to create backup before writing
            validator: Optional DataValidator instance

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If validation fails
            IOError: If write operation fails
        """
        # Step 1: Validate data if validator provided
        if validator:
            is_valid, errors = validator.validate_all(data)
            if not is_valid:
                raise ValueError(f"Validation failed: {errors}")

        # Step 2: Create backup
        if backup:
            backup_path = self._create_backup()
            print(f"Backup created: {backup_path}")

        # Step 3: Write to temporary file
        temp_file = self.data_file.parent / f"{self.data_file.name}.tmp"

        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                # Acquire exclusive lock
                _lock_file(f)

                # Write data
                json.dump(data, f, ensure_ascii=False, indent=2)

                # Flush to disk
                f.flush()
                if sys.platform != 'win32':
                    os.fsync(f.fileno())

                # Release lock
                _unlock_file(f)

            # Step 4: Verify temporary file
            is_valid, _ = self._verify_temp_file(temp_file)
            if not is_valid:
                temp_file.unlink()
                raise IOError("Temporary file verification failed")

            # Step 5: Atomically replace main file
            temp_file.replace(self.data_file)

            print(f"Data written: {self.data_file}")
            return True

        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise IOError(f"Write failed: {e}")

    def get_venue(self, venue_id: int) -> Optional[Dict]:
        """
        Get single venue by ID

        Args:
            venue_id: Venue ID

        Returns:
            Venue dictionary or None if not found
        """
        venues = self.read_venues()

        for venue in venues:
            if venue.get('id') == venue_id:
                return venue

        return None

    def update_venue(
        self,
        venue_id: int,
        updates: Dict,
        backup: bool = True,
        validator: Optional[Any] = None,
        change_tracker: Optional[Any] = None
    ) -> bool:
        """
        Update single venue

        Args:
            venue_id: Venue ID to update
            updates: Dictionary of fields to update
            backup: Whether to create backup
            validator: Optional DataValidator instance
            change_tracker: Optional ChangeTracker instance

        Returns:
            True if successful, False if venue not found
        """
        venues = self.read_venues()

        # Find venue
        venue_index = None
        for i, venue in enumerate(venues):
            if venue.get('id') == venue_id:
                venue_index = i
                break

        if venue_index is None:
            return False

        # Track changes
        old_venue = venues[venue_index].copy()

        # Apply updates
        for key, value in updates.items():
            if change_tracker:
                # Log change
                old_value = old_venue.get(key)
                change_tracker.log_change(
                    venue_id=venue_id,
                    action='update',
                    field=key,
                    old_value=old_value,
                    new_value=value,
                    source='data_manager'
                )

            venues[venue_index][key] = value

        # Write back
        self.write_venues(venues, backup=backup, validator=validator)
        return True

    def _create_backup(self) -> Path:
        """
        Create backup with timestamp and MD5 hash

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Calculate MD5 hash of current file
        with open(self.data_file, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]

        backup_name = f"{self.data_file.stem}_{timestamp}_{file_hash}.json"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(self.data_file, backup_path)

        return backup_path

    def _verify_temp_file(self, temp_file: Path) -> Tuple[bool, str]:
        """
        Verify temporary file is valid JSON

        Args:
            temp_file: Path to temporary file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Basic validation
            if not isinstance(data, list):
                return False, "Data is not a list"

            # Check all venues have IDs
            for venue in data:
                if 'id' not in venue:
                    return False, f"Venue missing ID: {venue}"

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, f"Verification error: {e}"

    def list_backups(self) -> List[Dict]:
        """
        List all backups with metadata

        Returns:
            List of backup information dictionaries
        """
        backups = []

        for backup_file in self.backup_dir.glob("venues_*.json"):
            stat = backup_file.stat()

            # Parse filename
            parts = backup_file.stem.split('_')
            if len(parts) >= 3:
                timestamp = f"{parts[1]}_{parts[2]}"
                file_hash = parts[3] if len(parts) > 3 else ""

                backups.append({
                    'path': str(backup_file),
                    'timestamp': timestamp,
                    'hash': file_hash,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime)
                })

        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)

        return backups

    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore from backup

        Args:
            backup_path: Path to backup file

        Returns:
            True if successful
        """
        backup_file = Path(backup_path)

        if not backup_file.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Verify backup file
        is_valid, error = self._verify_temp_file(backup_file)
        if not is_valid:
            raise ValueError(f"Backup file invalid: {error}")

        # Create backup of current file before restoring
        self._create_backup()

        # Copy backup to main file
        shutil.copy2(backup_file, self.data_file)

        print(f"Restored from: {backup_path}")
        return True


# Required import for file operations
import os


if __name__ == '__main__':
    # Test usage
    manager = DataManager('venues.json')

    # Read venues
    try:
        venues = manager.read_venues()
        print(f"Loaded {len(venues)} venues")
    except FileNotFoundError:
        print("venues.json not found")
    except Exception as e:
        print(f"Error: {e}")

    # List backups
    backups = manager.list_backups()
    print(f"\nFound {len(backups)} backups")
    for backup in backups[:5]:
        print(f"  {backup['timestamp']} ({backup['hash']}) - {backup['size']} bytes")
