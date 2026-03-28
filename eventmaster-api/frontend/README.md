# EventMaster Developer Portal

AI 時代的活動場地智能接口 - 開發者入口網站

## 技術棧

- **框架**: Next.js 14 (Pages Router)
- **UI 庫**: React 18.2
- **樣式**: Tailwind CSS 3.3
- **執行環境**: Node.js 18+

## 安裝與執行

### 1. 安裝依賴

```bash
npm install
```

### 2. 設定環境變數（選用）

創建 `.env.local` 檔案：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. 執行開發伺服器

```bash
npm run dev
```

開啟瀏覽器訪問 [http://localhost:3000](http://localhost:3000)

### 4. 建置生產版本

```bash
npm run build
npm start
```

## 專案結構

```
frontend/
├── src/
│   ├── pages/
│   │   ├── index.js          # 首頁
│   │   ├── register.js       # API Key 註冊頁
│   │   ├── docs.js           # API 文檔
│   │   └── _app.js           # App wrapper
│   └── styles/
│       └── globals.css       # 全域樣式
├── public/                   # 靜態資源
├── package.json
├── next.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 頁面說明

### 首頁 (`/`)
- 介紹 EventMaster API 的核心價值
- 展示主要功能特性
- API 端點快速概覽
- CTA 導向註冊和文檔

### 註冊頁 (`/register`)
- API Key 申請表單
- 即時表單驗證
- 註冊成功後顯示 API Key
- 安全提示與使用說明

### 文檔頁 (`/docs`)
- 快速開始指南
- 完整 API 端點參考
- 認證方式說明
- 回應格式規範
- 錯誤代碼對照表

## API 整合

所有前端頁面都會與後端 API 通信：

```
Backend: http://localhost:8000
Frontend: http://localhost:3000
```

**重要**: 確保後端服務已啟動再執行前端。

### CORS 設定

後端需要允許來自 `http://localhost:3000` 的請求。已在 FastAPI 中設定 CORS middleware。

## 部署

### Vercel (推薦)

1. 將程式碼推送到 GitHub
2. 在 [Vercel](https://vercel.com) 匯入專案
3. 設定環境變數 `NEXT_PUBLIC_API_URL` 為生產 API URL
4. 自動部署完成

### Docker

```bash
docker build -t eventmaster-frontend .
docker run -p 3000:3000 eventmaster-frontend
```

## 開發指南

### 添加新頁面

在 `src/pages/` 目錄下創建 `.js` 檔案：

```javascript
import Link from 'next/link'

export default function NewPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 頁面內容 */}
    </div>
  )
}
```

### 樣式最佳實踐

- 使用 Tailwind utility classes
- 響應式設計：`sm:`, `md:`, `lg:`, `xl:`
- 自訂顏色使用 `tailwind.config.js` 中定義的顏色
- 保持一致的間距：`p-4`, `p-6`, `p-8`

### 組件重用

提取可重用組件到 `src/components/` 目錄：

```javascript
// src/components/Button.js
export default function Button({ children, onClick, variant = 'primary' }) {
  const baseClasses = 'px-6 py-3 rounded-lg font-semibold'
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-white text-blue-600 border-2 border-blue-600'
  }

  return (
    <button className={`${baseClasses} ${variantClasses[variant]}`} onClick={onClick}>
      {children}
    </button>
  )
}
```

## 故障排除

### `Module not found: Can't resolve '../styles/globals.css'`

確保 `src/styles/globals.css` 檔案存在。

### API 請求失敗

1. 檢查後端服務是否運行：`curl http://localhost:8000/health`
2. 確認 CORS 設定正確
3. 查看瀏覽器 DevTools Network 標籤

### Tailwind 樣式不生效

1. 確認 `tailwind.config.js` content 路徑正確
2. 檢查 `globals.css` 包含 Tailwind directives
3. 重新啟動開發伺服器

## 相關文檔

- [Next.js 文檔](https://nextjs.org/docs)
- [Tailwind CSS 文檔](https://tailwindcss.com/docs)
- [後端 API 文檔](../backend/README.md)

## 授權

© 2026 EventMaster. All rights reserved.
