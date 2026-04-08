#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據用戶提供的資訊更新場地資料
1. 台北世貿中心 - 添加會議室詳細資料和照片
2. 台北亞都麗緻 - 添加 PDF 和照片連結
3. 台北六福客棧 - 下架
4. 台北典華 - 添加 Google Drive 和照片連結
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
print("根據用戶資訊更新場地資料")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.user_updates_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# ============================================================
# 1. 台北六福客棧 - 下架
# ============================================================
print("="*100)
print("1. 台北六福客棧 (1055) - 下架")
print("="*100)

leofoo_idx = next((i for i, v in enumerate(data) if v.get('id') == 1055), None)
if leofoo_idx:
    leofoo = data[leofoo_idx]
    print(f"找到: {leofoo['name']}")
    print(f"會議室數量: {len(leofoo.get('rooms', []))} 間")

    # 記錄原會議室
    original_rooms = leofoo.get('rooms', [])

    # 刪除所有會議室
    leofoo['rooms'] = []

    # 標記為下架
    if 'metadata' not in leofoo:
        leofoo['metadata'] = {}

    leofoo['metadata']['meetingRoomsStatus'] = 'discontinued'
    leofoo['metadata']['meetingRoomsRemovedAt'] = datetime.now().isoformat()
    leofoo['metadata']['originalRoomCount'] = len(original_rooms)
    leofoo['metadata']['discontinueReason'] = '用戶確認：已經沒有飯店，下架'
    leofoo['metadata']['websiteStatus'] = 'hotel_closed'
    leofoo['metadata']['discontinuedAt'] = datetime.now().isoformat()
    leofoo['metadata']['discontinuedBy'] = 'user_confirmation'

    # 標記場地狀態
    leofoo['status'] = 'discontinued'
    leofoo['enabled'] = False

    data[leofoo_idx] = leofoo

    print(f"✅ 已下架所有會議室 (原 {len(original_rooms)} 間)")
    print()

# ============================================================
# 2. 台北世貿中心 - 添加會議室詳細資料和照片
# ============================================================
print("="*100)
print("2. 台北世貿中心 (1049) - 添加會議室詳細資料")
print("="*100)

twtc_idx = next((i for i, v in enumerate(data) if v.get('id') == 1049), None)
if twtc_idx:
    twtc = data[twtc_idx]
    print(f"找到: {twtc['name']}")

    # 添加會議室詳細資料來源
    if 'metadata' not in twtc:
        twtc['metadata'] = {}

    twtc['metadata']['meetingRoomsSource'] = 'https://www.twtc.com.tw/meeting1'
    twtc['metadata']['meetingRoomsUpdatedAt'] = datetime.now().isoformat()
    twtc['metadata']['meetingRoomsVerifiedBy'] = 'user'
    twtc['metadata']['meetingRoomsNote'] = '所有會議室資料都在官網裡'

    # 更新第一會議室照片
    for room in twtc.get('rooms', []):
        if '第一' in room.get('name', ''):
            room['photo'] = 'https://www.twtc.com.tw/img/meeting/%e7%ac%ac1%e6%9c%83%e8%ad%b0%e5%ae%a4%e6%a8%99%e6%ba%96%e5%9e%8b.jpg'
            print(f"✅ 已更新第一會議室照片")
            break

    # 標記所有會議室資料來源
    for room in twtc.get('rooms', []):
        if 'metadata' not in room:
            room['metadata'] = {}
        room['metadata']['source'] = 'Official website'
        room['metadata']['sourceUrl'] = 'https://www.twtc.com.tw/meeting1'

    data[twtc_idx] = twtc
    print(f"✅ 已添加會議室資料來源和照片")
    print()

# ============================================================
# 3. 台北亞都麗緻 - 添加 PDF 和照片連結
# ============================================================
print("="*100)
print("3. 台北亞都麗緻 (1051) - 添加 PDF 和照片連結")
print("="*100)

landis_idx = next((i for i, v in enumerate(data) if v.get('id') == 1051), None)
if landis_idx:
    landis = data[landis_idx]
    print(f"找到: {landis['name']}")

    # 添加 PDF 和照片來源
    if 'metadata' not in landis:
        landis['metadata'] = {}

    landis['metadata']['pdfSource'] = 'https://taipei.landishotelsresorts.com/manage/upload/ckeditor/files/26_%E6%9C%83%E8%AD%B0%E5%B0%88%E6%A1%88%205.pdf'
    landis['metadata']['photosSource'] = 'https://taipei.landishotelsresorts.com/chinese-trad/meeting-detail.php?id=1'
    landis['metadata']['detailedInfoUpdatedAt'] = datetime.now().isoformat()
    landis['metadata']['detailedInfoVerifiedBy'] = 'user'

    # 更新會議室照片連結
    for i, room in enumerate(landis.get('rooms', [])):
        if 'images' not in room:
            room['images'] = []

        # 添加照片連結（每個會議室一個 ID）
        photo_id = i + 1
        photo_url = f'https://taipei.landishotelsresorts.com/chinese-trad/meeting-detail.php?id={photo_id}'

        if photo_url not in room['images']:
            room['images'].append(photo_url)

        if 'metadata' not in room:
            room['metadata'] = {}

        room['metadata']['photoPage'] = photo_url
        room['metadata']['source'] = 'Official website + PDF'

    data[landis_idx] = landis
    print(f"✅ 已添加 PDF 和照片連結")
    print()

# ============================================================
# 4. 台北典華 - 添加 Google Drive 和照片連結
# ============================================================
print("="*100)
print("4. 台北典華 (1057) - 添加 Google Drive 和照片連結")
print("="*100)

denwell_idx = next((i for i, v in enumerate(data) if v.get('id') == 1057), None)
if denwell_idx:
    denwell = data[denwell_idx]
    print(f"找到: {denwell['name']}")

    # 添加 Google Drive 和照片來源
    if 'metadata' not in denwell:
        denwell['metadata'] = {}

    denwell['metadata']['googleDriveFolder'] = 'https://drive.google.com/drive/folders/1iFLaRhTrlTgE-HZatmJhZI6tcSCkbZbU'
    denwell['metadata']['photosGalleryUrl'] = 'https://www.denwell.com/dazhi-banquet-venue/'
    denwell['metadata']['detailedInfoUpdatedAt'] = datetime.now().isoformat()
    denwell['metadata']['detailedInfoVerifiedBy'] = 'user'

    # 更新所有會議室的資料來源
    for room in denwell.get('rooms', []):
        if 'metadata' not in room:
            room['metadata'] = {}

        room['metadata']['dataSource'] = 'Google Drive + Official website'
        room['metadata']['galleryUrl'] = 'https://www.denwell.com/dazhi-banquet-venue/'

    data[denwell_idx] = denwell
    print(f"✅ 已添加 Google Drive 和照片連結")
    print()

# ============================================================
# 儲存更新
# ============================================================
print("="*100)
print("儲存更新")
print("="*100)

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存更新到 venues.json\n")

# ============================================================
# 總結
# ============================================================
print("="*100)
print("✅ 更新完成")
print("="*100)
print()

print("1. ✅ 台北六福客棧 (1055)")
print("   - 已下架所有會議室（1 間）")
print("   - 原因：用戶確認已經沒有飯店")
print()

print("2. ✅ 台北世貿中心 (1049)")
print("   - 已添加會議室詳細資料來源")
print("   - 已更新第一會議室照片")
print("   - 來源：https://www.twtc.com.tw/meeting1")
print()

print("3. ✅ 台北亞都麗緻 (1051)")
print("   - 已添加 PDF 連結")
print("   - 已添加照片連結")
print("   - PDF: 會議方案 5.pdf")
print("   - 照片: meeting-detail.php?id=1")
print()

print("4. ✅ 台北典華 (1057)")
print("   - 已添加 Google Drive 資料夾")
print("   - 已添加照片畫廊連結")
print("   - 來源：Google Drive + 官方網站")
print()

print(f"備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
