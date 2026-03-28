# 技術棧決策文檔

**制定日期**: 2026-04-01
**決策者**: Jobs (CTO)
**審核者**: Jane (CEO)

---

## 📋 決策總結

| 技術層 | 選擇 | 理由 |
|--------|------|------|
| **後端框架** | FastAPI (Python 3.11+) | AI生態整合、快速開發、自動API文檔 |
| **資料庫** | PostgreSQL 15 | 關聯式資料、JSON支援、可靠性高 |
| **ORM** | SQLAlchemy 2.0 | 成熟、與FastAPI整合良好 |
| **快取** | Redis 7 | 高效能、資料結構豐富 |
| **前端** | Next.js 14 + Tailwind CSS | React生態、SEO友好、快速開發 |
| **部署** | Vercel (前端) + AWS EC2 (後端) | Vercel免費、AWS穩定 |
| **容器化** | Docker + Docker Compose | 開發環境一致性 |
| **CI/CD** | GitHub Actions | 與GitHub整合、免費 |
| **監控** | Prometheus + Grafana | 開源、強大 |

---

## 1. 後端框架：FastAPI vs Express.js

### 選擇：**FastAPI (Python 3.11+)**

### ✅ 優勢

1. **AI生態整合**
   - Python是AI/ML的標準語言
   - 易於整合OpenAI、Anthropic SDK
   - 未來可擴展到AI模型訓練

2. **開發效率**
   - 自動生成OpenAPI文檔
   - 型別提示（Type Hints）減少錯誤
   - 異步支持（async/await）

3. **效能**
   - 比Flask快2-3倍
   - 與Node.js（Express.js）相當
   - 支援WebSocket

4. **資料驗證**
   - Pydantic自動驗證
   - 自動生成API文檔
   - 減少样板代碼

### ❌ Express.js的劣勢

1. JavaScript型別系統較弱
2. 需要手動撰寫API文檔
3. 與AI生態整合較複雜

### 📊 效能比較

| 指標 | FastAPI | Express.js |
|------|---------|-----------|
| 簡單請求 | ~15ms | ~10ms |
| 複雜查詢 | ~50ms | ~45ms |
| 記憶體使用 | 50MB | 40MB |
| 開發速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 🎯 決策理由

**FastAPI勝出**，因為：
1. AI生態整合（最重要）
2. 自動API文檔節省時間
3. 型別安全減少bug
4. 與現有Python腳本（quality_gate.py等）兼容

---

## 2. 資料庫：PostgreSQL vs MongoDB

### 選擇：**PostgreSQL 15**

### ✅ 優勢

1. **關聯式資料模型**
   - 場地、會議室、可用性有明確關聯
   - 外鍵約束確保資料一致性
   - JOIN查詢效率高

2. **JSON支援**
   - JSONB欄位存儲隱藏知識
   - 關聯式 + 文檔型混合
   - 靈活性與一致性兼顧

3. **可靠性**
   - ACID事務
   - 成熟的備份與還原
   - 企業級穩定性

4. **搜尋能力**
   - 全文搜尋（Full-Text Search）
   - 地理位置查詢（PostGIS）
   - 複雜索引

### ❌ MongoDB的劣勢

1. 無事務支援（MongoDB 4.0後才有，但不成熟）
2. 資料一致性較弱
3. JOIN查詢效能差
4. 運維成本高

### 📊 資料模型比較

**PostgreSQL Schema**:
```sql
venues (id, name, city, address, ...)
  ├── meeting_rooms (id, venue_id, name, capacity, ...)
  ├── availability (id, venue_id, date, status, ...)
  └── hidden_knowledge (id, venue_id, knowledge_type, content, ...)
```

**MongoDB Schema**:
```javascript
venues: [
  {
    _id: ObjectId,
    name: "...",
    meeting_rooms: [...],  // 嵌入文檔
    availability: [...],    // 嵌入文檔
    hidden_knowledge: {...} // 嵌入文檔
  }
]
```

### 🎯 決策理由

**PostgreSQL勝出**，因為：
1. 場地資料有明確關聯關係
2. JSONB支援靈活性
3. 事務確保資料一致性
4. 全文搜尋支援智能搜尋

---

## 3. 快取層：Redis vs Memcached

### 選擇：**Redis 7**

### ✅ 優勢

1. **資料結構豐富**
   - String: 簡單快取
   - Hash: 場地物件
   - List: 場地列表
   - Set: 標籤、設備
   - Sorted Set: 排行榜、推薦

2. **持久化**
   - RDB快照
   - AOF日誌
   - 重啟後資料不丟失

3. **功能豐富**
   - 發布/訂閱（即時可用性更新）
   - 事務
   - Lua腳本

### ❌ Memcached的劣勢

1. 只支援String
2. 無持久化
3. 功能較少

### 🎯 決策理由

**Redis勝出**，因為：
1. 未來需要發布/訂閱（即時可用性）
2. 豐富的資料結構
3. 持久化確保快取穩定性

---

## 4. 部署平台：AWS vs GCP vs Azure

### 選擇：**混合部署**
- **前端**: Vercel
- **後端**: AWS EC2

### ✅ 優勢

**Vercel（前端）**:
- 免費額度（100GB bandwidth）
- 自動HTTPS
- CDN全球分發
- Zero-conf deployment

**AWS（後端）:
- 成熟穩定
- 豐富的服務（RDS、ElastiCache）
- 台灣區域（ap-northeast-1）
- 按需付費

### 📊 成本比較

| 平台 | 月度成本 | 備註 |
|------|----------|------|
| Vercel | $0 (免費) | 前端部署 |
| AWS EC2 (t3.medium) | $30 | 後端API |
| AWS RDS PostgreSQL | $50 | 資料庫 |
| AWS ElastiCache Redis | $25 | 快取 |
| **總計** | **$105/月** | |

### ❌ GCP/Azure的劣勢

1. 台灣節點較少
2. 文檔較少
3. 社群較小

### 🎯 決策理由

**Vercel + AWS混合部署**，因為：
1. Vercel免費部署前端
2. AWS成熟穩定
3. 成本可控（初期<200USD/月）
4. 未來可擴展

---

## 5. 前端框架：React vs Vue.js

### 選擇：**Next.js 14 (React)**

### ✅ 優勢

1. **SEO友好**
   - Server-Side Rendering (SSR)
   - Static Site Generation (SSG)
   - 開發者門戶需要SEO

2. **開發者體驗**
   - App Router（RSC支援）
   - Server Actions（API routes）
   - TypeScript支援

3. **生態系**
   - Tailwind CSS整合
   - 大量組件庫
   - 社群活躍

4. **部署簡單**
   - Vercel一鍵部署
   - 自動優化

### ❌ Vue.js的劣勢

1. SEO支援較弱（需Nuxt.js）
2. 台灣開發者較少
3. 就業市場較小

### 🎯 決策理由

**Next.js勝出**，因為：
1. SEO對開發者門戶重要
2. 與Vercel完美整合
3. 台灣React開發者多
4. 未來招聘容易

---

## 6. 容器化：Docker

### 選擇：**Docker + Docker Compose**

### ✅ 優勢

1. **環境一致性**
   - 開發環境 = 生產環境
   - 消除"在我機器上能跑"問題

2. **快速啟動**
   - 一個命令啟動所有服務
   - `docker-compose up`

3. **隔離性**
   - 後端、資料庫、Redis獨立容器
   - 避免版本衝突

### Docker Compose配置

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/eventmaster
      - REDIS_URL=redis://redis:6379/0

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=eventmaster

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 7. CI/CD：GitHub Actions

### 選擇：**GitHub Actions**

### ✅ 優勢

1. **與GitHub整合**
   - 無需額外設定
   - 免費（公開repo）

2. **YAML配置**
   - 簡單易懂
   - 豐富的actions

3. **自動化**
   - 自動測試
   - 自動部署
   - 自動通知

### Workflow範例

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to AWS
        run: |
          # 部署腳本
```

---

## 8. 監控：Prometheus + Grafana

### 選擇：**Prometheus + Grafana**

### ✅ 優勢

1. **開源免費**
2. **強大的查詢語言（PromQL）**
3. **豐富的可視化**
4. **警報系統**

### 監控指標

```python
# API回應時間
histogram = Histogram('api_response_time_ms', 'API response time', ['endpoint'])

# 請求計數
counter = Counter('api_requests_total', 'Total API requests', ['endpoint', 'status'])

# 錯誤率
gauge = Gauge('api_error_rate', 'API error rate')
```

---

## 9. 開發工具

### IDE
- **VS Code**（免費、擴展豐富）

### 擴展
- Python
- Pylance
- Docker
- GitHub Copilot（AI輔助）

### API測試
- **Postman** 或 **Insomnia**
- **Bruno**（開源、輕量）

### 資料庫管理
- **pgAdmin** 或 **DBeaver**

---

## 📦 技術棧總結

```yaml
Backend:
  框架: FastAPI 0.104+
  語言: Python 3.11+
  ORM: SQLAlchemy 2.0
  資料驗證: Pydantic v2

Database:
  主資料庫: PostgreSQL 15
  快取: Redis 7
  ORM: SQLAlchemy 2.0

Frontend:
  框架: Next.js 14 (App Router)
  樣式: Tailwind CSS 3
  語言: TypeScript 5

DevOps:
  容器化: Docker 24+
  部署: Vercel (前端) + AWS EC2 (後端)
  CI/CD: GitHub Actions

Monitoring:
  指標: Prometheus
  可視化: Grafana
  日誌: Elasticsearch + Kibana (未來)
```

---

## 🎯 決策確認

所有技術棧決策已確認，將於W1 Day 5-6建立開發環境。

**如有異議，請在W1 Day 5（4/5）前提出。**

---

**文檔所有者**: Jobs (CTO)
**制定日期**: 2026-04-01
**下次審閱**: W1 Day 7 (2026-04-07)
**版本**: 1.0 (Final)
