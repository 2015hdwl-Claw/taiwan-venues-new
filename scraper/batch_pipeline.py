#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次 pipeline fix + knowledge
"""

import sys
import subprocess
import time

# 有資料的場地 ID（排除 0 房的 1083, 1085, 1090, 1099）
VENUE_IDS = [
    1043, 1045, 1049, 1051, 1053, 1075, 1076, 1077, 1086, 1095, 1100,
    1122, 1124, 1126, 1128, 1129, 1334, 1448, 1493, 1494, 1495, 1500, 1501
]

def main():
    print(f"Processing {len(VENUE_IDS)} venues...")
    print("="*60)

    for vid in VENUE_IDS:
        print(f"\n[{vid}] Fix + Knowledge...")

        # Fix
        result = subprocess.run(
            [sys.executable, "tools/pipeline.py", "fix", "--venue", str(vid)],
            capture_output=True,
            encoding='utf-8',
            errors='ignore',
            timeout=60
        )
        if result.returncode != 0:
            print(f"  Fix failed: {result.stderr[:100]}")

        # Knowledge
        result = subprocess.run(
            [sys.executable, "tools/pipeline.py", "knowledge", "--venue", str(vid), "--save"],
            capture_output=True,
            encoding='utf-8',
            errors='ignore',
            timeout=60
        )
        if result.returncode != 0:
            print(f"  Knowledge failed: {result.stderr[:100]}")
        else:
            # Extract summary
            lines = result.stdout.split('\n')
            for line in lines:
                if 'rules' in line.lower() or 'rule' in line.lower():
                    print(f"  {line.strip()[:80]}")
                    break

    print(f"\n{'='*60}")
    print("Done!")

if __name__ == "__main__":
    main()
