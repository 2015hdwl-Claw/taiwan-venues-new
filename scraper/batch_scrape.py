#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次爬蟲 - 指定場地 ID 列表
"""

import sys
import subprocess
import time

# 27 個台北市場地 ID（排除已測試的 1042, 1072, 1103, 1125 和失敗的 1057）
# 已處理: 1043, 1045, 1049, 1051, 1053, 1075, 1076, 1077, 1083, 1085, 1086, 1090, 1095, 1099, 1100
VENUE_IDS = [
    1122, 1124, 1126, 1128, 1129, 1334, 1448,
    1493, 1494, 1495, 1500, 1501
]

def main():
    results = []

    for vid in VENUE_IDS:
        print(f"\n{'='*60}")
        print(f"處理場地 ID: {vid}")
        print('='*60)

        start = time.time()
        # SPA sites timeout 較長
        slow_sites = [1051, 1095, 1099, 1100, 1122, 1128, 1493, 1494]
        timeout_val = 300 if vid in slow_sites else 180
        result = subprocess.run(
            [sys.executable, "-W", "ignore", "-m", "scraper", "--test", str(vid)],
            capture_output=True,
            encoding='utf-8',
            errors='ignore',
            timeout=timeout_val
        )
        elapsed = time.time() - start

        # 檢查是否成功（輸出包含 "會議室" 或 "成功"）
        success = "會議室" in result.stdout or "成功" in result.stdout

        results.append({
            'id': vid,
            'success': success,
            'time': elapsed
        })

        # 顯示摘要
        if success:
            # 提取會議室數量
            lines = result.stdout.split('\n')
            for line in lines:
                if '會議室' in line and ('個' in line or '提取' in line):
                    safe_line = line.strip().encode('cp950', errors='ignore').decode('cp950')
                    print(f"  [OK] {safe_line}")
        else:
            print(f"  [FAIL] No data")

        # 避免 HTTP 限制
        if vid != VENUE_IDS[-1]:
            time.sleep(2)

    # 摘要
    print(f"\n{'='*60}")
    print("Summary")
    print('='*60)
    success_count = sum(1 for r in results if r['success'])
    print(f"Success: {success_count}/{len(VENUE_IDS)}")
    print(f"Failed: {len(VENUE_IDS) - success_count}")
    print(f"Total time: {sum(r['time'] for r in results):.1f}s")

if __name__ == "__main__":
    main()
