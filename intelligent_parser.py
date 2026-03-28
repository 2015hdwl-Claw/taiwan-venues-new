#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能場地資料解析器
自動從原始文字中精準提取場地資訊
"""

import re
from typing import Dict, List, Optional


class VenueDataParser:
    """智能場地資料解析器"""

    def __init__(self):
        # 場地名稱關鍵詞
        self.venue_name_patterns = [
            r'([\u4e00-\u9fff]{2,8})\s*廳',
            r'([\u4e00-\u9fff]{2,8})\s*室',
            r'([A-Za-z\s]+Ballroom)',
            r'([A-Za-z\s]+Room)',
        ]

        # 數值提取模式
        self.area_patterns = [
            r'(\d+(?:\.\d+)?)\s*平方公尺',
            r'(\d+(?:\.\d+)?)\s*sqm',
            r'(\d+(?:\.\d+)?)\s*坪',
        ]

        self.capacity_patterns = [
            r'(\d{1,4})\s*人',
            r'pax[:\s]*(\d{1,4})',
            r'capacity[:\s]*(\d{1,4})',
        ]

    def parse_venue_block(self, text: str) -> List[Dict]:
        """解析一段包含場地資訊的文字"""
        venues = []

        # 1. 嘗試識別場地名稱
        venue_name = self._extract_venue_name(text)

        # 2. 提取面積
        area_sqm = self._extract_area(text)

        # 3. 提取容量
        capacity = self._extract_capacity(text)

        # 4. 提取樓層
        floor = self._extract_floor(text)

        # 5. 提取特色
        features = self._extract_features(text)

        # 如果找到有意義的資訊，建立場地
        if venue_name or (area_sqm and capacity):
            venue = {
                'name': venue_name or '會議室',
                'floor': floor,
                'area_sqm': area_sqm,
                'capacity': capacity,
                'features': features,
                'raw_text': text[:200]
            }
            venues.append(venue)

        return venues

    def _extract_venue_name(self, text: str) -> Optional[str]:
        """提取場地名稱"""

        # 專用模式
        specific_names = [
            r'(\d+[Ff][\u4e00-\u9fff]{2,6})',  # "2F茹曦廳"
            r'([\u4e00-\u9fff]{2,6})\s*[\u4e00-\u9fff]{1,3}廳',  # "茹曦廳"
            r'^([\u4e00-\u9fff]{2,6})\s*[,，]',  # 開頭就是場地名
            r'([\u4e00-\u9fff]{2,6})\s*挑高無柱',  # "茹曦廳 挑高無柱"
            r'([\u4e00-\u9fff]{2,6})\s*宴會廳',
            r'(Ballroom|Meeting Room)',
        ]

        for pattern in specific_names:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # 移除樓層標記
                name = re.sub(r'^\d+[Ff]', '', name)
                # 移除常見後綴
                name = re.sub(r'\s*挑高無柱.*$', '', name)
                name = name.strip()
                if name and len(name) >= 2:
                    return name

        # 從 notes 中提取
        if '廳別資訊' in text or '場地規格' in text:
            # 尋找 "2F 茹曦廳" 模式
            match = re.search(r'(\d+[Ff][\u4e00-\u9fff]{2,6})', text)
            if match:
                return re.sub(r'^\d+[Ff]', '', match.group(1)).strip()

        return None

    def _extract_area(self, text: str) -> Optional[float]:
        """提取面積（平方米）"""
        # 先找主要場地的面積
        for pattern in self.area_patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        return None

    def _extract_capacity(self, text: str) -> Optional[int]:
        """提取容量"""
        # 尋找最大容量
        capacities = []
        for pattern in self.capacity_patterns:
            matches = re.findall(pattern, text)
            capacities.extend([int(m) for m in matches])

        return max(capacities) if capacities else None

    def _extract_floor(self, text: str) -> Optional[str]:
        """提取樓層"""
        floor_patterns = [
            r'(\d+)[Ff]地板',
            r'(\d+)[Ff]\s*樓',
            r'B(\d)',
        ]

        for pattern in floor_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

    def _extract_features(self, text: str) -> List[str]:
        """提取特色"""
        features = []

        feature_keywords = {
            '挑高無柱': r'挑高\s*無柱',
            '無柱設計': r'無柱',
            '落地窗': r'落地窗',
            '自然光': r'自然光|陽光灑落',
            '獨立接待區': r'獨立.*接待區',
        }

        for feature, pattern in feature_keywords.items():
            if re.search(pattern, text):
                features.append(feature)

        return features

    def parse_pdf_table_row(self, row_text: str) -> Dict:
        """解析 PDF 表格的一行"""
        # 假設格式：場地名 | 樓層 | 坪 | 平方米 | 挑高 | 宴會 | 教室 | 劇院
        parts = [p.strip() for p in row_text.split('|')]

        if len(parts) < 4:
            return None

        # 跳過標題行
        if parts[0] in ['場地名稱', 'Function Room', 'Floor', 'Level']:
            return None

        venue = {
            'name': parts[0],
            'floor': parts[1],
            'area_sqm': self._safe_float(parts[3]),
            'capacity_theater': self._safe_int(parts[8]) if len(parts) > 8 else None,
        }

        return venue

    def _safe_int(self, s: str) -> Optional[int]:
        """安全轉整數"""
        try:
            return int(re.sub(r'[^\d]', '', str(s)))
        except:
            return None

    def _safe_float(self, s: str) -> Optional[float]:
        """安全轉浮點數"""
        try:
            return float(re.sub(r'[^\d.]', '', str(s)))
        except:
            return None


# 測試解析器
def test_parser():
    parser = VenueDataParser()

    # 測試案例 1: 茹曦酒店的描述文字
    text1 = "2F 茹曦廳 挑高無柱、空間寬敞，為每一個難忘的時刻提供完美的場地。無論精彩的動人的婚禮宴席，或是多達1,000人的盛大晚宴，茹曦廳都能為您創造獨一無二活動成果。場地規格：220~836平方公尺；賓客數量：至多 1,200 人"

    print("測試 1: 茹曦廳描述")
    print("="*70)
    result1 = parser.parse_venue_block(text1)
    for v in result1:
        print(f"場地名: {v['name']}")
        print(f"樓層: {v['floor']}")
        print(f"面積: {v['area_sqm']} 平方米")
        print(f"容量: {v['capacity']} 人")
        print(f"特色: {v['features']}")
        print()

    # 測試案例 2: PDF 表格行
    text2 = "大宴會廳|B2|290|960|7.3|37x26|780|624|1170|1200"
    print("測試 2: PDF 表格行")
    print("="*70)
    result2 = parser.parse_pdf_table_row(text2)
    if result2:
        print(f"場地名: {result2['name']}")
        print(f"樓層: {result2['floor']}")
        print(f"面積: {result2['area_sqm']} 平方米")
        print(f"容量: {result2['capacity_theater']} 人")
        print()

        # 測試案例 3: 文華東方 PDF
    text3 = "大宴會廳 B2 290 960 10,333 7.3 / 24 37 × 26 780 624 1,170 1,200"
    print("測試 3: 文華東方 PDF（空格分隔）")
    print("="*70)
    # 先轉換為表格格式
    parts = text3.split()
    if len(parts) >= 10:
        table_text = "|".join(parts)
        result3 = parser.parse_pdf_table_row(table_text)
        if result3:
            print(f"場地名: {result3['name']}")
            print(f"樓層: {result3['floor']}")
            print(f"面積: {result3['area_sqm']} 平方米")
            print(f"容量: {result3['capacity_theater']} 人")
        print()

    # 測試案例 4: 改進的茹曦廳提取
    text4 = "2F 茹曦廳 挑高無柱、空間寬廣，為每一個難忘的時刻提供完美的場地。場地規格：836平方公尺；賓客數量：至多1,200人"
    print("測試 4: 茹曦廳改進提取")
    print("="*70)
    result4 = parser.parse_venue_block(text4)
    if result4:
        for v in result4:
            print(f"場地名: {v['name']}")
            print(f"面積: {v['area_sqm']} 平方米")
            print(f"容量: {v['capacity']} 人")
        print()
    # 先轉換為表格格式
    parts = text3.split()
    if len(parts) >= 10:
        table_text = "|".join(parts)
        result3 = parser.parse_pdf_table_row(table_text)
        if result3:
            print(f"場地名: {result3['name']}")
            print(f"樓層: {result3['floor']}")
            print(f"面積: {result3['area_sqm']} 平方米")
            print(f"容量: {result3['capacity_theater']} 人")


if __name__ == '__main__':
    test_parser()
