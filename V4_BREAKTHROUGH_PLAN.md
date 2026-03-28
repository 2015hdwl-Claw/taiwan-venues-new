# V4 突破無頁面場地方案

## 📊 現狀分析

### V4 當前使用技術
- ✅ **Scrapling Fetcher** (已使用)
  - `Fetcher.get(url, impersonate='chrome', timeout=15)`
  - 模擬Chrome瀏覽器，繞過基本反爬蟲
- ❌ **StealthyFetcher** (已import但未使用)
  - 可處理更複雜的反爬蟲機制
  - 支援JavaScript渲染（部分）

### 無頁面場地分類 (31個)

| 類型 | 數量 | 原因 | 突破方案 |
|------|------|------|----------|
| **URL重定向** | ~8 | 國際酒店品牌重定向到品牌頁 | 處理Redirect + 修改URL |
| **JS渲染** | ~5 | 需要執行JavaScript才能看到內容 | StealthyFetcher + Playwright |
| **404錯誤** | 5 | meeting.com.tw 子域名失效 | 更新URL或標記discontinued |
| **網站結構特殊** | ~13 | 導航列不是標準 `<nav>` | 改進HTML解析 |

## 🚀 突破方案

### 方案 1: 處理 URL 重定向 (優先)
**問題**: 國際酒店重定向到品牌頁
**影響**: citizenM, Sheraton, Marriott, Regent等

**解決方案**:
```python
# 1. 檢測重定向
response = Fetcher.get(url, impersonate='chrome', timeout=15, follow_redirects=True)
if response.url != url:
    print(f"Redirect detected: {url} -> {response.url}")

# 2. 修正URL
# citizenM: 使用正確的酒店頁面
# Sheraton: 找到具體酒店頁面而非品牌頁
```

### 方案 2: 使用 StealthyFetcher
**問題**: 高級反爬蟲機制
**影響**: 部分國際酒店

**解決方案**:
```python
from scrapling.fetchers import StealthyFetcher

# StealthyFetcher 使用方式
fetcher = StealthyFetcher()
response = fetcher.fetch(url, timeout=20)  # 注意是 .fetch() 不是 .get()
```

### 方案 3: Playwright 完整 JS 渲染
**問題**: 大量 JavaScript 渲染
**影響**: 現代化酒店網站

**解決方案**:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle')
    html = page.content()
    # 正常解析 HTML
```

### 方案 4: 智能 URL 修正
**問題**: meeting.com.tw 子域名404
**影響**: 5個集思場地

**解決方案**:
```python
# 檢查子域名是否存在
# 不存在則使用主域名 meeting.com.tw
broken_subdomains = {
    1495: 'https://www.meeting.com.tw/',  # 原: /tech/
    1496: 'https://www.meeting.com.tw/',  # 原: /hsph/
    # ...
}
```

## 🛠️ 實作建議

### 階段 1: 快速修復 (1-2天)
1. **修復 URL 重定向處理**
2. **更新 meeting.com.tw 404 場地**
3. **改進 HTML 解析器** (支援多種導航結構)

### 階段 2: 中期突破 (3-5天)
1. **整合 StealthyFetcher**
2. **增加 URL 自動修正**
3. **手動修復高價值場地** (五星酒店)

### 階段 3: 長期方案 (1週)
1. **Playwright 整合** (處理複雜JS)
2. **智能重試機制**
3. **人工驗證流程**

## 📊 預期效果

| 方案 | 預期突破場地 | 成功率 | 開發時間 |
|------|--------------|--------|----------|
| 修復重定向 | 5-8 | 80% | 1天 |
| StealthyFetcher | 3-5 | 60% | 2天 |
| Playwright | 8-12 | 90% | 3天 |
| URL修正 | 5 | 100% | 1小時 |

## 🎯 建議優先順序

1. **立即執行**: URL修正 (meeting.com.tw 404問題)
2. **高優先**: 修復重定向處理
3. **中優先**: 整合StealthyFetcher
4. **長期考慮**: Playwright完整方案
