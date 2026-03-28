#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正後的智能場地解析器
解決單位混淆、容量混亂、尺寸缺失等問題
"""

import re
from typing import Dict, List, Optional, Tuple


class CorrectedVenueParser:
    """修正後的場地解析器"""

    def __init__(self):
        pass

    def parse_capacity_table_row(self, row_text: str) -> Optional[Dict]:
        """
        解析晶華酒店風格的容量表格

        表格格式：
        場地 | 尺寸(sqm/sqft) | 高度(m) | 前台 | 宴會 | 劇院 | 自助餐 | 課堂 | 歌廳 | U-蹄形
        貴賓廳 | 776 / 8508 | 2.3 | 580 | 576 | 700 | - | 429 | - | -
        """
        parts = [p.strip() for p in row_text.split('|')]

        if len(parts) < 8:
            return None

        # 跳過標題行
        if parts[0] in ['場地', '功能空間', '晶英會']:
            return None

        venue_name = parts[0].strip()

        # 解析尺寸：776 / 8508 (sqm / sqft)
        size_text = parts[1]
        sqm, sqft = self._parse_size_dual_unit(size_text)

        # 高度
        ceiling = self._safe_float(parts[2])

        # 容量：前台 | 宴會 | 劇院 | 自助餐 | 課堂 | 歌廳 | U-蹄形
        capacity = {
            'reception': self._safe_int(parts[3]),   # 前台/招待會
            'banquet': self._safe_int(parts[4]),     # 宴會/圓桌式
            'theater': self._safe_int(parts[5]),     # 劇院式
            'buffet': self._safe_int(parts[6]),      # 自助餐式
            'classroom': self._safe_int(parts[7]),   # 課堂式
            'cocktail': self._safe_int(parts[8]) if len(parts) > 8 else None,  # 歌廳/雞尾酒會
            'u_shape': self._safe_int(parts[9]) if len(parts) > 9 else None,  # U-蹄形
        }

        # 過滤掉 None 值
        capacity = {k: v for k, v in capacity.items() if v is not None}

        if not venue_name or not sqm:
            return None

        return {
            'name': venue_name,
            'sqm': sqm,
            'sqft': sqft,
            'area_ping': round(sqm / 3.3058, 2) if sqm else None,
            'ceiling': ceiling,
            'capacity': capacity,
            'raw_text': row_text
        }

    def _parse_size_dual_unit(self, text: str) -> Tuple[Optional[float], Optional[int]]:
        """
        解析雙單位尺寸：776 / 8508 (sqm / sqft)

        Returns:
            (sqm, sqft)
        """
        # 移除多餘空白
        text = text.strip()

        # 匹配：數字 / 數字
        match = re.match(r'(\d+(?:\.\d+)?)\s*/\s*(\d+)', text)
        if match:
            sqm = float(match.group(1))
            sqft = int(match.group(2))
            return sqm, sqft

        # 如果只有一個數字
        match = re.match(r'(\d+(?:\.\d+)?)', text)
        if match:
            value = float(match.group(1))
            # 判斷是 sqm 或 sqft
            if value > 1000:  # 可能是 sqft
                return round(value / 10.764, 2), int(value)
            else:  # 可能是 sqm
                return value, round(value * 10.764)

        return None, None

    def parse_dimensions_text(self, text: str) -> Dict[str, Optional[float]]:
        """
        解析尺寸文字：31.8 × 24.4 × 2.3 公尺（長×寬×高）

        Returns:
            {'length': 31.8, 'width': 24.4, 'ceiling': 2.3}
        """
        result = {'length': None, 'width': None, 'ceiling': None}

        # 匹配：數字 × 數字 × 數字 公尺
        pattern = r'(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*[公米m]'
        match = re.search(pattern, text)

        if match:
            result['length'] = float(match.group(1))
            result['width'] = float(match.group(2))
            result['ceiling'] = float(match.group(3))

        return result

    def parse_equipment_list(self, html: str) -> List[str]:
        """
        解析設備清單

        從 HTML 中提取設備資訊：
        - 投影設備
        - 音響系統
        - 麥克風
        - 免費高速上網
        """
        equipment = []

        # 常見設備關鍵詞
        equipment_keywords = [
            '投影設備', '投影機', '投影',
            '音響系統', '音響', '擴音系統',
            '麥克風', '微風', 'microphone',
            '免費上網', '免費高速上網', 'WiFi', 'Wi-Fi', 'wifi',
            '舞台燈光', '燈光',
            '白板', '會議設備',
            '投影幕', '投影布幕',
            '液晶投影機', 'LCD',
        ]

        text_lower = html.lower()

        for keyword in equipment_keywords:
            if keyword.lower() in text_lower or keyword in html:
                if keyword not in equipment:
                    equipment.append(keyword)

        return equipment

    def extract_room_from_html_section(self, section_html: str, venue_name: str) -> Optional[Dict]:
        """
        從 HTML 區塊中提取場地完整資訊

        Args:
            section_html: 場地的 HTML 區塊
            venue_name: 場地名稱（如：貴賓廳）
        """
        room = {
            'name': venue_name,
            'nameEn': '',
            'floor': None,
            'area': None,
            'areaUnit': '坪',
            'sqm': None,
            'sqft': None,
            'ceiling': None,
            'length': None,
            'width': None,
            'dimensions': '',
            'pillar': False,
            'pillarCount': 0,
            'hasWindow': True,
            'shape': '長方形',
            'capacity': {
                'theater': None,
                'classroom': None,
                'banquet': None,
                'reception': None,
            },
            'equipment': [],
            'features': [],
            'images': [],
            'notes': ''
        }

        # 1. 提取面積資訊
        area_info = self._extract_area_from_html(section_html)
        if area_info:
            room.update(area_info)

        # 2. 提取尺寸資訊
        dimensions = self.parse_dimensions_text(section_html)
        if dimensions['length']:
            room['length'] = dimensions['length']
            room['width'] = dimensions['width']
            room['ceiling'] = dimensions['ceiling']
            room['dimensions'] = f"{dimensions['length']}×{dimensions['width']}×{dimensions['ceiling']}m"

        # 3. 提取容量資訊
        capacity = self._extract_capacity_from_html(section_html)
        if capacity:
            room['capacity'].update(capacity)

        # 4. 提取設備
        room['equipment'] = self.parse_equipment_list(section_html)

        # 5. 提取特色
        room['features'] = self._extract_features_from_html(section_html)

        # 6. 提取描述文字
        description = self._extract_description_from_html(section_html)
        if description:
            room['notes'] = description[:200]

        return room

    def _extract_area_from_html(self, html: str) -> Optional[Dict]:
        """從 HTML 提取面積資訊"""
        # 匹配：235 坪 或 777 平方米
        patterns = [
            r'(\d+(?:\.\d+)?)\s*坪',
            r'(\d+(?:\.\d+)?)\s*平方公尺',
            r'(\d+(?:\.\d+)?)\s*sqm',
            r'約\s*(\d+(?:\.\d+)?)\s*平方米',
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                value = float(match.group(1))

                # 判斷單位
                if '坪' in match.group(0):
                    sqm = round(value * 3.3058, 2)
                    return {'area': value, 'sqm': sqm}
                else:
                    ping = round(value / 3.3058, 2)
                    return {'area': ping, 'sqm': value}

        return None

    def _extract_capacity_from_html(self, html: str) -> Optional[Dict]:
        """從 HTML 提取容量資訊"""
        capacity = {}

        # 匹配：劇院式 700 人
        patterns = {
            'theater': r'劇院式[：:]\s*(\d+)',
            'classroom': r'課桌式[：:]\s*(\d+)|課堂式[：:]\s*(\d+)',
            'banquet': r'圓桌式[：:]\s*(\d+)|宴會式[：:]\s*(\d+)',
            'reception': r'招待會[：:]\s*(\d+)|前台[：:]\s*(\d+)',
            'u_shape': r'U型[：:]\s*(\d+)|U-蹄形[：:]\s*(\d+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, html)
            if match:
                capacity[key] = int(match.group(1))

        return capacity if capacity else None

    def _extract_features_from_html(self, html: str) -> List[str]:
        """從 HTML 提取特色"""
        features = []

        feature_keywords = {
            '無柱設計': r'無柱',
            '挑高': r'挑高',
            '落地窗': r'落地窗',
            '自然採光': r'自然採光|陽光',
            '可合併': r'可合併|可個別預訂',
        }

        for feature, pattern in feature_keywords.items():
            if re.search(pattern, html):
                features.append(feature)

        return features

    def _extract_description_from_html(self, html: str) -> Optional[str]:
        """從 HTML 提取描述文字"""
        # 移除 HTML 標籤
        text = re.sub(r'<[^>]+>', ' ', html)
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text).strip()

        # 尋找包含場地特質的句子
        sentences = text.split('。')
        for sentence in sentences:
            if any(kw in sentence for kw in ['間', '可', '適合', '提供', '設有']):
                return sentence.strip()

        return text[:100] if len(text) > 50 else None

    def _safe_int(self, s: str) -> Optional[int]:
        """安全轉整數"""
        if not s or s == '-':
            return None
        try:
            return int(re.sub(r'[^\d]', '', str(s)))
        except:
            return None

    def _safe_float(self, s: str) -> Optional[float]:
        """安全轉浮點數"""
        if not s or s == '-':
            return None
        try:
            return float(re.sub(r'[^\d.]', '', str(s)))
        except:
            return None


def test_corrected_parser():
    """測試修正後的解析器"""
    parser = CorrectedVenueParser()

    print("="*70)
    print("測試 1: 解析容量表格行")
    print("="*70)

    # 晶華酒店官網實際數據
    test_row = "貴賓廳|776 / 8508|2.3|580|576|700|-|429|-|-"

    result = parser.parse_capacity_table_row(test_row)
    if result:
        print(f"場地名: {result['name']}")
        print(f"面積: {result['sqm']} 平方米 ({result['sqft']} 平方英尺)")
        print(f"坪數: {result['area_ping']} 坪")
        print(f"高度: {result['ceiling']} 米")
        print(f"容量: {result['capacity']}")
    else:
        print("❌ 解析失敗")

    print("\n" + "="*70)
    print("測試 2: 解析尺寸文字")
    print("="*70)

    dimension_text = "31.8 × 24.4 × 2.3 公尺（長×寬×高）"
    dimensions = parser.parse_dimensions_text(dimension_text)

    print(f"長: {dimensions['length']} 米")
    print(f"寬: {dimensions['width']} 米")
    print(f"高: {dimensions['ceiling']} 米")

    print("\n" + "="*70)
    print("測試 3: 解析設備清單")
    print("="*70)

    equipment_html = """
    除了會議文具用品之外，各個場地皆設有免費高速上網及視聽配備，
    包括兩組麥克風、投影設備和音響系統。
    """

    equipment = parser.parse_equipment_list(equipment_html)
    print(f"設備: {', '.join(equipment)}")

    print("\n" + "="*70)
    print("測試 4: 驗證正確性")
    print("="*70)

    # 驗證面積轉換
    sqm = 777
    expected_ping = round(sqm / 3.3058, 2)
    actual_ping = 235

    print(f"正確計算: {sqm} 平方米 = {expected_ping} 坪")
    print(f"網頁顯示: {actual_ping} 坪")
    status = "OK" if abs(expected_ping - actual_ping) < 1 else "ERROR"
    print(f"差異: {abs(expected_ping - actual_ping):.2f} 坪 ({status})")


if __name__ == '__main__':
    test_corrected_parser()
