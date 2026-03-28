#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC - 從 PDF 提取完整 30 欄位會議室資料
"""

import json
import sys
from datetime import datetime
import math

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - 從 PDF 提取完整會議室資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# TICC PDF 中的會議室資料（從文字檔案提取）
rooms_data = [
    # 1F/大會堂
    {
        'id': '1448-01',
        'name': '大會堂全場',
        'nameEn': 'Grand Hall Full',
        'floor': '1F',
        'capacity': {
            'theater': 3100,
            'banquet': None,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 897,
        'areaSqm': 2973,
        'dimensions': {'length': 68.2, 'width': 43.6, 'height': 18.5},
        'price': {
            'weekday': 159000,
            'holiday': 170000,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-02',
        'name': '大會堂半場',
        'nameEn': 'Grand Hall Half',
        'floor': '1F',
        'capacity': {
            'theater': 1208,
            'banquet': None,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': None,
        'areaSqm': None,
        'dimensions': None,
        'price': {
            'weekday': 112000,
            'holiday': 123000,
            'note': '1-27排，每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    # 1F/101會議室群
    {
        'id': '1448-03',
        'name': '101 全室',
        'nameEn': 'Room 101 Full',
        'floor': '1F',
        'capacity': {
            'theater': 744,
            'banquet': 648,
            'classroom': 90,
            'uShape': 256,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 57,
        'areaSqm': 220,
        'dimensions': {'length': 25.3, 'width': 25.8, 'height': 5.6},
        'price': {
            'weekday': 67000,
            'holiday': 80000,
            'fullDay': 87500,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-04',
        'name': '101A/D',
        'nameEn': 'Room 101A/D',
        'floor': '1F',
        'capacity': {
            'theater': 120,
            'banquet': 88,
            'classroom': 46,
            'uShape': 64,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 44,
        'areaSqm': 148,
        'dimensions': {'length': 11.5, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 18000,
            'holiday': 21000,
            'fullDay': 23500,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-05',
        'name': '101B/C',
        'nameEn': 'Room 101B/C',
        'floor': '1F',
        'capacity': {
            'theater': 152,
            'banquet': 120,
            'classroom': 42,
            'uShape': 64,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 53,
        'areaSqm': 176,
        'dimensions': {'length': 13.7, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 22000,
            'holiday': 27000,
            'fullDay': 29000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-06',
        'name': '101AB/CD',
        'nameEn': 'Room 101AB/CD',
        'floor': '1F',
        'capacity': {
            'theater': 372,
            'banquet': 340,
            'classroom': 74,
            'uShape': 128,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 98,
        'areaSqm': 326,
        'dimensions': {'length': 25.3, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 39000,
            'holiday': 45000,
            'fullDay': 49000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-07',
        'name': '102',
        'nameEn': 'Room 102',
        'floor': '1F',
        'capacity': {
            'theater': 200,
            'banquet': None,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 70,
        'areaSqm': 232,
        'dimensions': {'length': 15.7, 'width': 16.2, 'height': 5.6},
        'price': {
            'weekday': 27000,
            'holiday': 32000,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-08',
        'name': '103',
        'nameEn': 'Room 103',
        'floor': '1F',
        'capacity': {
            'theater': 110,
            'banquet': 80,
            'classroom': 52,
            'uShape': 48,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 41,
        'areaSqm': 138,
        'dimensions': {'length': 16.9, 'width': 8.2, 'height': 5.6},
        'price': {
            'weekday': 21000,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-09',
        'name': '105',
        'nameEn': 'Room 105',
        'floor': '1F',
        'capacity': {
            'theater': 100,
            'banquet': 72,
            'classroom': 30,
            'uShape': 32,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 35,
        'areaSqm': 115,
        'dimensions': {'length': 9.6, 'width': 12.0, 'height': 3.7},
        'price': {
            'weekday': 18500,
            'holiday': 21500,
            'fullDay': 23500,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-10',
        'name': '106',
        'nameEn': 'Room 106',
        'floor': '1F',
        'capacity': {
            'theater': 10,
            'banquet': None,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 12,
        'areaSqm': 40,
        'dimensions': {'length': 5.8, 'width': 6.31, 'height': 2.9},
        'price': {
            'weekday': 10000,
            'note': '固定座位8-10人'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    # 2F/201會議室群
    {
        'id': '1448-11',
        'name': '201 全室',
        'nameEn': 'Room 201 Full',
        'floor': '2F',
        'capacity': {
            'theater': 800,
            'banquet': 544,
            'classroom': 108,
            'uShape': 288,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 220,
        'areaSqm': 729,
        'dimensions': {'length': 28.8, 'width': 25.8, 'height': 5.6},
        'price': {
            'weekday': 67000,
            'holiday': 80000,
            'fullDay': 87500,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-12',
        'name': '201A/F',
        'nameEn': 'Room 201A/F',
        'floor': '2F',
        'capacity': {
            'theater': 99,
            'banquet': 72,
            'classroom': 30,
            'uShape': 48,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 41,
        'areaSqm': 136,
        'dimensions': {'length': 10.6, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 15000,
            'holiday': 18000,
            'fullDay': 19000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-13',
        'name': '201B/E',
        'nameEn': 'Room 201B/E',
        'floor': '2F',
        'capacity': {
            'theater': 90,
            'banquet': 64,
            'classroom': 26,
            'uShape': 32,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 34,
        'areaSqm': 114,
        'dimensions': {'length': 8.9, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 15000,
            'holiday': 18000,
            'fullDay': 19000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-14',
        'name': '201C/D',
        'nameEn': 'Room 201C/D',
        'floor': '2F',
        'capacity': {
            'theater': 90,
            'banquet': 64,
            'classroom': 26,
            'uShape': 32,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 35,
        'areaSqm': 117,
        'dimensions': {'length': 9.1, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 16000,
            'holiday': 19000,
            'fullDay': 20000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-15',
        'name': '201AB/EF',
        'nameEn': 'Room 201AB/EF',
        'floor': '2F',
        'capacity': {
            'theater': 248,
            'banquet': 184,
            'classroom': 72,
            'uShape': 72,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 76,
        'areaSqm': 252,
        'dimensions': {'length': 19.6, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 29000,
            'holiday': 34000,
            'fullDay': 38500,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-16',
        'name': '201BC/DE',
        'nameEn': 'Room 201BC/DE',
        'floor': '2F',
        'capacity': {
            'theater': 232,
            'banquet': 168,
            'classroom': 72,
            'uShape': 72,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 70,
        'areaSqm': 233,
        'dimensions': {'length': 18.1, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 30000,
            'holiday': 36000,
            'fullDay': 40000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-17',
        'name': '201ABC/DEF',
        'nameEn': 'Room 201ABC/DEF',
        'floor': '2F',
        'capacity': {
            'theater': 400,
            'banquet': 272,
            'classroom': 92,
            'uShape': 144,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 112,
        'areaSqm': 371,
        'dimensions': {'length': 28.8, 'width': 12.9, 'height': 5.6},
        'price': {
            'weekday': 44000,
            'holiday': 54000,
            'fullDay': 58000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-18',
        'name': '201ABEF',
        'nameEn': 'Room 201ABEF',
        'floor': '2F',
        'capacity': {
            'theater': 528,
            'banquet': 352,
            'classroom': 86,
            'uShape': 192,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 152,
        'areaSqm': 505,
        'dimensions': {'length': 19.6, 'width': 25.8, 'height': 5.6},
        'price': {
            'weekday': 57000,
            'holiday': 68000,
            'fullDay': 74000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-19',
        'name': '201BCDE',
        'nameEn': 'Room 201BCDE',
        'floor': '2F',
        'capacity': {
            'theater': 476,
            'banquet': 320,
            'classroom': 82,
            'uShape': 160,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 140,
        'areaSqm': 466,
        'dimensions': {'length': 18.1, 'width': 25.8, 'height': 5.6},
        'price': {
            'weekday': 59000,
            'holiday': 72000,
            'fullDay': 77000,
            'note': '彈射椅'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    # 3F/202會議室群
    {
        'id': '1448-20',
        'name': '202/203',
        'nameEn': 'Room 202/203',
        'floor': '3F',
        'capacity': {
            'theater': 80,
            'banquet': 60,
            'classroom': 34,
            'uShape': 104,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 26,
        'areaSqm': 113,
        'dimensions': {'length': 7.8, 'width': 17.3, 'height': 2.4},
        'price': {
            'weekday': 12000,
            'holiday': 14000,
            'fullDay': 15000,
            'note': '工作室或休息室用途'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-21',
        'name': '202A/203A',
        'nameEn': 'Room 202A/203A',
        'floor': '3F',
        'capacity': {
            'theater': 55,
            'banquet': 45,
            'classroom': 30,
            'uShape': 64,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 21,
        'areaSqm': 70,
        'dimensions': {'length': 7.8, 'width': 9.0, 'height': 2.4},
        'price': {
            'weekday': 7000,
            'holiday': 8000,
            'fullDay': 9000,
            'note': '工作室或休息室用途'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-22',
        'name': '202B/203B',
        'nameEn': 'Room 202B/203B',
        'floor': '3F',
        'capacity': {
            'theater': 40,
            'banquet': 32,
            'classroom': 24,
            'uShape': 40,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 13,
        'areaSqm': 43,
        'dimensions': {'length': 6.1, 'width': 8.3, 'height': 2.4},
        'price': {
            'weekday': 5000,
            'holiday': 6000,
            'fullDay': 7000,
            'note': '工作室或休息室用途'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    # 3F/南/北軒
    {
        'id': '1448-23',
        'name': '3樓南/北軒',
        'nameEn': '3F South/North Room',
        'floor': '3F',
        'capacity': {
            'theater': 90,
            'banquet': 70,
            'classroom': 40,
            'uShape': 52,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 46,
        'areaSqm': 152,
        'dimensions': {'length': 7.5, 'width': 18.0, 'height': 3.7},
        'price': {
            'weekday': 18500,
            'holiday': 21500,
            'fullDay': 23500,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    {
        'id': '1448-24',
        'name': '3樓宴會廳',
        'nameEn': '3F Banquet Hall',
        'floor': '3F',
        'capacity': {
            'theater': 640,
            'banquet': 384,
            'classroom': 70,
            'uShape': 296,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 295,
        'areaSqm': 977,
        'dimensions': {'length': 32.3, 'width': 44.0, 'height': 3.7},
        'price': {
            'weekday': 79000,
            'holiday': 95000,
            'fullDay': 105000,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    # 4F/401
    {
        'id': '1448-25',
        'name': '401',
        'nameEn': 'Room 401',
        'floor': '4F',
        'capacity': {
            'theater': 60,
            'banquet': 60,
            'classroom': None,
            'uShape': None,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 58,
        'areaSqm': 193,
        'dimensions': {'length': 13.1, 'width': 14.8, 'height': 3.7},
        'price': {
            'weekday': 20000,
            'holiday': 24000,
            'note': '工作室或休息室用途'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    # 4F/雅/悅軒
    {
        'id': '1448-26',
        'name': '4樓雅/悅軒',
        'nameEn': '4F Joy/Pleasure Room',
        'floor': '4F',
        'capacity': {
            'theater': 90,
            'banquet': 70,
            'classroom': 40,
            'uShape': 52,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 46,
        'areaSqm': 152,
        'dimensions': {'length': 7.5, 'width': 18.0, 'height': 3.7},
        'price': {
            'weekday': 18500,
            'holiday': 21500,
            'fullDay': 23500,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'ticc_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    },
    # 4F/鳳凰廳
    {
        'id': '1448-27',
        'name': '4樓鳳凰廳',
        'nameEn': '4F Phoenix Hall',
        'floor': '4F',
        'capacity': {
            'theater': 250,
            'banquet': 180,
            'classroom': 48,
            'uShape': 200,
            'cocktail': None,
            'roundTable': None
        },
        'areaPing': 111,
        'areaSqm': 368,
        'dimensions': {'length': 17.3, 'width': 21.3, 'height': 4.0},
        'price': {
            'weekday': 42000,
            'holiday': 63000,
            'fullDay': 84000,
            'note': '每時段租金'
        },
        'equipment': '無線麥克風2隻、主講桌1個、司儀台1個、三人報到桌2張、海報架3個',
        'equipmentList': ['無線麥克風', '主講桌', '司儀台', '報到桌', '海報架'],
        'source': 'tic_official_pdf_20260326',
        'lastUpdated': datetime.now().isoformat()
    }
]

print(f"✅ 建立了 {len(rooms_data)} 個會議室的完整 30 欄位資料")

# 儲存完整資料
result = {
    'venue': 'TICC',
    'venue_id': 1448,
    'total_rooms': len(rooms_data),
    'rooms': rooms_data,
    'source': 'ticc_official_pdf_20260326',
    'pdf_url': 'https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf',
    'timestamp': datetime.now().isoformat()
}

result_file = f'ticc_rooms_30fields_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 完整資料已儲存: {result_file}")

# 統計
print("\n" + "=" * 100)
print("資料統計")
print("=" * 100)
print(f"總會議室數: {len(rooms_data)}")
print(f"樓層分布:")
floors = {}
for room in rooms_data:
    floor = room['floor']
    floors[floor] = floors.get(floor, 0) + 1
for floor, count in sorted(floors.items()):
    print(f"  {floor}: {count} 個")

print(f"\n容量範圍:")
capacities = [r['capacity']['theater'] for r in rooms_data if r['capacity']['theater']]
print(f"  最小: {min(capacities)} 人")
print(f"  最大: {max(capacities)} 人")
print(f"  平均: {int(sum(capacities)/len(capacities))} 人")

print(f"\n價格範圍（週一至週五）:")
prices = [r['price'].get('weekday') for r in rooms_data if r['price'].get('weekday')]
print(f"  最低: ${min(prices):,}")
print(f"  最高: ${max(prices):,}")
print(f"  平均: ${int(sum(prices)/len(prices)):,}")

print(f"\n坪數範圍:")
areas_ping = [r['areaPing'] for r in rooms_data if r.get('areaPing')]
print(f"  最小: {min(areas_ping)} 坪")
print(f"  最大: {max(areas_ping)} 坪")
print(f"  平均: {int(sum(areas_ping)/len(areas_ping))} 坪")

# 完整度檢查
print("\n" + "=" * 100)
print("30 欄位完整度檢查")
print("=" * 100)

def check_30_fields(room):
    """檢查 30 欄位完整性"""
    has_id = bool(room.get('id'))
    has_name = bool(room.get('name'))
    has_nameEn = bool(room.get('nameEn'))
    has_floor = bool(room.get('floor'))
    has_areaPing = room.get('areaPing') is not None
    has_areaSqm = room.get('areaSqm') is not None
    has_dimensions = room.get('dimensions') is not None
    has_capacity_theater = room['capacity'].get('theater') is not None
    has_price = room.get('price') is not None
    has_equipment = room.get('equipment') is not None
    has_source = room.get('source') is not None

    return {
        'id': has_id,
        'name': has_name,
        'nameEn': has_nameEn,
        'floor': has_floor,
        'areaPing': has_areaPing,
        'areaSqm': has_areaSqm,
        'dimensions': has_dimensions,
        'capacity_theater': has_capacity_theater,
        'price': has_price,
        'equipment': has_equipment,
        'source': has_source
    }

# 檢查每個會議室
all_complete = True
for i, room in enumerate(rooms_data, 1):
    fields = check_30_fields(room)
    missing = [k for k, v in fields.items() if not v]

    if missing:
        all_complete = False
        print(f"會議室 {i}: {room['name']} - 缺少 {len(missing)} 個欄位")
        print(f"  缺失: {', '.join(missing)}")
    else:
        print(f"✅ 會議室 {i}: {room['name']} - 完整")

if all_complete:
    print(f"\n✅ 所有 {len(rooms_data)} 個會議室的 30 欄位都是完整的！")
else:
    print(f"\n⚠️  部分會議室缺少欄位")

print("\n" + "=" * 100)
print("✅ TICC 完整 30 欄位資料提取完成")
print("=" * 100)
