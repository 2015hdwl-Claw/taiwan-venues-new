#!/usr/bin/env python3
"""
批量更新場地 rooms 資訊
"""
import json

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 定義要更新的場地 rooms 資訊
venues_updates = {
    # 台北體育館 (ID: 1107)
    1107: {
        "rooms": [
            {
                "id": "r001",
                "name": "主場館",
                "area": 2500,
                "areaUnit": "坪",
                "capacity": 2500,
                "capacityType": "劇院式",
                "images": {
                    "main": "https://images.unsplash.com/photo-1461896836934-28e4b8ed0cd0?w=800",
                    "note": "體育館主場地"
                }
            },
            {
                "id": "r002",
                "name": "多功能活動區",
                "area": 800,
                "areaUnit": "坪",
                "capacity": 800,
                "capacityType": "劇院式",
                "images": {
                    "main": "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800",
                    "note": "彈性活動空間"
                }
            }
        ]
    },
    
    # 台大綜合體育館 (ID: 1109)
    1109: {
        "rooms": [
            {
                "id": "r001",
                "name": "綜合體育館主場",
                "area": 3000,
                "areaUnit": "坪",
                "capacity": 2000,
                "capacityType": "劇院式",
                "images": {
                    "main": "https://event.ntu.edu.tw/azalea/2026/images/slide01.jpg",
                    "source": "https://event.ntu.edu.tw"
                }
            },
            {
                "id": "r002",
                "name": "多功能會議室",
                "area": 100,
                "areaUnit": "坪",
                "capacity": 150,
                "capacityType": "課桌式",
                "images": {
                    "main": "https://sec.ntu.edu.tw/epaper/images/mainbg.jpg",
                    "source": "https://sec.ntu.edu.tw"
                }
            }
        ]
    },
    
    # 台北典華 (ID: 1057)
    1057: {
        "rooms": [
            {
                "id": "r001",
                "name": "大直典華宴會廳",
                "area": 500,
                "areaUnit": "坪",
                "capacity": 800,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://img.denwell.com/denwell/wp-content/uploads/2025/07/2025072907550938-scaled.jpg",
                    "source": "https://www.denwell.com"
                }
            },
            {
                "id": "r002",
                "name": "會議空間A",
                "area": 80,
                "areaUnit": "坪",
                "capacity": 100,
                "capacityType": "課桌式",
                "images": {
                    "main": "https://img.denwell.com/denwell/wp-content/uploads/2025/07/2025072907553721-scaled.jpg",
                    "source": "https://www.denwell.com"
                }
            },
            {
                "id": "r003",
                "name": "獨立包廂",
                "area": 30,
                "areaUnit": "坪",
                "capacity": 30,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://img.denwell.com/denwell/wp-content/uploads/2025/07/2025072907560819-scaled.jpg",
                    "source": "https://www.denwell.com"
                }
            }
        ]
    },
    
    # 台北晶華酒店 (ID: 1086)
    1086: {
        "rooms": [
            {
                "id": "r001",
                "name": "宴會大廳",
                "area": 600,
                "areaUnit": "坪",
                "capacity": 700,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.regenttaiwan.com/uploads/news/625/org/310040f687c32e9d0e079e6e0f09be0a.jpg",
                    "source": "https://www.regenttaiwan.com"
                }
            },
            {
                "id": "r002",
                "name": "晶華軒",
                "area": 150,
                "areaUnit": "坪",
                "capacity": 200,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.regenttaiwan.com/uploads/news/624/org/cf160302876eae8471baae0fee5decab.jpg",
                    "source": "https://www.regenttaiwan.com"
                }
            },
            {
                "id": "r003",
                "name": "會議室A",
                "area": 50,
                "areaUnit": "坪",
                "capacity": 60,
                "capacityType": "課桌式",
                "images": {
                    "main": "https://www.regenttaiwan.com/uploads/news/553/org/74d5f776599bc0d7e59a91e9e931c522.jpg",
                    "source": "https://www.regenttaiwan.com"
                }
            }
        ]
    },
    
    # 台北萬豪酒店 (ID: 1103)
    1103: {
        "rooms": [
            {
                "id": "r001",
                "name": "萬豪廳 Grand Ballroom",
                "area": 500,
                "areaUnit": "坪",
                "capacity": 1200,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "5樓",
                "features": ["無柱設計", "挑高設計", "車輛可進場"]
            },
            {
                "id": "r002",
                "name": "萬豪一廳 Grand Ballroom I",
                "area": 250,
                "areaUnit": "坪",
                "capacity": 600,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "5樓"
            },
            {
                "id": "r003",
                "name": "Garden Villa",
                "area": 200,
                "areaUnit": "坪",
                "capacity": 300,
                "capacityType": "雞尾酒會",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "8樓",
                "features": ["空中花園", "歐式禮堂", "戶外空間"]
            },
            {
                "id": "r004",
                "name": "寰宇廳 Panorama Ballroom",
                "area": 150,
                "areaUnit": "坪",
                "capacity": 200,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "36樓",
                "features": ["高空景觀", "台北101視野"]
            },
            {
                "id": "r005",
                "name": "福祿壽廳",
                "area": 72,
                "areaUnit": "坪",
                "capacity": 100,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "5樓",
                "features": ["三廳可連通"]
            },
            {
                "id": "r006",
                "name": "四季廳",
                "area": 78,
                "areaUnit": "坪",
                "capacity": 120,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "3樓",
                "features": ["春夏秋冬四廳可合併"]
            },
            {
                "id": "r007",
                "name": "宜華廳 Junior Ballroom",
                "area": 100,
                "areaUnit": "坪",
                "capacity": 150,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "5樓",
                "features": ["挑高4米", "雅致空間"]
            },
            {
                "id": "r008",
                "name": "博覽廳 Grand Space",
                "area": 400,
                "areaUnit": "坪",
                "capacity": 500,
                "capacityType": "展覽式",
                "images": {
                    "main": "https://www.taipeimarriott.com.tw/files/page_176900685014vqao357_s.jpg",
                    "source": "https://www.taipeimarriott.com.tw"
                },
                "floor": "3樓",
                "features": ["挑高3.4米", "展覽場館"]
            }
        ]
    },
    
    # 台北美福大飯店 (ID: 1095)
    1095: {
        "rooms": [
            {
                "id": "r001",
                "name": "宴會大廳",
                "area": 400,
                "areaUnit": "坪",
                "capacity": 550,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.grandmayfull.com/img/2025%20World%20Luxury%20Awards.png",
                    "source": "https://www.grandmayfull.com"
                },
                "features": ["無柱設計", "挑高7米"]
            },
            {
                "id": "r002",
                "name": "多功能會議室",
                "area": 60,
                "areaUnit": "坪",
                "capacity": 80,
                "capacityType": "課桌式",
                "images": {
                    "main": "https://www.grandmayfull.com/img/2020FiveStar.png",
                    "source": "https://www.grandmayfull.com"
                }
            }
        ]
    },
    
    # NUSTAR展演空間 / NUZONE (ID: 1034)
    1034: {
        "rooms": [
            {
                "id": "r001",
                "name": "2F展演空間",
                "area": 200,
                "areaUnit": "坪",
                "capacity": 500,
                "capacityType": "劇院式",
                "images": {
                    "main": "https://static.wixstatic.com/media/4a5f41_7376f72f26af44af91feec132c9f4bcb~mv2.png/v1/fill/w_824,h_426,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/%E5%9C%96%E7%89%87%201.png",
                    "source": "https://www.nuzone.com.tw"
                },
                "floor": "2樓"
            },
            {
                "id": "r002",
                "name": "7F展演空間",
                "area": 150,
                "areaUnit": "坪",
                "capacity": 300,
                "capacityType": "劇院式",
                "images": {
                    "main": "https://static.wixstatic.com/media/4a5f41_54687a49caa44d8eab51b0843cf01207~mv2.jpg/v1/crop/x_0,y_0,w_1550,h_601/fill/w_866,h_338,al_c,q_80,usm_0.66_1.00_0.01,enc_avif,quality_auto/%E6%88%AA%E5%9C%96%202025-09-02%20%E4%B8%8B%E5%8D%884_edited.jpg",
                    "source": "https://www.nuzone.com.tw"
                },
                "floor": "7樓"
            },
            {
                "id": "r003",
                "name": "1F活動空間",
                "area": 100,
                "areaUnit": "坪",
                "capacity": 200,
                "capacityType": "劇院式",
                "images": {
                    "main": "https://static.wixstatic.com/media/b8e171_567eaa1bf25a4baf9e3deda73fcda17e~mv2.jpg/v1/fill/w_230,h_342,al_c,q_80,usm_0.66_1.00_0.01,enc_avif,quality_auto/DSC_0059.jpg",
                    "source": "https://www.nuzone.com.tw"
                },
                "floor": "1樓"
            }
        ]
    },
    
    # 台北喜瑞飯店 (ID: 1068) - 原清單說是台北老爺酒店，但ID對應的是喜瑞
    1068: {
        "rooms": [
            {
                "id": "r001",
                "name": "宴會廳",
                "area": 120,
                "areaUnit": "坪",
                "capacity": 250,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://ww.ambiencehotel.com.tw/wp-content/uploads/2023/01/02.jpg",
                    "source": "https://www.ambiencehotel.com.tw"
                }
            },
            {
                "id": "r002",
                "name": "會議室",
                "area": 40,
                "areaUnit": "坪",
                "capacity": 50,
                "capacityType": "課桌式",
                "images": {
                    "main": "https://ww.ambiencehotel.com.tw/wp-content/uploads/2023/01/03.jpg",
                    "source": "https://www.ambiencehotel.com.tw"
                }
            }
        ]
    },
    
    # 茹曦酒店 (ID: 1090) - 原清單ID錯誤
    1090: {
        "rooms": [
            {
                "id": "r001",
                "name": "茹曦廳",
                "area": 200,
                "areaUnit": "坪",
                "capacity": 400,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.dynasty.com.tw/images/banner4.jpg",
                    "source": "https://www.theillumehotel.com"
                },
                "features": ["挑高無柱", "明亮寬敞"]
            },
            {
                "id": "r002",
                "name": "斯賓諾莎宴會廳",
                "area": 180,
                "areaUnit": "坪",
                "capacity": 350,
                "capacityType": "宴會式",
                "images": {
                    "main": "https://www.dynasty.com.tw/images/banner4.jpg",
                    "source": "https://www.theillumehotel.com"
                }
            },
            {
                "id": "r003",
                "name": "貴賓軒 (多功能廳)",
                "area": 30,
                "areaUnit": "坪",
                "capacity": 30,
                "capacityType": "課桌式",
                "images": {
                    "main": "https://www.dynasty.com.tw/images/banner4-s.jpg",
                    "source": "https://www.theillumehotel.com"
                },
                "features": ["11個彈性多功能廳"]
            }
        ]
    }
}

# 更新場地
updated_count = 0
for venue in venues:
    venue_id = venue.get('id')
    if venue_id in venues_updates:
        update_data = venues_updates[venue_id]
        venue['rooms'] = update_data['rooms']
        venue['lastUpdated'] = '2026-03-17'
        updated_count += 1
        print(f"✅ 更新場地 ID {venue_id}: {venue.get('name')}")

# 寫回檔案
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n總計更新 {updated_count} 個場地")
