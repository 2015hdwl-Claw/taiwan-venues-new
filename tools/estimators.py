#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/estimators.py - Unified estimation formulas (single source of truth)

Area and pricing estimation formulas ONLY exist here.
Do NOT duplicate these formulas elsewhere.

Rules from memory/feedback_venue_scraping.md:
- area = max(theater*0.9, banquet*1.5, classroom*1.3, ushape*2.0) / 3.3058
- pricing = area * rate_per_ping (by venue type)
- All estimated pricing gets note: "price needs inquiry"
"""

from .constants import (
    AREA_RATIOS, SQM_TO_PING, AREA_ROUND,
    PRICE_RATES, VENUE_TYPE_TO_RATE, VENUE_RATE_OVERRIDES,
    get_rate_per_ping,
)


def estimate_area(capacity: dict) -> float | None:
    """
    Estimate room area in ping from capacity.

    Uses the LARGEST capacity across all layout types to estimate
    the minimum required area, then converts to ping.

    Returns None if no capacity data available.
    """
    if not capacity or not isinstance(capacity, dict):
        return None

    estimates = []
    for layout, ratio in AREA_RATIOS.items():
        count = capacity.get(layout)
        if count and count > 0:
            estimates.append(count * ratio)

    if not estimates:
        return None

    max_sqm = max(estimates)
    ping = round(max_sqm / SQM_TO_PING / AREA_ROUND) * AREA_ROUND
    return ping


def estimate_pricing(area_ping: float, venue_id: int = 0,
                     venue_type: str = '') -> dict | None:
    """
    Estimate pricing from area.

    Returns {"halfDay": ..., "fullDay": ..., "note": ...} or None.
    """
    try:
        area_ping = float(area_ping)
    except (TypeError, ValueError):
        return None
    if area_ping <= 0:
        return None

    # 1. Check venue ID override first
    rate_key = VENUE_RATE_OVERRIDES.get(venue_id)

    # 2. Then check venue type mapping
    if not rate_key:
        rate_key = VENUE_TYPE_TO_RATE.get(venue_type, 'default')

    # 3. Get rate with area-based adjustment
    rate = get_rate_per_ping(area_ping, rate_key)

    # Calculate (round to nearest 1000 for hotels, 100 for government)
    rate_info = PRICE_RATES.get(rate_key, PRICE_RATES['default'])
    if rate_key == 'government':
        half_day = int(area_ping * rate / 100) * 100
    else:
        half_day = int(area_ping * rate / 1000) * 1000

    full_day = half_day * 2

    return {
        'halfDay': half_day,
        'fullDay': full_day,
        'note': rate_info['note'],
    }


def estimate_room(room: dict, venue_id: int = 0,
                  venue_type: str = '') -> dict:
    """
    Estimate missing area and pricing for a single room.

    Returns dict with changes made: {"area_added": bool, "pricing_added": bool}
    Only fills in MISSING values, never overwrites existing data.
    """
    changes = {'area_added': False, 'pricing_added': False}

    # Estimate area if missing
    if not room.get('area'):
        area = estimate_area(room.get('capacity', {}))
        if area:
            room['area'] = area
            room['areaUnit'] = 'ping'
            changes['area_added'] = True

    # Estimate pricing if missing
    pricing = room.get('pricing')
    has_price = (isinstance(pricing, dict) and
                 (pricing.get('halfDay') or pricing.get('fullDay')))
    if not has_price:
        area_val = room.get('area', 0)
        if area_val:
            est = estimate_pricing(area_val, venue_id, venue_type)
            if est:
                if not isinstance(room.get('pricing'), dict):
                    room['pricing'] = {}
                room['pricing'].update(est)
                changes['pricing_added'] = True

    return changes


def estimate_venue(venue: dict) -> dict:
    """
    Estimate missing area and pricing for all rooms in a venue.

    Returns stats: {"rooms_fixed": N, "area_added": N, "pricing_added": N}
    """
    vid = venue.get('id', 0)
    vtype = venue.get('venueType', '')
    stats = {'rooms_fixed': 0, 'area_added': 0, 'pricing_added': 0}

    for room in venue.get('rooms', []):
        changes = estimate_room(room, vid, vtype)
        if changes['area_added'] or changes['pricing_added']:
            stats['rooms_fixed'] += 1
            stats['area_added'] += int(changes['area_added'])
            stats['pricing_added'] += int(changes['pricing_added'])

    return stats
