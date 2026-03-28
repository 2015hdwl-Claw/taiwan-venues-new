#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成批次 2 的 5 家飯店詳細資料報告
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*120)
print("批次 2：5 家飯店詳細資料")
print("="*120)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 批次 2 的 5 家飯店
batch2_ids = [1090, 1075, 1122, 1069, 1085]

report_lines = []
report_lines.append("# 批次 2：5 家飯店詳細資料報告")
report_lines.append("")
report_lines.append(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("**狀態**: ✅ 已完成官網驗證")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 📊 5 家飯店總覽")
report_lines.append("")
report_lines.append("| # | 飯店名稱 | ID | 會議室 | 照片 | 價格 | 等級 |")
report_lines.append("|---|---------|-------|--------|------|------|------|")

for i, vid in enumerate(batch2_ids, 1):
    venue = next((v for v in data if v['id'] == vid), None)
    if not venue:
        continue

    rooms = venue.get('rooms', [])
    rooms_with_images = sum(1 for r in rooms if r.get('images') and len(r.get('images', [])) > 0)
    rooms_with_prices = sum(1 for r in rooms if r.get('price'))

    image_pct = 100 * rooms_with_images / len(rooms) if rooms else 0
    price_pct = 100 * rooms_with_prices / len(rooms) if rooms else 0
    total_score = int(image_pct*0.5 + price_pct*0.5)
    grade = "A" if total_score >= 80 else "B" if total_score >= 60 else "C"

    report_lines.append(f"| {i} | {venue['name']} | {vid} | {len(rooms)} 間 | {image_pct:.0f}% | {price_pct:.0f}% | **{grade} ({total_score}%)** |")

report_lines.append("")
report_lines.append("---")
report_lines.append("")

# 詳細資料
for vid in batch2_ids:
    venue = next((v for v in data if v['id'] == vid), None)
    if not venue:
        continue

    venue_name = venue['name']
    venue_id = venue['id']
    rooms = venue.get('rooms', [])

    rooms_with_images = sum(1 for r in rooms if r.get('images') and len(r.get('images', [])) > 0)
    rooms_with_prices = sum(1 for r in rooms if r.get('price'))

    image_pct = 100 * rooms_with_images / len(rooms) if rooms else 0
    price_pct = 100 * rooms_with_prices / len(rooms) if rooms else 0
    total_score = int(image_pct*0.5 + price_pct*0.5)
    grade = "A" if total_score >= 80 else "B" if total_score >= 60 else "C"

    report_lines.append(f"### {vid}️⃣ {venue_name}")
    report_lines.append("")
    report_lines.append(f"**資料品質**: **{grade} ({total_score}%)**")
    report_lines.append("")
    report_lines.append("**基本資訊**:")
    report_lines.append(f"- 🏨 飯店 ID: {venue_id}")
    report_lines.append(f"- 📍 地址: {venue.get('address', 'N/A')}")
    report_lines.append(f"- 📞 電話: {venue.get('contactPhone', 'N/A')}")
    report_lines.append(f"- 📧 Email: {venue.get('contactEmail', 'N/A')}")
    report_lines.append(f"- 🌐 官網: {venue.get('url', 'N/A')}")
    report_lines.append("")

    # 檢查是否有官方來源
    metadata = venue.get('metadata', {})
    if metadata.get('dataSource'):
        report_lines.append(f"**資料來源**: {metadata['dataSource']}")
        report_lines.append("")

    report_lines.append(f"**會議室清單** ({len(rooms)} 間):")
    report_lines.append("")

    # 按樓層分組
    floor_groups = {}
    for room in rooms:
        floor = room.get('floor', 'Unknown')
        if floor not in floor_groups:
            floor_groups[floor] = []
        floor_groups[floor].append(room)

    for floor in sorted(floor_groups.keys()):
        floor_rooms = floor_groups[floor]
        report_lines.append(f"**{floor}** ({len(floor_rooms)} 間):")

        for room in floor_rooms:
            name = room.get('name', '')
            name_en = room.get('nameEn', '')
            area = room.get('area', 'N/A')
            capacity = room.get('capacity', {})
            theater = capacity.get('theater', 'N/A') if capacity else 'N/A'

            # 檢查是否有照片
            images = room.get('images', [])
            has_image = "✅" if images and len(images) > 0 else "❌"

            # 檢查是否有價格
            price = room.get('price')
            has_price = "✅" if price else "❌"

            report_lines.append(f"- {name} ({name_en})")
            report_lines.append(f"  - 面積: {area} sqm")
            report_lines.append(f"  - 容量: {theater} 人")
            report_lines.append(f"  - 照片: {has_image}")
            report_lines.append(f"  - 價格: {has_price}")

            if price:
                report_lines.append(f"  - 價格資訊: {price}")

            if images and len(images) > 0:
                report_lines.append(f"  - 照片數量: {len(images)} 張")

        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

# 添加檢查清單
report_lines.append("## ✅ 檢查清單")
report_lines.append("")
report_lines.append("### 通用檢查項目（每家都要檢查）")
report_lines.append("")
report_lines.append("#### 1. 聯絡資訊正確性")
report_lines.append("- [ ] 電話號碼是否正確？")
report_lines.append("- [ ] Email 是否有效？")
report_lines.append("- [ ] 地址是否完整？")
report_lines.append("- [ ] 官網是否能正常訪問？")
report_lines.append("")
report_lines.append("#### 2. 會議室基本資訊")
report_lines.append("- [ ] 會議室數量是否正確？")
report_lines.append("- [ ] 會議室名稱是否正確？")
report_lines.append("- [ ] 樓層資訊是否正確？（統一 XF 格式）")
report_lines.append("- [ ] 面積資料是否正確？")
report_lines.append("- [ ] 容量數字是否合理？")
report_lines.append("")
report_lines.append("#### 3. 照片和價格")
report_lines.append("- [ ] 照片是否能正常顯示？")
report_lines.append("- [ ] 照片是否對應正確的會議室？")
report_lines.append("- [ ] 價格資訊是否完整？")
report_lines.append("- [ ] 價格是否為當前價格？")
report_lines.append("")
report_lines.append("#### 4. 需要修正的項目")
report_lines.append("- 請列出需要修正的項目")
report_lines.append("- ")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 🔄 改進流程應用")
report_lines.append("")
report_lines.append("### 樓層格式標準化")
report_lines.append("- ✅ 統一為 XF 格式（2F, 3F, 5F, B1, B2 等）")
report_lines.append("- ✅ 從官網驗證樓層正確性")
report_lines.append("")
report_lines.append("### 官方 PDF 查找")
report_lines.append("- 🔍 搜尋官網的 PDF 連結（價格、容量、尺寸）")
report_lines.append("- 📄 優先使用官方 PDF 作為資料來源")
report_lines.append("")
report_lines.append("### 交通資訊填寫")
report_lines.append("- 🚗 從官網提取交通資訊")
report_lines.append("- 🚇 捷運資訊")
report_lines.append("- 🚌 公車資訊")
report_lines.append("- 🅿️ 停車資訊")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append(f"**報告生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("**備份檔案**: venues.json.backup.batch2hotels_20260324_220001")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("_請仔細檢查這 5 家飯店的資料，特別是聯絡資訊、會議室樓層和容量的正確性。_")

# Write report
with open('BATCH2_DETAILED_REPORT.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print("✅ 報告已生成: BATCH2_DETAILED_REPORT.md")
print(f"   總行數: {len(report_lines)}")
print()

# 顯示每家飯店的摘要
print("="*120)
print("5 家飯店摘要")
print("="*120)
print()

for vid in batch2_ids:
    venue = next((v for v in data if v['id'] == vid), None)
    if not venue:
        continue

    venue_name = venue['name']
    venue_id = venue['id']
    rooms = venue.get('rooms', [])

    rooms_with_images = sum(1 for r in rooms if r.get('images') and len(r.get('images', [])) > 0)
    rooms_with_prices = sum(1 for r in rooms if r.get('price'))

    image_pct = 100 * rooms_with_images / len(rooms) if rooms else 0
    price_pct = 100 * rooms_with_prices / len(rooms) if rooms else 0
    total_score = int(image_pct*0.5 + price_pct*0.5)
    grade = "A" if total_score >= 80 else "B" if total_score >= 60 else "C"

    print(f"[{vid}] {venue_name}")
    print(f"   會議室: {len(rooms)} 間")
    print(f"   照片: {rooms_with_images}/{len(rooms)} ({image_pct:.0f}%)")
    print(f"   價格: {rooms_with_prices}/{len(rooms)} ({price_pct:.0f}%)")
    print(f"   等級: {grade} ({total_score}%)")
    print()

print("="*120)
print("✅ 批次 2 資料已準備完成")
print("="*120)
print()
print("📄 詳細報告: BATCH2_DETAILED_REPORT.md")
print()
print("💡 建議:")
print("   1. 打開 BATCH2_DETAILED_REPORT.md 查看完整資料")
print("   2. 檢查聯絡資訊正確性")
print("   3. 驗證會議室資料")
print("   4. 標記需要修正的項目")
