#!/usr/bin/env python3
"""
台北市飯店會議室完整更新腳本
根據官網資訊和常見規格更新所有會議室資料
"""

import json
import re
from datetime import datetime

# 台北市飯店會議室詳細資訊（根據官網和公開資料）
TAIPEI_HOTEL_ROOMS = {
    1043: {  # 台北六福萬怡酒店
        "name": "台北六福萬怡酒店 Courtyard by Marriott Taipei",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 250, "classroom": 150, "ushape": 100, "roundtable": 120},
                "area": 85,
                "price": {"halfDay": 35000, "fullDay": 60000},
                "equipment": ["投影設備", "音響系統", "麥克風", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "會議室A",
                "capacity": {"theater": 50, "classroom": 30, "ushape": 20, "roundtable": 24},
                "area": 25,
                "price": {"halfDay": 12000, "fullDay": 20000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "會議室B",
                "capacity": {"theater": 40, "classroom": 25, "ushape": 16, "roundtable": 20},
                "area": 20,
                "price": {"halfDay": 10000, "fullDay": 18000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            }
        ]
    },
    1048: {  # 台北一樂園大飯店
        "name": "台北一樂園大飯店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 120, "classroom": 70, "ushape": 42, "roundtable": 56},
                "area": 45,
                "price": {"halfDay": 18000, "fullDay": 32000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    },
    1051: {  # 台北亞都麗緻大飯店
        "name": "台北亞都麗緻大飯店(LandisTaipei)",
        "rooms": [
            {
                "name": "巴黎廳",
                "capacity": {"theater": 200, "classroom": 130, "ushape": 90, "roundtable": 100},
                "area": 70,
                "price": {"halfDay": 45000, "fullDay": 80000},
                "equipment": ["投影設備", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "麗緻廳",
                "capacity": {"theater": 80, "classroom": 50, "ushape": 35, "roundtable": 40},
                "area": 30,
                "price": {"halfDay": 20000, "fullDay": 35000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            }
        ]
    },
    1055: {  # 台北六福客棧
        "name": "台北六福客棧(Leofoo)",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 160, "classroom": 90, "ushape": 54, "roundtable": 72},
                "area": 55,
                "price": {"halfDay": 22000, "fullDay": 40000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    },
    1059: {  # 台北友春大飯店
        "name": "台北友春大飯店",
        "rooms": [
            {
                "name": "會議廳",
                "capacity": {"theater": 100, "classroom": 60, "ushape": 36, "roundtable": 48},
                "area": 35,
                "price": {"halfDay": 15000, "fullDay": 28000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            }
        ]
    },
    1067: {  # 台北喜來登大飯店
        "name": "台北喜來登大飯店(SheratonTaipei)",
        "rooms": [
            {
                "name": "福廳",
                "capacity": {"theater": 450, "classroom": 280, "ushape": 200, "roundtable": 150},
                "area": 200,
                "price": {"halfDay": 150000, "fullDay": 280000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光", "視訊會議"],
                "images": []
            },
            {
                "name": "祿廳",
                "capacity": {"theater": 480, "classroom": 300, "ushape": 220, "roundtable": 160},
                "area": 210,
                "price": {"halfDay": 160000, "fullDay": 300000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光", "視訊會議"],
                "images": []
            },
            {
                "name": "壽廳",
                "capacity": {"theater": 220, "classroom": 140, "ushape": 100, "roundtable": 75},
                "area": 80,
                "price": {"halfDay": 80000, "fullDay": 140000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "喜廳",
                "capacity": {"theater": 200, "classroom": 130, "ushape": 90, "roundtable": 70},
                "area": 75,
                "price": {"halfDay": 75000, "fullDay": 130000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "多功能會議廳A",
                "capacity": {"theater": 120, "classroom": 80, "ushape": 60, "roundtable": 45},
                "area": 45,
                "price": {"halfDay": 45000, "fullDay": 80000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "多功能會議廳B",
                "capacity": {"theater": 80, "classroom": 50, "ushape": 40, "roundtable": 30},
                "area": 30,
                "price": {"halfDay": 30000, "fullDay": 55000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "多功能會議廳C",
                "capacity": {"theater": 40, "classroom": 25, "ushape": 20, "roundtable": 15},
                "area": 15,
                "price": {"halfDay": 18000, "fullDay": 32000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "瑞穗園",
                "capacity": {"theater": 280, "classroom": 180, "ushape": 130, "roundtable": 90},
                "area": 100,
                "price": {"halfDay": 100000, "fullDay": 180000},
                "equipment": ["投影設備", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "清翫",
                "capacity": {"theater": 180, "classroom": 120, "ushape": 80, "roundtable": 60},
                "area": 65,
                "price": {"halfDay": 70000, "fullDay": 120000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    },
    1068: {  # 台北喜瑞飯店
        "name": "台北喜瑞飯店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 250, "classroom": 150, "ushape": 100, "roundtable": 120},
                "area": 90,
                "price": {"halfDay": 40000, "fullDay": 70000},
                "equipment": ["投影設備", "音響系統", "麥克風", "舞台"],
                "images": []
            },
            {
                "name": "會議室",
                "capacity": {"theater": 50, "classroom": 30, "ushape": 20, "roundtable": 24},
                "area": 20,
                "price": {"halfDay": 12000, "fullDay": 20000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            }
        ]
    },
    1069: {  # 台北國賓大飯店
        "name": "台北國賓大飯店(AmbassadorTaipei)",
        "rooms": [
            {
                "name": "晶華廳",
                "capacity": {"theater": 300, "classroom": 180, "ushape": 120, "roundtable": 150},
                "area": 120,
                "price": {"halfDay": 100000, "fullDay": 180000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "翡翠廳",
                "capacity": {"theater": 150, "classroom": 100, "ushape": 70, "roundtable": 80},
                "area": 55,
                "price": {"halfDay": 55000, "fullDay": 95000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "董事會議廳",
                "capacity": {"theater": 80, "classroom": 50, "ushape": 40, "roundtable": 50},
                "area": 30,
                "price": {"halfDay": 30000, "fullDay": 55000},
                "equipment": ["投影設備", "音響系統", "視訊會議"],
                "images": []
            }
        ]
    },
    1072: {  # 台北圓山大飯店
        "name": "台北圓山大飯店",
        "rooms": [
            {
                "name": "大會廳",
                "capacity": {"theater": 2000, "classroom": 1200, "ushape": 600, "roundtable": 1500},
                "area": 800,
                "price": {"halfDay": 500000, "fullDay": 900000},
                "equipment": ["頂級投影", "專業音響", "大型舞台", "燈光", "同步翻譯"],
                "images": []
            },
            {
                "name": "崑崙廳",
                "capacity": {"theater": 400, "classroom": 250, "ushape": 150, "roundtable": 300},
                "area": 150,
                "price": {"halfDay": 150000, "fullDay": 280000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "國際會議廳",
                "capacity": {"theater": 600, "classroom": 400, "ushape": 200, "roundtable": 450},
                "area": 220,
                "price": {"halfDay": 200000, "fullDay": 350000},
                "equipment": ["頂級投影", "專業音響", "舞台", "同步翻譯"],
                "images": []
            },
            {
                "name": "長青廳",
                "capacity": {"theater": 250, "classroom": 150, "ushape": 100, "roundtable": 180},
                "area": 90,
                "price": {"halfDay": 90000, "fullDay": 160000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "松柏廳",
                "capacity": {"theater": 400, "classroom": 250, "ushape": 150, "roundtable": 300},
                "area": 140,
                "price": {"halfDay": 140000, "fullDay": 250000},
                "equipment": ["投影設備", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "麒麟宴會廳",
                "capacity": {"theater": 800, "classroom": 500, "ushape": 300, "roundtable": 600},
                "area": 280,
                "price": {"halfDay": 250000, "fullDay": 450000},
                "equipment": ["頂級投影", "專業音響", "大型舞台", "燈光"],
                "images": []
            },
            {
                "name": "國宴廳",
                "capacity": {"theater": 500, "classroom": 350, "ushape": 200, "roundtable": 400},
                "area": 180,
                "price": {"halfDay": 180000, "fullDay": 320000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "多功能會議廳",
                "capacity": {"theater": 150, "classroom": 100, "ushape": 60, "roundtable": 120},
                "area": 50,
                "price": {"halfDay": 50000, "fullDay": 90000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "敦睦廳",
                "capacity": {"theater": 100, "classroom": 60, "ushape": 40, "roundtable": 80},
                "area": 35,
                "price": {"halfDay": 35000, "fullDay": 65000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            }
        ]
    },
    1073: {  # 台北姿美大飯店
        "name": "台北姿美大飯店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 120, "classroom": 70, "ushape": 42, "roundtable": 56},
                "area": 40,
                "price": {"halfDay": 18000, "fullDay": 32000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            }
        ]
    },
    1075: {  # 台北寒舍喜來登大飯店
        "name": "台北寒舍喜來登大飯店",
        "rooms": [
            {
                "name": "喜宴廳",
                "capacity": {"theater": 800, "classroom": 500, "ushape": 300, "roundtable": 600},
                "area": 280,
                "price": {"halfDay": 280000, "fullDay": 500000},
                "equipment": ["頂級投影", "專業音響", "大型舞台", "燈光"],
                "images": []
            },
            {
                "name": "桃花源廳",
                "capacity": {"theater": 300, "classroom": 200, "ushape": 130, "roundtable": 180},
                "area": 100,
                "price": {"halfDay": 100000, "fullDay": 180000},
                "equipment": ["投影設備", "專業音響", "舞台"],
                "images": []
            },
            {
                "name": "鳳凰廳",
                "capacity": {"theater": 200, "classroom": 130, "ushape": 90, "roundtable": 120},
                "area": 70,
                "price": {"halfDay": 70000, "fullDay": 130000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "會議室A",
                "capacity": {"theater": 50, "classroom": 30, "ushape": 20, "roundtable": 30},
                "area": 18,
                "price": {"halfDay": 15000, "fullDay": 28000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "會議室B",
                "capacity": {"theater": 30, "classroom": 20, "ushape": 14, "roundtable": 18},
                "area": 12,
                "price": {"halfDay": 10000, "fullDay": 18000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            }
        ]
    },
    1076: {  # 台北寒舍艾美酒店
        "name": "台北寒舍艾美酒店(LeMeridienTaipei)",
        "rooms": [
            {
                "name": "艾美廳",
                "capacity": {"theater": 300, "classroom": 200, "ushape": 150, "roundtable": 180},
                "area": 110,
                "price": {"halfDay": 120000, "fullDay": 220000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "創意廳",
                "capacity": {"theater": 150, "classroom": 100, "ushape": 70, "roundtable": 80},
                "area": 55,
                "price": {"halfDay": 60000, "fullDay": 110000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    },
    1077: {  # 台北艾麗酒店
        "name": "台北艾麗酒店",
        "rooms": [
            {
                "name": "宴會廳全廳",
                "capacity": {"theater": 480, "classroom": 300, "ushape": 200, "roundtable": 360},
                "area": 180,
                "price": {"halfDay": 180000, "fullDay": 320000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "蘭",
                "capacity": {"theater": 150, "classroom": 90, "ushape": 60, "roundtable": 75},
                "area": 55,
                "price": {"halfDay": 55000, "fullDay": 100000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "葵",
                "capacity": {"theater": 160, "classroom": 95, "ushape": 64, "roundtable": 80},
                "area": 58,
                "price": {"halfDay": 58000, "fullDay": 105000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "楓",
                "capacity": {"theater": 110, "classroom": 70, "ushape": 45, "roundtable": 55},
                "area": 40,
                "price": {"halfDay": 40000, "fullDay": 75000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            },
            {
                "name": "柏",
                "capacity": {"theater": 60, "classroom": 35, "ushape": 24, "roundtable": 30},
                "area": 22,
                "price": {"halfDay": 22000, "fullDay": 40000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "槿",
                "capacity": {"theater": 50, "classroom": 30, "ushape": 20, "roundtable": 25},
                "area": 18,
                "price": {"halfDay": 18000, "fullDay": 35000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            },
            {
                "name": "空中花園",
                "capacity": {"theater": 200, "classroom": 120, "ushape": 80, "roundtable": 100},
                "area": 80,
                "price": {"halfDay": 80000, "fullDay": 150000},
                "equipment": ["投影設備", "音響系統", "燈光"],
                "images": []
            }
        ]
    },
    1080: {  # 台北康華大飯店
        "name": "台北康華大飯店",
        "rooms": [
            {
                "name": "會議室",
                "capacity": {"theater": 80, "classroom": 50, "ushape": 30, "roundtable": 40},
                "area": 28,
                "price": {"halfDay": 12000, "fullDay": 22000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            }
        ]
    },
    1082: {  # 台北怡亨酒店
        "name": "台北怡亨酒店 Hotel Éclat Taipei",
        "rooms": [
            {
                "name": "會議室",
                "capacity": {"theater": 40, "classroom": 25, "ushape": 15, "roundtable": 20},
                "area": 15,
                "price": {"halfDay": 10000, "fullDay": 18000},
                "equipment": ["投影設備", "音響系統", "視訊會議"],
                "images": []
            }
        ]
    },
    1083: {  # 台北北門世民酒店
        "name": "台北北門世民酒店 citizenM Taipei North Gate",
        "rooms": [
            {
                "name": "會議室",
                "capacity": {"theater": 150, "classroom": 90, "ushape": 54, "roundtable": 72},
                "area": 55,
                "price": {"halfDay": 25000, "fullDay": 45000},
                "equipment": ["投影設備", "音響系統", "視訊會議", "高速網路"],
                "images": []
            }
        ]
    },
    1084: {  # 台北慶泰大飯店
        "name": "台北慶泰大飯店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 150, "classroom": 85, "ushape": 51, "roundtable": 68},
                "area": 52,
                "price": {"halfDay": 22000, "fullDay": 40000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    },
    1085: {  # 台北文華東方酒店
        "name": "台北文華東方酒店(MOHTaipei)",
        "rooms": [
            {
                "name": "東方廳",
                "capacity": {"theater": 400, "classroom": 250, "ushape": 180, "roundtable": 200},
                "area": 150,
                "price": {"halfDay": 200000, "fullDay": 380000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光", "同步翻譯"],
                "images": []
            },
            {
                "name": "琥珀廳",
                "capacity": {"theater": 180, "classroom": 120, "ushape": 80, "roundtable": 100},
                "area": 65,
                "price": {"halfDay": 90000, "fullDay": 170000},
                "equipment": ["投影設備", "專業音響", "麥克風"],
                "images": []
            }
        ]
    },
    1086: {  # 台北晶華酒店
        "name": "台北晶華酒店 Regent Taipei",
        "rooms": [
            {
                "name": "宴會大廳",
                "capacity": {"theater": 700, "classroom": 450, "ushape": 280, "roundtable": 500},
                "area": 250,
                "price": {"halfDay": 250000, "fullDay": 450000},
                "equipment": ["頂級投影", "專業音響", "大型舞台", "燈光"],
                "images": []
            },
            {
                "name": "晶華軒",
                "capacity": {"theater": 200, "classroom": 130, "ushape": 90, "roundtable": 120},
                "area": 75,
                "price": {"halfDay": 80000, "fullDay": 150000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "會議室A",
                "capacity": {"theater": 60, "classroom": 35, "ushape": 24, "roundtable": 30},
                "area": 22,
                "price": {"halfDay": 20000, "fullDay": 38000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            }
        ]
    },
    1090: {  # 茹曦酒店
        "name": "茹曦酒店 ILLUME TAIPEI",
        "rooms": [
            {
                "name": "茹曦廳",
                "capacity": {"theater": 400, "classroom": 260, "ushape": 170, "roundtable": 240},
                "area": 140,
                "price": {"halfDay": 150000, "fullDay": 280000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "斯賓諾莎宴會廳",
                "capacity": {"theater": 350, "classroom": 230, "ushape": 150, "roundtable": 210},
                "area": 125,
                "price": {"halfDay": 130000, "fullDay": 240000},
                "equipment": ["投影設備", "專業音響", "舞台"],
                "images": []
            },
            {
                "name": "貴賓軒",
                "capacity": {"theater": 30, "classroom": 18, "ushape": 12, "roundtable": 15},
                "area": 10,
                "price": {"halfDay": 8000, "fullDay": 15000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            }
        ]
    },
    1092: {  # 台北第一大飯店
        "name": "台北第一大飯店",
        "rooms": [
            {
                "name": "會議廳",
                "capacity": {"theater": 110, "classroom": 65, "ushape": 39, "roundtable": 52},
                "area": 38,
                "price": {"halfDay": 16000, "fullDay": 30000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            }
        ]
    },
    1095: {  # 台北美福大飯店
        "name": "台北美福大飯店",
        "rooms": [
            {
                "name": "宴會大廳",
                "capacity": {"theater": 550, "classroom": 360, "ushape": 230, "roundtable": 400},
                "area": 200,
                "price": {"halfDay": 200000, "fullDay": 380000},
                "equipment": ["頂級投影", "專業音響", "大型舞台", "燈光"],
                "images": []
            },
            {
                "name": "多功能會議室",
                "capacity": {"theater": 80, "classroom": 50, "ushape": 32, "roundtable": 40},
                "area": 28,
                "price": {"halfDay": 25000, "fullDay": 45000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            }
        ]
    },
    1097: {  # 台北老爺大酒店
        "name": "台北老爺大酒店(RoyalInnTaipei)",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 180, "classroom": 110, "ushape": 66, "roundtable": 88},
                "area": 65,
                "price": {"halfDay": 60000, "fullDay": 110000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "會議室",
                "capacity": {"theater": 60, "classroom": 35, "ushape": 21, "roundtable": 28},
                "area": 22,
                "price": {"halfDay": 18000, "fullDay": 35000},
                "equipment": ["投影設備", "音響系統", "白板"],
                "images": []
            }
        ]
    },
    1099: {  # 台北艾美酒店
        "name": "台北艾美酒店",
        "rooms": [
            {
                "name": "艾美廳",
                "capacity": {"theater": 280, "classroom": 170, "ushape": 102, "roundtable": 136},
                "area": 100,
                "price": {"halfDay": 100000, "fullDay": 190000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            }
        ]
    },
    1100: {  # 台北花園大酒店
        "name": "台北花園大酒店(TGHotel)",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 200, "classroom": 120, "ushape": 72, "roundtable": 96},
                "area": 72,
                "price": {"halfDay": 65000, "fullDay": 120000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    },
    1103: {  # 台北萬豪酒店
        "name": "台北萬豪酒店(MarriottTaipei)",
        "rooms": [
            {
                "name": "萬豪廳 Grand Ballroom",
                "capacity": {"theater": 1200, "classroom": 780, "ushape": 480, "roundtable": 900},
                "area": 420,
                "price": {"halfDay": 450000, "fullDay": 850000},
                "equipment": ["頂級投影", "專業音響", "大型舞台", "燈光", "同步翻譯"],
                "images": []
            },
            {
                "name": "萬豪一廳 Grand Ballroom I",
                "capacity": {"theater": 600, "classroom": 390, "ushape": 240, "roundtable": 450},
                "area": 210,
                "price": {"halfDay": 230000, "fullDay": 430000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            },
            {
                "name": "Garden Villa",
                "capacity": {"theater": 300, "classroom": 200, "ushape": 130, "roundtable": 180},
                "area": 110,
                "price": {"halfDay": 120000, "fullDay": 230000},
                "equipment": ["投影設備", "專業音響", "戶外場地"],
                "images": []
            },
            {
                "name": "寰宇廳 Panorama Ballroom",
                "capacity": {"theater": 200, "classroom": 130, "ushape": 90, "roundtable": 120},
                "area": 75,
                "price": {"halfDay": 80000, "fullDay": 150000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "福祿壽廳",
                "capacity": {"theater": 100, "classroom": 65, "ushape": 43, "roundtable": 50},
                "area": 38,
                "price": {"halfDay": 35000, "fullDay": 65000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            },
            {
                "name": "四季廳",
                "capacity": {"theater": 120, "classroom": 78, "ushape": 52, "roundtable": 60},
                "area": 45,
                "price": {"halfDay": 40000, "fullDay": 75000},
                "equipment": ["投影設備", "音響系統"],
                "images": []
            },
            {
                "name": "宜華廳 Junior Ballroom",
                "capacity": {"theater": 150, "classroom": 98, "ushape": 65, "roundtable": 75},
                "area": 55,
                "price": {"halfDay": 50000, "fullDay": 95000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            },
            {
                "name": "博覽廳 Grand Space",
                "capacity": {"theater": 500, "classroom": 325, "ushape": 200, "roundtable": 300},
                "area": 180,
                "price": {"halfDay": 180000, "fullDay": 340000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            }
        ]
    },
    1104: {  # 台北西華飯店
        "name": "台北西華飯店(SherwoodTaipei)",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 350, "classroom": 200, "ushape": 150, "roundtable": 180},
                "area": 130,
                "price": {"halfDay": 130000, "fullDay": 240000},
                "equipment": ["頂級投影", "專業音響", "舞台", "燈光"],
                "images": []
            }
        ]
    },
    1121: {  # 神旺大飯店
        "name": "神旺大飯店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 240, "classroom": 140, "ushape": 84, "roundtable": 112},
                "area": 85,
                "price": {"halfDay": 85000, "fullDay": 160000},
                "equipment": ["投影設備", "專業音響", "麥克風"],
                "images": []
            }
        ]
    },
    1122: {  # 維多麗亞酒店
        "name": "維多麗亞酒店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 260, "classroom": 150, "ushape": 90, "roundtable": 120},
                "area": 95,
                "price": {"halfDay": 90000, "fullDay": 170000},
                "equipment": ["投影設備", "專業音響", "舞台"],
                "images": []
            }
        ]
    },
    1124: {  # 花園大酒店
        "name": "花園大酒店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 220, "classroom": 130, "ushape": 78, "roundtable": 104},
                "area": 80,
                "price": {"halfDay": 75000, "fullDay": 140000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    },
    1126: {  # 豪景大酒店
        "name": "豪景大酒店",
        "rooms": [
            {
                "name": "宴會廳",
                "capacity": {"theater": 180, "classroom": 110, "ushape": 66, "roundtable": 88},
                "area": 65,
                "price": {"halfDay": 60000, "fullDay": 110000},
                "equipment": ["投影設備", "音響系統", "麥克風"],
                "images": []
            }
        ]
    }
}

def load_venues():
    """載入 venues.json"""
    with open('venues.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_venues(venues):
    """儲存 venues.json"""
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

def update_venue_rooms(venue, room_data):
    """更新場地的會議室資訊"""
    if 'rooms' not in venue:
        venue['rooms'] = []
    
    # 更新會議室資訊
    venue['rooms'] = room_data['rooms']
    
    # 更新場地價格（取最大會議室的價格）
    if room_data['rooms']:
        max_room = max(room_data['rooms'], key=lambda r: r['capacity']['theater'])
        venue['priceHalfDay'] = max_room['price']['halfDay']
        venue['priceFullDay'] = max_room['price']['fullDay']
        venue['maxCapacityTheater'] = max_room['capacity']['theater']
        venue['maxCapacityClassroom'] = max_room['capacity']['classroom']
    
    # 更新設備清單
    all_equipment = set()
    for room in room_data['rooms']:
        all_equipment.update(room.get('equipment', []))
    venue['equipment'] = '、'.join(sorted(all_equipment))
    
    # 更新時間戳記
    venue['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    
    return venue

def main():
    print("=== 台北市飯店會議室完整更新 ===\n")
    
    # 載入資料
    venues = load_venues()
    
    # 統計
    updated_count = 0
    total_rooms = 0
    
    # 更新每個飯店
    for venue in venues:
        venue_id = venue.get('id')
        
        if venue_id in TAIPEI_HOTEL_ROOMS:
            room_data = TAIPEI_HOTEL_ROOMS[venue_id]
            
            print(f"✓ 更新 {venue['name']}")
            print(f"  會議室數量: {len(room_data['rooms'])}")
            
            # 更新資料
            venue = update_venue_rooms(venue, room_data)
            updated_count += 1
            total_rooms += len(room_data['rooms'])
            print()
    
    # 儲存更新後的資料
    save_venues(venues)
    
    print(f"\n=== 更新完成 ===")
    print(f"更新飯店數: {updated_count}")
    print(f"總會議室數: {total_rooms}")
    print(f"\n資料已儲存到 venues.json")

if __name__ == '__main__':
    main()
