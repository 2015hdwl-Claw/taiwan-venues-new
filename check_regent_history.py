#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查晶華飯店會議室資料歷史
"""
import json
import sys
import io
import subprocess

# 設置 UTF-8 編碼輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 獲取指定 commit 的 venues.json
commit_hash = "6b212a1"
result = subprocess.run(
    ['git', 'show', f'{commit_hash}:venues.json'],
    capture_output=True,
    text=True,
    encoding='utf-8'
)

if result.returncode == 0:
    data = json.loads(result.stdout)
    for v in data:
        if v.get('id') == 1086:
            print(f'=== Commit {commit_hash} (2026-03-17 批次添加) ===')
            print(f'場地: {v.get("name")}')
            print(f'會議室數量: {len(v.get("rooms", []))}')
            print()
            for i, room in enumerate(v.get('rooms', []), 1):
                print(f'{i}. {room.get("name")} ({room.get("id")})')
                print(f'   面積: {room.get("area")} {room.get("areaUnit", "")}')
                print(f'   容量: {room.get("capacity")}')
                img = room.get('images', {}).get('main', '')
                if img:
                    print(f'   照片: {img[:60]}...')
                else:
                    print(f'   照片: 無')
                print()
            break
else:
    print(f'Error: {result.stderr}')
