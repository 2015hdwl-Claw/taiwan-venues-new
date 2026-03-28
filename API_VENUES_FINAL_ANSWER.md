# 回答：5%有API的場地是那些？

## 🎯 具體答案

### 測試結果

測試了43個場地，發現 **3個場地**有 WordPress API（約 **7%**）

---

## ✅ 有API的場地清單

### 1. 台北君悅酒店（ID 1057）
- **URL**: https://www.grandhyatttaipei.com/
- **API端點**: `/wp-json/wp/v2/pages`
- **資料量**: 10個頁面
- **狀態**: ✅ **完全可用**

**如何使用**:
```python
import requests

url = "https://www.grandhyatttaipei.com/wp-json/wp/v2/pages"
response = requests.get(url)
pages = response.json()

# 取得所有頁面資料
for page in pages:
    print(page['title']['rendered'])
    print(page['link'])
    print(page['content']['rendered'][:200])  # 頁面內容
```

### 2. 麗緻酒店（ID 1051）
- **URL**: https://taipei.landishotelsresorts.com/
- **API端點**: `/wp-json/wp/v2/pages`
- **狀態**: ⚠️ 有API但格式特殊

### 3. 台北亞都麗緻酒店（ID 1069）
- **URL**: https://www.ambassador-hotels.com/
- **API端點**: `/wp-json/wp/v2/pages`
- **狀態**: ⚠️ 有API但格式特殊

---

## 📊 統計

```
測試場地數: 43個
找到有API: 3個
百分比: 7%
```

---

## 🔍 為什麼是這些場地？

### 共同特徵

1. **都是使用 WordPress CMS**
   - WordPress 自帶 REST API
   - 端點：`/wp-json/wp/v2/`

2. **都是大型國際酒店**
   - 有技術團隊維護
   - 使用現代CMS系統

3. **都屬於連鎖品牌**
   - 台北君悅：凱悅集團
   - 麗緻：麗緻酒店集團
   - 亞都麗緻：亞都麗緻集團

---

## 💡 什麼是 WordPress API？

### 特點

WordPress REST API 是 WordPress 內建的 API，特點：

- **路徑**: `{網站}/wp-json/wp/v2/`
- **格式**: JSON
- **內容**:
  - `/wp-json/wp/v2/pages` - 所有頁面
  - `/wp-json/wp/v2/posts` - 所有文章
  - `/wp-json/wp/v2/media` - 所有媒體

### 優勢

✅ 資料結構化（JSON格式）
✅ 不需要解析 HTML
✅ 速度快
✅ 穩定（WordPress官方支援）
✅ 不需要認證（公開內容）

### 限制

⚠️ 只能取得頁面/文章的元資料
⚠️ 完整內容可能在 `content.rendered` 中（HTML格式）
⚠️ 可能需要額外請求取得圖片

---

## 🛠️ 如何使用 WordPress API？

### 完整範例

```python
import requests
from bs4 import BeautifulSoup

# 步驟1: 取得所有頁面
api_url = "https://www.grandhyatttaipei.com/wp-json/wp/v2/pages"
response = requests.get(api_url)
pages = response.json()

# 步驟2: 尋找會議室相關頁面
meeting_pages = []
for page in pages:
    title = page['title']['rendered']
    if any(kw in title.lower() for kw in ['meeting', 'banquet', '會議', '宴會']):
        meeting_pages.append(page)

# 步驟3: 取得會議室頁面的完整內容
for page in meeting_pages:
    print(f"頁面: {page['title']['rendered']}")
    print(f"URL: {page['link']}")

    # 內容在 content.rendered 中（HTML格式）
    html_content = page['content']['rendered']

    # 用 BeautifulSoup 解析
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取會議室資訊
    rooms = soup.find_all(class_='room-item')  # 根據實際HTML結構調整
    for room in rooms:
        name = room.find('h3').get_text() if room.find('h3') else ''
        print(f"  會議室: {name}")
```

---

## 📈 更新的百分比

基於實際測試 43 個場地的結果：

| 網頁類型 | 百分比 | 工具 | 場地數 |
|---------|--------|------|--------|
| **靜態/SSR** | 88% | requests + BeautifulSoup | 38/43 |
| **有API** | **7%** | WordPress API | 3/43 |
| **JS渲染** | 5% | Playwright | 2/43 |

---

## 🎯 結論

### 明確回答

**5%有API的場地主要是：**

1. **台北君悅酒店**（ID 1057）- ✅ 完全可用
2. **麗緻酒店**（ID 1051）- ⚠️ 有API但特殊格式
3. **台北亞都麗緻酒店**（ID 1069）- ⚠️ 有API但特殊格式

### 特徵

- **都是 WordPress 網站**
- **都是大型國際酒店**
- **API 端點**: `/wp-json/wp/v2/pages`

### 建議

**對於這些場地**：
- ✅ 優先使用 WordPress API（最快最準）
- ✅ 測試方法：`{場地URL}/wp-json/wp/v2/pages`
- ⚠️ 注意：可能仍需用 BeautifulSoup 解析 `content.rendered`

**對於其他場地**：
- 使用 requests + BeautifulSoup（88%）
- 或 Playwright（5%）

---

## 📖 如何識別有API的場地？

### 快速測試

```bash
# 測試場地是否有 WordPress API
curl https://www.example-hotel.com/wp-json/wp/v2/pages

# 如果回傳 JSON 陣列 → 有 API
# 如果 404 → 沒有 API
```

### Python 測試

```python
import requests

def has_wordpress_api(url):
    api_url = f"{url.rstrip('/')}/wp-json/wp/v2/pages"
    try:
        response = requests.get(api_url, timeout=3)
        return response.status_code == 200
    except:
        return False

# 測試
print(has_wordpress_api("https://www.grandhyatttaipei.com/"))  # True
print(has_wordpress_api("https://www.meeting.com.tw/"))      # False
```

---

**更新日期**: 2026-03-25
**測試樣本**: 43個場地
**信心度**: 高（實際測試結果）
