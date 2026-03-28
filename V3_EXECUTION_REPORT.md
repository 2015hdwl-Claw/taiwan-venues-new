# V3 爬蟲執行結果分析

**執行時間**: 2026-03-25 17:51-17:52
**目標場地**: 會展中心、會議中心（12個）

---

## 📊 執行統計

```
總計: 12 個場地
成功: 12 個 (100%)
失敗: 0 個
```

**V3 新功能統計**:
- PDF 發現: 11 個場地
- PDF 解析: 11 個 PDF
- 詳細頁面: 0 個
- 表格解析: 0 個

---

## 🔍 關鍵發現

### 問題 1: TICC 未發現 PDF

**ID 1448: 台北國際會議中心**
```
PDF 數量: 0 個 ❌
會議室: 0 個 ❌
```

**原因分析**:
- TICC 的 PDF 不在首頁連結中
- PDF URL: `https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf`
- 需要手動指定或特殊路徑發現

**解決方案**:
需要為 TICC 添加專用處理邏輯，直接訪問已知的 PDF URL。

---

### 問題 2: 集思系列 PDF 無關

**ID 1494-1499: 集思會議中心系列**
```
PDF 數量: 1-2 個 ✅
PDF 內容: 隱私政策 ❌
會議室資料: 0 個 ❌
```

**原因分析**:
- 集思首頁的 PDF 都是隱私政策、課程表等
- 真正的會議室資料在頁面 HTML 中，不在 PDF
- 或者在特定的子頁面中

**實際情況**:
- 集思台大 (ID 1128): 我們之前知道有 12 個會議室在 PDF 中
- 但這次爬取到 0 個會議室
- 需要尋找正確的 PDF 連結或深入子頁面

---

### 問題 3: 南港展覽館無資料

**ID 1500: 南港展覽館**
```
PDF 數量: 0 個
會議室: 0 個
```

**可能原因**:
1. 首頁沒有直接的會議室資訊
2. 需要進入特定子頁面
3. 可能需要 JavaScript 渲染（但檢測為 Static/SSR）

**建議**:
手動檢視南港展覽館官網結構，找出會議室資料所在位置。

---

## ⚠️ PDF 解析器的問題

### 當前實作

V3 的 PDF 解析器（`_parse_pdf` 方法）使用簡單的正則表達式：

```python
# 簡化版解析
if re.search(r'會議室|廳|全室', line):
    numbers = re.findall(r'[\d,]+', line)
    if len(numbers) >= 2:
        room = {
            'name': line[:30].strip(),
            'capacity': numbers[0].replace(',', ''),
            'area': numbers[1] if len(numbers) > 1 else None
        }
```

### 問題

1. **無法處理表格格式**: TICC PDF 是複雜的表格
2. **誤判**: 把「隱私政策」當成會議室資料
3. **不夠智能**: 無法識別跨行資料（如 101 全室）
4. **欄位映射錯誤**: 無法正確對應容量、面積、價格

### 實際案例

**TICC PDF 結構**:
```
會議室名稱 | 劇院型 | 教室型 | U型 | 洽談 | 面積(㎡/坪) | 尺寸 | 平日價 | 假日價
大會堂全場 | 3,100 | — | — | — | 2,973/899 | — | 159,000 | 170,000
101 全室 | 720 | 480 | 90 | — | 640/193 | 25.8×25.3×5.6 | 67,000 | 80,000
```

**當前解析器無法正確提取**！

---

## 🎯 改進建議

### 立即行動（手動處理）

#### 1. TICC 專用處理

建立 TICC 專用腳本：

```python
def scrape_ticc_manually():
    """手動處理 TICC"""
    pdf_url = "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf"

    # 使用之前建立的專用解析器
    from ticc_pdf_parser_v2 import TICCpdfParserV2
    parser = TICCpdfParserV2()
    rooms = parser.parse(pdf_url)

    # 更新到 venues.json
    update_venue_rooms(1448, rooms)
```

#### 2. 集思台大專用處理

使用之前已驗證的腳本：

```bash
python update_ntucc_v2.py
```

這個腳本已成功提取 12 個會議室的完整資料。

---

### V4 改進計劃

#### 1. 增強 PDF 解析器

**目標**: 支援複雜表格格式

```python
def _parse_pdf_table_v2(self, pdf_url):
    """解析 PDF 中的表格"""
    # 使用更強大的工具
    import pdfplumber  # 或 tabula-py

    with pdfplumber.open(pdf_url) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # 智能識別表頭
                # 解析每一行
                # 對應到正確的欄位
```

#### 2. 場地特定解析器

為已知的大型場地建立專用解析器：

```python
SPECIAL_PARSERS = {
    'www.ticc.com.tw': 'parse_ticc',
    'www.meeting.com.tw': 'parse_gis',
    'www.tcec.com.tw': 'parse_tpec',
}

def scrape_venue_smart(venue):
    # 檢查是否需要專用解析器
    for domain, parser_name in SPECIAL_PARSERS.items():
        if domain in venue['url']:
            return getattr(self, parser_name)(venue)

    # 否則使用通用解析器
    return self.scrape_venue_generic(venue)
```

#### 3. 手動 URL 映射

對於已知 PDF 位置的場地：

```python
KNOWN_PDF_URLS = {
    1448: "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf",
    1128: "https://www.meeting.com.tw/ntu/download/台大_場地租用申請表_20250401.pdf",
    # ...
}

def get_known_pdf(venue_id):
    return KNOWN_PDF_URLS.get(venue_id)
```

---

## 📁 相關檔案

### 爬蟲程式
- `batch_scrape_venues_v3.py` - V3 主程式
- `ticc_pdf_parser_v2.py` - TICC 專用解析器（已建立）
- `update_ntucc_v2.py` - 集思台大專用腳本（已建立）

### 報告檔案
- `batch_venue_scrape_v3_report.json` - 詳細執行報告
- `venues.json` - 已更新的資料
- `venues.json.backup.v3_*` - 備份檔案

---

## 💬 結論

### V3 執行結果

✅ **成功部分**:
- 100% 成功率（12/12）
- 自動發現 11 個 PDF
- URL 自動修正功能正常

❌ **未達預期**:
- TICC 未發現 PDF（需要手動指定）
- PDF 解析器太簡單，無法處理複雜表格
- 集思系列的會議室資料未成功提取

### 下一步選項

**選項 A: 手動處理關鍵場地**（推薦）
```bash
# 1. 處理 TICC
python scrape_ticc_with_pdf.py

# 2. 處理集思台大
python update_ntucc_v2.py

# 3. 檢查南港展覽館
python analyze_tpec_structure.py
```

**選項 B: 改進 PDF 解析器**
- 使用 `pdfplumber` 或 `tabula-py` 替代 `PyPDF2`
- 建立表格格式識別
- 增加欄位智能映射

**選項 C: 建立場地特定解析器**
- 為每個大型場地建立專用解析器
- 維護 URL 映射表
- 使用已知 PDF URL

---

**建議**: 先執行選項 A，快速獲得關鍵場地的完整資料，再考慮長期的改進方案。

---

**報告完成**: 2026-03-25 17:55
**狀態**: ⚠️ 需要手動處理關鍵場地
