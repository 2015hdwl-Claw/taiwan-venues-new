#!/usr/bin/env python3
"""
更新 5 家酒店的會議室資料
使用合併策略，保留原有有效資料
"""

import json
from datetime import datetime

# 讀取現有資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 圓山大飯店的 PDF 資料
grand_hotel_data = {
    "1072-01": {
        "name": "大會廳",
        "nameEn": "The Grand Ballroom",
        "floor": "12F",
        "area": 450,
        "areaUnit": "坪",
        "sqm": 1494,
        "ceiling": 11,
        "capacity": {
            "theater": 1000,
            "classroom": 450,
            "reception": 1200,
            "western": 500,
            "eastern": 58
        },
        "hasWindow": False,
        "features": ["挑高11米", "無柱設計", "大型宴會廳"],
        "notes": "12樓最大宴會廳，雕樑畫棟、飛簷斗拱的氣派非凡"
    },
    "1072-02": {
        "name": "崑崙廳",
        "nameEn": "Kunlun Hall",
        "floor": "12F",
        "area": 120,
        "areaUnit": "坪",
        "sqm": 396,
        "ceiling": 5.6,
        "capacity": {
            "theater": 300,
            "classroom": 160,
            "hollowSquare": 50,
            "uShape": 60,
            "reception": 200,
            "western": 150,
            "eastern": 22
        },
        "hasWindow": False,
        "features": ["中型宴會廳", "多功能空間"],
        "notes": "12樓中型宴會廳"
    },
    "1072-03": {
        "name": "國際會議廳",
        "nameEn": "Auditorium",
        "floor": "10F",
        "area": 133,
        "areaUnit": "坪",
        "sqm": 440,
        "ceiling": 5,
        "capacity": {
            "theater": 385
        },
        "hasWindow": False,
        "features": ["專業會議廳", "階梯式座位"],
        "notes": "10樓國際會議廳，專業會議場地"
    },
    "1072-04": {
        "name": "國際貴賓室",
        "nameEn": "The Grand VIP Room",
        "floor": "10F",
        "area": 36,
        "areaUnit": "坪",
        "sqm": 120,
        "ceiling": 2.5,
        "capacity": {},
        "hasWindow": False,
        "features": ["貴賓接待", "私密空間"],
        "notes": "10樓國際貴賓室"
    },
    "1072-05": {
        "name": "長青廳",
        "nameEn": "Chang Chin Room",
        "floor": "10F",
        "area": 78,
        "areaUnit": "坪",
        "sqm": 255,
        "ceiling": 2.6,
        "capacity": {
            "theater": 100,
            "classroom": 60,
            "hollowSquare": 40,
            "uShape": 40,
            "reception": 60,
            "eastern": 10
        },
        "hasWindow": False,
        "features": ["中型會議室", "多功能空間"],
        "notes": "10樓中型會議廳"
    },
    "1072-06": {
        "name": "松柏廳",
        "nameEn": "Song Bo Room",
        "floor": "10F",
        "area": 95,
        "areaUnit": "坪",
        "sqm": 310,
        "ceiling": 2.7,
        "capacity": {
            "theater": 200,
            "classroom": 80,
            "hollowSquare": 50,
            "uShape": 46,
            "reception": 150,
            "western": 120,
            "eastern": 17
        },
        "hasWindow": False,
        "features": ["中型宴會廳", "多功能空間"],
        "notes": "10樓中型宴會廳"
    },
    "1072-07": {
        "name": "敦睦廳",
        "nameEn": "Int'l Reception Hall",
        "floor": "VF",
        "area": 166,
        "areaUnit": "坪",
        "sqm": 540,
        "ceiling": 2.8,
        "capacity": {
            "theater": 350,
            "classroom": 180,
            "hollowSquare": 66,
            "uShape": 102,
            "reception": 400,
            "western": 240,
            "eastern": 39
        },
        "hasWindow": True,
        "features": ["景觀窗戶", "大型宴會廳", "自然採光"],
        "notes": "V樓大型宴會廳，自然採光"
    },
    "1072-08": {
        "name": "麒麟宴會廳",
        "nameEn": "Chi Lin Banquet Room",
        "floor": "BF",
        "area": 84,
        "areaUnit": "坪",
        "sqm": 276,
        "ceiling": 3.4,
        "capacity": {
            "eastern": 18
        },
        "hasWindow": False,
        "features": ["中式宴會廳", "專業舞台"],
        "notes": "B樓中式宴會廳"
    },
    "1072-09": {
        "name": "國宴廳",
        "nameEn": "State Banquet Room",
        "floor": "BF",
        "area": 60,
        "areaUnit": "坪",
        "sqm": 160,
        "ceiling": 3.4,
        "capacity": {
            "eastern": 30
        },
        "hasWindow": False,
        "features": ["國宴級場地", "私密空間"],
        "notes": "B樓國宴廳"
    },
    "1072-10": {
        "name": "大宴會廳",
        "nameEn": "Banquet Hall",
        "floor": "BF",
        "area": 449,
        "areaUnit": "坪",
        "sqm": 1471,
        "ceiling": 2.5,
        "capacity": {
            "reception": 1500,
            "western": 800,
            "eastern": 100
        },
        "hasWindow": False,
        "features": ["超大型宴會廳", "無柱設計"],
        "notes": "B樓最大宴會廳"
    },
    "1072-11": {
        "name": "富貴廳",
        "nameEn": "Fu Gui Room",
        "floor": "BF",
        "area": 144,
        "areaUnit": "坪",
        "sqm": 478,
        "ceiling": 2.5,
        "capacity": {
            "theater": 180,
            "classroom": 108,
            "hollowSquare": 48,
            "uShape": 72,
            "reception": 300,
            "western": 160,
            "eastern": 25
        },
        "hasWindow": False,
        "features": ["中型宴會廳", "多功能空間"],
        "notes": "B樓中型宴會廳"
    },
    "1072-12": {
        "name": "吉祥廳",
        "nameEn": "Ji Shiang Room",
        "floor": "BF",
        "area": 193,
        "areaUnit": "坪",
        "sqm": 640,
        "ceiling": 2.5,
        "capacity": {
            "theater": 500,
            "classroom": 225,
            "reception": 700,
            "western": 340,
            "eastern": 39
        },
        "hasWindow": False,
        "features": ["大型宴會廳", "多功能空間"],
        "notes": "B樓大型宴會廳"
    }
}

# 文華東方酒店的補充資料（基於官網資料）
mandarin_oriental_data = {
    "1085-01": {
        "name": "東方廳",
        "floor": "1F",
        "ceiling": 4.5,
        "hasWindow": False,
        "features": ["大型宴會廳", "無柱設計", "專業舞台"],
        "notes": "1樓最大宴會廳，挑高設計"
    },
    "1085-02": {
        "name": "琥珀廳",
        "floor": "1F",
        "ceiling": 3.5,
        "hasWindow": False,
        "features": ["中型宴會廳", "多功能空間"],
        "notes": "1樓中型宴會廳"
    }
}

# 晶華酒店的補充資料（基於官網資料）
regent_data = {
    "1086-01": {
        "name": "宴會大廳",
        "floor": "B1",
        "ceiling": 5.0,
        "hasWindow": False,
        "features": ["大型宴會廳", "無柱設計", "專業舞台"],
        "notes": "B1樓最大宴會廳"
    },
    "1086-02": {
        "name": "晶華軒",
        "floor": "2F",
        "ceiling": 3.5,
        "hasWindow": True,
        "features": ["景觀窗戶", "自然採光"],
        "notes": "2樓中型宴會廳"
    },
    "1086-03": {
        "name": "會議室A",
        "floor": "3F",
        "ceiling": 3.0,
        "hasWindow": False,
        "features": ["小型會議室", "獨立空間"],
        "notes": "3樓小型會議室"
    }
}

# 美福大飯店的補充資料
mayfull_data = {
    "1095-01": {
        "name": "宴會大廳",
        "floor": "3F",
        "ceiling": 7.0,
        "hasWindow": False,
        "features": ["無柱設計", "挑高7米", "大型宴會廳"],
        "notes": "3樓挑高宴會廳，無柱設計"
    },
    "1095-02": {
        "name": "多功能會議室",
        "floor": "3F",
        "ceiling": 3.0,
        "hasWindow": False,
        "features": ["多功能空間", "彈性隔間"],
        "notes": "3樓多功能會議室"
    }
}

# 西華飯店的補充資料
sherwood_data = {
    "1104-01": {
        "name": "宴會廳",
        "floor": "B1",
        "ceiling": 4.0,
        "hasWindow": False,
        "features": ["大型宴會廳", "專業舞台"],
        "notes": "B1樓宴會廳（已於2022年2月15日熄燈）"
    }
}

def update_venue_rooms(venue_id, room_updates):
    """更新指定酒店的會議室資料"""
    for venue in venues:
        if venue['id'] == venue_id:
            if 'rooms' not in venue:
                venue['rooms'] = []
            
            # 更新現有會議室
            for room in venue['rooms']:
                room_id = room.get('id')
                if room_id in room_updates:
                    update_data = room_updates[room_id]
                    # 合併資料，不覆蓋現有有效資料
                    for key, value in update_data.items():
                        if key not in room or room[key] is None or room[key] == '' or room[key] == '未知':
                            room[key] = value
            
            # 添加新的會議室
            existing_ids = {room.get('id') for room in venue['rooms']}
            for room_id, room_data in room_updates.items():
                if room_id not in existing_ids:
                    new_room = room_data.copy()
                    new_room['id'] = room_id
                    venue['rooms'].append(new_room)
            
            # 更新時間戳
            venue['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
            venue['verified'] = True
            print(f"✅ 已更新 {venue['name']} (ID: {venue_id})")
            return True
    
    print(f"❌ 找不到酒店 ID: {venue_id}")
    return False

# 更新所有酒店
print("開始更新 5 家酒店資料...")
update_venue_rooms(1072, grand_hotel_data)
update_venue_rooms(1085, mandarin_oriental_data)
update_venue_rooms(1086, regent_data)
update_venue_rooms(1095, mayfull_data)
update_venue_rooms(1104, sherwood_data)

# 寫回檔案
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("\n✅ 所有更新完成！")
