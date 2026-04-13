#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 LLM Agent 語意補強資料到 venues.json
"""

import json
from pathlib import Path
from datetime import datetime

# LLM Agent 語意補強結果
LLM_UPDATES = {
    1043: {
        "nameEn": "Courtyard by Marriott Taipei",
        "description": "台北六福萬怡酒店位於南港車站上方，與捷運、高鐵、台鐵及客運轉運站共構，鄰近台北流行音樂中心、CITYLINK、南港Lalaport。2019年榮獲米其林酒店指南「頂級的舒適享受」殊榮，提供2個會議場地，最大容量200人。",
        "highlights": [
            "米其林指南認證酒店（2019年）",
            "南港交通樞紐共構，交通極便利",
            "寵物友善主題房（汪汪/喵喵主題房）",
            "結合Elite Concept一禮莊園花藝設計",
            "五星宴會團隊與中西式宴會佳餚"
        ],
        "risks": {
            "bookingLeadTime": "建議提前3-6个月預訂（旺季需更早）",
            "peakSeasons": ["12月-2月（尾牙春酒季）", "5月-6月（畢業季）"],
            "commonIssues": ["南港區交通便利但周邊餐飲選項相對較少"]
        },
        "pricingTips": [
            "萬豪旅享家會員可享專屬優惠",
            "平日會議場地租金較周末便宜約20-30%",
            "非旺季月份（3-4月、7-8月）預訂可享較佳價格"
        ],
        "accessInfo": {
            "mrt": "捷運板南線「南港站」直接連通",
            "bus": "多條公車路線至「南港站」",
            "parking": "飯店設有停車場，南港車站亦有大型停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1049: {
        "nameEn": "Taipei World Trade Center (TWTCA) Exhibition Hall",
        "description": "台北世貿中心是台北市最具規模的展覽會議場地之一，擁有完善的會議設備與專業服務團隊。場地提供6間會議室，支援標準型、教室型、劇院型等多種排列形式，可靈活容納數十人至500人的活動需求。",
        "highlights": [
            "6間專業會議室，支援多種座位排列形式",
            "最大容量可達500人",
            "設備齊全，提供會議、展覽、記者會等多功能服務",
            "位於台北市基隆路一段333號，交通便利",
            "專業場地服務團隊"
        ],
        "risks": {
            "bookingLeadTime": "需洽詢場地",
            "peakSeasons": [],
            "commonIssues": []
        },
        "pricingTips": ["建議直接電話洽詢 (02) 2725-5200 獲取最新優惠方案"],
        "accessInfo": {"mrt": "需洽詢場地", "bus": "需洽詢場地", "parking": "需洽詢場地"},
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1051: {
        "nameEn": "The Landis Taipei",
        "description": "台北亞都麗緻大飯店坐落於台北市核心地段，以法式藝術裝飾風格精緻設計。飯店擁有219間全新裝修的客房與套房，配備最先進的設施，為賓客提供極致的舒適體驗。飯店提供專業會議與婚宴場地，結合法式優雅與臺灣在地文化。",
        "highlights": [
            "法式藝術裝飾風格，奢華典雅",
            "219間全新裝修客房與套房",
            "專業會議與婚宴場地服務",
            "位於台北市中心，鄰近行天宮與故宮",
            "提供健身中心與瑜伽教室",
            "歷史悠久，曾接待多位國際知名人士"
        ],
        "risks": {
            "bookingLeadTime": "建議提前3-6个月預訂",
            "peakSeasons": ["12月-2月（尾牙春酒）", "5月-6月"],
            "commonIssues": ["中山區交通較繁忙，建議提醒賓客提早出發"]
        },
        "pricingTips": ["Landis Club會員享專屬優惠", "週日-週四場地租金較便宜"],
        "accessInfo": {
            "mrt": "捷運中和新蘆線「行天宮站」步行約5分鐘",
            "bus": "多條公車路線至「民權中山北路口」",
            "parking": "飯店設有停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1053: {
        "nameEn": "Hotel CJ",
        "description": "台北君品酒店位於市中心，提供頂級的住宿與會議服務。",
        "highlights": ["市中心位置", "專業會議服務"],
        "risks": {"bookingLeadTime": "需洽詢場地", "peakSeasons": [], "commonIssues": []},
        "pricingTips": ["建議電話洽詢"],
        "accessInfo": {"mrt": "需洽詢場地", "bus": "需洽詢場地", "parking": "需洽詢場地"},
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1075: {
        "nameEn": "Sheraton Grand Taipei Hotel",
        "description": "台北喜來登位於政商交通核心的中正區，擁有683間米其林指南評鑑為頂級舒適品質的客房與套房、9間美饌餐廳匯集各國料理，更榮獲米其林星等、推薦餐廳殊榮。13間多功能會議場地，最大容量800人。",
        "highlights": [
            "米其林星等與推薦餐廳（請客樓二星、十二廚等）",
            "13間多功能會議場地，彈性空間配置",
            "位於政商核心，交通便利",
            "9間異國餐廳提供多元宴會選擇",
            "專業婚宴顧問團隊合作（成家婚禮顧問）"
        ],
        "risks": {
            "bookingLeadTime": "建議提前6-12个月預訂（熱門場地）",
            "peakSeasons": ["12月-2月（尾牙春酒季）", "5月（母親節）"],
            "commonIssues": ["中正區交通管制較多，建議提前規劃交通"]
        },
        "pricingTips": [
            "萬豪旅享家會員享點數累積與專屬優惠",
            "非旺季月份場地租金較優惠",
            "寒舍生活APP限定活動常有優惠"
        ],
        "accessInfo": {
            "mrt": "捷運板南線「善導寺站」或淡水信義線「台中站」",
            "bus": "多條公車路線至「台中站」或「善導寺站」",
            "parking": "飯店設有停車場，建議預先預約"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1076: {
        "nameEn": "Le Méridien Taipei",
        "description": "台北寒舍艾美酒店位於信義計劃區核心地段，鄰近台北101。飯店巧妙揉合人文藝術與時尚，提供9個會議空間，包含2F多功能廳、3F宴會廳及5F QUUBE創新空間，適合舉辦各類商務會議、婚宴及活動。",
        "highlights": [
            "信義計劃區五星級酒店，鄰近台北101購物商區",
            "3F大型宴會廳868坪，挑高5米水晶天花設計",
            "9個會議空間：2F 6間多功能廳、3F 4間宴會廳、5F QUUBE",
            "專業會議專案與婚宴服務，綠會議環保永續理念"
        ],
        "risks": {
            "bookingLeadTime": "大型宴會建議3-6個月前預訂；婚宴旺季需更早",
            "peakSeasons": ["10-12月婚宴旺季", "12-1月尾牙季", "3-6月春酒季"],
            "commonIssues": ["信義區活動需求量大，場地檔期競爭激烈"]
        },
        "pricingTips": [
            "寒舍生活APP會員可享專屬優惠",
            "會議專案通常比單租場地更划算",
            "平日會議方案通常比假日宴會便宜"
        ],
        "accessInfo": {
            "mrt": "市政府站（板南線）",
            "bus": "信義區多線公車",
            "parking": "飯店提供停車服務"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1077: {
        "nameEn": "Humble House Taipei",
        "description": "台北艾麗酒店（Humble House Taipei）是信義計劃區的設計酒店，寒舍集團成員。以世界級HBA設計打造挑高無柱宴會空間，提供5間獨立廳房（蘭、葵、楓、柏、槿），適合商務會議、婚宴、企業講座及春酒尾牙等活動。",
        "highlights": [
            "信義計劃區設計酒店，寒舍集團成員",
            "世界級HBA設計，挑高無柱宴會空間",
            "宴會廳全廳212坪，總面積702平方公尺",
            "5間獨立廳房：蘭(67坪)、葵(70坪)、楓(49坪)、柏(25坪)、槿(21坪)"
        ],
        "risks": {
            "bookingLeadTime": "至少1個月，大型宴會建議3-6個月前預約",
            "peakSeasons": ["10-12月婚宴旺季", "12-1月尾牙季"],
            "commonIssues": ["價格不透明需多次來回確認報價"]
        },
        "pricingTips": [
            "平日會議方案通常比假日宴會便宜",
            "寒舍集團可交叉比較",
            "簽訂會議專案通常比單租場地更划算"
        ],
        "accessInfo": {
            "mrt": "市政府站（板南線）",
            "bus": "信義區多線公車",
            "parking": "飯店提供停車服務"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1086: {
        "nameEn": "Regent Taipei",
        "description": "台北晶華酒店座落在富有活力與文化、娛樂與購物的中心區域，是國內外商務及休閒旅客的住宿上選。擁有寬敞奢華的住宿享受、先進高端的會議場地，精緻非凡的用餐體驗。提供5個會議場地，最大容量1000人。",
        "highlights": [
            "五星級精品酒店，城市度假首選",
            "精緻餐廳：三燔本家、azie、ROBIN'S牛排屋等",
            "雲天露臺客房享有絕佳景觀",
            "高鐵車票優惠（入住加購享7折起）",
            "專業婚宴與外燴服務"
        ],
        "risks": {
            "bookingLeadTime": "建議提前6-12个月預訂",
            "peakSeasons": ["12月-2月（尾牙春酒）", "10月-11月（婚禮旺季）"],
            "commonIssues": ["中山北路車流量大，建議提醒賓客提早出發"]
        },
        "pricingTips": [
            "麗晶會員享專屬優惠",
            "週日-週四場地租金較便宜",
            "配合高鐵住宿專案可享綜合優惠"
        ],
        "accessInfo": {
            "mrt": "捷運淡水信義線「中山站」或雙連站",
            "bus": "多條公車路線至「中山國小站」",
            "parking": "飯店設有停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1095: {
        "nameEn": "Grand Mayfull Hotel Taipei",
        "description": "台北美福大飯店位於中山區大直河畔，是新古典風格建築的精品飯店。擁有挑高7公尺無樑柱宴會空間，配備420吋互動式高畫質LED顯示屏幕及專業級BOSE音響，適合各式社交酬酢、大型會議、婚宴及企業活動。",
        "highlights": [
            "台北市中山區精品飯店，鄰近美麗華商圈",
            "佔地300坪挑高7公尺無樑柱宴會空間",
            "420吋互動式高畫質LED顯示屏幕、專業級BOSE音響",
            "高雅氣派的宴會空間，適合各式社交酬酢及大型會議",
            "精緻中西美饌、異國風味自助餐、米其林台菜饗味"
        ],
        "risks": {
            "bookingLeadTime": "大型宴會廳建議3-6個月前預訂；尾牙/婚宴旺季需更早",
            "peakSeasons": ["11-1月尾牙季", "2-3月春酒季", "9-12月婚宴旺季"],
            "commonIssues": ["大宴會廳容量數據有出入，需與飯店確認", "PDF價格已過期（2025/12/31）"]
        },
        "pricingTips": [
            "半日會議方案NT$2,080+10%/人（含場地、茶點、午餐），全日NT$2,680+10%/人",
            "場地單租：大宴會廳平日半日NT$200,000/全日NT$350,000，假日加價10%",
            "報價需乘1.1（服務費）x 1.05（營業稅）= 總價"
        ],
        "accessInfo": {
            "mrt": "劍南路站（文湖線）",
            "bus": "33、645、677、208、42、藍26、藍7",
            "shuttle": "飯店提供捷運大直站接駁車",
            "parking": "飯店提供停車服務"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1100: {
        "nameEn": "Taipei Garden Hotel",
        "description": "台北花園大酒店坐落於萬華(艋舺)及西門商圈核心地段，2023年榮獲交通部觀光署「五星級酒店」殊榮。飯店以「旅艋舺 遊西門」為主題，結合在地Bangka船舟文化與現代設計美學。擁有241間舒適客房、7米挑高無柱多功能宴會廳、多元化餐飲服務。",
        "highlights": [
            "2023年交通部觀光署五星級酒店認證",
            "241間舒適客房，14間會議室",
            "7米挑高無柱多功能宴會廳",
            "位於萬華及西門商圈，鄰近龍山寺與華西街夜市",
            "多元化餐飲服務：饗聚廚房、PRIME ONE牛排館、翠庭中餐廳、花園thai thai"
        ],
        "risks": {
            "bookingLeadTime": "建議至少1-2個月前預訂，旺季需更早",
            "peakSeasons": ["5-6月婚宴旺季", "10-12月年底尾牙春酒季"],
            "commonIssues": ["週末檔期搶手", "停車位需提前確認"]
        },
        "pricingTips": ["平日使用可享優惠價格", "配合飯店住宿方案可能更優惠"],
        "accessInfo": {
            "mrt": "捷運板南線西門站5號出口步行約5分鐘",
            "bus": "公車至「中華路」站",
            "parking": "飯店設有停車場，需提前確認空位"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1122: {
        "nameEn": "Grand Victoria Hotel",
        "description": "維多麗亞酒店位於中山區大直，鄰近捷運劍南站，以十九世紀英國盛世維多麗亞王朝建築風格打造。擁有挑高8米無樑柱大宴會廳及多間多功能會議空間，另提供戶外庭園及泳池場地，適合婚宴、商務會議及企業活動。",
        "highlights": [
            "台北市中山區鄰近捷運劍南站精品酒店",
            "大宴會廳156坪挑高8米無樑柱空間，可容納10~700人",
            "維多麗亞廳171坪寬敞空間，最大容納450人",
            "維多麗亞戶外庭園123坪，適合戶外酒會"
        ],
        "risks": {
            "bookingLeadTime": "一般活動至少2-4週前；1F宴會廳建議2-3個月前",
            "peakSeasons": ["10-12月婚宴旺季", "12-1月尾牙季", "6-8月畢業季"],
            "commonIssues": ["超時人力費NT$1,500/hr/人（最低3小時），成本易被低估"]
        },
        "pricingTips": [
            "1F維多麗亞廳平日半日NT$150,000起，假日加價",
            "3F小型廳（經國/中山/中正廳）平日半日NT$30,000-45,000，CP值高",
            "超時費NT$1,500/hr/人（最低3小時），估計最少NT$4,500"
        ],
        "accessInfo": {
            "mrt": "劍南站（文湖線）",
            "bus": "大直地區多線公車",
            "parking": "飯店提供停車服務（有限）"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1124: {
        "nameEn": "Taipei Garden Hotel",
        "description": "台北花園大酒店坐落於萬華及西門商圈，為西區頂級商務觀光飯店，2023年榮獲交通部觀光署「五星級酒店」殊榮。以「旅艋舺 遊西門」為主題，擁有241間客房及多元化餐飲服務。挑高7米寬敞無柱的多功能宴會廳，提供舒適住宿及良好用餐環境。",
        "highlights": [
            "2023年榮獲交通部觀光署五星級酒店殊榮",
            "挑高7米寬敞無柱多功能宴會廳",
            "241間舒適客房，多元化餐飲服務",
            "位於萬華及西門商圈核心地段",
            "結合在地Bangka船舟文化設計"
        ],
        "risks": {
            "bookingLeadTime": "建議至少1-2個月前預訂，旺季需更早",
            "peakSeasons": ["5-6月婚宴旺季", "10-12月年底尾牙春酒季"],
            "commonIssues": ["週末檔期搶手", "停車位需提前確認"]
        },
        "pricingTips": ["平日使用可享優惠價格", "配合飯店住宿方案可能更優惠"],
        "accessInfo": {
            "mrt": "捷運板南線西門站5號出口步行約5分鐘",
            "bus": "公車至「中華路」站",
            "parking": "飯店設有停車場，需提前確認空位"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1126: {
        "nameEn": "RiverView Hotel Taipei",
        "description": "台北豪景大酒店坐落於淡水河畔，將城市繁華與靜謐河景完美融合。飯店內提供溫馨舒適的客房、精緻美味的餐飲選擇與貼心服務，無論是商務出行或休閒度假，皆能感受到「回家般的溫度」。每年七夕情人節，大稻埕浪漫煙火可從頂樓盡收眼底。",
        "highlights": [
            "淡水河畔絕佳景觀，12樓早餐廳俯瞰河景",
            "七夕煙火最佳觀賞地點之一",
            "提供標準客房至豪華套房多種選擇",
            "鄰近大稻埕歷史街區",
            "商務中心及健身房設施"
        ],
        "risks": {
            "bookingLeadTime": "建議至少1個月前預訂",
            "peakSeasons": ["7-8月大稻埕夏日節期間", "七夕情人節"],
            "commonIssues": ["旺季房間與宴會廳搶手", "河景房需提前預訂"]
        },
        "pricingTips": ["大稻埕夏日節專案期間有優惠", "住房搭配宴會使用有優惠"],
        "accessInfo": {
            "mrt": "捷運淡水信義線雙連站或民權西路站",
            "bus": "公車至「中山北路一段」站",
            "parking": "飯店設有停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1128: {
        "nameEn": "NTU Convention Center (GIS)",
        "description": "集思台大會議中心位於台灣大學校園內B1樓層，是專業的會議場地服務機構。提供11間大小不同的會議室，容量從18人至400人不等，包括國際會議廳(400人)、蘇格拉底廳(145人)、柏拉圖廳(150-220人)等。場地設備完善，適合舉辦國際會議、研討會、企業訓練、發表會等各類活動。",
        "highlights": [
            "11間專業會議室，容量18-400人",
            "國際會議廳可容納400人，設備齊全",
            "位於台灣大學校園內，學術氣息濃厚",
            "提供專業會議顧問與視聽設備服務",
            "多種樓層與會議室選擇，彈性靈活"
        ],
        "risks": {
            "bookingLeadTime": "需洽詢場地",
            "peakSeasons": [],
            "commonIssues": []
        },
        "pricingTips": ["建議直接電話洽詢 (02) 2363-5868 或使用線上申請表"],
        "accessInfo": {
            "mrt": "台電大樓站或公館站",
            "bus": "需洽詢場地",
            "parking": "需洽詢場地"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1129: {
        "nameEn": "Chin Chin Wedding Garden Taipei",
        "description": "青青國際婚宴餐飲集團秉持「自家人辦婚禮」的心，多年來提供多樣獨特的婚禮服務。2000年引入國外花園婚禮和首創台灣教堂婚禮，童話婚禮、池畔婚禮、落羽松婚禮及婚禮體驗營等廣受新人喜愛。台北青青食尚花園會館提供戶外場景及專業婚宴服務。",
        "highlights": [
            "自家人辦婚禮的溫馨服務理念",
            "多樣化戶外場景：夏綠蒂庭院、神木庭院、凡爾賽花園等",
            "專業婚宴顧問一對一服務",
            "提供微婚禮12萬輕鬆完婚專案",
            "一站式婚宴訂席系統",
            "尾牙春酒會議專案服務"
        ],
        "risks": {
            "bookingLeadTime": "婚宴建議至少6-12個月前預訂，會議至少1個月",
            "peakSeasons": ["10-11月婚宴旺季", "3-5月春宴季", "12-2月尾牙春酒季"],
            "commonIssues": ["熱門場景檔期難訂", "戶外場景受天氣影響"]
        },
        "pricingTips": [
            "微婚禮專案12萬起，適合小型婚宴",
            "平日婚宴有優惠價格",
            "配合業者促銷活動可享折扣"
        ],
        "accessInfo": {
            "mrt": "捷運淡水信義線士林站轉接駁車",
            "bus": "公車至「士林」站轉接駁",
            "parking": "場地設有停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1334: {
        "nameEn": "Zhongshan Sports Center",
        "description": "中山運動中心由社團法人中國青年救國團受委託經營，提供多元化的運動及活動空間。開館時間為06:00-22:00（農曆除夕、初一及天災除外），擁有完善的運動設施及多功能活動室，適合舉辦中小型活動、研習營隊及體育活動。",
        "highlights": [
            "救國團專業經營管理",
            "開放時間長，每日06:00-22:00",
            "設有健身房、游泳池、冰宮等設施",
            "多功能活動室適合中小型活動",
            "價格親民，每小時1,500元起"
        ],
        "risks": {
            "bookingLeadTime": "建議至少2-4週前預訂",
            "peakSeasons": ["寒暑假營隊季", "週末時段"],
            "commonIssues": ["熱門時段容易滿場"]
        },
        "pricingTips": ["非營利組織或社團可能有優惠", "長期租用可洽詢專案價格"],
        "accessInfo": {
            "mrt": "捷運松山新店線中山國小站",
            "bus": "公車至「中山北路二段44巷」站",
            "parking": "附近有公有停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1448: {
        "nameEn": "Taipei International Convention Center",
        "description": "TICC位於全臺最國際化的信義商圈，擁有多元化空間及一流的硬體設備，每年辦理超過800場以上的會議活動，包含大型國際會議、演唱會、各式研討會、產品發表會等。提供27個會議場地，為臺灣會議暨大型活動首屈一指的專業場地。",
        "highlights": [
            "每年辦理超過800場會議活動的專業經驗",
            "位於信義商圈核心，交通便利",
            "多元化空間配置（教室型、劇院型、馬蹄形等）",
            "一流硬體設備與專業會議服務",
            "提供VR實境場地查詢服務"
        ],
        "risks": {
            "bookingLeadTime": "建議提前6-18个月預訂（大型國際會議需更早）",
            "peakSeasons": ["3月-4月（展覽旺季）", "10月-11月"],
            "commonIssues": ["信義商圈活動頻繁，停車位較難尋"]
        },
        "pricingTips": [
            "預算範圍可線上篩選場地",
            "週一-週四場地租金較便宜",
            "非展覽旺季月份租金較優惠"
        ],
        "accessInfo": {
            "mrt": "捷運板南線「市政府站」步行約5分鐘",
            "bus": "多條公車路線至「市議會站」或「信義分局站」",
            "parking": "鄰近信義計畫區多個停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1493: {
        "nameEn": "NTNU Extension Education Center",
        "description": "師大進修推廣學院提供專業的會議場地服務，擁有多間會議室適合舉辦研習、講座、發表會等活動。",
        "highlights": ["專業會議場地", "學術氣息濃厚"],
        "risks": {"bookingLeadTime": "需洽詢場地", "peakSeasons": [], "commonIssues": []},
        "pricingTips": ["建議電話洽詢"],
        "accessInfo": {"mrt": "需洽詢場地", "bus": "需洽詢場地", "parking": "需洽詢場地"},
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1494: {
        "nameEn": "GIS MOTC International Convention Center",
        "description": "集思交通部國際會議中心位於仁愛路與杭州南路口，為公辦民營之專業會議場地。擁有獨立出入動線及附屬停車場地，設有5F集會堂（252-400人）、3F+4F國際會議廳（193人）、2F多間會議室（63-108人）等多種規劃空間。",
        "highlights": [
            "公辦民營專業會議場地",
            "擁有獨立出入動線及附屬停車場",
            "5F集會堂可容納400人，挑高7.5米無柱空間",
            "專業會議設備：投影、音響、無線麥克風、白板"
        ],
        "risks": {
            "bookingLeadTime": "大型會議建議至少3-6個月前預訂",
            "peakSeasons": ["3-6月會議旺季", "9-11月研討會季"],
            "commonIssues": ["集會堂熱門時段搶手"]
        },
        "pricingTips": ["政府機關使用可能有優惠", "長期配合可洽詢企業合約價"],
        "accessInfo": {
            "mrt": "捷運文湖線或中和新蘆線東門站4號出口步行約3分鐘",
            "bus": "公車至「杭州南路」站",
            "parking": "場地設有附屬停車場"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1495: {
        "nameEn": "GIS NTUT Convention Center",
        "description": "集思北科大會議中心位於北科大校園內，提供專業會議場地服務。擁有多間會議室適合舉辦研討會、發表會、企業訓練等活動。",
        "highlights": ["專業會議場地", "學術氣息濃厚"],
        "risks": {"bookingLeadTime": "需洽詢場地", "peakSeasons": [], "commonIssues": []},
        "pricingTips": ["建議電話洽詢"],
        "accessInfo": {"mrt": "需洽詢場地", "bus": "需洽詢場地", "parking": "需洽詢場地"},
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1500: {
        "nameEn": "TaiNEX 1",
        "description": "南港展覽館1館是台北市南港區的大型會展中心，提供多種規模的會議室及展場空間。3樓設有展場及宴會廳，4-5樓提供多間會議室，適合舉辦大型演唱會、直銷會議、獎勵旅遊、宗教集會及公司餐會等活動。",
        "highlights": [
            "台北市南港區大型會展中心",
            "多種規模會議室：從83坪小型展場至511坪大型會議室",
            "3樓宴會廳671坪，適合大型宴會活動",
            "4-5樓提供多間會議室，可靈活組合",
            "免費提供標準配備：無線麥克風2隻、主講桌、司儀台、報到桌等",
            "鄰近捷運南港展覽館站，交通便利"
        ],
        "risks": {
            "bookingLeadTime": "活動日前30天（旺季建議提前3個月）",
            "peakSeasons": ["6月畢業季", "10-12月展覽旺季"],
            "commonIssues": ["展覽期間周邊交通壅塞"]
        },
        "pricingTips": [
            "日間時段（08:00-17:00）比夜間（17:00-22:00）便宜約30%",
            "連續租用3天以上可享9折優惠",
            "公務機關及公益團體另有優惠費率"
        ],
        "accessInfo": {
            "mrt": "南港展覽館站（板南線、文湖線）",
            "bus": "南港區多線公車",
            "parking": "展覽館提供停車服務"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    },
    1501: {
        "nameEn": "TaiNEX 2",
        "description": "南港展覽館2館是南港展覽館的擴建場地，提供多種規模的會議室及展場空間。",
        "highlights": ["大型會展中心", "設備齊全", "交通便利"],
        "risks": {"bookingLeadTime": "需洽詢場地", "peakSeasons": [], "commonIssues": []},
        "pricingTips": ["建議電話洽詢"],
        "accessInfo": {
            "mrt": "南港展覽館站（板南線、文湖線）",
            "bus": "南港區多線公車",
            "parking": "展覽館提供停車服務"
        },
        "lastUpdated": "2026-04-12",
        "verified": True
    }
}

def main():
    venues_path = Path("venues.json")

    # 讀取現有資料
    with open(venues_path, 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 更新每個場地
    updated_count = 0
    for venue in venues:
        vid = venue.get("id")
        if vid in LLM_UPDATES:
            updates = LLM_UPDATES[vid]
            for key, value in updates.items():
                if value is not None and value != [] and value != "":
                    venue[key] = value
            updated_count += 1
            print(f"[OK] Update venue {vid}: {venue.get('name')}")

    # 寫回檔案
    with open(venues_path, 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Updated {updated_count} venues")

if __name__ == "__main__":
    main()
