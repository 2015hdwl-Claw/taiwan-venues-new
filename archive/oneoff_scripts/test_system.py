#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試核心系統
"""
import json
import sys
import io
from pathlib import Path

# 設置 UTF-8 編碼輸出
if hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

print('=' * 70)
print('場地更新系統 - 核心測試')
print('=' * 70)
print()

# 測試 1: 統一更新引擎
print('[測試 1] 統一更新引擎')
print('-' * 70)
from unified_updater import VenueUpdater

updater = VenueUpdater('venues.json')
print('✓ 系統載入成功')
print()

# 測試 2: 品質檢驗系統
print('[測試 2] 品質檢驗系統')
print('-' * 70)
from quality_checker import QualityChecker

checker = QualityChecker('venues.json', 'hotel_sources.json')
print('✓ 系統載入成功')

# 檢查一個場地
result = checker.check_venue(1086)
print(f"✓ 晶華飯店品質分數: {result['score']}/100")
print()

# 測試 3: 批量處理管道
print('[測試 3] 批量處理管道')
print('-' * 70)
from batch_processor import BatchProcessor

processor = BatchProcessor()
print('✓ 系統載入成功')

# 顯示待處理場地
pending = processor.get_pending_venues(priority='high', max_photos=0)
print(f'✓ 高優先級無照片場地: {len(pending)} 個')
for venue in pending:
    print(f"  - {venue['id']}: {venue['name']}")
print()

print('=' * 70)
print('所有核心系統測試通過！')
print('=' * 70)
print()
print('[系統功能]')
print('  1. VenueUpdater: 統一更新引擎')
print('  2. QualityChecker: 品質檢驗系統')
print('  3. BatchProcessor: 批量處理管道')
print()
print('[下一步]')
print('  - 使用 webReader 爬取場地官網')
print('  - 使用 updater.add_photos() 添加照片')
print('  - 使用 checker.check_venue() 檢驗品質')
print('  - 使用 processor.process_batch() 批量處理')
