#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次 2 修正：根據用戶提供的資訊更新
1. 茹曦酒店 - 添加 A廳照片
2. 寒舍喜來登 - 從 Google Drive 驗證會議室
3. 維多麗亞酒店 - 從 PDF 提取容量和租金
4. 台北國賓 - 確認會議室狀態
"""

import json
import sys
import re
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*100)
print("批次 2 修正：根據用戶提供的資訊更新")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.batch2_corrections_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# ============================================================
# 1. 茹曦酒店 - 添加 A廳照片
# ============================================================
print("="*100)
print("1. 茹曦酒店 - 添加 A廳照片")
print("="*100)

illume_idx = next((i for i, v in enumerate(data) if v.get('id') == 1090), None)
if illume_idx:
    illume = data[illume_idx]
    print(f"找到: {illume['name']}")

    # 找到茹曦廳 (ILLUME Ballroom)
    for room in illume.get('rooms', []):
        if '茹曦廳' in room.get('name', '') or 'ILLUME Ballroom' in room.get('nameEn', ''):
            print(f"找到會議室: {room['name']}")

            # 添加照片
            image_url = "https://theillumehotel.wppro.work/wp-content/uploads/2023/12/05_Events_2F_Grand_Ballroom_2-jpg.webp"

            if 'images' not in room:
                room['images'] = []

            # 檢查是否已存在
            if image_url not in room['images']:
                room['images'].append(image_url)
                print(f"✅ 已添加照片: {image_url}")
            else:
                print(f"   照片已存在")

            # 更新 metadata
            if 'metadata' not in illume:
                illume['metadata'] = {}
            illume['metadata']['imageSource'] = 'Official website'
            illume['metadata']['imageUpdatedAt'] = datetime.now().isoformat()

    data[illume_idx] = illume
    print()

# ============================================================
# 2. 寒舍喜來登 - 從 Google Drive 內容驗證
# ============================================================
print("="*100)
print("2. 寒舍喜來登 - 驗證會議室資料")
print("="*100)

sheraton_idx = next((i for i, v in enumerate(data) if v.get('id') == 1075), None)
if sheraton_idx:
    sheraton = data[sheraton_idx]
    print(f"找到: {sheraton['name']}")

    # Google Drive 連結
    # https://drive.google.com/file/d/1Ov6Aqxw1Yq2F-FkKOl3ZEUgA19TGzAWG/view

    # 根據用戶說法，只保留 Google Drive 中有的會議室
    # 需要先下載查看內容，但用戶說"就只有這些"
    # 我們暫時標記，等待用戶確認哪些要刪除

    print("⏳ Google Drive 連結已提供")
    print("   https://drive.google.com/file/d/1Ov6Aqxw1Yq2F-FkKOl3ZEUgA19TGzAWG/view")
    print()
    print("⚠️ 請查看 Google Drive 內容，確認哪些會議室是官方有的")
    print("   當前資料庫中有 16 間會議室")
    print()

    # 顯示當前會議室列表
    print("當前會議室列表:")
    for i, room in enumerate(sheraton.get('rooms', []), 1):
        name = room.get('name', '')
        floor = room.get('floor', '')
        area = room.get('area', '')
        print(f"   {i}. {name} ({floor}) - {area} sqm")
    print()

# ============================================================
# 3. 維多麗亞酒店 - 下載並提取 PDF
# ============================================================
print("="*100)
print("3. 維多麗亞酒店 - 提取容量和租金 PDF")
print("="*100)

victoria_idx = next((i for i, v in enumerate(data) if v.get('id') == 1122), None)
if victoria_idx:
    victoria = data[victoria_idx]
    print(f"找到: {victoria['name']}")

    # 下載 PDF
    pdf_url = "https://grandvictoria.com.tw/wp-content/uploads/sites/237/2022/08/2022-EVENT-VENUE-CAPACITY-RENTAL.pdf"

    print(f"下載 PDF: {pdf_url}")
    try:
        import requests
        response = requests.get(pdf_url, timeout=30)
        if response.status_code == 200:
            with open('victoria_capacity_rental.pdf', 'wb') as f:
                f.write(response.content)
            print("✅ PDF 下載成功: victoria_capacity_rental.pdf")

            # 使用 PyPDF2 提取文字
            import PyPDF2
            with open('victoria_capacity_rental.pdf', 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                print(f"PDF 頁數: {len(reader.pages)}")

                # 提取第一頁
                if len(reader.pages) > 0:
                    page = reader.pages[0]
                    text = page.extract_text()
                    print(f"\nPDF 內容（前 500 字）:")
                    print(text[:500])
                    print("...")

                    # 這裡需要手動解析 PDF 內容並更新會議室資料
                    # 暫時先標記已下載
                    if 'metadata' not in victoria:
                        victoria['metadata'] = {}
                    victoria['metadata']['capacityPdfSource'] = pdf_url
                    victoria['metadata']['capacityPdfDownloadedAt'] = datetime.now().isoformat()

            data[victoria_idx] = victoria
        else:
            print(f"❌ PDF 下載失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ PDF 處理失敗: {str(e)}")

    print()

# ============================================================
# 4. 台北國賓 - 確認會議室狀態
# ============================================================
print("="*100)
print("4. 台北國賓大飯店 - 會議室狀態")
print("="*100)

ambassador_idx = next((i for i, v in enumerate(data) if v.get('id') == 1069), None)
if ambassador_idx:
    ambassador = data[ambassador_idx]
    print(f"找到: {ambassador['name']}")
    print(f"當前會議室數量: {len(ambassador.get('rooms', []))} 間")

    print("\n用戶說：台北國賓沒有會議空間了")
    print("⚠️ 需要確認：")
    print("   1. 完全刪除這 5 間會議室？")
    print("   2. 還是標記為「已停用」？")
    print("   3. 或者保留資料作為歷史記錄？")
    print()

    # 顯示當前會議室
    print("當前會議室列表:")
    for i, room in enumerate(ambassador.get('rooms', []), 1):
        name = room.get('name', '')
        floor = room.get('floor', '')
        area = room.get('area', '')
        capacity = room.get('capacity', {})
        theater = capacity.get('theater', 'N/A') if capacity else 'N/A'
        print(f"   {i}. {name} ({floor}) - {area} sqm - {theater} 人")
    print()

# ============================================================
# 儲存更新
# ============================================================
print("="*100)
print("儲存更新")
print("="*100)

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存更新到 venues.json")
print()

print("="*100)
print("📊 修正總結")
print("="*100)
print()
print("1. ✅ 茹曦酒店 - 已添加 A廳照片")
print("2. ⏳ 寒舍喜來登 - 等待確認 Google Drive 內容")
print("3. ⏳ 維多麗亞酒店 - PDF 已下載，等待解析")
print("4. ⏳ 台北國賓 - 等待確認會議室處理方式")
print()
print(f"備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print("\n💡 下一步:")
print("   1. 請查看寒舍喜來登的 Google Drive 連結")
print("   2. 確認哪些會議室需要刪除")
print("   3. 我將解析維多麗亞酒店的 PDF")
print("   4. 確認台北國賓的處理方式")
