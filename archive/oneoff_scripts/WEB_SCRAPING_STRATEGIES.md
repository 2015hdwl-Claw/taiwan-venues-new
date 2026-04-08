# 不同網頁技術的擷取策略

## 🌐 網頁技術分類

### 1. 靜態網頁（Static HTML）
**特徵**：
- 純 HTML + CSS
- 內容直接在 HTML 源碼中
- 右鍵「檢視網頁原始碼」可以看到所有內容

**範例**：
- 傳統企業官網
- 政府機關網站
- 簡單的展示型網站

**擷取方式**：
```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
# 直接解析 HTML 即可
```

---

### 2. 伺服器端渲染（Server-Side Rendering, SSR）
**特徵**：
- 使用 PHP, Python, Ruby, Node.js 等後端語言
- 伺服器產生完整 HTML 後送給瀏覽器
- 右鍵「檢視網頁原始碼」可以看到所有內容

**範例**：
- WordPress 網站
- Django/Flask 網站
- Ruby on Rails 網站
- 傳統電商網站

**擷取方式**：
```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
# 與靜態網頁相同，直接解析 HTML
```

---

### 3. 客戶端渲染（Client-Side Rendering, CSR）
**特徵**：
- 使用 React, Vue, Angular, Ember.js 等前端框架
- HTML 源碼只有基本的 `<div id="root"></div>`
- 實際內容由 JavaScript 動態載入
- 右鍵「檢視網頁原始碼」**看不到**內容
- 需要在「開發者工具 > Elements」才能看到

**範例**：
- 現代單頁應用（SPA）
- Facebook, Instagram, Twitter
- 使用 Next.js, Nuxt.js 的網站

**擷取方式（3種）**：

#### 方式A：使用 Playwright（推薦）
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)

    # 等待 JavaScript 渲染完成
    page.wait_for_selector('.room-list')

    # 提取內容
    rooms = page.query_selector_all('.room')
    for room in rooms:
        name = room.query_selector('.name').text_content()

    browser.close()
```

#### 方式B：使用 Selenium
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get(url)

# 等待 JavaScript 渲染
driver.implicitly_wait(10)

# 提取內容
rooms = driver.find_elements(By.CLASS_NAME, 'room')
for room in rooms:
    name = room.find_element(By.CLASS_NAME, 'name').text

driver.quit()
```

#### 方式C：API 逆向（最乾淨）
```python
import requests

# 1. 開啟開發者工具 > Network
# 2. 重新整理頁面
# 3. 找到 XHR/Fetch 請求
# 4. 複製 API URL

api_url = "https://api.example.com/venues/123/rooms"
response = requests.get(api_url)
data = response.json()

# 直接使用 JSON 資料
for room in data['rooms']:
    print(room['name'], room['capacity'])
```

---

### 4. 混合式網頁（Hybrid）
**特徵**：
- 部分內容是靜態 HTML
- 部分內容由 JavaScript 動態載入
- 需要組合多種方法

**範例**：
- 電商網站（產品列表靜態，價格動態）
- 新聞網站（標題靜態，留言動態）

**擷取方式**：
```python
# 步驟1：用 requests + BeautifulSoup 提取靜態內容
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 提取靜態資料
venue_name = soup.find('h1').text

# 步驟2：用 Playwright 提取動態內容
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)

    # 提取動態載入的會議室資料
    rooms = page.query_selector_all('.room-dynamic')

    browser.close()
```

---

## 🔍 如何判斷網頁類型？

### 測試步驟

#### 步驟1：查看原始碼
```
1. 在網頁上右鍵 > 檢視網頁原始碼
2. 搜尋關鍵字（如會議室名稱）
```

**結果判斷**：
- ✅ 找到內容 → 靜態網頁或 SSR → 用 requests + BeautifulSoup
- ❌ 找不到內容 → CSR（JS渲染）→ 用 Playwright 或 API 逆向

#### 步驟2：查看開發者工具
```
1. 按 F12 開啟開發者工具
2. 切換到 Elements 標籤
3. 搜尋關鍵字
```

**結果判斷**：
- ✅ 在 Elements 中找到，但在原始碼找不到 → CSR
- ✅ 兩者都有 → 靜態或 SSR

#### 步驟3：檢查 Network 請求
```
1. 按 F12 > Network 標籤
2. 重新整理頁面
3. 查看 XHR/Fetch 請求
```

**結果判斷**：
- ✅ 看到 `/api/rooms` 之類的請求 → 可以直接調用 API（最乾淨）

---

## 🛠️ 完整擷取策略

### 策略1：自動判斷並選擇方法

```python
class UniversalVenueExtractor:
    def __init__(self):
        self.session = requests.Session()

    def extract_venue(self, url):
        """自動判斷並選擇擷取方法"""

        # 嘗試1：靜態/SSR 網頁（用 requests）
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 檢查是否有會議室資料
            if self._has_meeting_rooms(soup):
                print('✅ 靜態/SSR 網頁，使用 requests + BeautifulSoup')
                return self._extract_static(soup, url)
        except Exception as e:
            print(f'⚠️  靜態方法失敗: {e}')

        # 嘗試2：CSR 網頁（用 Playwright）
        try:
            print('🔄 嘗試使用 Playwright...')
            return self._extract_dynamic_playwright(url)
        except Exception as e:
            print(f'⚠️  Playwright 失敗: {e}')

        # 嘗試3：API 逆向
        try:
            print('🔄 嘗試 API 逆向...')
            return self._extract_api(url)
        except Exception as e:
            print(f'⚠️  API 逆向失敗: {e}')

        # 全部失敗
        return {'success': False, 'error': '無法擷取此網站'}

    def _has_meeting_rooms(self, soup):
        """檢查是否包含會議室資料"""
        # 檢查常見的會議室標識
        indicators = [
            soup.find_all(class_=re.compile(r'room|meeting|banquet', re.I)),
            soup.find_all(['h2', 'h3'], string=re.compile(r'會議|宴會|Meeting')),
        ]

        total_found = sum(len(items) for items in indicators)
        return total_found > 0

    def _extract_static(self, soup, url):
        """擷取靜態/SSR 網頁"""
        # 使用 BeautifulSoup 提取
        extractor = StaticExtractor()
        return extractor.extract(soup, url)

    def _extract_dynamic_playwright(self, url):
        """使用 Playwright 擷取動態網頁"""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle')

            # 等待會議室內容載入
            page.wait_for_selector('.room, .meeting-room', timeout=5000)

            # 提取 HTML
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            browser.close()

            # 使用相同的提取邏輯
            extractor = StaticExtractor()
            return extractor.extract(soup, url)

    def _extract_api(self, url):
        """嘗試 API 逆向"""
        # 常見的 API 路徑
        possible_apis = [
            f'{url}/api/rooms',
            f'{url}/api/venues/meeting-rooms',
            f'{url}/wp-json/wp/v2/rooms',  # WordPress
        ]

        for api_url in possible_apis:
            try:
                response = self.session.get(api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_api_response(data, api_url)
            except:
                continue

        raise Exception('找不到 API 端點')
```

### 策略2：三階段擷取流程

```python
class ThreeStageExtractor:
    """三階段擷取器"""

    def __init__(self):
        self.static_extractor = StaticExtractor()
        self.dynamic_extractor = PlaywrightExtractor()
        self.api_extractor = APIExtractor()

    def extract_venue(self, url):
        """完整三階段擷取"""

        # 階段1：快速測試（靜態方法）
        print('階段1：測試靜態擷取...')
        static_result = self.static_extractor.quick_test(url)

        if static_result['confidence'] > 0.8:
            print('✅ 使用靜態方法（快）')
            return self.static_extractor.full_extract(url)

        # 階段2：嘗試 API（最乾淨）
        print('階段2：嘗試 API 逆向...')
        api_result = self.api_extractor.try_extract(url)

        if api_result['success']:
            print('✅ 使用 API（最準確）')
            return api_result

        # 階段3：使用 Playwright（保險）
        print('階段3：使用 Playwright（保險）...')
        return self.dynamic_extractor.extract(url)
```

---

## 📊 三種方法比較

| 方法 | 速度 | 成功率 | 準確度 | 資源消耗 | 適用場景 |
|------|------|--------|--------|----------|----------|
| **requests + BeautifulSoup** | ⚡⚡⚡ 最快 | 60-70% | 高 | 🟢 低 | 靜態/SSR 網站 |
| **Playwright/Selenium** | ⚡ 慢 | 95%+ | 高 | 🔴 高 | CSR 網站 |
| **API 逆向** | ⚡⚡ 快 | 90%+ | 最高 | 🟢 低 | 有 API 的網站 |

### 建議順序

```
1. 先試 requests + BeautifulSoup（最快）
   ↓ 失敗
2. 再試 API 逆向（最乾淨）
   ↓ 失敗
3. 最後用 Playwright（保險）
```

---

## 🎯 針對場地網站的建議

### 台灣場地網站常見技術

1. **大型酒店**：多用 SSR（WordPress, 自家 CMS）
   - ✅ 優先用 requests + BeautifulSoup

2. **會議中心**：多用 SSR 或混合式
   - ✅ 先試 requests，失敗再用 Playwright

3. **新創公司**：多用 CSR（React, Vue）
   - ✅ 先試 API，失敗再用 Playwright

4. **政府機關**：純靜態 HTML
   - ✅ 用 requests + BeautifulSoup

### 實際建議

```python
# 針對台灣場地網站的擷取策略

def scrape_taiwan_venue(url):
    # 80% 的台灣場地網站是靜態/SSR
    result = try_static_extraction(url)

    if not result['success']:
        # 15% 可以用 API
        result = try_api_extraction(url)

    if not result['success']:
        # 5% 需要 Playwright
        result = try_playwright_extraction(url)

    return result
```

---

## 🔧 安裝需求

### requests + BeautifulSoup（靜態）
```bash
pip install requests beautifulsoup4 lxml
```

### Playwright（動態）
```bash
pip install playwright
playwright install chromium
```

### Selenium（動態，備選）
```bash
pip install selenium
# 需要另外下載 ChromeDriver
```

---

## 📝 完整範例

```python
#!/usr/bin/env python3
"""
通用場地擷取器 - 自動判斷網頁類型並選擇最佳方法
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

class UniversalVenueScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape(self, url: str) -> Dict:
        """智慧擷取場地資料"""

        print(f'開始擷取: {url}')
        print('='*60)

        # 步驟1：測試是否為靜態網頁
        if self._is_static_page(url):
            print('✅ 檢測到靜態/SSR 網頁')
            return self._scrape_static(url)

        # 步驟2：嘗試 API
        api_result = self._try_api(url)
        if api_result:
            print('✅ 找到 API 端點')
            return api_result

        # 步驟3：使用 Playwright
        print('🔄 使用 Playwright 擷取動態內容')
        return self._scrape_dynamic(url)

    def _is_static_page(self, url: str) -> bool:
        """測試是否為靜態網頁"""

        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 檢查是否有會議室關鍵字
            text = soup.get_text().lower()
            keywords = ['會議室', 'meeting', '宴會', 'banquet', '場地租借']

            found = sum(1 for kw in keywords if kw in text)

            # 如果找到關鍵字，可能是靜態網頁
            return found >= 2

        except:
            return False

    def _scrape_static(self, url: str) -> Dict:
        """擷取靜態網頁"""

        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 使用已有的提取邏輯
        return {
            'success': True,
            'method': 'static',
            'data': self._extract_venue_data(soup, url)
        }

    def _try_api(self, url: str) -> Optional[Dict]:
        """嘗試 API 逆向"""

        # 常見的 API 路徑
        api_paths = [
            '/api/rooms',
            '/api/venue/meeting-rooms',
            '/wp-json/wp/v2/pages',  # WordPress
        ]

        for path in api_paths:
            try:
                api_url = url.rstrip('/') + path
                response = self.session.get(api_url, timeout=5)

                if response.status_code == 200:
                    data = response.json()

                    # 檢查是否為有效資料
                    if self._is_valid_api_data(data):
                        return {
                            'success': True,
                            'method': 'api',
                            'data': self._parse_api_data(data)
                        }
            except:
                continue

        return None

    def _scrape_dynamic(self, url: str) -> Dict:
        """使用 Playwright 擷取"""

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle')

            # 等待內容載入
            page.wait_for_timeout(2000)

            # 取得渲染後的 HTML
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            browser.close()

            return {
                'success': True,
                'method': 'playwright',
                'data': self._extract_venue_data(soup, url)
            }

    def _extract_venue_data(self, soup, url: str) -> Dict:
        """提取場地資料（通用方法）"""

        # 這裡使用之前定義的完整提取邏輯
        # 包括：聯絡資訊、交通資訊、場地規則、平面圖、會議室

        return {
            'name': soup.find('h1').get_text().strip(),
            'url': url,
            # ... 其他欄位
        }
```

---

**文件版本**: v1.0
**建立日期**: 2026-03-25
**涵蓋**: 靜態、SSR、CSR 網頁的擷取策略
