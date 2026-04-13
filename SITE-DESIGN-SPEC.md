# 活動大師 Activity Master - 完整網站設計規格

> 供 Google Stitch 網頁設計使用
> 網站 URL: https://taiwan-venues-new-indol.vercel.app/
> 技術棧: 純靜態 HTML + Tailwind CSS (CDN) + Vanilla JS, 無框架
> 語言: 繁體中文 (zh-TW)

---

## 1. 全站設計系統

### 1.1 色彩系統 (Material Design 3 Teal 主題)

| Token | Hex | 用途 |
|-------|-----|------|
| primary | #0d9488 (teal-600) | 主按鈕、連結、重點圖示、品牌色 |
| primary-container | #008378 | 次級容器背景 |
| on-primary | #ffffff | 主色上的文字 |
| surface | #f8f9fd | 頁面背景（微灰藍白） |
| on-surface | #191c1f | 主文字色（深灰黑） |
| on-surface-variant | #3d4947 | 次要文字（中灰） |
| surface-container-low | #f2f3f8 | 區塊背景 |
| surface-container-lowest | #ffffff | 卡片背景（純白） |
| surface-container-high | #e7e8ec | 邊框色、分隔線 |
| surface-container | #eceef2 | 一般容器背景 |
| error | #ba1a1a | 錯誤紅 |
| error-container | #ffdad6 | 錯誤背景（淺紅） |
| brand-teal | #0d9488 | 品牌青綠 |
| brand-teal-hover | #0f766e | Hover 狀態 |
| brand-teal-surface | #f0fdfa | 淡青綠背景 |
| inverse-surface | #191c1f | 深色區塊（CTA, Footer）文字白 |

### 1.2 字型

| 用途 | 字型 | 備註 |
|------|------|------|
| Headline (標題) | Space Grotesk | 幾何無襯線，用於 H1-H3、導航、品牌名 |
| Body (內文) | Inter | 清晰無襯線，用於段落、說明文字 |

### 1.3 圓角系統

| Token | 值 | 用途 |
|-------|-----|------|
| DEFAULT | 1rem (16px) | 一般卡片 |
| lg | 2rem (32px) | 大型面板 |
| xl | 3rem (48px) | 特大區塊 |
| full | 9999px | 按鈕、標籤、輸入框 |

### 1.4 圖示系統

- Google Material Symbols Outlined
- 使用: span.material-symbols-outlined > icon_name
- 設定: font-variation-settings FILL 0, wght 400, GRAD 0, opsz 24

### 1.5 共用 UI 元件

#### 按鈕
- Primary: bg-primary text-on-primary rounded-full px-6 py-4 hover:bg-brand-teal-hover
- Secondary: border-2 border-primary text-primary rounded-full px-6 py-4 hover:bg-primary/5
- Small Pill: border border-outline-variant rounded-full px-5 py-3 text-sm

#### 卡片
- bg-surface-container-lowest rounded-xl border border-surface-container-high p-6
- Hover: hover:border-primary/30 hover:shadow-lg

#### 手風琴 (Accordion)
- details + summary 原生 HTML
- 背景: bg-surface-container-low rounded-xl border border-surface-container-high
- 箭頭圖示: expand_more + CSS group-open:rotate-180

---

## 2. 頁面清單與網址結構

- /                              -> 首頁 (index.html)
- /venue?id={id}                 -> 場地動態頁 (venue.html + venue.js)
- /room?id={id}                  -> 會議室動態頁 (room.html + room.js)
- /knowledge                     -> 知識庫/FAQ頁 (knowledge.html)
- /venues/{id}                   -> 場地預渲染靜態頁 x48
- /taipei-event-venue            -> 台北城市頁
- /new-taipei-event-venue        -> 新北城市頁
- /taichung-event-venue          -> 台中城市頁
- /small-event-venue             -> 小型場地分類頁
- /seminar-venue                 -> 講座場地分類頁
- /meeting-room-rental           -> 會議室租借分類頁
- /blog                          -> Blog 索引頁
- /blog/taipei-top-10-venues     -> Blog 文章頁 x5
- /faq                           -> FAQ 索引頁
- /faq/venue-catering-rules      -> FAQ 頁 x4

---

## 3. 各頁面詳細設計規格

### 3.1 首頁 / (index.html)

#### 導航列 (Sticky Top Nav)
- 背景: bg-white/80 backdrop-blur-xl sticky top-0 z-50
- 高度: py-4, px-8
- 左側: 品牌名「活動大師 Activity Master」(text-2xl, font-bold, text-teal-700)
- 中間導航連結 (hidden md:flex gap-8):
  - 「場地列表」(active: text-teal-600, border-b-2 border-teal-600)
  - 「關於我們」(text-neutral-600)
  - 「Blog」(text-neutral-600)
- 右側: 「AI 助理」按鈕 (圓角膠囊, border-teal-600)

#### Hero Section
- 背景: bg-surface, py-24 md:py-40
- H1: 「找場地，不再踩坑」(font-size 136px 桌面/64px 平板)
- 副標: 「活動企劃的場地知識庫 / 官網沒寫的潛規則，我們幫你整理好了」
- 雙按鈕: 「開始搜尋」(Primary 實心) / 「問 AI 助理」(Secondary 外框)

#### 痛點區塊 (Pain Points)
- 背景: bg-surface-container-low
- 標題: 「你是不是也遇過這些問題？」(text-4xl md:text-5xl, 居中)
- 三欄 grid (md:grid-cols-3 gap-8):
  - 白色圓角卡片 (bg-surface-container-lowest rounded-xl p-12)
  - 每張有 64x64 圖示容器 (bg-error-container rounded-2xl) + Material icon
  - 1: block - 隱藏的場地限制
  - 2: payments - 價格資訊不透明
  - 3: forum - 溝通效率低下

#### SEO 內容區塊
- 背景: bg-surface, max-w-4xl mx-auto
- About: 300字平台介紹
- 城市入口 (grid 2x2): 台北23/新北10/台中7/其他8
- 分類入口 (grid 1x3): 小型10-30人/講座20-80人/會議商務
- FAQ 手風琴: 4個問答

#### 場地列表區塊
- 標題: 「台北精選場地」+ 數量計數
- 篩選列: 搜尋框 + 3下拉(縣市/類型/人數) + 清除按鈕
- 場地卡片 Grid (1/2/4欄): 圖片+名+類型+城市+人數+價格

#### 目標用戶: 四欄圓形圖示 (企業公關/行銷顧問/婚禮顧問/社群策展人)

#### 深色 CTA: bg-[#191c1f], 超大裝飾文字, 白色標題, Primary按鈕

#### 頁尾: bg-[#191c1f], 品牌名+版權+導航連結

---

### 3.2 場地詳情頁 /venue?id={id}

JS 動態渲染, 從 venues.json 抓取

- 導航列: 同首頁, 右側AI助理(實心綠色)
- Loading: 旋轉動畫 / Error: 警告圖示+返回按鈕
- Hero (兩欄 8+4): 左側主圖600px+浮動標籤 / 右側資訊面板(地址/數量/容納/價格/時段/設備) + 按鈕(查看會議室/問AI) + 分享(LINE/FB/複製) + 聯絡(電話/官網)
- 重要提醒: bg-error-container/30, 預約天數/旺季/常見問題
- 場地相簿: Grid (2/3/4欄)
- 會議室列表: Grid (1/2/3欄), 圖片+名稱+坪數+容納+價格
- 租借規定: gavel圖示, Grid(2欄)
- 省錢技巧: lightbulb圖示, bg-brand-teal-surface
- 聯絡資訊: Grid(2/4欄)
- 頁尾: 深色

---

### 3.3 會議室詳情頁 /room?id={id}

- 導航列: 同上, 右側"Login"外框
- 麵包屑: 首頁 > 場地名 > 會議室名
- Hero (兩欄1/2): 圖片(4:3) / badge+名稱+位置+按鈕列
- 快速資訊 Grid 4欄: 面積/容納/天花板/樓層
- 容納人數 4欄: 劇院/課桌/U型/宴會 (emoji+人數)
- 價格方案 3欄: 半天/全天(強調)/超時
- 設備清單 / 空間特色(tags) / 隱藏限制 / 進場資訊
- AI CTA: bg-brand-teal-surface
- 頁尾: 深色

---

### 3.4 知識庫 /knowledge
7個FAQ問答 (大型場地/天花板/隱藏費/價格/潛規則/尾牙/平台介紹)

### 3.5 場地靜態頁 /venues/{id} x48
靜態HTML含 title/meta/Schema/breadcrumb/介紹/優勢/注意事項/省錢技巧/交通/FAQ/CTA/會議室/E-E-A-T/OG

### 3.6 城市入口頁 x3
600-800字介紹+動態卡片+Top6精選+FAQ+E-E-A-T+CTA+內部連結

### 3.7 分類入口頁 x3
同城市頁結構, 依搜尋意圖分類

### 3.8 Blog索引 /blog
雙欄卡片grid (分類pill+日期+標題+摘要)

### 3.9 Blog文章 /blog/{slug} x5
麵包屑+標籤+日期+閱讀時間+H1+正文800-1200字+AI重點摘要+CTA+相關文章+E-E-A-T+Schema Article

### 3.10 FAQ索引 /faq
雙欄grid: 4張分類卡

### 3.11 FAQ分類 /faq/{slug} x4
麵包屑+H1+手風琴(4-5題)+CTA+相關FAQ+E-E-A-T

---

## 4. AI 聊天浮動視窗

### 浮動按鈕
- fixed bottom:32px right:32px, 64x64px圓形, bg-[#0d9488]
- 圖示: robot_2 白色28px
- Hover: scale(1.05)
- 未讀badge: 紅點20px

### 聊天視窗
- fixed bottom:112px right:32px, 380x560px(桌面)/100vw x 100vh(手機)
- 圓角24px, 動畫0.3s
- 結構:
  1. Header: teal背景, robot_2頭像+「活動企劃小幫手」+綠色脈衝+關閉
  2. 場地情境列: 淡綠, 「針對[場地名]提問」+清除 (僅場地頁)
  3. 訊息區域: surface背景, 4px scrollbar, 使用者靠右teal/AI靠左白色
  4. 快捷操作: pill按鈕(天花板高度/電力負載/詢問信)
  5. 輸入列: 圓角pill輸入框+teal圓形發送鈕
  6. 打字指示器: 三圓點彈跳

---

## 5. 導航關係

首頁
+-- 場地列表(同頁) / Blog(/blog) / 城市入口x3 / 分類入口x3
+-- 場地動態頁 -- 會議室頁
+-- 知識庫 / 場地靜態頁x48 / FAQ索引 -- FAQ分類x4
+-- AI聊天(浮動,全站)

---

## 6. 響應式

- Mobile(<768px): 單欄, 聊天全螢幕, 隱藏導航連結
- Tablet(768-1024px): 雙欄
- Desktop(>1024px): 四欄場地grid, 12欄hero grid

---

## 7. 動態資料

venues.json: 58筆場地, 每筆 id/name/venueType/city/address/images/rooms[]
rooms[]: id/name/floor/capacity{theater,classroom,ushape,banquet}/area/ceilingHeight/pricing/equipment/limitations
統計: 48 active, 台北23/新北10/台中7/高雄7/新竹1, 總會議室~370間

---

## 8. 第三方服務

| 服務 | 用途 |
|------|------|
| GA4 (G-YGTFFCFZHC) | 流量追蹤 |
| Google Search Console | SEO 索引 |
| Bing Webmaster Tools | Bing SEO |
| Tailwind CSS CDN | CSS 框架 |
| Google Fonts | Space Grotesk + Inter |
| Material Symbols | 圖示 |
| HuggingFace (bge-small-zh) | AI Embedding |
| Z.AI Anthropic (Claude Sonnet) | LLM |
| Vercel (cleanUrls) | 部署 |
