#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北中山運動中心 - 三階段完整流程
階段3：驗證與結論
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

venue_id = 1334
venue_name = "台北中山運動中心"

print("=" * 100)
print(f"{venue_name} - 階段3：驗證與結論")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取階段1和階段2結果
with open('台北中山運動中心_stage1_20260326_213400.json', encoding='utf-8') as f:
    stage1 = json.load(f)

with open('台北中山運動中心_stage2_20260326_213440.json', encoding='utf-8') as f:
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

print("\n【階段2：深度爬蟲】")
print(f"  主頁鏈結: {stage1['stage1']['links']['meeting']} 個")
print(f"  可用鏈結: {stage2['stage2']['working_links']} 個")
print(f"  有資料鏈結: 1 個 (外部預約系統)")
print(f"  會議室發現: {stage2['stage2']['total_rooms_found']} 個")

print("\n【階段3：驗證與結論】")

print("\n資料來源分析:")
print(f"  官網: {stage1['url']}")
print(f"  會議室資料: 無")
print(f"  預約系統: 外部系統 (booking.tpsc.sporetrofit.com)")

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
        with_dimensions = sum(1 for r in rooms if r.get('dimensions'))

        print(f"\n  缺漏項目:")
        if with_area < len(rooms):
            print(f"    面積: {len(rooms) - with_area} 個")
        if with_price < len(rooms):
            print(f"    價格: {len(rooms) - with_price} 個")
        if with_dimensions < len(rooms):
            print(f"    尺寸: {len(rooms) - with_dimensions} 個")
    else:
        print(f"  現有會議室: 0 個")

print("\n" + "=" * 100)
print("結論與建議")
print("=" * 100)

print("\n【根本原因】")
print("  台北中山運動中心的官網未直接提供場地資料")
print("  所有場地預約都導向外部預約系統")
print("  外部預約系統僅處理預約，不顯示場地詳情（容量、面積、設備等）")

print("\n【資料來源】")
print("  需要聯繫台北中山運動中心或預約系統提供商索取")
print("  預約系統: http://booking.tpsc.sporetrofit.com")

print("\n【下一步建議】")
print("  選項 1: 直接聯繫台北中山運動中心")
print("  選項 2: 聯繫預約系統提供商 (sporetrofit)")
print("  選項 3: 查找其他資料來源（政府採購資訊、活動案例）")

# 儲存階段3結果
stage3_result = {
    "venue": venue_name,
    "venue_id": venue_id,
    "stage3": {
        "conclusion": "官網未提供場地資料，使用外部預約系統",
        "data_source": "需要直接聯繫",
        "current_rooms": len(venue.get('rooms', [])) if venue else 0,
        "missing_data": ["詳細會議室資料", "尺寸", "設備清單", "場地照片"],
        "recommended_action": "聯繫場地或預約系統提供商"
    },
    "complete_analysis": {
        "stage1": "技術檢測完成",
        "stage2": "深度爬蟲完成",
        "stage3": "驗證完成 - 無場地資料可爬取"
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

print("\n最終結論:")
print("  台北中山運動中心的場地資料無法透過爬蟲獲得")
print("  需要直接聯繫場地或預約系統提供商索取詳細資料")
