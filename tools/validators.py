#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/validators.py - Format validation (equipment, pricing, schema)

Rules from memory:
- equipment MUST be array, not string (frontend does .slice().join())
- pricing MUST have halfDay or fullDay (not price.weekday)
- area uses single value in ping (not areaSqm/areaPing dual fields)
- images format: {"main": "url", "gallery": ["url"]}, not list
"""

from .constants import (
    SCHEMA_RULES, DEFAULT_EQUIPMENT,
    CAPACITY_RANGE, AREA_RANGE, PRICE_RANGE,
)


def validate_room(room: dict) -> list[str]:
    """
    Validate a single room against frontend schema requirements.

    Returns list of issue descriptions. Empty list = valid.
    """
    issues = []

    # 0. room must have id
    if not room.get('id'):
        issues.append("missing room id")

    # 1. equipment must be array
    equip = room.get('equipment')
    if equip is not None:
        if isinstance(equip, str):
            issues.append(f"equipment is string, not array: {equip[:50]}")
        elif not isinstance(equip, list):
            issues.append(f"equipment is {type(equip).__name__}, expected array")

    # 2. pricing must have halfDay or fullDay
    pricing = room.get('pricing')
    if pricing is not None:
        if not isinstance(pricing, dict):
            issues.append(f"pricing is {type(pricing).__name__}, expected dict")
        elif not (pricing.get('halfDay') or pricing.get('fullDay') or pricing.get('note')):
            issues.append("pricing dict missing halfDay/fullDay/note")

    # 3. images must be dict with main key
    images = room.get('images')
    if images is not None:
        if isinstance(images, list):
            issues.append("images is list, expected dict {main, gallery}")
        elif isinstance(images, dict) and not images.get('main'):
            issues.append("images dict missing 'main' key")

    # 4. area should exist and be reasonable
    area = room.get('area')
    if area is not None:
        if not isinstance(area, (int, float)):
            issues.append(f"area is {type(area).__name__}, expected number")
        elif not (AREA_RANGE[0] <= area <= AREA_RANGE[1]):
            issues.append(f"area {area} out of range {AREA_RANGE}")

    # 5. capacity values should be reasonable
    cap = room.get('capacity')
    if cap and isinstance(cap, dict):
        for layout, val in cap.items():
            if val is not None:
                if not isinstance(val, int):
                    issues.append(f"capacity.{layout} is {type(val).__name__}, expected int")
                elif not (CAPACITY_RANGE[0] <= val <= CAPACITY_RANGE[1]):
                    issues.append(f"capacity.{layout}={val} out of range")

    # 6. pricing values should be reasonable
    if pricing and isinstance(pricing, dict):
        for key in ('halfDay', 'fullDay'):
            val = pricing.get(key)
            if val is not None:
                if not isinstance(val, (int, float)):
                    issues.append(f"pricing.{key} is {type(val).__name__}, expected number")
                elif not (PRICE_RANGE[0] <= val <= PRICE_RANGE[1]):
                    issues.append(f"pricing.{key}={val} out of range")

    # 7. limitations should be array of strings
    limitations = room.get('limitations')
    if limitations is not None:
        if not isinstance(limitations, list):
            issues.append(f"limitations is {type(limitations).__name__}, expected array")
        elif not all(isinstance(x, str) for x in limitations):
            issues.append("limitations array contains non-string items")

    # 8. loadIn should be dict
    load_in = room.get('loadIn')
    if load_in is not None:
        if not isinstance(load_in, dict):
            issues.append(f"loadIn is {type(load_in).__name__}, expected dict")

    return issues


def validate_venue(venue: dict) -> dict:
    """
    Validate all rooms in a venue + venue-level knowledge fields.

    Returns {"issues": [...], "rooms_with_issues": N, "total_issues": N}
    """
    all_issues = []
    rooms_with_issues = 0

    for room in venue.get('rooms', []):
        room_issues = validate_room(room)
        if room_issues:
            rooms_with_issues += 1
            for issue in room_issues:
                all_issues.append(f"  {room.get('id', '?')} {room.get('name', '?')}: {issue}")

    # Venue-level knowledge validation
    risks = venue.get('risks')
    if risks is not None:
        if not isinstance(risks, dict):
            all_issues.append(f"  venue.risks is {type(risks).__name__}, expected dict")

    pricing_tips = venue.get('pricingTips')
    if pricing_tips is not None:
        if not isinstance(pricing_tips, list):
            all_issues.append(f"  venue.pricingTips is {type(pricing_tips).__name__}, expected array")
        elif not all(isinstance(x, str) for x in pricing_tips):
            all_issues.append("  venue.pricingTips contains non-string items")

    rules = venue.get('rules')
    if rules is not None:
        if not isinstance(rules, dict):
            all_issues.append(f"  venue.rules is {type(rules).__name__}, expected dict")

    return {
        'issues': all_issues,
        'rooms_with_issues': rooms_with_issues,
        'total_issues': len(all_issues),
    }


def fix_room(room: dict, venue_id: int = 0) -> list[str]:
    """
    Auto-fix common schema issues in a room.

    Returns list of fixes applied.
    """
    fixes = []

    # Fix area: string/dict -> float
    area = room.get('area')
    if isinstance(area, str):
        try:
            room['area'] = float(area)
            fixes.append(f"area: str -> float {room['area']}")
        except ValueError:
            # Try to extract number from string
            import re
            nums = re.findall(r'[\d.]+', area)
            if nums:
                room['area'] = float(nums[0])
                fixes.append(f"area: extracted {room['area']} from string")
            else:
                del room['area']
                fixes.append("area: removed invalid string")
    elif isinstance(area, dict):
        # Extract from dict (e.g. {"ping": 50, "sqm": 165})
        if 'ping' in area:
            room['area'] = float(area['ping'])
        elif 'sqm' in area:
            room['area'] = round(float(area['sqm']) / 3.3058, 1)
        else:
            del room['area']
        fixes.append(f"area: dict -> float {room.get('area', 'removed')}")

    # Fix equipment: dict -> array
    equip = room.get('equipment')
    if isinstance(equip, dict):
        room['equipment'] = list(equip.values()) if equip else list(DEFAULT_EQUIPMENT)
        fixes.append(f"equipment: dict -> array")

    # Fix missing room id: generate from venue_id + sequential number
    if not room.get('id') and venue_id:
        import re
        name = room.get('name', '')
        # Try to extract numbers from room name
        nums = re.findall(r'\d+', name)
        suffix = nums[0] if nums else ''
        if not suffix:
            # Generate a short hash-like suffix from the name
            clean = re.sub(r'[^\w]', '', name)
            suffix = str(abs(hash(clean)) % 1000)
        room['id'] = f"{venue_id}-{suffix}"
        fixes.append(f"id: generated {room['id']}")

    # Fix equipment: string -> array
    equip = room.get('equipment')
    if isinstance(equip, str):
        room['equipment'] = [equip]
        fixes.append(f"equipment: string -> array")
    elif equip is None:
        room['equipment'] = list(DEFAULT_EQUIPMENT)
        fixes.append(f"equipment: None -> defaults")

    # Fix pricing: ensure dict with at least halfDay or fullDay
    pricing = room.get('pricing')
    if pricing is None:
        room['pricing'] = {}
        pricing = room['pricing']

    # Fix images: list -> dict
    images = room.get('images')
    if isinstance(images, list):
        main = images[0] if images else ''
        room['images'] = {'main': main, 'gallery': images}
        fixes.append(f"images: list -> dict")

    # Fix capacity: remove 0 values
    cap = room.get('capacity')
    if isinstance(cap, dict):
        zeros = [k for k, v in cap.items() if v == 0]
        for k in zeros:
            del cap[k]
        if zeros:
            fixes.append(f"capacity: removed 0 values ({', '.join(zeros)})")

    return fixes


def audit_venue(venue: dict) -> dict:
    """
    Full audit of a venue: what's missing, what's wrong.

    Returns {"missing_area": N, "missing_price": N, "missing_img": N,
             "missing_knowledge": N, "schema_issues": N, "details": [...]}
    """
    missing_area = 0
    missing_price = 0
    missing_img = 0
    details = []

    for room in venue.get('rooms', []):
        rid = room.get('id', '?')
        rname = room.get('name', '?')

        if not room.get('area'):
            missing_area += 1

        pricing = room.get('pricing')
        has_price = (isinstance(pricing, dict) and
                     (pricing.get('halfDay') or pricing.get('fullDay')))
        if not has_price:
            missing_price += 1

        images = room.get('images', {})
        has_img = isinstance(images, dict) and images.get('main')
        if not has_img:
            missing_img += 1

        issues = validate_room(room)
        if issues:
            for issue in issues:
                details.append(f"  {rid} {rname}: {issue}")

    val_result = validate_venue(venue)

    # Knowledge coverage
    has_risks = bool(venue.get('risks'))
    has_pricing_tips = bool(venue.get('pricingTips'))
    has_rules = isinstance(venue.get('rules'), dict) and len(venue.get('rules', {})) > 0
    knowledge_score = sum([has_risks, has_pricing_tips, has_rules])
    rooms_with_limitations = sum(
        1 for r in venue.get('rooms', [])
        if isinstance(r.get('limitations'), list) and len(r.get('limitations', [])) > 0
    )

    return {
        'venue_id': venue.get('id'),
        'venue_name': venue.get('name', ''),
        'total_rooms': len(venue.get('rooms', [])),
        'missing_area': missing_area,
        'missing_price': missing_price,
        'missing_img': missing_img,
        'knowledge': {
            'has_risks': has_risks,
            'has_pricing_tips': has_pricing_tips,
            'has_rules': has_rules,
            'knowledge_score': f"{knowledge_score}/3",
            'rooms_with_limitations': rooms_with_limitations,
        },
        'schema_issues': val_result['total_issues'],
        'details': details,
    }
