#!/usr/bin/env python3
"""
台北市場地會議室資訊更新腳本
更新日期: 2026-03-17
"""

import json
from datetime import datetime

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 場地更新資料
venue_updates = {
    # 公務人力發展學院
    1042: {
        "rooms": [
            {
                "name": "1F 前瞻廳",
                "capacity": 220,
                "area": "約150坪",
                "layout": "階梯教室型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統、麥克風",
                "photo": "https://www.hrd.gov.tw/media/1015/1f.jpg"
            },
            {
                "name": "1F 101階梯教室",
                "capacity": 41,
                "area": "約30坪",
                "layout": "階梯教室型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.hrd.gov.tw/media/1019/101.jpg"
            },
            {
                "name": "1F 103階梯教室",
                "capacity": 78,
                "area": "約50坪",
                "layout": "階梯戲院型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.hrd.gov.tw/media/1020/103.jpg"
            },
            {
                "name": "2F 201教室",
                "capacity": 30,
                "area": "約20坪",
                "layout": "教室型/U型/分組型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.hrd.gov.tw/media/1021/201_1.jpg"
            },
            {
                "name": "2F 202教室",
                "capacity": 30,
                "area": "約20坪",
                "layout": "教室型/U型/分組型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.hrd.gov.tw/media/1022/202.jpg"
            }
        ],
        "maxCapacityTheater": 220,
        "contactPhone": "02-7712-2323"
    },
    
    # 台北世貿中心展覽大樓
    1049: {
        "rooms": [
            {
                "name": "第一會議室",
                "capacity": 230,
                "area": "約120坪",
                "layout": "劇院型/教室型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統、同步翻譯設備",
                "photo": "https://www.twtc.com.tw/images/meeting/room1.jpg"
            },
            {
                "name": "A+會議室",
                "capacity": 80,
                "area": "約50坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、視訊會議系統",
                "photo": "https://www.twtc.com.tw/images/meeting/aplus.jpg"
            },
            {
                "name": "第二會議室",
                "capacity": 100,
                "area": "約60坪",
                "layout": "劇院型/教室型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.twtc.com.tw/images/meeting/room2.jpg"
            },
            {
                "name": "第三會議室",
                "capacity": 80,
                "area": "約45坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.twtc.com.tw/images/meeting/room3.jpg"
            },
            {
                "name": "第四會議室",
                "capacity": 80,
                "area": "約45坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.twtc.com.tw/images/meeting/room4.jpg"
            },
            {
                "name": "第五會議室",
                "capacity": 80,
                "area": "約45坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.twtc.com.tw/images/meeting/room5.jpg"
            },
            {
                "name": "一樓貴賓室",
                "capacity": 30,
                "area": "約25坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、沙發座椅",
                "photo": "https://www.twtc.com.tw/images/meeting/vip.jpg"
            }
        ],
        "maxCapacityTheater": 230,
        "contactPhone": "02-2725-5200"
    },
    
    # 集思台大會議中心
    1128: {
        "rooms": [
            {
                "name": "國際會議廳",
                "capacity": 180,
                "area": "約100坪",
                "layout": "劇院型/教室型",
                "price": "每小時 5,000 元起",
                "equipment": "投影設備、音響系統、同步翻譯設備",
                "photo": "https://www.meeting.com.tw/ntu/images/hall.jpg"
            },
            {
                "name": "第一會議室",
                "capacity": 50,
                "area": "約30坪",
                "layout": "會議型/U型",
                "price": "每小時 2,000 元起",
                "equipment": "投影設備、白板",
                "photo": "https://www.meeting.com.tw/ntu/images/room1.jpg"
            },
            {
                "name": "第二會議室",
                "capacity": 30,
                "area": "約20坪",
                "layout": "會議型",
                "price": "每小時 1,500 元起",
                "equipment": "投影設備、白板",
                "photo": "https://www.meeting.com.tw/ntu/images/room2.jpg"
            },
            {
                "name": "多媒體教室",
                "capacity": 40,
                "area": "約25坪",
                "layout": "教室型",
                "price": "每小時 2,500 元起",
                "equipment": "電腦設備、投影系統",
                "photo": "https://www.meeting.com.tw/ntu/images/computer.jpg"
            }
        ],
        "maxCapacityTheater": 180,
        "contactPhone": "02-3366-9366"
    },
    
    # 台北國際會議中心 (TICC)
    1448: {
        "rooms": [
            {
                "name": "大會堂",
                "capacity": 3100,
                "area": "約600坪",
                "layout": "劇院型",
                "price": "請洽詢",
                "equipment": "頂級音響燈光、同步翻譯設備、直播系統",
                "photo": "https://www.ticc.com.tw/images/auditorium.jpg"
            },
            {
                "name": "201會議室",
                "capacity": 500,
                "area": "約200坪",
                "layout": "劇院型/教室型/宴會型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統、同步翻譯設備",
                "photo": "https://www.ticc.com.tw/images/201.jpg"
            },
            {
                "name": "101會議室",
                "capacity": 200,
                "area": "約80坪",
                "layout": "劇院型/教室型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.ticc.com.tw/images/101.jpg"
            },
            {
                "name": "102會議室",
                "capacity": 100,
                "area": "約50坪",
                "layout": "會議型/教室型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.ticc.com.tw/images/102.jpg"
            },
            {
                "name": "103會議室",
                "capacity": 50,
                "area": "約30坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.ticc.com.tw/images/103.jpg"
            },
            {
                "name": "104會議室",
                "capacity": 50,
                "area": "約30坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.ticc.com.tw/images/104.jpg"
            },
            {
                "name": "105會議室",
                "capacity": 30,
                "area": "約20坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.ticc.com.tw/images/105.jpg"
            }
        ],
        "maxCapacityTheater": 3100,
        "contactPhone": "02-2725-5200"
    },
    
    # 台北寒舍喜來登大飯店
    1075: {
        "rooms": [
            {
                "name": "喜宴廳",
                "capacity": 800,
                "area": "約400坪",
                "layout": "宴會型/劇院型",
                "price": "請洽詢",
                "equipment": "頂級音響燈光、LED螢幕",
                "photo": "https://www.sheratongrandtaipei.com/images/ballroom.jpg"
            },
            {
                "name": "桃花源廳",
                "capacity": 300,
                "area": "約150坪",
                "layout": "宴會型/會議型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.sheratongrandtaipei.com/images/taohua.jpg"
            },
            {
                "name": "鳳凰廳",
                "capacity": 200,
                "area": "約100坪",
                "layout": "宴會型/會議型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.sheratongrandtaipei.com/images/phoenix.jpg"
            },
            {
                "name": "會議室A",
                "capacity": 50,
                "area": "約25坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.sheratongrandtaipei.com/images/meeting-a.jpg"
            },
            {
                "name": "會議室B",
                "capacity": 30,
                "area": "約20坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.sheratongrandtaipei.com/images/meeting-b.jpg"
            }
        ],
        "maxCapacityTheater": 800,
        "venueType": "飯店場地",
        "contactPhone": "02-2321-5511"
    },
    
    # 寒舍艾美酒店
    1113: {
        "rooms": [
            {
                "name": "艾美廳",
                "capacity": 600,
                "area": "約300坪",
                "layout": "宴會型/劇院型",
                "price": "請洽詢",
                "equipment": "頂級音響燈光、LED螢幕",
                "photo": "https://www.lemeridien.com/taipei/images/ballroom.jpg"
            },
            {
                "name": "北歐廳",
                "capacity": 300,
                "area": "約150坪",
                "layout": "宴會型/會議型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.lemeridien.com/taipei/images/nordic.jpg"
            },
            {
                "name": "法式廳",
                "capacity": 150,
                "area": "約80坪",
                "layout": "宴會型/會議型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.lemeridien.com/taipei/images/french.jpg"
            },
            {
                "name": "會議室1",
                "capacity": 40,
                "area": "約20坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.lemeridien.com/taipei/images/meeting1.jpg"
            },
            {
                "name": "會議室2",
                "capacity": 40,
                "area": "約20坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.lemeridien.com/taipei/images/meeting2.jpg"
            }
        ],
        "maxCapacityTheater": 600,
        "contactPhone": "02-7722-3800"
    },
    
    # CLBC大安商務中心
    1032: {
        "rooms": [
            {
                "name": "多功能活動空間",
                "capacity": 100,
                "area": "約50坪",
                "layout": "活動型/會議型",
                "price": "每小時 3,000 元起",
                "equipment": "投影設備、音響系統",
                "photo": "https://clbc.tw/wp-content/uploads/2018/12/main-feature.jpg"
            },
            {
                "name": "大會議室",
                "capacity": 20,
                "area": "約15坪",
                "layout": "會議型",
                "price": "每小時 1,500 元起",
                "equipment": "投影設備、白板",
                "photo": "https://clbc.tw/images/meeting-room.jpg"
            },
            {
                "name": "小會議室",
                "capacity": 8,
                "area": "約8坪",
                "layout": "會議型",
                "price": "每小時 800 元起",
                "equipment": "投影設備、白板",
                "photo": "https://clbc.tw/images/small-room.jpg"
            }
        ],
        "maxCapacityTheater": 100,
        "contactPhone": "02-2700-3939"
    },
    
    # 青青婚宴會館
    1129: {
        "rooms": [
            {
                "name": "水晶宴會廳",
                "capacity": 400,
                "area": "約200坪",
                "layout": "宴會型",
                "price": "每桌 18,800 元起",
                "equipment": "頂級音響燈光、LED螢幕",
                "photo": "https://www.77-67.com/images/crystal.jpg"
            },
            {
                "name": "花園宴會廳",
                "capacity": 250,
                "area": "約120坪",
                "layout": "宴會型",
                "price": "每桌 16,800 元起",
                "equipment": "音響燈光、投影設備",
                "photo": "https://www.77-67.com/images/garden.jpg"
            },
            {
                "name": "浪漫廳",
                "capacity": 150,
                "area": "約80坪",
                "layout": "宴會型",
                "price": "每桌 14,800 元起",
                "equipment": "音響燈光、投影設備",
                "photo": "https://www.77-67.com/images/romantic.jpg"
            }
        ],
        "maxCapacityTheater": 400,
        "contactPhone": "02-8667-6767"
    },
    
    # 台北唯客樂文旅
    1065: {
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": 120,
                "area": "約60坪",
                "layout": "宴會型/會議型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.victoriam.com/images/ballroom.jpg"
            },
            {
                "name": "會議室A",
                "capacity": 30,
                "area": "約15坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.victoriam.com/images/meeting-a.jpg"
            },
            {
                "name": "會議室B",
                "capacity": 20,
                "area": "約12坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.victoriam.com/images/meeting-b.jpg"
            }
        ],
        "maxCapacityTheater": 120,
        "contactPhone": "02-2597-3888"
    },
    
    # 台北商務會館
    1066: {
        "rooms": [
            {
                "name": "國際會議廳",
                "capacity": 180,
                "area": "約90坪",
                "layout": "劇院型/教室型",
                "price": "每小時 5,000 元起",
                "equipment": "投影設備、音響系統、同步翻譯設備",
                "photo": "https://www.tbc-group.com/images/conference.jpg"
            },
            {
                "name": "第一會議室",
                "capacity": 50,
                "area": "約25坪",
                "layout": "會議型",
                "price": "每小時 2,000 元起",
                "equipment": "投影設備、白板",
                "photo": "https://www.tbc-group.com/images/room1.jpg"
            },
            {
                "name": "第二會議室",
                "capacity": 30,
                "area": "約15坪",
                "layout": "會議型",
                "price": "每小時 1,500 元起",
                "equipment": "投影設備、白板",
                "photo": "https://www.tbc-group.com/images/room2.jpg"
            }
        ],
        "maxCapacityTheater": 180,
        "contactPhone": "02-2703-5656"
    },
    
    # 師大進修推廣學院
    1493: {
        "rooms": [
            {
                "name": "國際會議廳",
                "capacity": 200,
                "area": "約100坪",
                "layout": "劇院型",
                "price": "請洽詢",
                "equipment": "投影設備、音響系統、同步翻譯設備",
                "photo": "https://www.sce.ntnu.edu.tw/images/auditorium.jpg"
            },
            {
                "name": "第一會議室",
                "capacity": 80,
                "area": "約40坪",
                "layout": "教室型/會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.sce.ntnu.edu.tw/images/room1.jpg"
            },
            {
                "name": "第二會議室",
                "capacity": 50,
                "area": "約25坪",
                "layout": "會議型",
                "price": "請洽詢",
                "equipment": "投影設備、白板",
                "photo": "https://www.sce.ntnu.edu.tw/images/room2.jpg"
            },
            {
                "name": "電腦教室",
                "capacity": 40,
                "area": "約30坪",
                "layout": "教室型",
                "price": "請洽詢",
                "equipment": "電腦設備、投影系統",
                "photo": "https://www.sce.ntnu.edu.tw/images/computer.jpg"
            }
        ],
        "maxCapacityTheater": 200,
        "contactPhone": "02-7734-5872"
    },
    
    # CAMA咖啡
    1031: {
        "rooms": [
            {
                "name": "包場空間",
                "capacity": 40,
                "area": "約30坪",
                "layout": "活動型",
                "price": "請洽詢",
                "equipment": "基本音響設備",
                "photo": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800"
            }
        ],
        "maxCapacityTheater": 40,
        "contactPhone": "請洽各分店"
    },
    
    # Regus商務中心
    1035: {
        "rooms": [
            {
                "name": "會議室A",
                "capacity": 20,
                "area": "約12坪",
                "layout": "會議型",
                "price": "每小時 1,500 元起",
                "equipment": "投影設備、白板、視訊會議系統",
                "photo": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800"
            },
            {
                "name": "會議室B",
                "capacity": 10,
                "area": "約8坪",
                "layout": "會議型",
                "price": "每小時 1,000 元起",
                "equipment": "投影設備、白板",
                "photo": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800"
            },
            {
                "name": "會議室C",
                "capacity": 35,
                "area": "約20坪",
                "layout": "會議型/教室型",
                "price": "每小時 2,500 元起",
                "equipment": "投影設備、音響系統",
                "photo": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800"
            }
        ],
        "maxCapacityTheater": 35,
        "contactPhone": "請洽各分店"
    },
    
    # Simple Kaffa
    1036: {
        "rooms": [
            {
                "name": "包場空間",
                "capacity": 55,
                "area": "約40坪",
                "layout": "活動型",
                "price": "請洽詢",
                "equipment": "基本音響設備",
                "photo": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800"
            }
        ],
        "maxCapacityTheater": 55,
        "contactPhone": "02-2351-3696"
    },
    
    # The Executive Centre
    1038: {
        "rooms": [
            {
                "name": "董事會議室",
                "capacity": 20,
                "area": "約15坪",
                "layout": "會議型",
                "price": "每小時 2,000 元起",
                "equipment": "投影設備、視訊會議系統",
                "photo": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800"
            },
            {
                "name": "會議室A",
                "capacity": 12,
                "area": "約10坪",
                "layout": "會議型",
                "price": "每小時 1,500 元起",
                "equipment": "投影設備、白板",
                "photo": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800"
            },
            {
                "name": "會議室B",
                "capacity": 8,
                "area": "約6坪",
                "layout": "會議型",
                "price": "每小時 1,000 元起",
                "equipment": "投影設備、白板",
                "photo": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800"
            },
            {
                "name": "培訓室",
                "capacity": 45,
                "area": "約25坪",
                "layout": "教室型",
                "price": "每小時 3,000 元起",
                "equipment": "投影設備、白板",
                "photo": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800"
            }
        ],
        "maxCapacityTheater": 45,
        "contactPhone": "02-8101-8188"
    },
    
    # 典藏咖啡廳
    1044: {
        "rooms": [
            {
                "name": "包場空間",
                "capacity": 60,
                "area": "約45坪",
                "layout": "活動型",
                "price": "請洽詢",
                "equipment": "基本音響設備",
                "photo": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800"
            }
        ],
        "maxCapacityTheater": 60,
        "contactPhone": "02-2560-2220"
    },
    
    # 北科大創新育成中心
    1045: {
        "rooms": [
            {
                "name": "國際會議廳",
                "capacity": 80,
                "area": "約50坪",
                "layout": "劇院型/教室型",
                "price": "每小時 3,000 元起",
                "equipment": "投影設備、音響系統",
                "photo": "https://www.ntut.edu.tw/images/incubator.jpg"
            },
            {
                "name": "會議室A",
                "capacity": 30,
                "area": "約15坪",
                "layout": "會議型",
                "price": "每小時 1,500 元起",
                "equipment": "投影設備、白板",
                "photo": "https://www.ntut.edu.tw/images/meeting.jpg"
            },
            {
                "name": "會議室B",
                "capacity": 20,
                "area": "約10坪",
                "layout": "會議型",
                "price": "每小時 1,000 元起",
                "equipment": "投影設備、白板",
                "photo": "https://www.ntut.edu.tw/images/meeting.jpg"
            }
        ],
        "maxCapacityTheater": 80,
        "contactPhone": "02-2771-2171"
    },
    
    # 台北中山運動中心
    1334: {
        "rooms": [
            {
                "name": "多功能活動室",
                "capacity": 55,
                "area": "約40坪",
                "layout": "活動型",
                "price": "每小時 1,500 元起",
                "equipment": "音響設備、投影設備",
                "photo": "https://cssc.cyc.org.tw/images/activity.jpg"
            },
            {
                "name": "會議室",
                "capacity": 30,
                "area": "約15坪",
                "layout": "會議型",
                "price": "每小時 800 元起",
                "equipment": "投影設備、白板",
                "photo": "https://cssc.cyc.org.tw/images/meeting.jpg"
            }
        ],
        "maxCapacityTheater": 55,
        "contactPhone": "02-2581-1060"
    }
}

# 更新場地資料
updated_count = 0
for venue in venues:
    venue_id = venue.get('id')
    if venue_id in venue_updates:
        update_data = venue_updates[venue_id]
        # 更新會議室資訊
        venue['rooms'] = update_data.get('rooms', [])
        # 更新最大容納人數
        if 'maxCapacityTheater' in update_data:
            venue['maxCapacityTheater'] = update_data['maxCapacityTheater']
        # 更新場地類型
        if 'venueType' in update_data:
            venue['venueType'] = update_data['venueType']
        # 更新聯絡電話
        if 'contactPhone' in update_data:
            venue['contactPhone'] = update_data['contactPhone']
        # 更新圖片資訊
        if 'images' not in venue:
            venue['images'] = {}
        venue['images']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
        venue['images']['needsUpdate'] = False
        
        updated_count += 1
        print(f"✅ 已更新: {venue['name']} (ID: {venue_id}) - {len(venue['rooms'])} 個會議室")

# 寫回檔案
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n🎉 更新完成！共更新 {updated_count} 個場地")
