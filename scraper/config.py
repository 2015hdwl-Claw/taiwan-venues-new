#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/config.py - 統一爬蟲配置
所有常數定義，不包含邏輯
"""

# === 客房排除關鍵字（出現 = 客房，不是會議室）===
EXCLUDE_ROOM_KEYWORDS = [
    '客房', 'Superior Room', 'Deluxe Room', 'Suite',
    '標準房', '豪華房', '家庭房', '雙人房', '單人房',
    'Our Rooms',
]

# === 通用名稱（需要額外驗證）===
GENERIC_ROOM_NAMES = [
    'Meeting Room', 'Conference Room', 'Function Room',
]

# === 會議室確認關鍵字 ===
CONFIRM_ROOM_KEYWORDS = [
    '會議', '宴會', '展覽', '演講', '活動', '廳', '室', '館',
    'Meeting', 'Banquet', 'Ballroom', 'Hall', 'Conference', 'Venue',
    'Center', 'Room',  # 搭配樓層等確認
]

# === 樓層模式（如 "7F", "3樓" 表示是實體空間）===
FLOOR_PATTERN = r'(\d+[F樓])'

# === 會議相關 URL 路徑 ===
MEETING_URL_PATTERNS = [
    '/meeting', '/meetings', '/banquet', '/banquets',
    '/events', '/mice', '/conference', '/venue',
    '/zh-TW/meeting', '/tw/meeting', '/en/meeting',
    '/facility', '/space', '/wedding',
    '/venue/room-info',
    '/wedding/meeting', '/wedding/banquet',
    '/zh-TW/banquet', '/zh-TW/meetings',
    '/en/banquet', '/en/meetings',
]

# === 導航關鍵字 ===
MEETING_NAV_KEYWORDS = [
    '會議', '宴會', '場地', '活動', 'MICE', '婚宴',
    'Meeting', 'Banquet', 'Events', 'Conference', 'Venue',
    'Wedding', 'Ballroom', 'Function',
]

# === PDF 關鍵字（用於發現價目表 PDF）===
PDF_KEYWORDS = [
    '價目', '價格', '收費', '場地', '會議室', '容量',
    'price', 'rate', 'venue', 'meeting', 'capacity', 'floor plan',
]

# === HTTP 請求 headers ===
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

# === JS 框架偵測 ===
JS_FRAMEWORK_SIGNATURES = {
    'React': ['react', 'reactdom', 'react-dom'],
    'Vue': ['vue', 'vuetify', 'nuxt'],
    'Angular': ['angular', 'ng-'],
    'jQuery': ['jquery', 'jquery.min'],
    'Next.js': ['_next/', 'next.js'],
    'Wix': ['wix', 'parastorage'],
    'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
    'Drupal': ['drupal', 'sites/default'],
    'Squarespace': ['squarespace'],
}

# === 品質評分權重 ===
QUALITY_WEIGHTS = {
    'has_name': 10,
    'has_capacity': 15,
    'has_area': 15,
    'has_price': 20,
    'has_image': 20,
    'has_equipment': 10,
    'has_floor': 5,
    'has_dimensions': 5,
}

QUALITY_LEVELS = {
    'high': 70,     # ≥ 70: 可直接使用
    'medium': 40,   # ≥ 40: 需補充
    # < 40: 需重新爬取
}
