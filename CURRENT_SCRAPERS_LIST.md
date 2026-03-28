# 現有爬蟲程式清單

## 📊 目前可用的爬蟲程式

### 主要爬蟲（推薦使用）

| 程式 | 用途 | 狀態 | 技術 |
|------|------|------|------|
| **full_site_scraper_v4.py** | V4完整爬蟲 | ✅ 活躍 | Scrapling + BeautifulSoup |
| **parallel_venue_scraper.py** | 並行快速爬蟲 | ✅ 活躍 | requests + BeautifulSoup (8 threads) |
| **practical_scraper.py** | 實用爬蟲測試 | ✅ 活躍 | requests + BeautifulSoup |
| **complete_room_extractor.py** | 完整會議室擷取 | ✅ 新建立 | requests + BeautifulSoup |

### 輔助工具

| 程式 | 用途 |
|------|------|
| **venue_discovery_tool.py** | 新增場地 |
| **check_v4_progress.py** | 檢查進度 |
| **check_rooms_data.py** | 檢查會議室資料 |
| **find_api_venues.py** | 找有API的場地 |

### 舊版本（建議清理）

- hotel_scraper.py
- smart_scraper.py
- advanced_scraper.py
- improved_scraper.py
- precise_scraper.py
- auto_scraper.py
- final_auto_scraper.py
- fixed_auto_scraper.py
- scraper_with_images.py
- complete_scraper.py
- direct_html_scraper.py
- unified_scraper.py
- universal_venue_scraper.py
- enhanced_venue_scraper.py
- universal_venue_scraper_v2.py
- smart_universal_scraper.py
- deep_scraper.py
- intelligent_scraper_v3.py
- full_site_scraper_v4_enhanced.py

**共19個舊版本可以刪除**

---

## 🎯 現在使用的爬蟲

### 1. full_site_scraper_v4.py
- **用途**: 完整站點爬取
- **技術**: Scrapling Fetcher
- **成功率**: ~70%
- **使用場地**: 14個

### 2. parallel_venue_scraper.py
- **用途**: 快速並行爬取
- **技術**: requests + BeautifulSoup + ThreadPoolExecutor (8 threads)
- **成功率**: 92%
- **使用場地**: 23個
- **速度**: 0.5秒/場地

### 3. practical_scraper.py
- **用途**: 測試單個場地
- **技術**: requests + BeautifulSoup
- **用途**: 開發測試

### 4. complete_room_extractor.py
- **用途**: 完整會議室資料擷取
- **技術**: requests + BeautifulSoup
- **狀態**: 新建立，未測試

---

## 📋 爬蟲比較

| 爬蟲 | 速度 | 成功率 | 完整性 | 推薦度 |
|------|------|--------|--------|--------|
| parallel_venue_scraper.py | ⚡⚡⚡ 最快 | 92% | 中 | ⭐⭐⭐⭐⭐ |
| full_site_scraper_v4.py | ⚡⚡ 中等 | 70% | 高 | ⭐⭐⭐ |
| practical_scraper.py | ⚡⚡ 快 | 93% | 低 | ⭐⭐⭐⭐ |
| complete_room_extractor.py | ⚡⚡ 快 | 未知 | 最高 | ⭐⭐⭐⭐⭐ (理論) |

---

## 💡 建議

### 日常使用
```bash
# 快速更新場地
python parallel_venue_scraper.py
```

### 新增場地
```bash
# 1. 新增場地
python venue_discovery_tool.py

# 2. 爬取資料
python parallel_venue_scraper.py
```

### 完整擷取（包含所有欄位）
```bash
# 使用新的完整擷取器（需測試）
python complete_room_extractor.py
```

---

## 🗑️ 建議清理的舊版本

可以刪除19個舊版本爬蟲，保留：
- full_site_scraper_v4.py
- parallel_venue_scraper.py
- practical_scraper.py
- complete_room_extractor.py
- 輔助工具（5個）

**總計**: 保留8個核心檔案，刪除19個舊版本
