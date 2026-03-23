#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
追蹤晶華飯店照片變化歷史
"""
import json
import sys
import io
import subprocess

# 設置 UTF-8 編碼輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

commits = [
    ("6b212a1", "2026-03-17 批次添加會議室"),
    ("193a5a7", "2026-03-17 更新 9 間重點飯店會議室"),
    ("79f6a86", "2026-03-18 為 9 間飯店會議室添加照片"),
    ("2170a07", "2026-03-23 Add photos to 7 Taipei hotels"),
]

for commit_hash, desc in commits:
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
                print(f'\n=== {desc} ===')
                print(f'Commit: {commit_hash}')
                print()
                for i, room in enumerate(v.get('rooms', []), 1):
                    images = room.get('images')
                    if isinstance(images, dict):
                        photo = images.get('main', '無')
                    elif isinstance(images, list) and len(images) > 0:
                        photo = images[0]
                    else:
                        photo = '無'

                    if photo != '無':
                        photo_short = photo.split('/')[-1][:50]
                    else:
                        photo_short = '無'
                    print(f'{i}. {room.get("name"):8s} - 照片: {photo_short}')
                break

# 檢查當前狀態
print(f'\n=== 當前狀態 (HEAD) ===')
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    for v in data:
        if v.get('id') == 1086:
            for i, room in enumerate(v.get('rooms', []), 1):
                photo = room.get('photo', '無')
                if photo and photo != '無':
                    photo_short = photo.split('/')[-1][:50]
                else:
                    photo_short = '無'
                print(f'{i}. {room.get("name"):8s} - 照片: {photo_short}')
            break
