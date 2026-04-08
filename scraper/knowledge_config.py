#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/knowledge_config.py - 活動情境定義與問題模板
用於知識提取與詢問信生成
"""

# === 問題分類 ===
QUESTION_CATEGORIES = {
    "physical": "空間限制",
    "equipment": "設備規格",
    "pricing": "定價細節",
    "catering": "餐飲規定",
    "logistics": "交通後勤",
    "booking": "預訂風險",
    "decoration": "佈置規定",
    "schedule": "時間安排",
}

# === 6 種活動情境 ===
EVENT_SCENARIOS = {
    "研討會": {
        "label": "研討會",
        "description": "100-500人學術/企業研討會，需投影、分組討論空間",
        "defaultCapacity": {"min": 100, "max": 500},
        "questions": [
            {
                "id": "seminar_ceiling",
                "text": "研討會需要架設大型投影螢幕或LED背板，場地天花板高度是否足夠（建議3公尺以上）？",
                "category": "physical",
                "targetFields": ["rooms[].ceilingHeight", "rooms[].limitations[]"],
            },
            {
                "id": "seminar_pillar",
                "text": "會議室是否有柱子？柱子是否會遮擋後方觀眾的視線？",
                "category": "physical",
                "targetFields": ["rooms[].pillar", "rooms[].pillarInfo"],
            },
            {
                "id": "seminar_projector",
                "text": "場地內建投影設備的規格為何（流明數、投影距離）？是否可自備投影設備？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]", "rooms[].limitations[]"],
            },
            {
                "id": "seminar_wifi",
                "text": "場地可提供的網路頻寬為何？是否有獨立WiFi供會議使用？視訊直播是否順暢？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "seminar_mic",
                "text": "場地提供幾支無線麥克風？是否有桌上型麥克風供與會者提問？額外租借費用？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "seminar_recording",
                "text": "場地是否允許錄影直播？是否有相關設備可租借或需自備？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]", "rules.sound"],
            },
            {
                "id": "seminar_breakout",
                "text": "是否有鄰近的小會議室可供分組討論使用？費用如何計算？",
                "category": "physical",
                "targetFields": ["rooms[].breakoutRooms"],
            },
            {
                "id": "seminar_setup_time",
                "text": "活動前多久可以進場佈置？活動結束後多久需完成撤場？",
                "category": "schedule",
                "targetFields": ["rooms[].loadIn.loadInTime", "rooms[].loadIn.loadOutTime"],
            },
            {
                "id": "seminar_catering",
                "text": "場地是否限定使用場地指定餐飲？是否可外燴或自備茶點？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "seminar_lunch",
                "text": "午宴/便當是否可安排在會議室內用餐？有無額外清潔費？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "seminar_parking",
                "text": "場地是否提供免費停車位？可提供幾個？與會者近百人，停車是否方便？",
                "category": "logistics",
                "targetFields": ["logistics.parking"],
            },
            {
                "id": "seminar_mrt",
                "text": "場地離最近捷運站步行幾分鐘？是否有接駁車？",
                "category": "logistics",
                "targetFields": ["logistics.nearestMRT"],
            },
            {
                "id": "seminar_overtime",
                "text": "超時使用場地的計費方式為何？是否有彈性空間？",
                "category": "pricing",
                "targetFields": ["rooms[].pricing.overtimePerHour", "rooms[].loadIn.overtimeRate"],
            },
            {
                "id": "seminar_booking_lead",
                "text": "場地通常需要提前多久預訂？旺季時是否更難訂？",
                "category": "booking",
                "targetFields": ["risks.bookingLeadTime", "risks.peakSeasons"],
            },
            {
                "id": "seminar_price_diff",
                "text": "平日與假日的場地費是否有價差？半天與全天方案的時段如何劃分？",
                "category": "pricing",
                "targetFields": ["pricingTips[]"],
            },
            {
                "id": "seminar_cancellation",
                "text": "預訂後若需取消或改期，退費政策為何？需提前多久通知？",
                "category": "booking",
                "targetFields": ["rules.cancellation"],
            },
            {
                "id": "seminar_decoration",
                "text": "會場佈置（海報架、指示牌、簽名牆）是否有限制？可否使用膠帶或圖釘？",
                "category": "decoration",
                "targetFields": ["rules.decoration"],
            },
            {
                "id": "seminar_elevator",
                "text": "若有大型設備需運送，場地是否有貨梯？載重與尺寸限制？",
                "category": "logistics",
                "targetFields": ["rooms[].loadIn.elevatorCapacity", "rooms[].loadIn.elevatorSize"],
            },
        ],
    },
    "發表會": {
        "label": "發表會",
        "description": "產品發表、記者會、媒體活動，重視舞台、燈光、視覺效果",
        "defaultCapacity": {"min": 100, "max": 300},
        "questions": [
            {
                "id": "launch_stage",
                "text": "場地是否有固定舞台？尺寸多大？是否可加建舞台？高度限制？",
                "category": "physical",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "launch_ceiling",
                "text": "天花板高度是否足夠架設LED牆或大型背板（建議4公尺以上）？",
                "category": "physical",
                "targetFields": ["rooms[].ceilingHeight", "rooms[].limitations[]"],
            },
            {
                "id": "launch_lighting",
                "text": "場地內建燈光控制系統是否可調整？是否可自帶燈光設備？電力供應足夠嗎？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]", "rooms[].limitations[]"],
            },
            {
                "id": "launch_sound",
                "text": "場地音響系統規格？是否可外接音響設備？音量是否有限制？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]", "rules.sound"],
            },
            {
                "id": "launch_led",
                "text": "是否可架設LED電視牆？場地是否提供？尺寸與費用？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "launch_livestream",
                "text": "場地是否支援直播設備安裝？網路頻寬是否足夠穩定推流？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "launch_backstage",
                "text": "是否有後台/休息室供貴賓或表演者使用？",
                "category": "physical",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "launch_loadin",
                "text": "大型道具設備的進場動線為何？是否有貨梯？載重限制？可前一天進場佈置嗎？",
                "category": "logistics",
                "targetFields": ["rooms[].loadIn"],
            },
            {
                "id": "launch_setup_time",
                "text": "進場佈置可提前多久開始？活動結束後撤場時間多久？超時費用？",
                "category": "schedule",
                "targetFields": ["rooms[].loadIn.loadInTime", "rooms[].loadIn.loadOutTime"],
            },
            {
                "id": "launch_pillar",
                "text": "場地是否有柱子？是否影響攝影機或觀眾視線？",
                "category": "physical",
                "targetFields": ["rooms[].pillar", "rooms[].pillarInfo"],
            },
            {
                "id": "launch_power",
                "text": "場地電力供應是否充足？若有大型LED牆和燈光設備，是否需要額外拉電？",
                "category": "equipment",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "launch_catering",
                "text": "場地是否限定使用指定餐飲服務？可否安排茶會或自助餐？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "launch_parking",
                "text": "場地停車位數量？媒體轉播車是否有專用停車位？",
                "category": "logistics",
                "targetFields": ["logistics.parking", "logistics.busParking"],
            },
            {
                "id": "launch_booking",
                "text": "發表會檔期通常需要提前多久預訂？旺季時段有哪些？",
                "category": "booking",
                "targetFields": ["risks.bookingLeadTime", "risks.peakSeasons"],
            },
            {
                "id": "launch_insurance",
                "text": "大型活動是否需要額外投保公共意外責任險？場地是否有保險要求？",
                "category": "booking",
                "targetFields": ["rules.insurance"],
            },
            {
                "id": "launch_decoration",
                "text": "場地佈置限制？可否使用吊掛設備？天花板承重限制？",
                "category": "decoration",
                "targetFields": ["rules.decoration"],
            },
            {
                "id": "launch_cancellation",
                "text": "若活動取消或延期，退費政策為何？",
                "category": "booking",
                "targetFields": ["rules.cancellation"],
            },
        ],
    },
    "尾牙": {
        "label": "尾牙",
        "description": "企業年終聚餐，需宴會場地、舞台表演、音響燈光",
        "defaultCapacity": {"min": 100, "max": 1000},
        "questions": [
            {
                "id": "party_capacity",
                "text": "宴會式（圓桌）最大可容納多少人？若需舞台，容量是否會減少？",
                "category": "physical",
                "targetFields": ["rooms[].capacity.banquet"],
            },
            {
                "id": "party_stage",
                "text": "是否有固定舞台？尺寸多大？是否可加建伸展台或T台？",
                "category": "physical",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "party_ceiling",
                "text": "天花板高度是否足夠安排舞台表演（建議4公尺以上）？",
                "category": "physical",
                "targetFields": ["rooms[].ceilingHeight", "rooms[].limitations[]"],
            },
            {
                "id": "party_sound",
                "text": "場地音響系統規格？是否可外接樂器或DJ設備？音量是否有限制？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]", "rules.sound"],
            },
            {
                "id": "party_lighting",
                "text": "場地燈光是否可調暗？是否有舞台燈光設備？可否自帶燈光？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "party_screen",
                "text": "是否有投影或LED螢幕可播放影片？尺寸？是否可雙螢幕？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "party_catering",
                "text": "是否限定使用場地指定餐飲？中式/西式/自助餐選擇？每桌價格區間？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "party_alcohol",
                "text": "是否可自備酒類？是否有開瓶費？場地是否提供酒水服務？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "party_performance",
                "text": "是否允許安排表演節目（樂團、魔術、舞蹈）？是否有額外費用？",
                "category": "decoration",
                "targetFields": ["rules.sound"],
            },
            {
                "id": "party_lottery",
                "text": "是否可安排抽獎活動？大型獎品（如機車、電視）進場動線？",
                "category": "logistics",
                "targetFields": ["rooms[].loadIn"],
            },
            {
                "id": "party_setup",
                "text": "可提前多久進場佈置？尾牙通常需要至少半天佈置，是否可前一天進場？",
                "category": "schedule",
                "targetFields": ["rooms[].loadIn.setupDayBefore", "rooms[].loadIn.setupDayBeforeNote"],
            },
            {
                "id": "party_overtime",
                "text": "尾牙若超時（常見到晚上10點後），超時費用如何計算？",
                "category": "pricing",
                "targetFields": ["rooms[].loadIn.overtimeRate"],
            },
            {
                "id": "party_parking",
                "text": "尾牙參加者多達數百人，停車位是否足夠？是否提供免費停車？",
                "category": "logistics",
                "targetFields": ["logistics.parking"],
            },
            {
                "id": "party_bus",
                "text": "是否有遊覽車接送的空間？大型車可否停靠？",
                "category": "logistics",
                "targetFields": ["logistics.busParking"],
            },
            {
                "id": "party_peak",
                "text": "尾牙旺季（12月-1月）是否更難預訂？價格是否較高？建議提前多久訂？",
                "category": "booking",
                "targetFields": ["risks.bookingLeadTime", "risks.peakSeasons", "seasonal.peakMonths"],
            },
            {
                "id": "party_cancellation",
                "text": "尾牙取消或改期的退費政策？旺季是否有特殊規定？",
                "category": "booking",
                "targetFields": ["rules.cancellation"],
            },
        ],
    },
    "家庭日": {
        "label": "家庭日",
        "description": "企業家庭日，需室內外空間、親子友善設施、大量停車",
        "defaultCapacity": {"min": 200, "max": 2000},
        "questions": [
            {
                "id": "family_indoor_outdoor",
                "text": "場地是否有室內外空間可同時使用？戶外空間面積？是否有遮雨設施？",
                "category": "physical",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "family_capacity",
                "text": "包含家屬在內可能達數百至上千人，場地最大容納人數？",
                "category": "physical",
                "targetFields": ["rooms[].capacity"],
            },
            {
                "id": "family_safety",
                "text": "場地是否有安全限制？兒童活動區域是否需要額外安排？",
                "category": "physical",
                "targetFields": ["rules.other"],
            },
            {
                "id": "family_catering",
                "text": "是否可安排自助餐或餐車？是否限定使用場地餐飲？可否自備食物？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "family_bbq",
                "text": "戶外區域是否可安排烤肉或炊煮活動？是否有消防安全限制？",
                "category": "catering",
                "targetFields": ["rules.catering", "rules.other"],
            },
            {
                "id": "family_games",
                "text": "是否可在場地內安排闖關遊戲、充氣城堡等大型遊具？有無限制？",
                "category": "decoration",
                "targetFields": ["rules.decoration", "rules.insurance"],
            },
            {
                "id": "family_parking",
                "text": "家庭日參加者多自駕，停車位是否充足？免費停車時數？",
                "category": "logistics",
                "targetFields": ["logistics.parking"],
            },
            {
                "id": "family_bus",
                "text": "是否有遊覽車接駁空間？大型車停靠位置與限制？",
                "category": "logistics",
                "targetFields": ["logistics.busParking"],
            },
            {
                "id": "family_accessibility",
                "text": "場地是否無障礙友善？推嬰兒車是否方便？有無電梯？",
                "category": "logistics",
                "targetFields": ["logistics.wheelchairAccessible"],
            },
            {
                "id": "family_restroom",
                "text": "場地洗手間數量是否足夠應付大量人潮？是否有哺集乳室？",
                "category": "physical",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "family_noise",
                "text": "場地音量是否有限制？是否影響周邊住家？可否播放音樂？",
                "category": "equipment",
                "targetFields": ["rules.sound"],
            },
            {
                "id": "family_setup",
                "text": "大型活動佈置通常需一整天，是否可前一天進場？額外費用？",
                "category": "schedule",
                "targetFields": ["rooms[].loadIn.setupDayBefore"],
            },
            {
                "id": "family_weather",
                "text": "若遇雨天，是否有備用室內場地方案？室內空間是否足夠？",
                "category": "physical",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "family_insurance",
                "text": "大型家庭日是否需額外投保？場地保險要求？",
                "category": "booking",
                "targetFields": ["rules.insurance"],
            },
            {
                "id": "family_overtime",
                "text": "活動若延長，超時費用如何計算？是否可彈性延長？",
                "category": "pricing",
                "targetFields": ["rooms[].loadIn.overtimeRate"],
            },
        ],
    },
    "說明會": {
        "label": "說明會",
        "description": "50-200人產品說明、政策宣導、招商說明，重視投影音響品質",
        "defaultCapacity": {"min": 50, "max": 200},
        "questions": [
            {
                "id": "briefing_projector",
                "text": "投影設備規格？流明數是否足夠在明亮環境下清晰投影？是否有備用投影機？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "briefing_screen",
                "text": "投影螢幕尺寸？是否可使用雙螢幕或三螢幕？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "briefing_mic",
                "text": "場地提供幾支麥克風？是否有簡報筆/翻頁器？額外租借費用？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "briefing_sound",
                "text": "音響品質是否清晰？是否適合播放影片？是否有環繞音效？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "briefing_livestream",
                "text": "是否可安排同步直播（線上參與）？網路頻寬是否穩定？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "briefing_seating",
                "text": "座位安排是否可彈性調整（劇院式、教室式、U型）？不同排法的容量？",
                "category": "physical",
                "targetFields": ["rooms[].capacity"],
            },
            {
                "id": "briefing_ceiling",
                "text": "天花板高度是否影響投影效果或視線？",
                "category": "physical",
                "targetFields": ["rooms[].ceilingHeight"],
            },
            {
                "id": "briefing_pillar",
                "text": "是否有柱子遮擋視線？哪些座位區視線不佳？",
                "category": "physical",
                "targetFields": ["rooms[].pillar", "rooms[].pillarInfo"],
            },
            {
                "id": "briefing_catering",
                "text": "是否可安排茶點服務？費用如何計算？是否可自備？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "briefing_parking",
                "text": "場地是否提供免費停車？停車位數量？附近是否有公共停車場？",
                "category": "logistics",
                "targetFields": ["logistics.parking"],
            },
            {
                "id": "briefing_mrt",
                "text": "最近捷運站步行距離？方便與會者到達嗎？",
                "category": "logistics",
                "targetFields": ["logistics.nearestMRT"],
            },
            {
                "id": "briefing_setup",
                "text": "可提前多久進場測試設備？是否有技術人員現場支援？",
                "category": "schedule",
                "targetFields": ["rooms[].loadIn.loadInTime"],
            },
            {
                "id": "briefing_price",
                "text": "半天與全天的時段劃分？平日與假日的價差？是否有多時段折扣？",
                "category": "pricing",
                "targetFields": ["pricingTips[]"],
            },
            {
                "id": "briefing_booking",
                "text": "預訂需提前多久？是否有最低消費？",
                "category": "booking",
                "targetFields": ["risks.bookingLeadTime"],
            },
            {
                "id": "briefing_decoration",
                "text": "可否在會場外設置報到處或展示區？場地是否提供指示牌？",
                "category": "decoration",
                "targetFields": ["rules.decoration"],
            },
            {
                "id": "briefing_cancellation",
                "text": "取消或改期的退費政策？",
                "category": "booking",
                "targetFields": ["rules.cancellation"],
            },
        ],
    },
    "培訓課程": {
        "label": "培訓課程",
        "description": "20-80人企業內訓、工作坊，需白板、分組空間、餐飲安排",
        "defaultCapacity": {"min": 20, "max": 80},
        "questions": [
            {
                "id": "training_seating",
                "text": "是否可安排課桌式（每人一桌）或U型座位？不同排法的容量上限？",
                "category": "physical",
                "targetFields": ["rooms[].capacity.classroom", "rooms[].capacity.ushape"],
            },
            {
                "id": "training_whiteboard",
                "text": "場地是否有白板或 flipchart？數量？是否可額外租借？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "training_projector",
                "text": "投影設備規格？是否可連接筆電投影？是否有HDMI/VGA接頭？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "training_wifi",
                "text": "是否有穩定WiFi供學員使用？頻寬是否足夠多人同時連線？",
                "category": "equipment",
                "targetFields": ["rooms[].equipment[]"],
            },
            {
                "id": "training_power",
                "text": "座位區是否有電源插座？數量是否足夠學員筆電充電？",
                "category": "equipment",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "training_breakout",
                "text": "是否有鄰近空間可供分組討論？可同時分幾組？",
                "category": "physical",
                "targetFields": ["rooms[].breakoutRooms"],
            },
            {
                "id": "training_room_layout",
                "text": "會議室形狀（長方形/正方形/扇形）？是否適合分組活動？",
                "category": "physical",
                "targetFields": ["rooms[].layout"],
            },
            {
                "id": "training_ceiling",
                "text": "天花板高度是否足夠？培訓通常不需高天花板，但有無壓迫感？",
                "category": "physical",
                "targetFields": ["rooms[].ceilingHeight"],
            },
            {
                "id": "training_natural_light",
                "text": "會議室是否有自然採光？長時間培訓是否會覺得昏暗？",
                "category": "physical",
                "targetFields": ["rooms[].limitations[]"],
            },
            {
                "id": "training_lunch",
                "text": "是否可安排午餐（便當或自助餐）？費用？用餐地點在會議室內或另設餐區？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "training_tea",
                "text": "茶水服務是否包含在場地費中？還是額外計費？上下午各幾次？",
                "category": "catering",
                "targetFields": ["rules.catering"],
            },
            {
                "id": "training_setup",
                "text": "可提前多久進場準備教材？培訓結束後撤場時間？",
                "category": "schedule",
                "targetFields": ["rooms[].loadIn.loadInTime", "rooms[].loadIn.loadOutTime"],
            },
            {
                "id": "training_parking",
                "text": "講師和學員的停車需求？是否有免費停車位？",
                "category": "logistics",
                "targetFields": ["logistics.parking"],
            },
            {
                "id": "training_mrt",
                "text": "交通是否便利？捷運站步行距離？",
                "category": "logistics",
                "targetFields": ["logistics.nearestMRT"],
            },
            {
                "id": "training_multi_day",
                "text": "若為多天課程，是否可前一晚保留教材不撤場？費用如何計算？",
                "category": "pricing",
                "targetFields": ["rooms[].loadIn.setupDayBefore", "rooms[].loadIn.setupDayBeforeNote"],
            },
            {
                "id": "training_accommodation",
                "text": "若為外地培訓，場地是否附設住宿或鄰近飯店？有無企業優惠？",
                "category": "logistics",
                "targetFields": ["logistics"],
            },
            {
                "id": "training_booking",
                "text": "場地預訂提前量？週末是否較容易訂到？",
                "category": "booking",
                "targetFields": ["risks.bookingLeadTime"],
            },
        ],
    },
}

# === 問題→schema 欄位對照 ===
# 用於判斷某問題的答案是否已存在於 AI 知識庫
# key: targetField 路徑, value: 檢查函數（接收 ai_knowledge_base venue dict）
def _safe_get(obj, *keys, default=None):
    """安全多層取值，處理中間值為 None 的情況"""
    current = obj
    for key in keys:
        if current is None or not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def _has_truthy(obj, *keys):
    """安全多層取值並檢查是否為 truthy"""
    val = _safe_get(obj, *keys)
    return bool(val)


FIELD_CHECKERS = {
    "rooms[].ceilingHeight": lambda v: any(
        r.get("ceilingHeight") for r in v.get("rooms", [])
    ),
    "rooms[].pillar": lambda v: any(
        r.get("pillar") is not None for r in v.get("rooms", [])
    ),
    "rooms[].pillarInfo": lambda v: any(
        r.get("pillarInfo") for r in v.get("rooms", [])
    ),
    "rooms[].limitations[]": lambda v: any(
        r.get("limitations") and len(r["limitations"]) > 0
        for r in v.get("rooms", [])
    ),
    "rooms[].equipment[]": lambda v: any(
        r.get("equipment") and len(r["equipment"]) > 0
        for r in v.get("rooms", [])
    ),
    "rooms[].capacity": lambda v: any(
        r.get("capacity") for r in v.get("rooms", [])
    ),
    "rooms[].capacity.banquet": lambda v: any(
        _safe_get(r, "capacity", "banquetEastern")
        or _safe_get(r, "capacity", "banquetWestern")
        or _safe_get(r, "capacity", "banquet")
        for r in v.get("rooms", [])
    ),
    "rooms[].capacity.classroom": lambda v: any(
        _safe_get(r, "capacity", "classroom") for r in v.get("rooms", [])
    ),
    "rooms[].capacity.ushape": lambda v: any(
        _safe_get(r, "capacity", "uShape") or _safe_get(r, "capacity", "ushape")
        for r in v.get("rooms", [])
    ),
    "rooms[].loadIn": lambda v: any(
        r.get("loadIn") for r in v.get("rooms", [])
    ),
    "rooms[].loadIn.elevatorCapacity": lambda v: any(
        _safe_get(r, "loadIn", "elevatorCapacity")
        or _safe_get(r, "loadIn", "elevator")
        for r in v.get("rooms", [])
    ),
    "rooms[].loadIn.elevatorSize": lambda v: any(
        _safe_get(r, "loadIn", "elevatorSize") for r in v.get("rooms", [])
    ),
    "rooms[].loadIn.loadInTime": lambda v: any(
        _safe_get(r, "loadIn", "loadInTime")
        or _safe_get(r, "loadIn", "setupTime")
        for r in v.get("rooms", [])
    ),
    "rooms[].loadIn.loadOutTime": lambda v: any(
        _safe_get(r, "loadIn", "loadOutTime")
        or _safe_get(r, "loadIn", "teardownTime")
        for r in v.get("rooms", [])
    ),
    "rooms[].loadIn.setupDayBefore": lambda v: any(
        _safe_get(r, "loadIn", "setupDayBefore") is not None
        for r in v.get("rooms", [])
    ),
    "rooms[].loadIn.setupDayBeforeNote": lambda v: any(
        _safe_get(r, "loadIn", "setupDayBeforeNote") for r in v.get("rooms", [])
    ),
    "rooms[].loadIn.overtimeRate": lambda v: any(
        _safe_get(r, "loadIn", "overtimeRate") for r in v.get("rooms", [])
    ),
    "rooms[].breakoutRooms": lambda v: any(
        r.get("breakoutRooms") for r in v.get("rooms", [])
    ),
    "rooms[].layout": lambda v: any(
        r.get("layout") for r in v.get("rooms", [])
    ),
    "rooms[].pricing.overtimePerHour": lambda v: any(
        _safe_get(r, "pricing", "overtimePerHour")
        or _safe_get(r, "pricing", "additionalHour")
        or _safe_get(r, "pricing", "overtime")
        for r in v.get("rooms", [])
    ),
    "risks.bookingLeadTime": lambda v: bool(
        _safe_get(v, "risks", "bookingLeadTime")
    ),
    "risks.peakSeasons": lambda v: bool(
        _safe_get(v, "risks", "peakSeasons") or _safe_get(v, "seasonal", "peakMonths")
    ),
    "rules.catering": lambda v: bool(_safe_get(v, "rules", "catering")),
    "rules.decoration": lambda v: bool(_safe_get(v, "rules", "decoration")),
    "rules.sound": lambda v: bool(_safe_get(v, "rules", "sound")),
    "rules.cancellation": lambda v: bool(_safe_get(v, "rules", "cancellation")),
    "rules.insurance": lambda v: bool(_safe_get(v, "rules", "insurance")),
    "rules.other": lambda v: bool(_safe_get(v, "rules", "other")),
    "rules.loadIn": lambda v: bool(_safe_get(v, "rules", "loadIn")),
    "pricingTips[]": lambda v: bool(
        v.get("pricingTips") and len(v["pricingTips"]) > 0
    ),
    "logistics": lambda v: bool(v.get("logistics")),
    "logistics.parking": lambda v: bool(_safe_get(v, "logistics", "parking")),
    "logistics.nearestMRT": lambda v: bool(_safe_get(v, "logistics", "nearestMRT")),
    "logistics.busParking": lambda v: bool(_safe_get(v, "logistics", "busParking")),
    "logistics.wheelchairAccessible": lambda v: _safe_get(v, "logistics", "wheelchairAccessible") is not None,
    "seasonal.peakMonths": lambda v: bool(
        _safe_get(v, "seasonal", "peakMonths")
    ),
}

# === 知識提取用關鍵字 ===
# 用於 KnowledgeExtractor 從文字中偵測特定知識類型

RULES_KEYWORDS = {
    "catering": {
        "zh": ["外燴", "外食", "餐飲", "自備食物", "禁帶", "禁止外食",
               "限用", "指定餐飲", "餐盒", "便當", "宴席", "廚房"],
        "en": ["catering", "outside food", "beverage", "corkage", "banquet"],
    },
    "decoration": {
        "zh": ["佈置", "裝潢", "膠帶", "圖釘", "釘子", "貼紙", "海報",
               "吊掛", "懸吊", "氣球", "花藝", "禁止釘", "牆面"],
        "en": ["decoration", "tape", "nail", "pin", "balloon", "banner", "hanging"],
    },
    "sound": {
        "zh": ["音量", "分貝", "音響", "噪音", "音樂限制", "音響設備",
               "擴音", "喇叭", "外部音響"],
        "en": ["sound", "volume", "noise", "decibel", "dB", "speaker", "amplifier"],
    },
    "loadIn": {
        "zh": ["進場", "撤場", "布置時間", "佈置時間", "卸貨", "貨梯",
               "載重", "進場時間", "撤場時間", "動線"],
        "en": ["setup", "teardown", "load-in", "loadout", "freight", "elevator"],
    },
    "cancellation": {
        "zh": ["取消", "退費", "違約", "改期", "延期", "退訂", "訂金"],
        "en": ["cancellation", "refund", "penalty", "reschedule", "deposit"],
    },
    "insurance": {
        "zh": ["保險", "公共意外", "責任險", "投保"],
        "en": ["insurance", "liability", "coverage"],
    },
}

LOADIN_KEYWORDS = {
    "elevator": {
        "zh": ["貨梯", "電梯", "升降機", "載貨電梯"],
        "en": ["freight elevator", "cargo elevator", "service elevator", "lift"],
    },
    "elevator_spec": {
        "zh": ["載重", "限重", "噸", "公斤", "尺寸"],
        "en": ["capacity", "weight limit", "ton", "kg", "dimension", "size"],
    },
    "vehicle": {
        "zh": ["車輛", "卸貨區", "車道", "車輛直達", "貨車"],
        "en": ["vehicle", "loading dock", "truck", "delivery"],
    },
    "setup_teardown": {
        "zh": ["進場時間", "撤場時間", "布置時間", "前一天進場", "夜間佈置"],
        "en": ["setup time", "teardown time", "day before", "overnight setup"],
    },
}

EQUIPMENT_SPEC_KEYWORDS = {
    "projector": {
        "zh": ["投影機", "投影設備", "流明", "投影距離"],
        "en": ["projector", "lumens", "throw distance"],
    },
    "screen": {
        "zh": ["投影幕", "螢幕", "投影螢幕", "布幕"],
        "en": ["screen", "projection screen"],
    },
    "microphone": {
        "zh": ["麥克風", "無線麥克風", "有線麥克風", "桌上型麥克風"],
        "en": ["microphone", "wireless mic", "gooseneck mic"],
    },
    "sound_system": {
        "zh": ["音響", "聲道", "喇叭", "擴大機", "混音器"],
        "en": ["sound system", "speaker", "amplifier", "mixer", "channel"],
    },
    "lighting": {
        "zh": ["燈光", "調光", "舞台燈", "LED燈", "照明"],
        "en": ["lighting", "dimmer", "stage light", "LED"],
    },
    "network": {
        "zh": ["網路", "WiFi", "頻寬", "寬頻", "網際網路"],
        "en": ["network", "WiFi", "bandwidth", "internet", "broadband"],
    },
}


def get_all_questions(scenario: str = None) -> list:
    """取得所有或指定情境的問題列表"""
    if scenario:
        s = EVENT_SCENARIOS.get(scenario)
        return s["questions"] if s else []
    all_q = []
    for s in EVENT_SCENARIOS.values():
        all_q.extend(s["questions"])
    return all_q


def get_scenarios_list() -> list:
    """取得所有情境名稱列表"""
    return list(EVENT_SCENARIOS.keys())


def get_question_by_id(question_id: str) -> dict:
    """根據 ID 取得問題"""
    for scenario in EVENT_SCENARIOS.values():
        for q in scenario["questions"]:
            if q["id"] == question_id:
                return q
    return None


# === 本地 PDF → 場地對照表 ===
# 用於 pipeline.py knowledge --pdf 模式
# key: 相對於專案根目錄的 PDF 路徑, value: venue ID
LOCAL_PDF_MAP = {
    # 集思竹科 (1042)
    "jhsi_hcph_docs/竹科_租借辦法_202312.pdf": 1042,
    "jhsi_hcph_docs/竹科_管理規則_202312.pdf": 1042,
    "jhsi_hcph_docs/竹科_餐飲管理規則_202312.pdf": 1042,
    "jhsi_hcph_docs/竹科-場地租用申請表-20250402.pdf": 1042,
    "jhsi_hcph_docs/竹科_會議事務用品訂購單_20250214.pdf": 1042,

    # 集思台中新烏日 (1498)
    "jhsi_wuri_docs/台中新烏日-租借辦法_2022.pdf": 1498,
    "jhsi_wuri_docs/台中新烏日-管理規則_2022.pdf": 1498,
    "jhsi_wuri_docs/台中新烏日-外食餐飲管理規則_2022.pdf": 1498,
    "jhsi_wuri_docs/台中新烏日_場地租借申請表_20260102.pdf": 1498,
    "jhsi_wuri_docs/台中新烏日_事務單_20260102.pdf": 1498,

    # 美福飯店
    "mayfull_pkg1.pdf": 1090,
    "mayfull_pkg2.pdf": 1090,

    # 晶華酒店
    "regent_meeting_package.pdf": 1086,
    "regent_floorplan_8.pdf": 1086,
    "regent_floorplan_9.pdf": 1086,
    "regent_floorplan_10.pdf": 1086,
    "regent_floorplan_11.pdf": 1086,
    "regent_floorplan_12.pdf": 1086,
    "regent_floorplan_13.pdf": 1086,

    # 台北花園酒店
    "tghotel_rooms.pdf": 1083,

    # 圓山大飯店
    "archive/oneoff_scripts/grand_hotel_capacity.pdf": 1072,
    "archive/oneoff_scripts/grand_hotel_dimensions.pdf": 1072,

    # 六福萬怡
    "archive/oneoff_scripts/marriott_pricing.pdf": 1043,
    "archive/oneoff_scripts/marriott_venue_intro.pdf": 1043,

    # 喜來登
    "archive/oneoff_scripts/sheraton_meeting_rooms.pdf": 1075,

    # 集思系列會議中心
    "archive/oneoff_scripts/gis_ntu_2025.pdf": 1128,   # 集思台大會議中心
    "archive/oneoff_scripts/gis_motc_2025.pdf": 1494,  # 集思交通部國際會議中心
    "archive/oneoff_scripts/gis_hsp_2026.pdf": 1496,   # 集思竹科會議中心
    "archive/oneoff_scripts/gis_wuri_2026.pdf": 1498,  # 集思台中新烏日會議中心
    "archive/oneoff_scripts/gis_wuri_2026_correct.pdf": 1498,
    "archive/oneoff_scripts/gis_tc_2025.pdf": 1497,    # 集思台中文心會議中心
    "archive/oneoff_scripts/gis_tc_2025_correct.pdf": 1497,

    # 南港展覽館
    "archive/oneoff_scripts/nangang_official.pdf": 1500,
    "archive/oneoff_scripts/nangang_pricing_2021.pdf": 1500,

    # 台大醫院國際會議中心
    "archive/oneoff_scripts/ntucc_venue_list_20250401.pdf": 1126,
    "archive/oneoff_scripts/ntucc_pricing.pdf": 1126,

    # 維多麗雅酒店
    "archive/oneoff_scripts/victoria_pdf.pdf": 1051,
    "archive/oneoff_scripts/victoria_capacity.pdf": 1051,
    "archive/oneoff_scripts/victoria_2022.pdf": 1051,
    "archive/oneoff_scripts/victoria_2022_event_venue.pdf": 1051,

    # 台北國際會議中心 (TICC)
    "archive/oneoff_scripts/ticc_official_20260326_203540.pdf": 1500,

    # 台北世貿中心
    "archive/oneoff_scripts/twtc_pricing_2025.pdf": 1501,

    # 集思竹科課程表
    "archive/oneoff_scripts/集思竹科課程表_20260326_213828.pdf": 1042,

    # 台中自然科学博物馆
    "archive/oneoff_scripts/nutut_venue_rental.pdf": 1498,

    # 台北國際會議中心 (TICC)  
    "archive/oneoff_scripts/ticc_rental_standards.pdf": 1448,

    # 台北文華東方
    "archive/oneoff_scripts/mandarin_oriental_meeting.pdf": 1085,
    "archive/oneoff_scripts/mandarin_pdf.pdf": 1085,
    "archive/oneoff_scripts/test_mandarin.pdf": 1085,
}


def get_venue_pdfs(venue_id: int, project_root: str = ".") -> list:
    """取得指定場地的所有本地 PDF 路徑"""
    pdfs = []
    for rel_path, vid in LOCAL_PDF_MAP.items():
        if vid == venue_id:
            full_path = os.path.join(project_root, rel_path)
            if os.path.exists(full_path):
                pdfs.append(full_path)
    return pdfs


def get_all_pdf_groups() -> dict:
    """取得所有 {venue_id: [pdf_paths]} 對照"""
    groups = {}
    for rel_path, vid in LOCAL_PDF_MAP.items():
        groups.setdefault(vid, []).append(rel_path)
    return groups


# Need 'os' for get_venue_pdfs
import os
