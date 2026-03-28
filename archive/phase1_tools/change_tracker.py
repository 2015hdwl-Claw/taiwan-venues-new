#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Change Tracker - Track all data changes with audit trail

Provides comprehensive change tracking:
- JSON-based logging of all changes
- Checksum verification for data integrity
- Full audit trail with timestamps
- Query by venue, date range, action type
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ChangeRecord:
    """Single change record"""
    timestamp: str
    venueId: int
    action: str  # create, update, delete, restore
    field: str
    oldValue: Any
    newValue: Any
    source: str  # system, user, scraper, manual
    checksum: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class ChangeTracker:
    """
    Track all changes to venues data

    Log format:
    {
      "timestamp": "2026-03-26T10:30:00",
      "venueId": 1128,
      "action": "update",
      "field": "phone",
      "oldValue": "+886-2-3366-4504",
      "newValue": "+886-2-3366-4505",
      "source": "manual",
      "checksum": "a1b2c3d4"
    }
    """

    def __init__(self, log_file: str = "./data/changes.log"):
        """
        Initialize ChangeTracker

        Args:
            log_file: Path to change log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_change(
        self,
        venue_id: int,
        action: str,
        field: str,
        old_value: Any,
        new_value: Any,
        source: str = "system"
    ) -> None:
        """
        Log a single change

        Args:
            venue_id: Venue ID
            action: Action type (create, update, delete, restore)
            field: Field name
            old_value: Previous value
            new_value: New value
            source: Change source (system, user, scraper, manual)
        """
        # Validate action
        valid_actions = ['create', 'update', 'delete', 'restore']
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Create change record
        change = ChangeRecord(
            timestamp=datetime.utcnow().isoformat(),
            venueId=venue_id,
            action=action,
            field=field,
            oldValue=old_value,
            newValue=new_value,
            source=source,
            checksum=self._compute_checksum(new_value)
        )

        # Append to log file
        self._append_to_log(change)

    def log_batch_changes(
        self,
        venue_id: int,
        changes: Dict[str, tuple],
        source: str = "scraper"
    ) -> None:
        """
        Log multiple changes for one venue

        Args:
            venue_id: Venue ID
            changes: Dictionary of {field: (old_value, new_value)}
            source: Change source

        Example:
            changes = {
                'phone': ('old-phone', 'new-phone'),
                'email': ('old-email', 'new-email')
            }
        """
        for field, (old_val, new_val) in changes.items():
            self.log_change(
                venue_id=venue_id,
                action='update',
                field=field,
                old_value=old_val,
                new_value=new_val,
                source=source
            )

    def get_history(
        self,
        venue_id: Optional[int] = None,
        action: Optional[str] = None,
        field: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get change history with optional filters

        Args:
            venue_id: Filter by venue ID
            action: Filter by action type
            field: Filter by field name
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum number of records to return

        Returns:
            List of change records (newest first)
        """
        if not self.log_file.exists():
            return []

        # Read all logs
        changes = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    change = json.loads(line)
                    changes.append(change)
                except json.JSONDecodeError:
                    continue

        # Apply filters
        if venue_id is not None:
            changes = [c for c in changes if c.get('venueId') == venue_id]

        if action is not None:
            changes = [c for c in changes if c.get('action') == action]

        if field is not None:
            changes = [c for c in changes if c.get('field') == field]

        if start_date is not None:
            changes = [c for c in changes if c.get('timestamp', '') >= start_date]

        if end_date is not None:
            changes = [c for c in changes if c.get('timestamp', '') <= end_date]

        # Sort by timestamp (newest first)
        changes.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Limit
        return changes[:limit]

    def get_venue_changes(self, venue_id: int, limit: int = 50) -> List[Dict]:
        """
        Get all changes for a specific venue

        Args:
            venue_id: Venue ID
            limit: Maximum records

        Returns:
            List of changes (newest first)
        """
        return self.get_history(venue_id=venue_id, limit=limit)

    def get_recent_changes(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """
        Get recent changes within time window

        Args:
            hours: Number of hours to look back
            limit: Maximum records

        Returns:
            List of recent changes
        """
        start_date = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        return self.get_history(start_date=start_date, limit=limit)

    def get_change_summary(self, venue_id: int) -> Dict:
        """
        Get summary of changes for a venue

        Args:
            venue_id: Venue ID

        Returns:
            Summary dictionary with statistics
        """
        changes = self.get_venue_changes(venue_id, limit=10000)

        if not changes:
            return {
                'venueId': venue_id,
                'totalChanges': 0,
                'lastModified': None,
                'actions': {},
                'fields': {}
            }

        # Count actions
        action_counts = {}
        for change in changes:
            action = change.get('action', 'unknown')
            action_counts[action] = action_counts.get(action, 0) + 1

        # Count modified fields
        field_counts = {}
        for change in changes:
            field = change.get('field', 'unknown')
            field_counts[field] = field_counts.get(field, 0) + 1

        return {
            'venueId': venue_id,
            'totalChanges': len(changes),
            'lastModified': changes[0].get('timestamp'),
            'actions': action_counts,
            'fields': field_counts
        }

    def verify_integrity(self, venue_id: int, current_value: Any, field: str) -> bool:
        """
        Verify data integrity using checksums

        Args:
            venue_id: Venue ID
            current_value: Current value to verify
            field: Field name

        Returns:
            True if checksum matches latest change
        """
        changes = self.get_venue_changes(venue_id, limit=1)

        if not changes:
            # No changes recorded, can't verify
            return True

        latest_change = changes[0]

        # Only verify if it's the same field
        if latest_change.get('field') != field:
            return True

        # Compute checksum of current value
        current_checksum = self._compute_checksum(current_value)

        # Compare with logged checksum
        logged_checksum = latest_change.get('checksum', '')

        return current_checksum == logged_checksum

    def _compute_checksum(self, value: Any) -> str:
        """
        Compute MD5 checksum of value

        Args:
            value: Any JSON-serializable value

        Returns:
            Hex string of MD5 hash
        """
        # Convert to JSON string for consistent hashing
        value_str = json.dumps(value, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(value_str.encode('utf-8')).hexdigest()

    def _append_to_log(self, change: ChangeRecord) -> None:
        """
        Append change record to log file

        Args:
            change: ChangeRecord to append
        """
        with open(self.log_file, 'a', encoding='utf-8') as f:
            json.dump(change.to_dict(), f, ensure_ascii=False)
            f.write('\n')

    def export_changes(
        self,
        output_file: str,
        venue_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> int:
        """
        Export changes to JSON file

        Args:
            output_file: Output file path
            venue_id: Optional venue ID filter
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Number of exported records
        """
        changes = self.get_history(
            venue_id=venue_id,
            start_date=start_date,
            end_date=end_date,
            limit=100000
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, ensure_ascii=False, indent=2)

        return len(changes)

    def get_statistics(self, days: int = 30) -> Dict:
        """
        Get change statistics for time period

        Args:
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        changes = self.get_history(start_date=start_date, limit=100000)

        # Count by action
        action_counts = {}
        for change in changes:
            action = change.get('action', 'unknown')
            action_counts[action] = action_counts.get(action, 0) + 1

        # Count by source
        source_counts = {}
        for change in changes:
            source = change.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1

        # Count unique venues
        unique_venues = set()
        for change in changes:
            unique_venues.add(change.get('venueId'))

        return {
            'periodDays': days,
            'totalChanges': len(changes),
            'uniqueVenues': len(unique_venues),
            'actions': action_counts,
            'sources': source_counts
        }


if __name__ == '__main__':
    # Test usage
    tracker = ChangeTracker()

    # Log a change
    tracker.log_change(
        venue_id=1128,
        action='update',
        field='phone',
        old_value='+886-2-3366-4504',
        new_value='+886-2-3366-4505',
        source='manual'
    )

    # Get history
    history = tracker.get_venue_changes(1128)
    print(f"Found {len(history)} changes")

    # Get summary
    summary = tracker.get_change_summary(1128)
    print(f"Summary: {summary}")

    # Get statistics
    stats = tracker.get_statistics(days=7)
    print(f"Statistics: {stats}")
