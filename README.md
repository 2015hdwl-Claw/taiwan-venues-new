# 活動大師 EventMaster B2B

**企業場地選擇的風險管理專家**

> 80%的企業因選錯場地損失超過NT$100,000 - 我們幫您避免這些風險

## 🎯 B2B 企業服務

### 目標客戶
- **公關/活動公司**: 提升客戶滿意度，降低風險
- **企業行銷團隊**: 快速找到符合品牌形象的專業場地
- **活動策劃師**: 獲取專業場地知識庫和風險評估工具

### 核心價值
- ⚠️ **風險評估**: 識別場地隱藏限制（噪音、場地高度、進場時間等）
- 📊 **專業知識**: 80個精選場地的完整資訊庫
- 💡 **企業服務**: 對接專業場地顧問，提供定制化諮詢

## 功能特色

✨ **快速搜尋**: 關鍵字搜尋場地名稱、地址
📍 **地區篩選**: 22 縣市場地完整收錄
🏢 **類型分類**: 飯店、會議中心、展演場地等
👥 **人數篩選**: 依容納人數快速找到合適場地
💰 **預算篩選**: 符合預算的場地推薦
📱 **響應式設計**: 支援手機、平板、桌面
🏢 **企業洽詢**: 專業企業服務申請
📝 **反饋系統**: 收集用戶需求與建議

## 技術架構

- **前端**: 純 HTML + CSS + JavaScript (無框架)
- **數據**: 靜態 JSON 文件
- **部署**: Vercel 靜態網站託管

## 檔案結構

```
/
├── index.html      # 主頁面
├── style.css       # 樣式表
├── app.js          # 應用邏輯
├── venues.json     # 場地資料 (371 筆)
├── vercel.json     # Vercel 配置
└── README.md       # 說明文件
```

## 本地開發

```bash
# 安裝 Python (用於本地伺服器)
python3 -m http.server 8080

# 或使用 Node.js
npx serve .
```

## 部署到 Vercel

### 方案一：GitHub Actions 自動部署（推薦）

#### 1. 獲取 Vercel 憑證
```bash
# 登入 Vercel
vercel login

# 創建 token
vercel tokens create
```

#### 2. 設置 GitHub Secrets
前往 GitHub 倉庫設置：
```
https://github.com/[你的用戶名]/taiwan-venues-new/settings/secrets/actions
```

添加三個 secrets：
- `VERCEL_TOKEN`: [步驟1獲取的token]
- `VERCEL_ORG_ID`: `team_bEVp3hy4mKo0yPojpBFOPhPA`
- `VERCEL_PROJECT_ID`: `prj_P77DQj4nniLgZgLM6g4ENFnoSiCD`

#### 3. 推送觸發部署
```bash
git add .
git commit -m "Update B2B content"
git push origin main
```
✅ 每次推送到 main 分支都會自動部署！

### 方案二：快速部署腳本
```bash
# 核心文件部署（58KB vs 125MB）
./deploy-core.sh

# 完整部署（含 git commit）
./deploy.sh
```

### 方案三：Vercel CLI 手動部署
```bash
# 安裝 Vercel CLI
npm i -g vercel

# 部署到生產環境
vercel --prod
```

## 測試狀態

### ✅ 已測試功能
- [x] B2B 內容顯示正確
- [x] 企業洽詢表單提交成功
- [x] 用戶反饋表單提交成功
- [x] localStorage 數據保存正常
- [x] 本地測試環境運行正常

### 📊 測試數據樣本
```json
// 企業洽詢
{
  "type": "pr",
  "companyName": "測試公司股份有限公司",
  "email": "test@company.com",
  "timestamp": "2026-03-28T03:07:08.823Z"
}

// 用戶反饋
{
  "profession": "pr",
  "frequency": "4-10",
  "concerns": "最關心場地的隱藏限制和風險評估資訊",
  "timestamp": "2026-03-28T03:08:02.165Z"
}
```

## 數據統計

- **總場地數**: 80 個（精選 B2B 場地）
- **縣市覆蓋**: 6 縣市（台北市、台中市、高雄市、新北市、新竹市）
- **場地類型**: 8 種類型（飯店、會議中心、展演、運動、婚宴、會展、展覽）
- **熱門地區**: 台北市 🔥、台中市 🔥、高雄市 🔥
- **熱門類型**: 飯店場地 🔥、會議中心 🔥

## 部署狀態

- **生產網站**: https://taiwan-venues-new.vercel.app
- **本地測試**: http://localhost:8888
- **最後更新**: 2026-03-28
- **當前版本**: B2B MVP v1.0

## 下一步計劃

### 第 1 週：市場測試
- 在 LinkedIn 發布貼文測試 B2B 受眾反應
- 聯繫 10 家目標企業
- 收集用戶反饋

### 第 2 週：優化疊代
- 根據反饋優化內容
- 調整 CTA 按鈕位置
- 測試不同的價值主張

### 監控指標
- **企業用戶比例** > 60%
- **反饋表單填寫率** > 10%
- **企業洽詢轉化率** > 5%

## 授權

© 2026 活動大師 EventMaster. All rights reserved.
