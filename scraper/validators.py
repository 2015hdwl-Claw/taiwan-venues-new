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


def is_valid_room_name(name: str) -> bool:
    """
    檢查名稱是否像合理的場地/會議室名稱。
    排除行銷文案、價格資料、表頭、表單欄位等。

    層層過濾：
    1. 基本格式（長度、空白）
    2. 文案/句子特徵（標點、行銷詞）
    3. 非名稱特徵（價格、時間、表頭、序號）
    4. 餐廳/非會議空間
    """
    if not name or len(name.strip()) < 2:
        return False

    s = name.strip()

    # === 1. 長度限制 ===
    # 場地名稱通常 2-30 字，極少超過 40
    if len(s) > 40:
        return False
    # 太短的單字（如 "的"、"看"）不是房間名
    if len(s) < 2:
        return False

    # === 2. 文案/句子特徵 ===
    # 句式標點
    if '。' in s or '！' in s or '？' in s or '；' in s:
        return False
    if s.endswith('...') or s.endswith('…'):
        return False
    # 換行符 → 多行文字
    if '\n' in s or '\r' in s:
        return False

    # 行銷動詞/代名詞
    marketing_words = [
        '邀請', '重新定義', '誠摯', '立即', '享受', '體驗',
        '歡迎您', '我們的', '為您', '讓您', '本公司',
        '了解更多', '立即前往', '馬上預約', '免費',
        '讚不絕口', '饕客', '招牌', '盡在', '搭配',
        '重溫', '絢麗', '查看', '適用', '選擇', '推薦',
        '回憶', '美好', '幸福', '浪漫', '夢幻',
        # 非場地描述詞
        '一覽', '行事曆', '分類', '擁有', '館內',
        '文具', '介紹', '說明', '專案', '方案',
    ]
    for w in marketing_words:
        if w in s:
            return False

    # 「的」字密度過高 → 文案
    if s.count('的') >= 2:
        return False

    # 過多逗號/頓號 → 段落
    punctuation_count = sum(1 for c in s if c in '，、；：,;:')
    if punctuation_count >= 3:
        return False

    # 全中文但超過 20 字 → 可能是文案（除非是很正式的名稱）
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', s))
    if cn_chars > 20:
        # 只有純粹的「XXX廳」格式才能超過 20 字
        has_room_kw = any(kw in s for kw in ['廳', '室', '館', 'Hall', 'Room'])
        if not has_room_kw:
            return False
        # 即使有廳/室，超過 20 字仍要檢查是否像文案
        if any(c in s for c in ['的', '了', '讓', '在', '有', '是']):
            return False

    # === 3. 非名稱特徵 ===

    # 以價格開頭或含大量價格數字 → 不是房間名
    if re.match(r'^[\$NTnt￥]', s):
        return False
    # 含貨幣符號和數字 → 價格資料
    if re.search(r'NT\$|NTD|\$.*\d{3,}', s, re.IGNORECASE):
        return False
    # 多個 4 位數以上數字（如 "宴會A廳(一) 116 384 250 250 150 $"）
    big_numbers = re.findall(r'\d{3,}', s)
    if len(big_numbers) >= 3:
        return False
    # 以數字+價格結尾（如 "全廳 450 700 450 300 $"）
    if re.search(r'\d+\s*\$?\s*$', s):
        return False

    # 純時間格式 → 不是房間名（如 "下午14:00-17:00", "全日"）
    if re.match(r'^(?:上午|下午|晚上|早上|全日|整天|夜間)\s*\d', s):
        return False
    if re.match(r'^\d{1,2}:\d{2}', s):
        return False
    # "全日" 或 "夜間進場" 之類
    if re.match(r'^(全日|整天|夜間|隔夜|半日)', s):
        return False

    # 表頭/欄位名（如 "廳別", "教室型(位)", "坪數"）
    header_words = [
        '廳別', '坪數', '平方公尺', '宴會型', '劇院型', '教室型',
        '樓層', '面積', '價格', '費用', '收費標準', '計費',
        '容納', '人數', '設備', '樓高', '尺寸', '備註',
        '欄位', '項目', '內容', '說明',
        'Theatre', 'Classroom', 'Hollow', 'Cocktail', 'Sq.Meters',
    ]
    s_lower = s.lower()
    for hw in header_words:
        if s_lower == hw.lower() or s.startswith(hw):
            return False

    # 序號開頭 → 可能是表單（如 "4. 燈效設備...", "三、申請日期"）
    if re.match(r'^[一二三四五六七八九十]+[、．.]', s):
        return False
    if re.match(r'^\d+[、．.)）]', s):
        return False

    # 表單欄位（如 "以下由場館填寫", "申請日期"）
    form_words = ['以下由', '申請', '填寫', '簽名', '蓋章', '附件', '備註欄']
    for fw in form_words:
        if s.startswith(fw):
            return False

    # 只剩價格（如 "12,000元", "6,000元"）
    if re.match(r'^[\d,]+\s*元?$', s):
        return False

    # === 3.5 句子片段/語法特徵 ===
    # 以虛詞/動詞開頭 → 句子片段（如 "的會議中心", "是臺灣最大", "配合貴賓"）
    bad_starts = [
        '的', '是', '在', '有', '讓', '被', '把', '將', '對', '為',
        '個', '配合', '包含', '同步', '提供', '位於', '位在',
        '關於', '對於', '透過', '經由', '由於', '隨著',
        '※', '※',
    ]
    for bs in bad_starts:
        if s.startswith(bs):
            return False

    # URL/電話 → 不是房間名
    if 'www.' in s or '.com' in s or '.tw' in s or 'http' in s:
        return False
    if 'TEL' in s.upper() or re.search(r'\d{2}-\d{4}', s):
        return False

    # 特殊字元 → 網頁片段（如 "民權館∣T (02)", "0%"）
    if any(c in s for c in ['∣', '%', '※', '→', '←', '※']):
        return False

    # 純數字+單位 → 不是名稱（如 "0%", "450人演講廳" 的片段 "人演講廳"）
    if re.match(r'^\d+%', s):
        return False

    # 太短的泛稱（如 "會議", "全館", "各廳", "教室", "間廳"）
    too_generic = [
        '會議', '宴會', '全館', '各廳', '教室', '間廳', '看廳',
        '大廳', '內室', '會館', '全場', '全廳', '餐廳',
        '婚宴會館', 'Jenny',
    ]
    if s in too_generic:
        return False

    # === 3.6 更嚴格的「室」/「館」排除 ===
    # 非會議室類型的「室」
    not_room_types = [
        '休息室', '工作室', '辦公室', '王室', '浴室', '臥室',
        '化妝室', '更衣室', '吸菸室', '哺乳室',
    ]
    for nrt in not_room_types:
        if s.endswith(nrt):
            return False

    # 非單一場地的「館」（整棟建築或其他會館）
    if s.endswith('會館') and len(s) > 4:
        # "XX會館" 且長度>4 通常是獨立場地名，不是某場地內的房間
        # 例外：如果是 "1F宴會會館" 之類帶樓層的才保留
        if not re.search(r'\d+[F樓]', s):
            return False

    # 路徑分隔符 → 網頁片段（如 "科技生活館/我在..."）
    if '/' in s:
        return False

    # 純英文單字/人名（如 "Jenny"）→ 不是房間名
    if re.match(r'^[A-Za-z]+$', s) and len(s) < 10:
        return False

    # 以「人」開頭的演講廳 → 片段（"450人演講廳" → "人演講廳"）
    if re.match(r'^人[演會議]', s):
        return False

    # 以「找」開頭 → 行銷導向
    if s.startswith('找'):
        return False

    # 以「你」開頭 → 文案
    if s.startswith('你'):
        return False

    # 「店內」→ 店面描述（如 "店內共有龍鳳廳"）
    if s.startswith('店內'):
        return False

    # 包含「共有」→ 描述性（如 "店內共有龍鳳廳"）
    if '共有' in s:
        return False

    # 純數字+人+廳室 → 片段
    if re.match(r'^\d+人', s):
        return False

    # 設計/工作室 → 非會議
    if '設計' in s and '工作室' in s:
        return False

    # 王室 → 政治描述
    if s.endswith('王室') or s.endswith('皇室'):
        return False

    # 旗艦 → 商店
    if '旗艦' in s:
        return False

    # 「多間」→ 描述數量不是名稱
    if s.startswith('多間'):
        return False

    # 「登編」→ 登記描述
    if s.startswith('登編'):
        return False

    # 展覽館 作為獨立場地名（如 "南港展覽館"）→ 不是某場地內的房間
    if re.match(r'^[\u4e00-\u9fff]{2,}展覽館$', s):
        return False

    # 旅館 → 整棟建築不是房間
    if s.endswith('旅館'):
        return False

    # === 4. 餐廳/非會議空間 ===
    restaurant_words = [
        '中餐廳', '西餐廳', '餐廳', '咖啡廳', '咖啡', '餐酒館',
        'Restaurant', 'Café', 'Cafe', 'Bistro', 'Bar',
    ]
    # 通用標籤（不是特定房間名稱）
    generic_labels = [
        'Banquet Rooms', 'Meeting Rooms', 'Function Rooms',
        '宴會廳Banquet', '會議廳Meeting',
    ]
    for gl in generic_labels:
        if gl.lower() in s_lower:
            return False
    for rw in restaurant_words:
        if rw.lower() in s_lower:
            # 但 "宴會廳" 或 "會議廳" 包含 "廳" 不算餐廳
            if '宴會' in s or '會議' in s or '展覽' in s:
                continue
            return False

    return True


def is_meeting_room(name: str, existing_data: dict = None) -> bool:
    """
    判斷是否為會議室（排除客房）

    規則：
    0. is_valid_room_name → False（非合理名稱）
    1. EXCLUDE_ROOM_KEYWORDS → False（客房）
    2. 通用名 + 有實際資料 → True
    3. 通用名 + 無資料 → False
    4. CONFIRM_ROOM_KEYWORDS → True
    5. 有樓層標記 → True
    6. 有實際容量/面積資料 → True（信任已有資料）
    7. 名稱含英文字母+數字組合（如 101A/D, 201AB）→ True（會議室配置）
    8. 其他 → False（保守排除）
    """
    if not is_valid_room_name(name):
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
