#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/constants.py — 統一常數定義
費率表、估算係數、場地分類、前端 schema 規則

所有魔術數字只存在這裡，其他模組一律 import
"""

import os

# === 專案路徑 ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')
VENUES_TAIPEI_FILE = os.path.join(PROJECT_ROOT, 'venues_taipei.json')
JS_FILES = [
    os.path.join(PROJECT_ROOT, 'app.js'),
    os.path.join(PROJECT_ROOT, 'venue.js'),
    os.path.join(PROJECT_ROOT, 'room.js'),
]

# === Area 估算係數（每人佔用 sqm，已驗證）===
AREA_RATIOS = {
    'theater': 0.9,      # 劇院式：0.9 sqm/人
    'banquet': 1.5,       # 宴會式：1.5 sqm/人
    'classroom': 1.3,     # 教室式：1.3 sqm/人
    'ushape': 2.0,        # U型：2.0 sqm/人
    'reception': 0.6,     # 酒會：0.6 sqm/人
    'cocktail': 0.6,      # 雞尾酒：0.6 sqm/人
}
SQM_TO_PING = 3.3058     # 1 坪 = 3.3058 sqm
AREA_ROUND = 0.5         # 四捨五入到 0.5 坪

# === Price 費率表（元/坪/halfDay，從已驗證場地統計）===
PRICE_RATES = {
    '政府': {'rate': 200, 'unit': '元/坪/halfDay', 'note': '政府機關場地，公務機關享8折優惠'},
    '集思': {'rate': 250, 'unit': '元/坪/halfDay', 'note': '價格需洽詢'},
    '一般飯店': {'rate': 600, 'unit': '元/坪/halfDay', 'note': '價格需洽詢'},
    '婚宴場地': {'rate': 650, 'unit': '元/坪/halfDay', 'note': '價格需洽詢'},
    '奢華飯店': {'rate': 1000, 'unit': '元/坪/halfDay', 'note': '價格需洽詢'},
    '展演場地': {'rate': 400, 'unit': '元/坪/halfDay', 'note': '價格需洽詢'},
    '會議中心': {'rate': 500, 'unit': '元/坪/halfDay', 'note': '價格需洽詢'},
    'default': {'rate': 500, 'unit': '元/坪/halfDay', 'note': '價格需洽詢'},
}

# === 場地類型 → 費率分類對照 ===
VENUE_TYPE_TO_RATE = {
    '飯店場地': '一般飯店',
    '婚宴場地': '婚宴場地',
    '展演場地': '展演場地',
    '會議中心': '會議中心',
}

# === 特定場地的費率覆蓋（ID → rate key）===
VENUE_RATE_OVERRIDES = {
    1042: '政府',        # 公務人力發展學院
    1043: '一般飯店',     # 六福萬怡
    1049: '會議中心',     # 世貿中心
    1051: '一般飯店',     # 亞都麗緻
    1085: '奢華飯店',     # 文華東方
    1086: '一般飯店',     # 晶華
    1095: '一般飯店',     # 美福
    1103: '一般飯店',     # 萬豪
    1072: '一般飯店',     # 圓山（非奢華，但有歷史溢價）
}

# === 費率調整係數（大場地通常單價較低）===
def get_rate_per_ping(area_ping: float, rate_key: str) -> int:
    """
    根據面積和場地類型，回傳 halfDay 單價（元/坪）
    大場地（>100坪）享 8 折，小場地（<20坪）加 2 成
    """
    base = PRICE_RATES.get(rate_key, PRICE_RATES['default'])['rate']
    if area_ping > 100:
        base = int(base * 0.8)
    elif area_ping < 20:
        base = int(base * 1.2)
    return base

# === 前端 schema 規則（驗證用）===
REQUIRED_ROOM_FIELDS = ['id', 'name']
OPTIONAL_ROOM_FIELDS = ['capacity', 'area', 'areaUnit', 'floor', 'pricing',
                        'equipment', 'images', 'ceilingHeight', 'source']

# 前端期望的格式
SCHEMA_RULES = {
    'equipment_must_be_array': True,
    'pricing_must_have_half_or_full': True,
    'area_unit_must_be_ping': True,
    'images_must_be_dict': True,  # {"main": "url", "gallery": ["url"]}
}

# === 預設 equipment（補齊用）===
DEFAULT_EQUIPMENT = ["投影設備", "音響系統", "無線網路"]

# === 容量合理性範圍 ===
CAPACITY_RANGE = (5, 20000)      # 高雄巨蛋 15000 人
AREA_RANGE = (3, 10000)          # 坪；高雄巨蛋 5445 坪
PRICE_RANGE = (1000, 5000000)    # halfDay/fullDay 元；巨蛋 2.1M/4.3M
