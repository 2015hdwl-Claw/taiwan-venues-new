# 活動大師 EventMaster

台灣活動場地查詢平台 - 371 個優質場地即時查詢

## 功能特色

✨ **快速搜尋**: 關鍵字搜尋場地名稱、地址
📍 **地區篩選**: 22 縣市場地完整收錄
🏢 **類型分類**: 飯店、會議中心、展演場地等
👥 **人數篩選**: 依容納人數快速找到合適場地
💰 **預算篩選**: 符合預算的場地推薦
📱 **響應式設計**: 支援手機、平板、桌面

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

```bash
# 安裝 Vercel CLI
npm i -g vercel

# 部署
vercel --prod
```

## 數據統計

- **總場地數**: 371 個
- **縣市覆蓋**: 22 縣市
- **場地類型**: 12 種類型
- **台北市**: 135 個 (最多)
- **飯店場地**: 178 個 (最多)

## 授權

© 2026 活動大師 EventMaster. All rights reserved.
