# 活動大師 - 完全自動執行差異化策略計畫

**制定日期**: 2026-03-17  
**執行負責人**: Jane (Global CEO)  
**技術執行**: Jobs (Global CTO)  
**執行狀態**: 🟢 立即執行中

---

## 📊 專案現況

### ✅ 已完成
- 深度資料（台北市 112 場地、496 會議室）
- 會議室規格（坪數、容納人數、配置）
- 篩選功能
- 比較功能
- 地圖顯示
- Vercel 自動部署

### 📈 資料分布
- **總場地數**: 348 個
- **台北市**: 112 個（32%）✅ 深度資料
- **台中市**: 39 個
- **高雄市**: 30 個
- **其他縣市**: 167 個

---

## 🎯 執行目標

### 差異化核心
1. **最完整、最準確的場地資料**
2. **全自動資料驗證與更新**
3. **零人工參與的資料維護**
4. **即時資料同步到 Vercel**

---

## 📅 執行時間表（按週規劃）

### 第 1 週（2026-03-17 ~ 03-23）：基礎建設

#### Day 1-2：自動化核心系統
- [ ] 開發「資料驗證引擎」
  - 自動訪問官網
  - 自動提取會議室資訊
  - 自動比對現有資料
  - 自動標記差異
  
- [ ] 開發「資料修正系統」
  - 自動更新錯誤資料
  - 自動補齊缺失欄位
  - 自動驗證照片 URL
  - 自動下載與優化照片

#### Day 3-4：自動同步系統
- [ ] 開發「Git 自動提交系統」
  - 自動生成 commit message
  - 自動 push 到 GitHub
  - 自動觸發 Vercel 部署
  - 自動驗證部署結果

#### Day 5-7：測試與優化
- [ ] 完整測試自動化流程
- [ ] 修正 bug
- [ ] 優化執行效率
- [ ] 文件化

**里程碑**: 自動化系統可獨立運行

---

### 第 2 週（2026-03-24 ~ 03-30）：資料擴充

#### Day 1-3：台中市場地深度資料
- [ ] 爬取台中市 39 個場地官網
- [ ] 提取會議室資訊
- [ ] 下載會議室照片
- [ ] 驗證資料準確性
- [ ] 自動更新到 venues.json

#### Day 4-6：高雄市場地深度資料
- [ ] 爬取高雄市 30 個場地官網
- [ ] 提取會議室資訊
- [ ] 下載會議室照片
- [ ] 驗證資料準確性
- [ ] 自動更新到 venues.json

#### Day 7：驗證與優化
- [ ] 驗證台中市、高雄市資料
- [ ] 修正錯誤
- [ ] 優化爬蟲效率

**里程碑**: 台中市、高雄市資料完整度達 90%

---

### 第 3 週（2026-03-31 ~ 04-06）：功能開發

#### Day 1-3：一鍵詢價功能
- [ ] 設計詢價表單 UI
- [ ] 開發 Email 發送 API
- [ ] 整合場地資料
- [ ] 自動生成詢價信

#### Day 4-6：檔期查詢功能
- [ ] 設計檔期查詢 UI
- [ ] 開發檔期爬蟲（支援主要場地）
- [ ] 即時更新檔期狀態
- [ ] 自動通知可用檔期

#### Day 7：整合測試
- [ ] 測試一鍵詢價
- [ ] 測試檔期查詢
- [ ] 修正 bug

**里程碑**: 一鍵詢價、檔期查詢功能上線

---

### 第 4 週（2026-04-07 ~ 04-13）：生態系建置

#### Day 1-3：活動公司資料庫
- [ ] 收集台灣活動公司資料
- [ ] 建立資料結構
- [ ] 開發搜尋功能
- [ ] 整合到主站

#### Day 4-6：餐飲外燴資料庫
- [ ] 收集台灣餐飲外燴資料
- [ ] 建立資料結構
- [ ] 開發搜尋功能
- [ ] 整合到主站

#### Day 7：AV 設備商資料庫
- [ ] 收集台灣 AV 設備商資料
- [ ] 建立資料結構
- [ ] 開發搜尋功能
- [ ] 整合到主站

**里程碑**: 生態系資料庫完整

---

### 第 5-8 週（2026-04-14 ~ 05-11）：全面擴充

#### 第 5 週：新北市、桃園市
- [ ] 新北市 24 個場地深度資料
- [ ] 桃園市 17 個場地深度資料

#### 第 6 週：台南市、其他縣市
- [ ] 台南市 21 個場地深度資料
- [ ] 其他縣市 105 個場地基礎資料

#### 第 7 週：線上預訂功能
- [ ] 設計預訂流程
- [ ] 開發預訂 API
- [ ] 整合場地系統

#### 第 8 週：評價系統
- [ ] 設計評價機制
- [ ] 開發評價 API
- [ ] 整合到場地頁面

**里程碑**: 全台 348 個場地資料完整度達 80%

---

## 🤖 最嚴格的資料清理自動化機制

### 核心架構

```
┌─────────────────────────────────────────────────────────┐
│                   自動化資料清理系統                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐│
│  │  資料驗證引擎  │──>│  資料修正系統  │──>│  自動同步系統  ││
│  └──────────────┘   └──────────────┘   └──────────────┘│
│         │                   │                   │        │
│         ▼                   ▼                   ▼        │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐│
│  │  網站爬蟲模組  │   │  資料比對模組  │   │  Git 自動化   ││
│  └──────────────┘   └──────────────┘   └──────────────┘│
│         │                   │                   │        │
│         └───────────────────┴───────────────────┘        │
│                             │                            │
│                             ▼                            │
│                    ┌──────────────┐                      │
│                    │  Vercel 部署  │                      │
│                    └──────────────┘                      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 1. 資料驗證引擎

#### 功能
- 自動訪問場地官網
- 自動提取會議室資訊
- 自動比對現有資料
- 自動標記差異

#### 技術實現
```python
class DataVerificationEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def verify_venue(self, venue_id):
        """驗證單一場地"""
        venue = self.load_venue(venue_id)
        website_data = self.crawl_website(venue['url'])
        
        differences = self.compare_data(venue, website_data)
        
        if differences:
            self.flag_for_update(venue_id, differences)
        
        return differences
    
    def crawl_website(self, url):
        """爬取官網資料"""
        # 智能爬蟲邏輯
        pass
    
    def compare_data(self, local_data, website_data):
        """比對資料差異"""
        # 資料比對邏輯
        pass
```

### 2. 資料修正系統

#### 功能
- 自動更新錯誤資料
- 自動補齊缺失欄位
- 自動驗證照片 URL
- 自動下載與優化照片

#### 技術實現
```python
class DataCorrectionSystem:
    def __init__(self):
        self.photo_downloader = PhotoDownloader()
        self.validator = DataValidator()
    
    def auto_correct(self, venue_id, differences):
        """自動修正資料"""
        venue = self.load_venue(venue_id)
        
        for field, (old_value, new_value) in differences.items():
            # 驗證新值
            if self.validator.validate_field(field, new_value):
                venue[field] = new_value
                self.log_correction(venue_id, field, old_value, new_value)
        
        # 更新照片
        if 'photos' in differences:
            self.update_photos(venue, differences['photos'])
        
        self.save_venue(venue)
    
    def update_photos(self, venue, photo_urls):
        """更新照片"""
        for room_name, photo_url in photo_urls.items():
            # 下載照片
            photo_path = self.photo_downloader.download(photo_url)
            
            # 優化照片
            optimized_path = self.photo_downloader.optimize(photo_path)
            
            # 更新資料
            venue['rooms'][room_name]['images']['main'] = optimized_path
```

### 3. 自動同步系統

#### 功能
- 自動生成 commit message
- 自動 push 到 GitHub
- 自動觸發 Vercel 部署
- 自動驗證部署結果

#### 技術實現
```python
class AutoSyncSystem:
    def __init__(self):
        self.github_api = GitHubAPI()
        self.vercel_api = VercelAPI()
    
    def sync_to_production(self, changes):
        """同步到生產環境"""
        # 1. 生成 commit message
        commit_msg = self.generate_commit_message(changes)
        
        # 2. Git commit & push
        self.git_commit(commit_msg)
        self.git_push()
        
        # 3. 等待 Vercel 部署
        deployment_id = self.vercel_api.trigger_deploy()
        self.wait_for_deployment(deployment_id)
        
        # 4. 驗證部署結果
        if self.verify_deployment():
            self.notify_success(changes)
        else:
            self.rollback()
            self.notify_failure(changes)
```

### 4. 執行排程

#### 每日自動執行
```python
# 每天凌晨 2:00 執行
schedule.every().day.at("02:00").do(daily_verification)

def daily_verification():
    """每日驗證"""
    # 1. 隨機抽取 10% 場地驗證
    venues_to_verify = random.sample(all_venues, len(all_venues) // 10)
    
    # 2. 執行驗證
    for venue_id in venues_to_verify:
        differences = verification_engine.verify_venue(venue_id)
        
        if differences:
            correction_system.auto_correct(venue_id, differences)
    
    # 3. 同步到生產環境
    if has_changes():
        sync_system.sync_to_production(changes)
```

#### 每週深度驗證
```python
# 每週日凌晨 3:00 執行
schedule.every().sunday.at("03:00").do(weekly_deep_verification)

def weekly_deep_verification():
    """每週深度驗證"""
    # 1. 驗證所有場地
    for venue_id in all_venues:
        differences = verification_engine.verify_venue(venue_id)
        
        if differences:
            correction_system.auto_correct(venue_id, differences)
    
    # 2. 驗證照片 URL
    for venue_id in all_venues:
        photo_validator.validate_all_photos(venue_id)
    
    # 3. 同步到生產環境
    sync_system.sync_to_production(all_changes)
```

---

## 📋 任務分配

### Jobs (Global CTO) - 技術開發

#### 第 1 週任務
1. **開發資料驗證引擎**
   - 檔案: `auto_verification_engine.py`
   - 功能: 自動爬取官網、比對資料
   - 預計工時: 16 小時

2. **開發資料修正系統**
   - 檔案: `auto_correction_system.py`
   - 功能: 自動修正錯誤、下載照片
   - 預計工時: 12 小時

3. **開發自動同步系統**
   - 檔案: `auto_sync_system.py`
   - 功能: Git 自動化、Vercel 部署
   - 預計工時: 8 小時

#### 第 2 週任務
1. **台中市場地資料更新**
   - 使用自動化系統更新 39 個場地
   - 預計工時: 20 小時（自動化後縮減為 4 小時）

2. **高雄市場地資料更新**
   - 使用自動化系統更新 30 個場地
   - 預計工時: 16 小時（自動化後縮減為 3 小時）

#### 第 3-8 週任務
- 持續擴充其他縣市資料
- 開發新功能（一鍵詢價、檔期查詢等）
- 建置生態系資料庫

---

## 🎯 里程碑與驗收標準

### 里程碑 1：自動化系統上線（第 1 週結束）
- [ ] 資料驗證引擎可獨立運行
- [ ] 資料修正系統可自動修正錯誤
- [ ] 自動同步系統可自動部署到 Vercel
- [ ] 完整測試報告

**驗收標準**:
- 系統可連續運行 24 小時無錯誤
- 自動修正成功率 > 95%
- 部署成功率 = 100%

### 里程碑 2：台中、高雄資料完整（第 2 週結束）
- [ ] 台中市 39 個場地完整度 > 90%
- [ ] 高雄市 30 個場地完整度 > 90%
- [ ] 所有會議室都有照片
- [ ] 所有價格資訊正確

**驗收標準**:
- 資料準確率 > 98%
- 照片覆蓋率 = 100%
- 用戶滿意度 > 4.5/5

### 里程碑 3：核心功能上線（第 3 週結束）
- [ ] 一鍵詢價功能可用
- [ ] 檔期查詢功能可用
- [ ] 整合測試通過

**驗收標準**:
- 詢價成功率 > 90%
- 檔期查詢準確率 > 95%
- 功能無 bug

### 里程碑 4：生態系完整（第 4 週結束）
- [ ] 活動公司資料庫 > 100 家
- [ ] 餐飲外燴資料庫 > 80 家
- [ ] AV 設備商資料庫 > 50 家

**驗收標準**:
- 資料完整度 > 85%
- 搜尋功能正常
- 整合到主站

### 里程碑 5：全面擴充完成（第 8 週結束）
- [ ] 全台 348 個場地完整度 > 80%
- [ ] 線上預訂功能上線
- [ ] 評價系統上線

**驗收標準**:
- 資料完整度 > 80%
- 預訂成功率 > 85%
- 評價系統穩定

---

## 🔧 技術規格

### 開發環境
- Python 3.10+
- Node.js 18+
- Git
- Vercel CLI

### 主要套件
```python
# requirements.txt
requests==2.31.0
beautifulsoup4==4.12.3
selenium==4.18.1
Pillow==10.2.0
schedule==1.2.0
python-dotenv==1.0.0
```

### 環境變數
```bash
# .env
GITHUB_TOKEN=ghp_xxx
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=xxx
SMTP_PASS=xxx
```

### 檔案結構
```
taiwan-venues-new/
├── auto_verification_engine.py    # 資料驗證引擎
├── auto_correction_system.py      # 資料修正系統
├── auto_sync_system.py            # 自動同步系統
├── photo_downloader.py            # 照片下載器
├── data_validator.py              # 資料驗證器
├── venue_crawler.py               # 場地爬蟲
├── config.py                      # 配置檔
├── logs/                          # 日誌目錄
│   ├── verification.log
│   ├── correction.log
│   └── sync.log
├── temp/                          # 暫存目錄
│   └── photos/
└── reports/                       # 報告目錄
    ├── daily/
    └── weekly/
```

---

## 📊 監控與報告

### 每日報告
- 驗證場地數量
- 發現錯誤數量
- 自動修正數量
- 部署次數

### 每週報告
- 資料完整度統計
- 系統運行狀況
- 用戶反饋統計
- 改進建議

### 即時告警
- 系統錯誤
- 部署失敗
- 資料異常
- 照片失效

---

## 🚀 立即執行

### 當前狀態
- ✅ 計畫已制定
- 🟢 立即開始開發
- ⏱️ 預計第 1 週完成自動化系統

### 下一步行動
1. **Jobs**: 開發 `auto_verification_engine.py`
2. **Jobs**: 開發 `auto_correction_system.py`
3. **Jobs**: 開發 `auto_sync_system.py`
4. **Jane**: 監控進度，調整計畫

---

**最後更新**: 2026-03-17 07:31  
**狀態**: 🟢 執行中  
**負責人**: Jane (Global CEO)
