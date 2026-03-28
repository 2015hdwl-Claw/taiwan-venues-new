#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Manager - LRU cache with TTL for venue data

Provides efficient caching:
- LRU (Least Recently Used) eviction
- TTL (Time To Live) expiration
- Pickle serialization for fast loading
- Automatic cache cleanup
"""
import pickle
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import OrderedDict
from data_manager import DataManager


class CacheManager:
    """
    LRU cache with TTL for venue data

    Features:
    - In-memory LRU cache
    - Persistent disk cache with pickle
    - Configurable TTL (default 1 hour)
    - Automatic cleanup of expired entries
    - Cache statistics
    """

    def __init__(
        self,
        cache_dir: str = "./data/cache",
        max_memory_items: int = 100,
        ttl_hours: int = 1
    ):
        """
        Initialize CacheManager

        Args:
            cache_dir: Directory for persistent cache
            max_memory_items: Maximum items in memory cache
            ttl_hours: Time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_memory_items = max_memory_items
        self.ttl = timedelta(hours=ttl_hours)

        # In-memory LRU cache
        self._memory_cache: OrderedDict[int, Dict] = OrderedDict()
        self._memory_timestamps: OrderedDict[int, datetime] = OrderedDict()

        # Data manager for loading from main DB
        self.data_manager = DataManager('venues.json')

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get_venue(self, venue_id: int) -> Optional[Dict]:
        """
        Get venue from cache (memory or disk)

        Cache hierarchy:
        1. Check memory cache (LRU)
        2. Check disk cache (if not expired)
        3. Load from main database

        Args:
            venue_id: Venue ID

        Returns:
            Venue dictionary or None
        """
        # Check memory cache
        if venue_id in self._memory_cache:
            # Check if expired
            cached_time = self._memory_timestamps.get(venue_id)
            if cached_time and (datetime.now() - cached_time) < self.ttl:
                # Move to end (most recently used)
                self._memory_cache.move_to_end(venue_id)
                self._hits += 1
                return self._memory_cache[venue_id]
            else:
                # Expired, remove from memory
                del self._memory_cache[venue_id]
                del self._memory_timestamps[venue_id]

        # Check disk cache
        cache_file = self.cache_dir / f"venue_{venue_id}.pkl"

        if cache_file.exists():
            # Check if expired
            cache_age = datetime.now() - datetime.fromtimestamp(
                cache_file.stat().st_mtime
            )

            if cache_age < self.ttl:
                # Load from disk
                try:
                    with open(cache_file, 'rb') as f:
                        venue = pickle.load(f)

                    # Store in memory
                    self._store_in_memory(venue_id, venue)
                    self._hits += 1
                    return venue
                except Exception as e:
                    print(f"Warning: Failed to load cache file: {e}")
                    # Remove corrupted cache file
                    cache_file.unlink()

        # Cache miss - load from main DB
        self._misses += 1
        venue = self.data_manager.get_venue(venue_id)

        if venue:
            # Store in cache
            self._store_in_memory(venue_id, venue)
            self._store_on_disk(venue_id, venue)

        return venue

    def get_venues(self, venue_ids: List[int]) -> List[Dict]:
        """
        Get multiple venues efficiently

        Args:
            venue_ids: List of venue IDs

        Returns:
            List of venue dictionaries
        """
        venues = []

        for venue_id in venue_ids:
            venue = self.get_venue(venue_id)
            if venue:
                venues.append(venue)

        return venues

    def update_venue(self, venue: Dict) -> None:
        """
        Update venue in cache

        Args:
            venue: Venue dictionary
        """
        venue_id = venue.get('id')

        if not venue_id:
            return

        # Update memory cache
        self._store_in_memory(venue_id, venue)

        # Update disk cache
        self._store_on_disk(venue_id, venue)

    def invalidate_venue(self, venue_id: int) -> None:
        """
        Invalidate venue from cache

        Args:
            venue_id: Venue ID
        """
        # Remove from memory
        if venue_id in self._memory_cache:
            del self._memory_cache[venue_id]
            del self._memory_timestamps[venue_id]

        # Remove from disk
        cache_file = self.cache_dir / f"venue_{venue_id}.pkl"
        if cache_file.exists():
            cache_file.unlink()

    def invalidate_all(self) -> None:
        """Clear all cache (memory and disk)"""
        # Clear memory
        self._memory_cache.clear()
        self._memory_timestamps.clear()

        # Clear disk
        for cache_file in self.cache_dir.glob("venue_*.pkl"):
            cache_file.unlink()

        print("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        Remove expired cache files from disk

        Returns:
            Number of files removed
        """
        removed = 0
        now = datetime.now()

        for cache_file in self.cache_dir.glob("venue_*.pkl"):
            # Check age
            cache_age = now - datetime.fromtimestamp(
                cache_file.stat().st_mtime
            )

            if cache_age > self.ttl:
                cache_file.unlink()
                removed += 1

        if removed > 0:
            print(f"Removed {removed} expired cache files")

        return removed

    def get_statistics(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Statistics dictionary
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        # Count disk cache files
        disk_cache_count = len(list(self.cache_dir.glob("venue_*.pkl")))

        return {
            'memoryCacheSize': len(self._memory_cache),
            'diskCacheSize': disk_cache_count,
            'maxMemoryItems': self.max_memory_items,
            'ttlHours': self.ttl.total_seconds() / 3600,
            'hits': self._hits,
            'misses': self._misses,
            'evictions': self._evictions,
            'hitRate': f"{hit_rate:.1f}%"
        }

    def _store_in_memory(self, venue_id: int, venue: Dict) -> None:
        """
        Store venue in memory cache with LRU eviction

        Args:
            venue_id: Venue ID
            venue: Venue dictionary
        """
        # Evict oldest if at capacity
        if len(self._memory_cache) >= self.max_memory_items:
            # Remove first (oldest) item
            oldest_id = next(iter(self._memory_cache))
            del self._memory_cache[oldest_id]
            del self._memory_timestamps[oldest_id]
            self._evictions += 1

        # Add/Update venue
        self._memory_cache[venue_id] = venue
        self._memory_timestamps[venue_id] = datetime.now()

        # Move to end (most recently used)
        self._memory_cache.move_to_end(venue_id)

    def _store_on_disk(self, venue_id: int, venue: Dict) -> None:
        """
        Store venue in disk cache

        Args:
            venue_id: Venue ID
            venue: Venue dictionary
        """
        cache_file = self.cache_dir / f"venue_{venue_id}.pkl"

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(venue, f)
        except Exception as e:
            print(f"Warning: Failed to write cache file: {e}")


class PrefetchCache:
    """
    Prefetch cache for batch operations

    Preloads frequently accessed venues into cache
    """

    def __init__(self, cache_manager: CacheManager):
        """
        Initialize prefetch cache

        Args:
            cache_manager: CacheManager instance
        """
        self.cache_manager = cache_manager
        self.data_manager = DataManager('venues.json')

    def prefetch_popular(self, limit: int = 20) -> int:
        """
        Preload popular venues into cache

        Popular criteria:
        - High priority (1 or 2)
        - Recently scraped
        - Has many rooms

        Args:
            limit: Maximum venues to prefetch

        Returns:
            Number of venues prefetched
        """
        venues = self.data_manager.read_venues()

        # Sort by priority and room count
        def sort_key(venue):
            priority = venue.get('priority', 5)
            room_count = len(venue.get('rooms', []))
            # Lower priority number = higher priority
            return (priority, -room_count)

        venues.sort(key=sort_key)

        # Prefetch top N
        prefetched = 0
        for venue in venues[:limit]:
            venue_id = venue.get('id')
            if venue_id:
                self.cache_manager.update_venue(venue)
                prefetched += 1

        print(f"Prefetched {prefetched} popular venues")
        return prefetched

    def prefetch_by_ids(self, venue_ids: List[int]) -> int:
        """
        Preload specific venues into cache

        Args:
            venue_ids: List of venue IDs

        Returns:
            Number of venues prefetched
        """
        prefetched = 0

        for venue_id in venue_ids:
            venue = self.data_manager.get_venue(venue_id)
            if venue:
                self.cache_manager.update_venue(venue)
                prefetched += 1

        print(f"Prefetched {prefetched} venues")
        return prefetched


if __name__ == '__main__':
    # Test usage
    print("Testing CacheManager:")

    cache_mgr = CacheManager()

    # Get venue (will load from DB)
    print("\nGetting venue 1128:")
    venue = cache_mgr.get_venue(1128)
    if venue:
        print(f"  Name: {venue.get('name')}")

    # Get same venue again (should hit cache)
    print("\nGetting venue 1128 again:")
    venue = cache_mgr.get_venue(1128)
    if venue:
        print(f"  Name: {venue.get('name')}")

    # Get statistics
    print("\nCache statistics:")
    stats = cache_mgr.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test prefetch
    print("\nTesting PrefetchCache:")
    prefetch = PrefetchCache(cache_mgr)
    prefetch.prefetch_popular(limit=5)

    # Statistics after prefetch
    print("\nCache statistics after prefetch:")
    stats = cache_mgr.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
