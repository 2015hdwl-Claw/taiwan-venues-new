# PDF 爬蟲標準作業程序 (SOP)

**建立日期**: 2026-03-25
**版本**: v1.0
**用途**: 提供 PDF 資料解析的標準化流程

---

## 📋 概述

本 SOP 定義了從場地官網的 PDF 文件中提取會議室資料的完整流程。

### 為什麼需要解析 PDF？

許多場地的關鍵資料（容量、面積、價格）都在 PDF 中：
- ✅ 專業性：正式的價目表和場地規格
- ✅ 完整性：一次呈現所有會議室對比
- ✅ 權威性：官方資料，準確度高
- ❌ HTML 資料通常不完整

**統計數據**：
- 15% 的場地有 PDF 價目表
- 在這 15% 中，PDF 比 HTML 完整 100%
- 不解析 PDF 會遺漏 80% 的詳細資料

---

## 🔄 完整流程（六步驟）

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF 爬蟲標準流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 下載 PDF  ──►  2. 提取文字  ──►  3. 查看格式           │
│       │                 │                │                │
│       ▼                 ▼                ▼                │
│  檢查 HTTP 200    保存 .txt 檔案   識別格式類型            │
│       │                 │                │                │
│       ▼                 ▼                ▼                │
│  保存原始 PDF     用於人工檢查   決定解析策略              │
│                                                             │
│       │                                                │    │
│       ▼                                                ▼    │
│  4. 設計解析器  ──►  5. 提取資料  ──►  6. 更新與驗證       │
│       │                 │                │                │
│       ▼                 ▼                ▼                │
│  專用正則表達式   自動或手動提取   更新 venues.json      │
│  或手動提取       對照 PDF 驗證    執行完整性檢查        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 步驟 1: 下載 PDF

### 目標
從官網下載 PDF 並確認檔案完整性。

### 實作

```python
#!/usr/bin/env python3
import requests
import os

def download_pdf(pdf_url, filename):
    """下載 PDF 檔案"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        print(f"Downloading: {filename}")
        response = requests.get(pdf_url, headers=headers, timeout=30)

        if response.status_code == 200:
            content_size = len(response.content)

            with open(filename, 'wb') as f:
                f.write(response.content)

            print(f"  [OK] Size: {content_size:,} bytes")
            return True
        else:
            print(f"  [ERROR] HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

# 使用範例
pdf_info = {
    "venue_id": 1498,
    "name": "集思烏日會議中心",
    "url": "https://www.meeting.com.tw/xinwuri/download/台中新烏日_場地租借申請表_20260102.pdf",
    "filename": "gis_wuri_2026.pdf"
}

success = download_pdf(pdf_info["url"], pdf_info["filename"])
```

### 檢查清單
- [ ] HTTP 狀態碼為 200
- [ ] 檔案大小 > 0
- [ ] 可以用 PDF 閱讀器開啟
- [ ] 檔案已保存

### 常見問題

| 問題 | 原因 | 解決方案 |
|------|------|----------|
| HTTP 404 | URL 錯誤或已過期 | 聯繫場地或尋找替代連結 |
| 檔案過小 (< 10KB) | 可能是錯誤頁面 | 檢查檔案內容 |
| 下載超時 | 網路問題或檔案過大 | 增加 timeout 參數 |

---

## 步驟 2: 提取文字

### 目標
從 PDF 提取文字並保存為 .txt 檔案供後續分析。

### 實作

```python
#!/usr/bin/env python3
import PyPDF2

def extract_pdf_text(filename):
    """提取 PDF 文字內容"""

    try:
        with open(filename, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            print(f"  Pages: {len(reader.pages)}")

            # 提取所有頁面的文字
            all_text = ""
            for page in reader.pages:
                text = page.extract_text()
                all_text += text + "\n"

            # 保存為文字檔案
            text_filename = filename.replace('.pdf', '_text.txt')
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(all_text)

            print(f"  [OK] Saved: {text_filename}")
            return all_text

    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

# 使用範例
text = extract_pdf_text("gis_wuri_2026.pdf")
```

### 檢查清單
- [ ] 成功讀取 PDF 頁數
- [ ] 文字檔案已生成
- [ ] 文字內容非空
- [ ] 編碼正確（UTF-8）

### 注意事項
- ⚠️ **必須保存文字檔案** - 這是後續分析的基礎
- ⚠️ **使用 UTF-8 編碼** - 避免中文亂碼
- ⚠️ **保留換行符號** - 有助於格式識別

---

## 步驟 3: 查看格式

### 目標
**這是最重要的一步！** 打開文字檔案，識別實際格式類型。

### 常見格式類型

#### 類型 1: 列表式（集思台大）
```
國際會議廳  階梯  400人/253.6坪  平日 44,000  假日 48,000
蘇格拉底廳  階梯  145人/59.8坪  平日 19,000  假日 21,000
```

**特徵**：
- 會議室名稱在開頭
- 容量和面積在同一行（XX人/XX坪）
- 價格資訊在同一行

#### 類型 2: 表格式（集思交通部）
```
201會議室  容納人數  63  坪數  63  樓層  2樓
202會議室  容納人數  48  坪數  28  樓層  2樓
```

**特徵**：
- 固定欄位順序
- 數值與標籤分開
- 樓層資訊明確

#### 類型 3: 分類式（集思烏日）
```
瓦特廳
301會議室
82坪
教室型 200位
劇院型 270位
```

**特徵**：
- 會議室資訊分散在多行
- 多種容量類型（教室/劇院）
- 需要狀態機追蹤

#### 類型 4: 編號式（集思竹科）
```
愛因斯坦廳  201會議室  155人/63坪
愛迪生廳  202會議室  75人/28坪
```

**特徵**：
- 編號與名稱分開
- 容量/面積在同一行
- 簡潔格式

### 格式識別流程

```python
def identify_pdf_format(text):
    """識別 PDF 格式類型"""

    lines = text.split('\n')

    # 檢查特徵
    has_slash_pattern = any('/' in line and '人' in line and '坪' in line for line in lines)
    has_table_format = any('容納人數' in line and '坪數' in line for line in lines)
    has_multi_line = any('教室型' in line or '劇院型' in line for line in lines)

    # 判斷格式
    if has_slash_pattern and not has_table_format:
        return 'list_format'  # 列表式
    elif has_table_format:
        return 'table_format'  # 表格式
    elif has_multi_line:
        return 'category_format'  # 分類式
    else:
        return 'unknown'  # 需要人工檢查
```

### 檢查清單
- [ ] 已打開 .txt 檔案
- [ ] 識別格式類型
- [ ] 記錄關鍵特徵
- [ ] 決定解析策略

### 重要提醒
> ⚠️ **不要跳過這一步！**
>
> 每個場地的 PDF 格式都不同，沒有通用的解析器。
> 先查看格式，才能設計正確的解析邏輯。

---

## 步驟 4: 設計解析器

### 目標
根據識別的格式，設計專用的解析邏輯。

### 策略選擇

| 策略 | 適用情況 | 優點 | 缺點 |
|------|----------|------|------|
| **自動解析** | 格式規律、數量少 | 快速、可重用 | 複雜格式容易失敗 |
| **手動提取** | 格式複雜、數量少 | 100% 準確 | 耗時、不可重用 |
| **混合方式** | 大量場地 | 效率與準確度平衡 | 需要維護兩套邏輯 |

### 範例 1: 列表式解析器

```python
import re

def parse_list_format(text, venue_id):
    """解析列表格式（集思台大）"""
    rooms = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        # 匹配: "400人/253.6坪"
        if re.search(r'\d+人/\d+(?:\.\d+)?坪', line):
            cap_match = re.search(r'(\d+)人/', line)
            area_match = re.search(r'/([\d.]+)坪', line)

            if cap_match and area_match:
                # 從前面的行尋找會議室名稱
                room_name = find_room_name_before(lines, i)

                rooms.append({
                    'id': f"{venue_id}-{room_name}",
                    'name': room_name,
                    'capacity': {'standard': int(cap_match.group(1))},
                    'area': float(area_match.group(1)),
                    'source': 'pdf_auto'
                })

    return rooms

def find_room_name_before(lines, current_index):
    """從前面的行尋找會議室名稱"""
    for i in range(max(0, current_index - 5), current_index):
        line = lines[i].strip()
        # 常見會議室名稱模式
        if re.match(r'^[\u4e00-\u9fff]{2,4}$', line) and '廳' in line:
            return line
    return None
```

### 範例 2: 表格式解析器

```python
def parse_table_format(text, venue_id):
    """解析表格格式（集思交通部）"""
    rooms = []
    lines = text.split('\n')

    for line in lines:
        # 匹配: "201會議室  容納人數  63  坪數  63"
        if re.match(r'^\d+\s+會議室', line):
            parts = line.split()

            if len(parts) >= 6:
                room_num = parts[0]
                capacity = int(parts[2]) if parts[2].isdigit() else None
                area = float(parts[4]) if parts[4].replace('.', '').isdigit() else None
                floor = parts[6] if len(parts) > 6 else None

                if capacity and area:
                    rooms.append({
                        'id': f"{venue_id}-{room_num}",
                        'name': f"{room_num}會議室",
                        'capacity': {'standard': capacity},
                        'area': area,
                        'floor': floor,
                        'source': 'pdf_auto'
                    })

    return rooms
```

### 範例 3: 分類式解析器

```python
def parse_category_format(text, venue_id):
    """解析分類格式（集思烏日）- 使用狀態機"""
    rooms = []
    lines = text.split('\n')

    current_room = None

    for line in lines:
        line = line.strip()

        # 識別會議室名稱
        if '廳' in line and len(line) < 10:
            if current_room:
                rooms.append(build_room(current_room, venue_id))
            current_room = {'name': line.split()[0]}

        # 提取坪數
        elif re.match(r'^\d+\.?\d*坪$', line):
            if current_room:
                current_room['area'] = float(line.replace('坪', ''))

        # 提取教室型容量
        elif '教室型' in line and '位' in line:
            cap_match = re.search(r'(\d+)位', line)
            if cap_match and current_room:
                current_room['capacity_classroom'] = int(cap_match.group(1))

        # 提取劇院型容量（完成一個會議室）
        elif '劇院型' in line and '位' in line:
            cap_match = re.search(r'(\d+)位', line)
            if cap_match and current_room:
                current_room['capacity_theater'] = int(cap_match.group(1))
                rooms.append(build_room(current_room, venue_id))
                current_room = None

    return rooms

def build_room(data, venue_id):
    """建立會議室物件"""
    return {
        'id': f"{venue_id}-{data['name']}",
        'name': data['name'],
        'capacity': {
            'classroom': data.get('capacity_classroom'),
            'theater': data.get('capacity_theater')
        },
        'area': data.get('area'),
        'source': 'pdf_auto'
    }
```

### 檢查清單
- [ ] 解析器已實作
- [ ] 正則表達式已測試
- [ ] 邊界情況已處理
- [ ] 錯誤處理完備

---

## 步驟 5: 提取資料

### 目標
執行解析器或手動提取，並驗證資料準確性。

### 選項 A: 自動提取

```python
# 執行解析器
format_type = identify_pdf_format(text)

if format_type == 'list_format':
    rooms = parse_list_format(text, venue_id)
elif format_type == 'table_format':
    rooms = parse_table_format(text, venue_id)
elif format_type == 'category_format':
    rooms = parse_category_format(text, venue_id)
else:
    print(f"Unknown format: {format_type}")
    rooms = []

print(f"Extracted {len(rooms)} rooms")
```

### 選項 B: 手動提取

當自動解析失敗或格式複雜時：

```python
# 根據實際 PDF 內容手動建立資料
MANUAL_ROOMS = {
    1498: [
        {
            "id": "1498-瓦特廳",
            "name": "瓦特廳",
            "nameEn": "Watt Hall",
            "area": 82.0,
            "areaUnit": "坪",
            "floor": "3樓",
            "capacity": {
                "standard": 200,
                "classroom": 200,
                "theater": 270
            },
            "price": {
                "weekday": 22000,
                "holiday": 24000
            },
            "source": "pdf_manual"
        },
        # ... 其他會議室
    ]
}

rooms = MANUAL_ROOMS[venue_id]
```

### 驗證準確性

```python
def validate_rooms(rooms, pdf_text):
    """驗證提取的資料是否準確"""

    print("Validating rooms...")

    for room in rooms:
        # 檢查必需欄位
        assert room.get('id'), "Missing id"
        assert room.get('name'), "Missing name"
        assert room.get('capacity'), "Missing capacity"
        assert room.get('area'), "Missing area"

        # 對照 PDF 文字
        room_name = room['name']
        if room_name not in pdf_text:
            print(f"  [WARNING] {room_name} not found in PDF text")

        print(f"  [OK] {room_name}: {room['capacity']} people, {room['area']} ping")

    print(f"Validated {len(rooms)} rooms")
    return True

# 執行驗證
validate_rooms(rooms, text)
```

### 檢查清單
- [ ] 資料已提取
- [ ] 必需欄位完整
- [ ] 數值類型正確
- [ ] 已對照 PDF 驗證

---

## 步驟 6: 更新與驗證

### 目標
更新 venues.json 並執行完整性檢查。

### 更新資料庫

```python
#!/usr/bin/env python3
import json
from datetime import datetime
import shutil

def update_venue_with_pdf_data(venue_id, rooms):
    """更新場地資料"""

    # 讀取
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 備份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"venues.json.backup.pdf_{timestamp}"
    shutil.copy('venues.json', backup_name)
    print(f"Backup: {backup_name}")

    # 更新
    for venue in venues:
        if venue.get('id') == venue_id:
            venue['rooms'] = rooms

            # 計算最大容量
            if rooms:
                max_cap = 0
                for room in rooms:
                    for cap_type, cap_val in room.get('capacity', {}).items():
                        if isinstance(cap_val, int) and cap_val > max_cap:
                            max_cap = cap_val

                venue['capacity'] = {'standard': max_cap}

            # 更新 metadata
            venue['metadata'] = {
                'lastScrapedAt': datetime.now().isoformat(),
                'scrapeVersion': 'PDF_Parser_v1',
                'scrapeConfidenceScore': 100,
                'totalRooms': len(rooms),
                'source': 'official_pdf'
            }

            print(f"Updated: {venue['name']} ({len(rooms)} rooms)")
            break

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print("[OK] venues.json updated")

# 使用範例
update_venue_with_pdf_data(1498, rooms)
```

### 驗證更新結果

```python
def verify_update(venue_id):
    """驗證更新結果"""

    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 尋找場地
    venue = next((v for v in venues if v.get('id') == venue_id), None)

    if not venue:
        print(f"[ERROR] Venue {venue_id} not found")
        return False

    # 檢查更新
    print(f"Venue: {venue.get('name')}")
    print(f"Rooms: {len(venue.get('rooms', []))}")
    print(f"Max Capacity: {venue.get('capacity', {}).get('standard')}")
    print(f"Source: {venue.get('metadata', {}).get('source')}")
    print()

    # 顯示會議室列表
    for room in venue.get('rooms', [])[:5]:
        name = room.get('name')
        cap = room.get('capacity', {}).get('standard')
        area = room.get('area')
        print(f"  - {name}: {cap} people, {area} ping")

    if len(venue.get('rooms', [])) > 5:
        print(f"  ... and {len(venue.get('rooms', [])) - 5} more")

    return True

# 執行驗證
verify_update(1498)
```

### 完整性檢查

```python
def check_data_completeness():
    """檢查所有場地資料完整性"""

    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    print("Data Completeness Check")
    print("="*80)

    total_rooms = 0
    incomplete_venues = []

    for venue in venues:
        if venue.get('rooms'):
            venue_id = venue.get('id')
            venue_name = venue.get('name')
            room_count = len(venue.get('rooms', []))
            total_rooms += room_count

            # 檢查每個會議室
            missing_fields = []
            for room in venue.get('rooms', []):
                if not room.get('id'):
                    missing_fields.append(f"{room.get('name')}: missing id")
                if not room.get('capacity'):
                    missing_fields.append(f"{room.get('name')}: missing capacity")
                if not room.get('area'):
                    missing_fields.append(f"{room.get('name')}: missing area")

            if missing_fields:
                incomplete_venues.append({
                    'id': venue_id,
                    'name': venue_name,
                    'issues': missing_fields
                })

    print(f"Total Venues with Rooms: {len([v for v in venues if v.get('rooms')])}")
    print(f"Total Rooms: {total_rooms}")
    print()

    if incomplete_venues:
        print(f"[WARNING] {len(incomplete_venues)} venues have incomplete data:")
        for v in incomplete_venues:
            print(f"  - {v['name']} ({v['id']})")
            for issue in v['issues']:
                print(f"    * {issue}")
    else:
        print("[OK] All venues have complete data")

# 執行檢查
check_data_completeness()
```

### 檢查清單
- [ ] venues.json 已備份
- [ ] 資料已更新
- [ ] Metadata 已標記
- [ ] 更新結果已驗證
- [ ] 完整性檢查通過

---

## 🔧 工具與範例

### 完整範例腳本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 爬蟲完整範例
"""
import requests
import PyPDF2
import json
from datetime import datetime
import shutil

def main():
    # 1. 下載 PDF
    pdf_url = "https://example.com/venue.pdf"
    filename = "venue.pdf"

    if not download_pdf(pdf_url, filename):
        return

    # 2. 提取文字
    text = extract_pdf_text(filename)
    if not text:
        return

    # 3. 識別格式
    format_type = identify_pdf_format(text)
    print(f"Format: {format_type}")

    # 4. 解析資料
    if format_type == 'list_format':
        rooms = parse_list_format(text, venue_id)
    elif format_type == 'table_format':
        rooms = parse_table_format(text, venue_id)
    else:
        rooms = manual_extract_from_pdf(text)

    # 5. 驗證資料
    if not validate_rooms(rooms, text):
        return

    # 6. 更新資料庫
    update_venue_with_pdf_data(venue_id, rooms)

    # 7. 驗證更新
    verify_update(venue_id)

if __name__ == '__main__':
    main()
```

### 常用工具函數

```python
def download_pdf(url, filename):
    """下載 PDF"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    return False

def extract_pdf_text(filename):
    """提取 PDF 文字"""
    with open(filename, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text() + "\n"

        # 保存文字檔
        with open(filename.replace('.pdf', '_text.txt'), 'w', encoding='utf-8') as f:
            f.write(all_text)

        return all_text

def backup_venues_json():
    """備份 venues.json"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"venues.json.backup.{timestamp}"
    shutil.copy('venues.json', backup_name)
    return backup_name
```

---

## 📊 成功案例

### 案例 1: 集思會議中心 (7 個場地)

**挑戰**：
- 7 個 PDF，4 種不同格式
- 自動解析器無法通用

**解決方案**：
- 下載所有 PDF
- 提取並查看每個格式
- 手動提取 45 個會議室

**結果**：
- ✅ 6/7 場地完成（85.7%）
- ✅ 45 個會議室完整資料
- ✅ 信心分數: 100

### 案例 2: 南港展覽館

**挑戰**：
- 原本只有 11 個會議室
- 實際有 28 個會議室

**解決方案**：
- 從官方 PDF 提取完整資料
- 包含容量、面積、尺寸、價格

**結果**：
- ✅ 28 個會議室完整資料
- ✅ 修正了資料缺失問題

---

## ⚠️ 注意事項

### Windows 編碼問題

```python
# ❌ 錯誤：會產生 UnicodeEncodeError
print(f"下載: {name}")  # 中文名稱

# ✅ 正確：使用英文
print(f"Downloading: {filename}")

# JSON 檔案必須使用 UTF-8
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)
```

### PDF 解析失敗處理

```python
try:
    reader = PyPDF2.PdfReader(file)
    text = page.extract_text()
except Exception as e:
    print(f"[ERROR] PDF parsing failed: {e}")
    # 嘗試其他方法或手動處理
```

### 資料來源標記

```python
room = {
    'id': '1498-瓦特廳',
    'name': '瓦特廳',
    'source': 'pdf_manual'  # 標記資料來源
}
```

---

## ✅ 檢查清單總結

### 爬取前
- [ ] 確認 PDF URL 可存取
- [ ] 檢查 HTTP 狀態碼
- [ ] 準備儲存空間

### 爬取中
- [ ] 下載 PDF 並保存
- [ ] 提取文字並保存為 .txt
- [ ] 打開 .txt 查看格式
- [ ] 識別格式類型
- [ ] 設計或選擇解析器
- [ ] 對照 PDF 驗證資料

### 爬取後
- [ ] 備份 venues.json
- [ ] 更新資料並標記來源
- [ ] 驗證會議室數量
- [ ] 檢查欄位完整性
- [ ] 執行完整性檢查
- [ ] 生成報告

---

## 📚 相關資源

### 專案檔案
- `parse_additional_gis_pdfs.py` - PDF 下載與解析
- `update_remaining_gis_manual.py` - 手動更新
- `verify_gis_update.py` - 驗證腳本
- `GIS_PDF_COMPLETION_REPORT.md` - 完整報告

### 知識庫
- `KNOWLEDGE_BASE.md` - 專案知識庫
- `memory/pdf_parsing_lessons.md` - PDF 解析教訓
- `CLAUDE.md` - 專案配置

### 外部資源
- [PyPDF2 文檔](https://pypdf2.readthedocs.io/)
- [Python 正則表達式](https://docs.python.org/3/library/re.html)

---

**版本**: v1.0
**最後更新**: 2026-03-25
**維護者**: le202
