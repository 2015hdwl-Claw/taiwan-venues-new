#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一批處理：5個高優先級無照片場地
- ID 1057: 台北典華
- ID 1065: 台北唯客樂文旅
- ID 1066: 台北商務會館
- ID 1107: 台北體育館
- ID 1334: 台北中山運動中心
"""

import json
import sys
import io
from datetime import datetime

# 設置 UTF-8 編碼輸出
if hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# 讀取知識庫
with open('hotel_sources.json', 'r', encoding='utf-8') as f:
    hotel_sources = json.load(f)

print('=' * 70)
print('第一批處理：5個高優先級無照片場地')
print('=' * 70)
print()

venues = hotel_sources.get('venues', {})

for venue_id in ['1057', '1065', '1066', '1107', '1334']:
    if venue_id in venues:
        v = venues[venue_id]
        print(f"ID {v['id']}: {v['name']}")
        print(f"  官網: {v.get('base_url', '待搜尋')}")
        print(f"  狀態: {v.get('status', 'pending')}")
        print(f"  備註: {v.get('notes', '')}")
        print()

print('=' * 70)
print('處理流程：')
print('1. 爬取每個場地的官網')
print('2. 找到正確的會議/婚宴場地頁面')
print('3. 收集照片和會議室資料')
print('4. 使用統一引擎更新')
print('5. 品質檢驗')
print('6. Git提交')
print('=' * 70)
