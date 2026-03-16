#!/usr/bin/env python3
"""
更新重複的台北市場地記錄
"""

import json
from datetime import datetime

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# TICC 會議室資訊
ticc_rooms = [
    {"name": "大會堂", "capacity": 3100, "area": "約600坪", "layout": "劇院型", "price": "請洽詢", "equipment": "頂級音響燈光、同步翻譯設備、直播系統", "photo": "https://www.ticc.com.tw/images/auditorium.jpg"},
    {"name": "201會議室", "capacity": 500, "area": "約200坪", "layout": "劇院型/教室型/宴會型", "price": "請洽詢", "equipment": "投影設備、音響系統、同步翻譯設備", "photo": "https://www.ticc.com.tw/images/201.jpg"},
    {"name": "101會議室", "capacity": 200, "area": "約80坪", "layout": "劇院型/教室型", "price": "請洽詢", "equipment": "投影設備、音響系統", "photo": "https://www.ticc.com.tw/images/101.jpg"},
    {"name": "102會議室", "capacity": 100, "area": "約50坪", "layout": "會議型/教室型", "price": "請洽詢", "equipment": "投影設備、白板", "photo": "https://www.ticc.com.tw/images/102.jpg"},
    {"name": "103會議室", "capacity": 50, "area": "約30坪", "layout": "會議型", "price": "請洽詢", "equipment": "投影設備、白板", "photo": "https://www.ticc.com.tw/images/103.jpg"},
    {"name": "104會議室", "capacity": 50, "area": "約30坪", "layout": "會議型", "price": "請洽詢", "equipment": "投影設備、白板", "photo": "https://www.ticc.com.tw/images/104.jpg"},
    {"name": "105會議室", "capacity": 30, "area": "約20坪", "layout": "會議型", "price": "請洽詢", "equipment": "投影設備、白板", "photo": "https://www.ticc.com.tw/images/105.jpg"}
]

# 師大進修推廣學院會議室資訊
ntnu_rooms = [
    {"name": "國際會議廳", "capacity": 200, "area": "約100坪", "layout": "劇院型", "price": "請洽詢", "equipment": "投影設備、音響系統、同步翻譯設備", "photo": "https://www.sce.ntnu.edu.tw/images/auditorium.jpg"},
    {"name": "第一會議室", "capacity": 80, "area": "約40坪", "layout": "教室型/會議型", "price": "請洽詢", "equipment": "投影設備、白板", "photo": "https://www.sce.ntnu.edu.tw/images/room1.jpg"},
    {"name": "第二會議室", "capacity": 50, "area": "約25坪", "layout": "會議型", "price": "請洽詢", "equipment": "投影設備、白板", "photo": "https://www.sce.ntnu.edu.tw/images/room2.jpg"},
    {"name": "電腦教室", "capacity": 40, "area": "約30坪", "layout": "教室型", "price": "請洽詢", "equipment": "電腦設備、投影系統", "photo": "https://www.sce.ntnu.edu.tw/images/computer.jpg"}
]

# CLBC 會議室資訊
clbc_rooms = [
    {"name": "多功能活動空間", "capacity": 100, "area": "約50坪", "layout": "活動型/會議型", "price": "每小時 3,000 元起", "equipment": "投影設備、音響系統", "photo": "https://clbc.tw/wp-content/uploads/2018/12/main-feature.jpg"},
    {"name": "大會議室", "capacity": 20, "area": "約15坪", "layout": "會議型", "price": "每小時 1,500 元起", "equipment": "投影設備、白板", "photo": "https://clbc.tw/images/meeting-room.jpg"},
    {"name": "小會議室", "capacity": 8, "area": "約8坪", "layout": "會議型", "price": "每小時 800 元起", "equipment": "投影設備、白板", "photo": "https://clbc.tw/images/small-room.jpg"}
]

# 更新記錄
updated_count = 0
for venue in venues:
    name = venue.get('name', '')
    
    # 更新 TICC 記錄
    if '台北國際會議中心(TICC)' in name or 'TICC' in name:
        venue['rooms'] = ticc_rooms
        venue['maxCapacityTheater'] = 3100
        if 'images' not in venue:
            venue['images'] = {}
        venue['images']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
        venue['images']['needsUpdate'] = False
        updated_count += 1
    
    # 更新師大進修推廣學院記錄
    elif '師大進修推廣學院' in name:
        venue['rooms'] = ntnu_rooms
        venue['maxCapacityTheater'] = 200
        if 'images' not in venue:
            venue['images'] = {}
        venue['images']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
        venue['images']['needsUpdate'] = False
        updated_count += 1
    
    # 更新 CLBC 記錄
    elif 'CLBC大安商務中心' in name:
        venue['rooms'] = clbc_rooms
        venue['maxCapacityTheater'] = 100
        if 'images' not in venue:
            venue['images'] = {}
        venue['images']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
        venue['images']['needsUpdate'] = False
        updated_count += 1

# 寫回檔案
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"✅ 更新完成！共更新 {updated_count} 筆記錄")
