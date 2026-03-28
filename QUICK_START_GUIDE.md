# 快速爬蟲工具組 - 使用指南

## 🚀 三分鐘上手

### 1. 並行爬蟲 (最快) - 推薦使用
```bash
python parallel_venue_scraper.py
```
- **速度**: 25場地/11.6秒 (0.5秒/場地)
- **成功率**: 92%
- **功能**: 自動找出需要更新的場地並爬取

### 2. 場地發現工具
```bash
python venue_discovery_tool.py
```
- 新增場地到資料庫
- 支援JSON匯入、手動輸入
- 自動檢查重複

### 3. 進度檢查
```bash
python check_v4_progress.py
```

---

## 📊 成果比較

| 工具 | 速度 | 成功率 | 說明 |
|------|------|--------|------|
| **並行爬蟲** | 0.5秒/場地 | 92% | ✅ 最快 |
| V4-Practical | 3-5秒/場地 | 93.5% | 穩定 |
| V4 完整爬蟲 | 10-15秒/場地 | 70% | 詳細 |

---

## 🔄 完整工作流程

```
發現新場地
    ↓
venue_discovery_tool.py
    ↓
parallel_venue_scraper.py (11秒完成25個)
    ↓
check_v4_progress.py (驗證)
```

**總耗時**: 約1分鐘完成25個場地的完整處理

---

## 🎯 使用場景

### 場景1: 快速處現有資料
```bash
python parallel_venue_scraper.py
```

### 場景2: 新增10個場地
```bash
# 步驟1: 新增場地
python venue_discovery_tool.py
# 選擇 1 (使用示範資料) 或 2 (匯入JSON)

# 步驟2: 爬取
python parallel_venue_scraper.py
```

### 場景3: 批次更新
```bash
# 第一次: 處理頁面數<5的場地
python parallel_venue_scraper.py

# 如需再爬一次 (再次執行即可)
python parallel_venue_scraper.py
```

---

## 📁 輸出檔案

### 1. venues.json (主資料庫)
自動更新所有場地資料

### 2. 備份檔案
```
venues.json.backup.parallel_YYYYMMDD_HHMMSS
```

### 3. 結果報告
```
parallel_scraper_results.json - 詳細結果
```

---

## ⚙️ 進階設定

### 調整並行數量
編輯 `parallel_venue_scraper.py`:
```python
scraper = FastParallelScraper(max_workers=8)  # 預設8
# 改成 16 更快，但可能被網站阻擋
# 改成 4 更穩定
```

### 只爬取特定場地
修改 `parallel_venue_scraper.py` 的篩選條件:
```python
# 只爬取頁面數=0的場地
v.get('metadata', {}).get('pagesDiscovered', 0) == 0

# 只爬取頁面數<10的場地
v.get('metadata', {}).get('pagesDiscovered', 0) < 10
```

---

## 🔍 故障排除

### 問題: SSL警告
**正常**: 忽略即可，程式會自動處理

### 問題: 403/404錯誤
- 404: 網站已失效
- 403: 網站拒絕爬蟲，需手動補充

### 問題: 速度太快被阻擋
**解決**: 降低 max_workers:
```python
scraper = FastParallelScraper(max_workers=4)  # 從8降到4
```

---

## 📈 效能數據

### 實測結果 (2026-03-25)
- 25個場地: 11.6秒
- 成功率: 92% (23/25)
- 平均: 0.5秒/場地
- 備份自動生成

### 與舊方法比較
- 舊方法: 25場地約需75-125秒
- 新方法: 25場地只需11.6秒
- **速度提升**: 6.5x - 10x

---

## 💡 最佳實踐

1. **優先使用並行爬蟲** - 最快
2. **發現工具補充新場地** - 保持資料新鮮
3. **定期檢查進度** - 確保資料品質
4. **備份自動生成** - 不用手動備份

---

**更新日期**: 2026-03-25
**適用版本**: Fast-Parallel V1.0
