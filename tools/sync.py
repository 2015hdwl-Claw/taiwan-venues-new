#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/sync.py - File sync (DATA_VERSION + cache-bust + consistency checks)

After Plan A unification:
- All pages load venues.json (venues_taipei.json no longer used by frontend)
- DATA_VERSION must be synced in: app.js, venue.js, room.js
- HTML script tags must also have matching ?v= cache-bust
"""

import json
import re
import os
from datetime import datetime

from .constants import VENUES_FILE, VENUES_TAIPEI_FILE, JS_FILES

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILES = [
    os.path.join(PROJECT_ROOT, 'index.html'),
    os.path.join(PROJECT_ROOT, 'venue.html'),
    os.path.join(PROJECT_ROOT, 'room.html'),
]

VERSION_PATTERN = re.compile(r"DATA_VERSION\s*=\s*['\"]([^'\"]+)['\"]")


def bump_version(dry_run: bool = False) -> str:
    """
    Update DATA_VERSION in all 3 JS files.

    Format: YYYYMMDD-vN (auto-increment N if same date)
    Returns the new version string.
    """
    today = datetime.now().strftime('%Y%m%d')

    # Find current max version number for today
    max_n = 0

    for js_file in JS_FILES:
        if not os.path.exists(js_file):
            continue
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = VERSION_PATTERN.search(content)
        if match:
            version_str = match.group(1)
            if version_str.startswith(today):
                parts = version_str.split('-v')
                if len(parts) == 2:
                    max_n = max(max_n, int(parts[1]))

    new_version = f"{today}-v{max_n + 1}"

    if not dry_run:
        # Update JS files
        for js_file in JS_FILES:
            if not os.path.exists(js_file):
                print(f"  [WARN] File not found: {js_file}")
                continue
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = VERSION_PATTERN.sub(
                f"DATA_VERSION = '{new_version}'", content
            )
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  {os.path.basename(js_file)}: -> {new_version}")

        # Update HTML cache-bust query strings
        for html_file in HTML_FILES:
            if not os.path.exists(html_file):
                continue
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Match script src="*.js?v=..." or script src="*.js"
            content = re.sub(
                r'(src="(?:app|venue|room)\.js)(\?v=[^"]*)?(")',
                rf'\1?v={new_version}\3',
                content
            )
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  {os.path.basename(html_file)}: cache-bust -> {new_version}")

    return new_version


def check_consistency() -> list[str]:
    """
    Check that all data sources and versions are consistent.

    Returns list of issues found. Empty list = all good.
    """
    issues = []

    # 1. Check DATA_VERSION is same in all 3 JS files
    versions = {}
    for js_file in JS_FILES:
        if not os.path.exists(js_file):
            issues.append(f"{os.path.basename(js_file)}: FILE NOT FOUND")
            continue
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = VERSION_PATTERN.search(content)
        if match:
            versions[os.path.basename(js_file)] = match.group(1)
        else:
            issues.append(f"{os.path.basename(js_file)}: DATA_VERSION not found")

    unique_versions = set(versions.values())
    if len(unique_versions) > 1:
        issues.append(f"DATA_VERSION mismatch: {versions}")

    # 2. Check data source consistency (all should use venues.json)
    for js_file in JS_FILES:
        if not os.path.exists(js_file):
            continue
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'venues_taipei.json' in content:
            issues.append(f"{os.path.basename(js_file)}: still uses venues_taipei.json (should use venues.json)")

    # 3. Check venues.json exists and is valid
    if not os.path.exists(VENUES_FILE):
        issues.append("venues.json: FILE NOT FOUND")
    else:
        try:
            with open(VENUES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            venues = data if isinstance(data, list) else data.get('venues', [])
            if len(venues) == 0:
                issues.append("venues.json: EMPTY (0 venues)")
        except json.JSONDecodeError as e:
            issues.append(f"venues.json: INVALID JSON - {e}")

    # 4. Check HTML cache-bust matches DATA_VERSION
    if versions:
        latest_version = list(versions.values())[0]
        for html_file in HTML_FILES:
            if not os.path.exists(html_file):
                continue
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Find script tags
            for match in re.finditer(r'src="((?:app|venue|room)\.js)(\?v=([^"]*))?(")', content):
                html_v = match.group(3)
                if html_v and html_v != latest_version:
                    issues.append(
                        f"{os.path.basename(html_file)}: script cache-bust "
                        f"'{html_v}' != DATA_VERSION '{latest_version}'"
                    )

    return issues


def sync_all(dry_run: bool = False) -> dict:
    """
    Run full sync: bump version + consistency check.

    Returns {"version": "...", "issues": [...]}
    """
    print("[sync] Bumping DATA_VERSION...")
    version = bump_version(dry_run)
    print(f"  New version: {version}")

    print("[sync] Checking consistency...")
    issues = check_consistency()
    if issues:
        print(f"  [WARN] {len(issues)} consistency issues:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"  All consistent")

    return {
        'version': version,
        'issues': issues,
    }
