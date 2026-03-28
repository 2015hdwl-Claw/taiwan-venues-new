#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transaction Writer - All-or-nothing writes with rollback

Provides transactional data operations:
- Automatic snapshot before changes
- Validation before commit
- Rollback on failure
- Change tracking integration
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from data_manager import DataManager
from data_validator import DataValidator
from change_tracker import ChangeTracker


class TransactionWriter:
    """
    Transactional write operations with automatic rollback

    Process:
    1. Create snapshot
    2. Validate data
    3. Write to temporary file
    4. Verify temporary file
    5. Replace main file (commit)
    6. Log changes
    7. Rollback on any error
    """

    def __init__(
        self,
        data_file: str = 'venues.json',
        snapshot_dir: str = './data/snapshots'
    ):
        """
        Initialize TransactionWriter

        Args:
            data_file: Path to main data file
            snapshot_dir: Directory for snapshots
        """
        self.data_file = Path(data_file)
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.data_manager = DataManager(data_file)
        self.validator = DataValidator(strict=False)
        self.change_tracker = ChangeTracker()

        # Current transaction state
        self._in_transaction = False
        self._current_snapshot = None

    def write_with_transaction(
        self,
        venue_data: List[Dict],
        source: str = 'system',
        pre_commit_hook: Optional[Callable] = None
    ) -> Tuple[bool, str]:
        """
        Write data with transaction support (all-or-nothing)

        Args:
            venue_data: List of venue dictionaries
            source: Change source (for logging)
            pre_commit_hook: Optional function to run before commit

        Returns:
            Tuple of (success, message)

        Example:
            success, message = writer.write_with_transaction(
                venues,
                source='scraper',
                pre_commit_hook=lambda data: print(f"Writing {len(data)} venues")
            )
        """
        try:
            # Step 1: Create snapshot
            snapshot_id = self._create_snapshot()
            self._current_snapshot = snapshot_id
            self._in_transaction = True

            print(f"Snapshot created: {snapshot_id}")

            # Step 2: Validate data
            is_valid, errors = self.validator.validate_all(venue_data)
            if not is_valid:
                raise ValueError(f"Validation failed:\n" + "\n".join(errors[:10]))

            print(f"Validation passed: {len(venue_data)} venues")

            # Step 3: Run pre-commit hook if provided
            if pre_commit_hook:
                pre_commit_hook(venue_data)

            # Step 4: Track changes (compare with current data)
            try:
                current_data = self.data_manager.read_venues()
                self._track_changes(current_data, venue_data, source)
            except FileNotFoundError:
                # No existing data, all are new
                pass

            # Step 5: Write data (DataManager handles backup + atomic write)
            self.data_manager.write_venues(
                venue_data,
                backup=True,
                validator=self.validator
            )

            # Step 6: Commit successful
            self._in_transaction = False
            self._current_snapshot = None

            message = f"Transaction committed: {len(venue_data)} venues written"
            print(message)
            return True, message

        except Exception as e:
            # Step 7: Rollback on error
            error_msg = f"Transaction failed: {str(e)}"
            print(error_msg)

            if self._in_transaction and self._current_snapshot:
                self._restore_from_snapshot(self._current_snapshot)
                error_msg += " (rolled back)"

            self._in_transaction = False
            self._current_snapshot = None

            return False, error_msg

    def update_venue_transaction(
        self,
        venue_id: int,
        updates: Dict,
        source: str = 'manual'
    ) -> Tuple[bool, str]:
        """
        Update single venue with transaction

        Args:
            venue_id: Venue ID
            updates: Dictionary of field updates
            source: Change source

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create snapshot
            snapshot_id = self._create_snapshot()
            self._current_snapshot = snapshot_id
            self._in_transaction = True

            # Read current data
            venues = self.data_manager.read_venues()

            # Find venue
            venue_index = None
            for i, venue in enumerate(venues):
                if venue.get('id') == venue_id:
                    venue_index = i
                    break

            if venue_index is None:
                raise ValueError(f"Venue {venue_id} not found")

            # Track changes
            old_venue = venues[venue_index]
            for field, new_value in updates.items():
                old_value = old_venue.get(field)
                self.change_tracker.log_change(
                    venue_id=venue_id,
                    action='update',
                    field=field,
                    old_value=old_value,
                    new_value=new_value,
                    source=source
                )

            # Apply updates
            venues[venue_index].update(updates)

            # Validate
            is_valid, errors = self.validator.validate_all(venues)
            if not is_valid:
                raise ValueError(f"Validation failed: {errors[:5]}")

            # Write
            self.data_manager.write_venues(
                venues,
                backup=True,
                validator=self.validator
            )

            # Commit
            self._in_transaction = False
            self._current_snapshot = None

            message = f"Venue {venue_id} updated successfully"
            return True, message

        except Exception as e:
            # Rollback
            if self._in_transaction and self._current_snapshot:
                self._restore_from_snapshot(self._current_snapshot)

            self._in_transaction = False
            self._current_snapshot = None

            return False, f"Update failed: {e}"

    def batch_update_transaction(
        self,
        updates: List[Dict[int, Dict]],
        source: str = 'scraper'
    ) -> Tuple[bool, str]:
        """
        Update multiple venues in one transaction

        Args:
            updates: List of {venue_id: {field: value}} dictionaries
            source: Change source

        Returns:
            Tuple of (success, message)

        Example:
            updates = [
                {1128: {'phone': '+886-2-3366-4505'}},
                {1129: {'email': 'new@example.com'}}
            ]
            success, msg = writer.batch_update_transaction(updates)
        """
        try:
            # Create snapshot
            snapshot_id = self._create_snapshot()
            self._current_snapshot = snapshot_id
            self._in_transaction = True

            # Read current data
            venues = self.data_manager.read_venues()

            # Apply all updates
            updated_count = 0
            for update_dict in updates:
                for venue_id, fields in update_dict.items():
                    # Find venue
                    venue_index = None
                    for i, venue in enumerate(venues):
                        if venue.get('id') == venue_id:
                            venue_index = i
                            break

                    if venue_index is None:
                        print(f"Warning: Venue {venue_id} not found, skipping")
                        continue

                    # Track and apply changes
                    old_venue = venues[venue_index]
                    for field, new_value in fields.items():
                        old_value = old_venue.get(field)
                        self.change_tracker.log_change(
                            venue_id=venue_id,
                            action='update',
                            field=field,
                            old_value=old_value,
                            new_value=new_value,
                            source=source
                        )
                        venues[venue_index][field] = new_value

                    updated_count += 1

            # Validate
            is_valid, errors = self.validator.validate_all(venues)
            if not is_valid:
                raise ValueError(f"Validation failed: {errors[:5]}")

            # Write
            self.data_manager.write_venues(
                venues,
                backup=True,
                validator=self.validator
            )

            # Commit
            self._in_transaction = False
            self._current_snapshot = None

            message = f"Batch update completed: {updated_count} venues updated"
            return True, message

        except Exception as e:
            # Rollback
            if self._in_transaction and self._current_snapshot:
                self._restore_from_snapshot(self._current_snapshot)

            self._in_transaction = False
            self._current_snapshot = None

            return False, f"Batch update failed: {e}"

    def _create_snapshot(self) -> str:
        """
        Create snapshot of current data

        Returns:
            Snapshot ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"snapshot_{timestamp}"
        snapshot_path = self.snapshot_dir / f"{snapshot_id}.json"

        if self.data_file.exists():
            shutil.copy2(self.data_file, snapshot_path)
        else:
            # Create empty snapshot
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

        return snapshot_id

    def _restore_from_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore from snapshot

        Args:
            snapshot_id: Snapshot ID to restore

        Returns:
            True if successful
        """
        snapshot_path = self.snapshot_dir / f"{snapshot_id}.json"

        if not snapshot_path.exists():
            print(f"Warning: Snapshot {snapshot_id} not found")
            return False

        # Verify snapshot
        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Verify it's a list
            if not isinstance(data, list):
                raise ValueError("Snapshot data is not a list")

        except Exception as e:
            print(f"Error: Snapshot verification failed: {e}")
            return False

        # Restore
        shutil.copy2(snapshot_path, self.data_file)
        print(f"Restored from snapshot: {snapshot_id}")

        return True

    def _track_changes(
        self,
        old_data: List[Dict],
        new_data: List[Dict],
        source: str
    ) -> None:
        """
        Track changes between old and new data

        Args:
            old_data: Original data
            new_data: New data
            source: Change source
        """
        # Create lookup by ID
        old_venues = {v.get('id'): v for v in old_data}
        new_venues = {v.get('id'): v for v in new_data}

        # Find new venues
        for venue_id in new_venues:
            if venue_id not in old_venues:
                self.change_tracker.log_change(
                    venue_id=venue_id,
                    action='create',
                    field='all',
                    old_value=None,
                    new_value=new_venues[venue_id].get('name'),
                    source=source
                )

        # Find deleted venues
        for venue_id in old_venues:
            if venue_id not in new_venues:
                self.change_tracker.log_change(
                    venue_id=venue_id,
                    action='delete',
                    field='all',
                    old_value=old_venues[venue_id].get('name'),
                    new_value=None,
                    source=source
                )

        # Find updated venues
        for venue_id in new_venues:
            if venue_id in old_venues:
                old_venue = old_venues[venue_id]
                new_venue = new_venues[venue_id]

                # Compare fields
                for field in new_venue:
                    if field in old_venue:
                        old_value = old_venue[field]
                        new_value = new_venue[field]

                        if old_value != new_value:
                            self.change_tracker.log_change(
                                venue_id=venue_id,
                                action='update',
                                field=field,
                                old_value=old_value,
                                new_value=new_value,
                                source=source
                            )

    def list_snapshots(self) -> List[Dict]:
        """
        List all snapshots

        Returns:
            List of snapshot information
        """
        snapshots = []

        for snapshot_file in self.snapshot_dir.glob("snapshot_*.json"):
            stat = snapshot_file.stat()

            # Parse timestamp from filename
            parts = snapshot_file.stem.split('_')
            timestamp = '_'.join(parts[1:3]) if len(parts) > 2 else parts[1]

            snapshots.append({
                'id': snapshot_file.stem,
                'timestamp': timestamp,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime)
            })

        # Sort by creation time (newest first)
        snapshots.sort(key=lambda x: x['created'], reverse=True)

        return snapshots

    def cleanup_old_snapshots(self, keep: int = 10) -> int:
        """
        Remove old snapshots, keeping only N most recent

        Args:
            keep: Number of snapshots to keep

        Returns:
            Number of snapshots deleted
        """
        snapshots = self.list_snapshots()

        if len(snapshots) <= keep:
            return 0

        # Delete old snapshots
        deleted = 0
        for snapshot in snapshots[keep:]:
            snapshot_path = self.snapshot_dir / f"{snapshot['id']}.json"
            snapshot_path.unlink()
            deleted += 1

        print(f"Cleaned up {deleted} old snapshots")
        return deleted


if __name__ == '__main__':
    # Test usage
    writer = TransactionWriter()

    # Test single venue update
    print("Testing venue update transaction:")
    success, message = writer.update_venue_transaction(
        venue_id=1128,
        updates={'phone': '+886-2-3366-9999'},
        source='test'
    )
    print(f"  {message}")

    # List snapshots
    print("\nSnapshots:")
    snapshots = writer.list_snapshots()
    for snapshot in snapshots[:5]:
        print(f"  {snapshot['id']} - {snapshot['timestamp']}")
