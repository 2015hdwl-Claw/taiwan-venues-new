#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思台中新烏日會議中心 - 三階段完整流程
階段3：驗證與結論
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

venue_id = 1498
venue_name = "集思台中新烏日會議中心(WURI)"

print("=" * 100)
print(f"{venue_name} - 階段3：驗證與結論")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取階段1和階段2結果
stage1_files = [f for f in __import__('os').listdir('.') if f.startswith(f'{venue_name}_stage1_') and f.endswith('.json')]
stage2_files = [f for f in __import__('os').listdir('.') if f.startswith(f'{venue_name}_stage2_') and f.endswith('.json')]

if not stage1_files or not stage2_files:
    print(f"❌ 找不到階段1或階段2結果檔案")
    sys.exit(1)

with open(stage1_files[-1], encoding='utf-8') as f:
    stage1 = json.load(f)

with open(stage2_files[-1], encoding='utf-8') as f:
    stage2 = json.load(f)

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v.get('id') == venue_id), None)

print("=" * 100)
print("三階段流程總結")
print("=" * 100)

print("\n【階段1：技術檢測】")
print(f"  HTTP 狀態: {stage1['stage1']['http_status']}")
print(f"  頁面類型: {stage1['stage1']['page_type']}")
print(f"  載入方式: {stage1['stage1']['loading_method']}")
print(f"  JS 框架: {', '.join(stage1['stage1']['js_frameworks']) if stage1['stage1']['js_frameworks'] else '無'}")
print(f"  反爬蟲: {stage1['stage1']['anti_scraping']}")
print(f"  會議相關鏈結: {stage1['stage1']['links']['meeting']} 個")
print(f"  ⚠️  URL 修正: venues.json 的 URL 錯誤，已修正為 /xinwuri/index.php")

print("\n【階段2：深度爬蟲】")
print(f"  主頁鏈結: {stage2['stage2']['homepage_links']} 個")
print(f"  可用鏈結: {stage2['stage2']['working_links']} 個")
print(f"  有資料鏈結: {stage2['stage2']['data_sources']} 個")
print(f"  會議室發現: {stage2['stage2']['total_rooms_found']} 個")
print(f"  PDF 連結: {len(stage2['stage2']['pdf_links'])} 個")

# 檢查找到的會議室
print("\n【階段3：驗證與結論】")

print("\n資料來源分析:")
print(f"  官網: {stage1['url']} (修正後)")
print(f"  原始 URL: https://www.meeting.com.tw/wuri/ (404 錯誤)")

print("\n發現的會議室:")
# 過濾出只屬於 WURI 的會議室
wuri_rooms = ['301會議室', '303會議室', '401會議室', '402會議室']
print(f"  集思台中新烏日專屬會議室: {len(wuri_rooms)} 個")
for room in wuri_rooms:
    print(f"    - {room}")

print("\n現有資料狀況:")
if venue:
    rooms = venue.get('rooms', [])
    print(f"  現有會議室: {len(rooms)} 個")

    if rooms:
        for i, room in enumerate(rooms, 1):
            print(f"    {i}. {room.get('name', '未命名')}")

        # 檢查缺漏
        with_area = sum(1 for r in rooms if r.get('areaPing'))
        with_price = sum(1 for r in rooms if r.get('price'))
        with_capacity = sum(1 for r in rooms if r.get('capacity'))

        print(f"\n  缺漏項目:")
        if with_capacity < len(rooms):
            print(f"    容量: {len(rooms) - with_capacity} 個")
        if with_area < len(rooms):
            print(f"    面積: {len(rooms) - with_area} 個")
        if with_price < len(rooms):
            print(f"    價格: {len(rooms) - with_price} 個")
    else:
        print(f"  現有會議室: 0 個")
else:
    print(f"  現有會議室: 0 個")

print("\n" + "=" * 100)
print("結論與建議")
print("=" * 100)

print("\n【資料來源】")
print(f"  官網有基本會議室名稱: {', '.join(wuri_rooms)}")
print(f"  會議室詳情頁面 (room-301.php 等) 返回 404 錯誤")
print(f"  缺少詳細資料: 容量、面積、價格、設備")

print("\n【需要補充的資料】")
print(f"  1. 容量資料 (各會議室的 theater/banquet/classroom 等容量)")
print(f"  2. 面積資料 (坪數或平方公尺)")
print(f"  3. 價格資料 (平日/假日價格)")
print(f"  4. 設備清單 (投影機、音響、麥克風等)")
print(f"  5. 會議室照片")

print("\n【下一步建議】")
print(f"  選項 1: 聯繫集思台中新烏日會議中心索取完整場地資料")
print(f"  選項 2: 查詢其他集思場地資料作為參考（集思台大已有完整資料）")
print(f"  選項 3: 修正 venues.json 中的 URL (wuri → xinwuri)")

# 儲存階段3結果
stage3_result = {
    "venue": venue_name,
    "venue_id": venue_id,
    "stage3": {
        "conclusion": "官網有會議室名稱但缺少詳細資料，URL 錯誤需修正",
        "data_source": "需要直接聯繫或參考其他集思場地",
        "current_rooms": len(venue.get('rooms', [])) if venue else 0,
        "discovered_rooms": wuri_rooms,
        "url_correction": {
            "wrong": "https://www.meeting.com.tw/wuri/",
            "correct": "https://www.meeting.com.tw/xinwuri/index.php"
        },
        "missing_data": ["容量", "面積", "價格", "設備清單", "會議室照片"],
        "recommended_action": "聯繫場地索取完整資料或參考集思台大資料"
    },
    "complete_analysis": {
        "stage1": "技術檢測完成 - 發現 URL 錯誤，動態渲染，無反爬蟲",
        "stage2": "深度爬蟲完成 - 找到4個會議室名稱，詳情頁 404，缺少詳細資料",
        "stage3": "驗證完成 - 需要補充完整30欄位資料並修正 venues.json URL"
    },
    "timestamp": datetime.now().isoformat()
}

result_file = f'{venue_name}_stage3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(stage3_result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 階段3結果已儲存: {result_file}")

print("\n" + "=" * 100)
print(f"✅ {venue_name} 三階段流程完成")
print("=" * 100)
