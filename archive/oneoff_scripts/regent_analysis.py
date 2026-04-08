#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析晶華飯店官網資料與資料庫欄位對應
"""
import json
import sys
import io

# 設置 UTF-8 編碼輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取當前資料庫
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 找出晶華飯店
for v in venues:
    if v.get('id') == 1086:
        print('=== 資料庫現有結構 ===')
        print(f'場地 ID: {v["id"]}')
        print(f'場地名稱: {v["name"]}')
        print(f'會議室數量: {len(v.get("rooms", []))}')
        print()

        print('=== 會議室欄位結構 ===')
        if v.get('rooms'):
            room = v['rooms'][0]
            print('欄位列表:')
            for key in room.keys():
                value = room[key]
                if isinstance(value, dict):
                    print(f'  {key}: (dict with {len(value)} keys)')
                elif isinstance(value, list):
                    print(f'  {key}: (list with {len(value)} items)')
                else:
                    value_str = str(value)[:50]
                    print(f'  {key}: {value_str}')
        break

print()
print('=== 官網完整資料 (/occasions/event-venues) ===')
print()

official_data = {
    "晶英會": {
        "name": "晶英會",
        "nameEn": "Crystal Room",
        "area_sqm": 270,
        "area_sqft": 2905,
        "area_ping": 81.8,  # 270/3.306
        "height": 2.4,
        "capacity": {
            "reception": 200,
            "banquet": 168,
            "theater": 200,
            "classroom": 132
        },
        "photo": "https://www.regenttaiwan.com/occasions/uploads/site/8/org/201844dbf31f9bbff3dbfccbd7f162e2.png",
        "description": "融合中式傳統簡約設計、與時俱進的會議設備，以及優雅待客之道的多功能場地。",
        "features": ["多功能場地", "中式傳統簡約設計"]
    },
    "晶華會": {
        "name": "晶華會",
        "nameEn": "Regent Club",
        "area_sqm": 357,
        "area_sqft": 3896,
        "area_ping": 108.0,  # 357/3.306
        "height": 2.3,
        "capacity": {
            "reception": 200,
            "banquet": 22,
            "theater": 360,
            "classroom": 160
        },
        "photo": "https://www.regenttaiwan.com/occasions/uploads/site/10/org/6c2a5bf5bad0d44bdd94c0ba1377b2d8.png",
        "description": "以頂級私人招待所風貌出現的晶華會，讓您的宴會活動不再一成不變。人生歡樂時、福祿壽喜宴，透過晶華會隱密尊貴的宴飲空間及私人管家式的貼心服務。",
        "features": ["隱密尊貴", "私人管家式服務"]
    },
    "宴會廳": {
        "name": "宴會廳",
        "nameEn": "Grand Ballroom",
        "area_sqm": 888,
        "area_sqft": 9555,
        "area_ping": 268.6,  # 888/3.306
        "height": "5(H) / 2.4(L)",  # 前高後低
        "capacity": {
            "reception": 1000,
            "banquet": 600,
            "theater": 600,
            "classroom": 300
        },
        "photo": "https://www.regenttaiwan.com/occasions/uploads/site/11/org/af16abb69345576b2e04d5c30a9645f8.jpg",
        "description": "挑高壯麗、氣宇非凡的晶華宴會廳，三面落地窗景攬入一室綠意，無論是大型的商務研討會、尊榮結婚喜宴或是品牌發表雞尾酒會，都是一個完美絕倫的場地首選。",
        "features": ["挑高5米", "三面落地窗", "無柱設計"],
        "floor": "B1"
    },
    "萬象廳": {
        "name": "萬象廳",
        "nameEn": "Universe Hall",
        "area_sqm": 470,
        "area_sqft": 5170,
        "area_ping": 142.2,  # 470/3.306
        "height": 2.35,
        "capacity": {
            "reception": 260,
            "banquet": 276,
            "theater": 440,
            "classroom": 207
        },
        "photo": "https://www.regenttaiwan.com/occasions/uploads/site/12/org/fb7ab9bad6dc7648a77ce3d8d60caa10.jpg",
        "description": "萬象廳擁有六間多功能貴賓廳，是舉辦研討會、喜慶宴會及社交活動的理想場地。",
        "features": ["6間多功能貴賓廳"]
    },
    "寰宇廳": {
        "name": "寰宇廳",
        "nameEn": "Panorama Hall",
        "description": "包含三間優雅的貴賓廳，多功能的場地是中型規模社交活動及喜慶宴會的理想選擇。",
        "features": ["3間優雅貴賓廳"],
        "photo": "https://www.regenttaiwan.com/occasions/uploads/site/13/org/b48d08f556da74184255812af8ddf8a4.jpg"
        # 官網沒有提供具體面積和容量數據
    },
    "貴賓廳": {
        "name": "貴賓廳",
        "nameEn": "VIP Rooms",
        "area_sqm": 776,
        "area_sqft": 8508,
        "area_ping": 234.7,  # 776/3.306
        "height": 2.3,
        "capacity": {
            "reception": 580,
            "banquet": 576,
            "theater": 700,
            "classroom": 429
        },
        "description": "9 間高雅的貴賓廳，可個別預訂或合併間數，無論任何大小規模的會議或派對，酒店都能為您量身訂做、精心策劃。",
        "features": ["9間貴賓廳", "可個別預訂或合併"]
    }
}

for name, data in official_data.items():
    print(f'--- {name} ---')
    print(f'面積: {data.get("area_ping", "N/A")} 坪 ({data.get("area_sqm", "N/A")} m²)')
    print(f'層高: {data.get("height", "N/A")}m')
    if data.get("capacity"):
        print(f'容量(劇院式): {data["capacity"].get("theater", "N/A")} 人')
    print(f'照片: {data.get("photo", "N/A")[:60]}...')
    print()
