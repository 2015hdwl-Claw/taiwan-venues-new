# EventMaster API 專案結構

**建立日期**: 2026-04-01
**用途**: Phase 1 開發專案結構規劃

---

## Repository 結構

```
eventmaster-api/
├── backend/                 # 後端API
│   ├── app/                # 應用程式代碼
│   │   ├── api/           # API端點
│   │   ├── models/        # 資料模型
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # 業務邏輯
│   │   └── middleware/    # 中介軟體
│   ├── tests/             # 測試
│   ├── migrations/        # 資料庫遷移
│   ├── requirements.txt   # Python依賴
│   └── main.py           # 應用程式入口
│
├── frontend/              # 開發者門戶
│   ├── src/
│   │   ├── pages/        # 頁面
│   │   ├── components/   # 組件
│   │   └── styles/       # 樣式
│   ├── public/           # 靜態資源
│   └── package.json
│
├── database/             # 資料庫腳本
│   ├── schema.sql       # 資料庫Schema
│   ├── seeds/           # 種子資料
│   └── migrations/      # 遷移腳本
│
├── docs/                # API文檔
│   ├── api-reference.md # API參考
│   ├── quick-start.md   # 快速開始
│   └── examples/        # 範例代碼
│
├── deploy/              # 部署腳本
│   ├── docker/         # Docker配置
│   ├── k8s/            # Kubernetes配置
│   └── terraform/      # 基礎設施代碼
│
├── scripts/            # 工具腳本
│   ├── seed_db.py     # 資料庫種子腳本
│   ├── migrate.py     # 遷移腳本
│   └── test_api.py    # API測試腳本
│
├── .github/           # GitHub配置
│   └── workflows/     # GitHub Actions
│
├── .env.example       # 環境變數範例
├── docker-compose.yml # Docker Compose配置
├── README.md          # 專案說明
└── LICENSE            # 授權
```

---

## 當前目錄結構（本地開發）

```
taiwan-venues-new/
├── venues.json                    # 現有場地資料（52個）
├── quality_gate.py               # 品質閘門
├── auto_verification_engine.py  # 自動驗證引擎
│
├── docs/                         # 計畫文檔
│   ├── VISION_AND_STRATEGY.md
│   ├── PHASE1_PROJECT_PLAN.md
│   ├── BUSINESS_PLAN.md
│   ├── W1_W2_ACTION_PLAN.md
│   └── PROJECT_KICKOFF_MEETING.md
│
├── reports/                      # 品質報告
│   ├── FIX_REPORT.md
│   └── quality_issues_report.json
│
└── [現有爬蟲腳本...]             # 暫時保留
```

---

## Phase 1 新增目錄（W1建立）

```
taiwan-venues-new/
├── eventmaster-api/              # 新建：API專案
│   ├── backend/
│   ├── frontend/
│   └── docs/
│
├── database-design/              # 新建：資料庫設計
│   ├── schema.md
│   ├── relationships.md
│   └── migrations/
│
└── communication/                # 新建：對外溝通
    ├── venue-proposal.md         # 場地合作提案
    ├── early-adopter.md          # 早期採用者計畫
    └── press-release.md          # 新聞稿
```

---

## 檔案命名規範

### 文檔文件
- 使用大寫底線：`VISION_AND_STRATEGY.md`
- 會議紀錄：`MEETING_YYYY-MM-DD.md`
- 週報：`WEEKLY_W{N}.md`

### 代碼文件
- Python: snake_case：`venue_service.py`
- JavaScript: camelCase：`venueService.js`
- 組件: PascalCase：`VenueCard.jsx`

### 資料文件
- JSON: kebab-case：`venue-data.json`
- 資料庫: snake_case：`venue_details`

---

## Git 分支策略

### 主要分支
- `main` - 生產環境
- `dev` - 開發環境

### 功能分支
- `feature/api-venues` - 場地API功能
- `feature/developer-portal` - 開發者門戶
- `feature/auth` - 認證功能
- `bugfix/xxx` - 錯誤修復

### 分支命名規範
```
feature/<功能名稱>
bugfix/<錯誤描述>
hotfix/<緊急修復>
release/<版本號>
```

---

## 環境變數配置

### .env.example
```bash
# 應用程式
APP_NAME=EventMaster API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# 資料庫
DATABASE_URL=postgresql://user:password@localhost:5432/eventmaster
REDIS_URL=redis://localhost:6379/0

# API認證
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# 外部服務
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# 部署
VERCEL_TOKEN=xxx
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

---

**文檔所有者**: Jobs (CTO)
**建立日期**: 2026-04-01
**下次更新**: W1 Day 3（實際建立目錄後）
