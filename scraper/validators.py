#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/validators.py - 驗證器
客房排除、合理性檢查、品質評分
"""

import re
from .config import (
    EXCLUDE_ROOM_KEYWORDS, GENERIC_ROOM_NAMES, CONFIRM_ROOM_KEYWORDS,
    FLOOR_PATTERN, QUALITY_WEIGHTS, QUALITY_LEVELS,
)


def is_meeting_room(name: str, existing_data: dict = None) -> bool:
    """
    判斷是否為會議室（排除客房）

    規則：
    1. EXCLUDE_ROOM_KEYWORDS → False（客房）
    2. 通用名 + 有實際資料 → True
    3. 通用名 + 無資料 → False
    4. CONFIRM_ROOM_KEYWORDS → True
    5. 有樓層標記 → True
    6. 有實際容量/面積資料 → True（信任已有資料）
    7. 名稱含英文字母+數字組合（如 101A/D, 201AB）→ True（會議室配置）
    8. 其他 → False（保守排除）
    """
    if not name or len(name.strip()) < 2:
        return False

    name_stripped = name.strip()
    name_lower = name_stripped.lower()

    # Rule 1: 排除客房
    for kw in EXCLUDE_ROOM_KEYWORDS:
        if kw.lower() in name_lower:
            return False

    # Rule 2/3: 通用名稱需要額外驗證
    is_generic = any(kw.lower() == name_lower for kw in GENERIC_ROOM_NAMES)
    if is_generic:
        # 如果有容量資料，可能是真的會議室
        if existing_data:
            cap = existing_data.get('capacity', {})
            if isinstance(cap, dict) and cap.get('theater') and cap['theater'] > 0:
                return True
        return False

    # Rule 4: 確認會議室關鍵字
    for kw in CONFIRM_ROOM_KEYWORDS:
        if kw.lower() in name_lower:
            return True

    # Rule 5: 樓層標記（如 "7F 超新星宴會廳"）
    if re.search(FLOOR_PATTERN, name_stripped):
        return True

    # Rule 6: 有實際容量/面積資料 → 信任已有資料
    if existing_data:
        cap = existing_data.get('capacity', {})
        if isinstance(cap, dict) and cap.get('theater') and cap['theater'] > 0:
            return True
        if existing_data.get('area') or existing_data.get('areaSqm') or existing_data.get('areaPing'):
            return True

    # Rule 7: 會議室配置名（如 101A/D, 201AB/EF, 大會堂全場）
    if re.match(r'^\d{2,3}[A-Z]', name_stripped):
        return True
    if re.search(r'[全半]場', name_stripped):
        return True
    # 英文單字（宴會廳名如 Spring, Fortune, Garden）
    if re.match(r'^[A-Z][a-z]+(?:\s[A-Za-z]+)*$', name_stripped):
        return True

    # Rule 8: 保守排除
    return False


def calculate_room_quality(room: dict) -> int:
    """計算會議室品質分數（0-100）"""
    score = 0

    # 名稱（非通用名）
    name = room.get('name', '')
    if name and not any(kw.lower() == name.lower() for kw in GENERIC_ROOM_NAMES):
        score += QUALITY_WEIGHTS['has_name']

    # 容量
    cap = room.get('capacity', {})
    if isinstance(cap, dict) and cap.get('theater'):
        score += QUALITY_WEIGHTS['has_capacity']

    # 面積
    if room.get('area') or room.get('areaSqm') or room.get('areaPing'):
        score += QUALITY_WEIGHTS['has_area']

    # 價格
    price = room.get('price')
    if price and isinstance(price, dict) and (price.get('weekday') or price.get('note')):
        score += QUALITY_WEIGHTS['has_price']

    # 照片
    images = room.get('images', {})
    if isinstance(images, dict) and images.get('main'):
        score += QUALITY_WEIGHTS['has_image']

    # 設備
    if room.get('equipment') or room.get('equipmentList'):
        score += QUALITY_WEIGHTS['has_equipment']

    # 樓層
    if room.get('floor'):
        score += QUALITY_WEIGHTS['has_floor']

    # 尺寸
    dims = room.get('dimensions', {})
    if isinstance(dims, dict) and dims.get('length'):
        score += QUALITY_WEIGHTS['has_dimensions']

    return min(score, 100)


def get_quality_level(score: int) -> str:
    """取得品質等級"""
    if score >= QUALITY_LEVELS['high']:
        return 'high'
    elif score >= QUALITY_LEVELS['medium']:
        return 'medium'
    return 'low'


def validate_capacity(capacity: dict) -> bool:
    """容量合理性：5-5000 人"""
    if not isinstance(capacity, dict):
        return False
    for key in ['theater', 'banquet', 'classroom', 'uShape', 'cocktail']:
        val = capacity.get(key)
        if val is not None:
            if not isinstance(val, (int, float)) or val < 5 or val > 5000:
                return False
    return True


def validate_area(area: float) -> bool:
    """面積合理性：5-10000"""
    if area is None:
        return False
    return 5 <= area <= 10000


def merge_room(existing: dict, new_data: dict) -> dict:
    """
    合併新舊資料，舊資料優先（如果已有正確值）
    """
    merged = dict(existing)
    for key, new_val in new_data.items():
        old_val = merged.get(key)
        if old_val is None or old_val == '' or old_val == {} or old_val == []:
            merged[key] = new_val
    return merged
