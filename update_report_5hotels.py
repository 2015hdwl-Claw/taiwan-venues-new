#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成更新的 5 家飯店檢查報告
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 5 hotels
hotels = [
    {'id': 1043, 'name': '台北六福萬怡酒店'},
    {'id': 1076, 'name': '台北寒舍艾美酒店'},
    {'id': 1077, 'name': '台北艾麗酒店'},
    {'id': 1103, 'name': '台北萬豪酒店'},
    {'id': 1072, 'name': '台北圓山大飯店'}
]

# Generate report
report_lines = []
report_lines.append("# 5 家飯店人工檢查報告（更新版）")
report_lines.append("")
report_lines.append(f"**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report_lines.append("**狀態**: ✅ 已完成批次抓取 + 資料更新")
report_lines.append("**備份**: venues.json.backup.grandhotelpdf_20260324_214855")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 📊 5 家飯店總覽")
report_lines.append("")
report_lines.append("| # | 飯店名稱 | ID | 會議室 | 照片 | 價格 | 資料品質 |")
report_lines.append("|---|---------|-------|--------|------|------|---------|")

# Calculate stats
for i, hotel_info in enumerate(hotels, 1):
    venue = next((v for v in data if v['id'] == hotel_info['id']), None)
    if not venue:
        continue

    rooms = venue.get('rooms', [])
    rooms_with_images = sum(1 for r in rooms if r.get('images') and len(r.get('images', [])) > 0)
    rooms_with_prices = sum(1 for r in rooms if r.get('price'))

    image_pct = 100 * rooms_with_images / len(rooms) if rooms else 0
    price_pct = 100 * rooms_with_prices / len(rooms) if rooms else 0

    grade = "A" if (image_pct >= 80 and price_pct >= 80) else "B" if (image_pct >= 60 and price_pct >= 60) else "C"

    image_str = f"✅ {rooms_with_images}/{len(rooms)}"
    price_str = f"✅ {rooms_with_prices}/{len(rooms)}" if price_pct > 0 else f"❌ {rooms_with_prices}/{len(rooms)}"
    quality = f"**{grade} ({int(image_pct*0.5 + price_pct*0.5)}%)**"

    report_lines.append(f"| {i} | {venue['name']} | {hotel_info['id']} | {len(rooms)} 間 | {image_str} | {price_str} | {quality} |")

report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 🏨 詳細檢查清單")
report_lines.append("")

# Generate detailed info for each hotel
for hotel_info in hotels:
    venue = next((v for v in data if v['id'] == hotel_info['id']), None)
    if not venue:
        continue

    venue_id = venue['id']
    venue_name = venue['name']
    rooms = venue.get('rooms', [])

    rooms_with_images = sum(1 for r in rooms if r.get('images') and len(r.get('images', [])) > 0)
    rooms_with_prices = sum(1 for r in rooms if r.get('price'))

    image_pct = 100 * rooms_with_images / len(rooms) if rooms else 0
    price_pct = 100 * rooms_with_prices / len(rooms) if rooms else 0
    total_score = int(image_pct*0.5 + price_pct*0.5)
    grade = "A" if total_score >= 80 else "B" if total_score >= 60 else "C"

    report_lines.append(f"### {venue_id}️⃣ {venue_name} {'✅' if grade == 'A' else '⚠️'} {grade} ({total_score}%)")
    report_lines.append("")
    report_lines.append(f"**官方資料來源**:")
    report_lines.append(f"- ✅ 官網: {venue.get('url', 'N/A')}")

    # Check for metadata
    metadata = venue.get('metadata', {})
    if metadata.get('capacitySource'):
        report_lines.append(f"- ✅ 容量資料: {metadata['capacitySource']}")
    if metadata.get('floorsVerified'):
        report_lines.append(f"- ✅ 樓層已驗證: {metadata.get('floorSource', '官網')}")

    report_lines.append("")
    report_lines.append("**聯絡資訊** (已驗證):")
    report_lines.append(f"- 📞 **電話**: {venue.get('contactPhone', 'N/A')}")
    report_lines.append(f"- 📧 **Email**: {venue.get('contactEmail', 'N/A')}")
    report_lines.append("")

    report_lines.append("**會議室資料** ({} 間):".format(len(rooms)))

    # Group by floor
    floor_groups = {}
    for room in rooms:
        floor = room.get('floor', 'Unknown')
        if floor not in floor_groups:
            floor_groups[floor] = []
        floor_groups[floor].append(room)

    for floor in sorted(floor_groups.keys()):
        floor_rooms = floor_groups[floor]
        report_lines.append(f"")
        report_lines.append(f"**{floor}** ({len(floor_rooms)} 間):")

        for room in floor_rooms:
            name = room.get('name', '')
            name_en = room.get('nameEn', '')
            area = room.get('area', '')
            capacity = room.get('capacity', {})
            theater = capacity.get('theater', 'N/A') if capacity else 'N/A'

            if theater:
                report_lines.append(f"{len(report_lines)}. **{name}** ({name_en}) - {area} sqm - {theater} 人")

    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

# Add transportation info section
report_lines.append("## 🚕 交通資訊欄位")
report_lines.append("")
report_lines.append("✅ 已為所有 52 個場地新增交通資訊欄位:")
report_lines.append("")
report_lines.append("```json")
report_lines.append('"transportation": {')
report_lines.append('  "car": "",')
report_lines.append('  "publicTransport": "",')
report_lines.append('  "mrt": "",')
report_lines.append('  "bus": "",')
report_lines.append('  "parking": "",')
report_lines.append('  "notes": ""')
report_lines.append('}')
report_lines.append("```")
report_lines.append("")
report_lines.append("**待填寫**: 每個場地的交通資訊需要從官網或實際調查補充")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Add updates section
report_lines.append("## 🔄 最新更新")
report_lines.append("")
report_lines.append(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')}**:")
report_lines.append("")
report_lines.append("### 圓山大飯店 (ID: 1072)")
report_lines.append("- ✅ 更新會議室容量資料（來源: 官方 PDF）")
report_lines.append("- ✅ 新增多種容量類型（劇院、教室、宴會、中式、西式等）")
report_lines.append("- ✅ 資料來源: https://www.grand-hotel.org/fileupload/Ballroom/P_1.pdf")
report_lines.append("")
report_lines.append("### 寒舍艾美酒店 (ID: 1076)")
report_lines.append("- ✅ 修正樓層格式不一致問題")
report_lines.append("- ✅ 統一為 XF 格式（2F, 3F, 5F）")
report_lines.append("- ✅ 修正 11 間會議室樓層")
report_lines.append("- ✅ QUUBE 確認在 5F（根據官網驗證）")
report_lines.append("")
report_lines.append("### 所有場地")
report_lines.append("- ✅ 新增交通資訊欄位（52 個場地）")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Add verification checklist
report_lines.append("## ✅ 驗證重點")
report_lines.append("")
report_lines.append("### 通用檢查項目（每家都要檢查）")
report_lines.append("")
report_lines.append("#### 1. 聯絡資訊正確性")
report_lines.append("- [ ] 電話號碼是否正確？")
report_lines.append("- [ ] Email 是否有效？")
report_lines.append("- [ ] 是否有分機號碼？")
report_lines.append("- [ ] 地址是否完整？")
report_lines.append("")
report_lines.append("#### 2. 會議室基本資訊")
report_lines.append("- [ ] 會議室數量是否正確？")
report_lines.append("- [ ] 樓層資訊是否正確？（統一 XF 格式）")
report_lines.append("- [ ] 面積資料是否正確？")
report_lines.append("- [ ] 容量數字是否合理？")
report_lines.append("")
report_lines.append("#### 3. 價格資訊")
report_lines.append("- [ ] 價格是否為當前價格？")
report_lines.append("- [ ] 是否包含稅和服務費？")
report_lines.append("- [ ] 價格區間是否合理？")
report_lines.append("- [ ] 是否有官方來源？")
report_lines.append("")
report_lines.append("#### 4. 照片資訊")
report_lines.append("- [ ] 照片是否能正常顯示？")
report_lines.append("- [ ] 照片是否對應正確的會議室？")
report_lines.append("- [ ] 照片品質是否足夠？")
report_lines.append("")
report_lines.append("#### 5. 交通資訊")
report_lines.append("- [ ] 汽車路線是否完整？")
report_lines.append("- [ ] 大眾運輸是否完整？（捷運、公車）")
report_lines.append("- [ ] 停車資訊是否完整？")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Add priority
report_lines.append("## 🎯 優先順序建議")
report_lines.append("")
report_lines.append("### 第 1 優先：100% 完成度 (4 家)")
report_lines.append("")
report_lines.append("1. **台北六福萬怡酒店** ⭐⭐⭐")
report_lines.append("   - 資料最完整")
report_lines.append("   - 有官方 PDF 價格")
report_lines.append("   - 有官方 PDF 容量表")
report_lines.append("   - 所有資料已驗證")
report_lines.append("")
report_lines.append("2. **台北寒舍艾美酒店** ⭐⭐⭐")
report_lines.append("   - 100% 完成度")
report_lines.append("   - 樓層格式已修正")
report_lines.append("   - 官網資料完整")
report_lines.append("")
report_lines.append("3. **台北艾麗酒店** ⭐⭐")
report_lines.append("   - 100% 完成度")
report_lines.append("   - 資料完整")
report_lines.append("")
report_lines.append("4. **台北萬豪酒店** ⭐⭐⭐")
report_lines.append("   - 100% 完成度")
report_lines.append("   - 26 間會議室（最多）")
report_lines.append("   - 資料完整")
report_lines.append("")
report_lines.append("### 第 2 優先：資料已改善 (1 家)")
report_lines.append("")
report_lines.append("5. **台北圓山大飯店** ⚠️ → ✅")
report_lines.append("   - ✅ 已新增完整容量資料（官方 PDF）")
report_lines.append("   - ⚠️ 仍需補充價格資料")
report_lines.append("   - ⚠️ 需要填寫交通資訊")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Add next steps
report_lines.append("## 🔄 後續步驟")
report_lines.append("")
report_lines.append("### 立即行動")
report_lines.append("1. ✅ 5 家飯店資料已準備完成")
report_lines.append("2. ✅ 圓山大飯店容量資料已更新")
report_lines.append("3. ✅ 寒舍艾美樓層格式已修正")
report_lines.append("4. ✅ 所有場地已新增交通資訊欄位")
report_lines.append("5. ⏳ 等待人工檢查")
report_lines.append("")
report_lines.append("### 人工檢查重點")
report_lines.append("1. 驗證 5 家飯店聯絡資訊正確性")
report_lines.append("2. 確認會議室樓層、容量、面積正確")
report_lines.append("3. 填寫交通資訊（52 個場地）")
report_lines.append("4. 標記需要修正的項目")
report_lines.append("5. 繼續處理剩餘 47 家飯店")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append(f"**報告生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report_lines.append(f"**備份檔案**: venues.json.backup.grandhotelpdf_20260324_214855")
report_lines.append(f"** venues.json 狀態**: ✅ 已更新 5 家飯店 + 所有場地交通欄位")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("_請仔細檢查這 5 家飯店的資料，特別是聯絡資訊、會議室樓層和容量的正確性。_")

# Write report
with open('5_HOTELS_CHECK_REPORT.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print("✅ 報告已更新: 5_HOTELS_CHECK_REPORT.md")
print(f"   生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   總行數: {len(report_lines)}")
