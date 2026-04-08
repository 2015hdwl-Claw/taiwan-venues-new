# SOP 改進報告：萬豪酒店案例檢討

> **日期**: 2026-03-17  
> **問題**: 為什麼已經有資料擷取 SOP 和清理流程，還是會發生錯誤？

---

## 🔍 問題根源分析

### 案例背景

**原本的資料**：
- URL: `https://www.taipeimarriott.com.tw/`（官網首頁）
- 聯絡電話: `02-2175-7999`（飯店總機）
- Email: `events.taipei@marriott.com`（通用信箱）
- images.source: `https://www.taipeimarriott.com.tw/websev?cat=page&subcat=17`

**正確的資料**（從會議&宴會頁面）：
- URL: `https://www.taipeimarriott.com.tw/`（官網首頁）
- meetingUrl: `https://www.taipeimarriott.com.tw/websev?cat=page&id=39`（會議&宴會頁面）
- 聯絡電話: `(02)8502-3899`（會議&宴會專線）
- Email: `catering@taipeimarriott.com.tw`（會議&宴會專用信箱）
- images.source: `https://www.taipeimarriott.com.tw/websev?cat=page&id=39`

---

## 📋 SOP 漏洞分析

### 漏洞 1：沒有指定「正確的官網頁面」

**問題**：
- SOP 只說要「訪問官網」
- 沒有說明應該訪問哪個頁面
- 萬豪酒店有多個頁面：
  - 官網首頁（一般資訊）
  - 會議&宴會頁面（id=39）
  - 會議室介紹頁面（subcat=17）
  - 場地簡介 PDF（/files/page_157062443710javl802.pdf）

**後果**：
- 提取了錯誤的聯絡資訊（飯店總機 vs 會議專線）
- 提取了通用信箱而非專用信箱

### 漏洞 2：沒有驗證「這是不是正確的頁面」

**問題**：
- SOP 沒有檢查 URL 是否指向「會議&宴會」頁面
- 沒有驗證「這個頁面是否包含會議室資訊」
- 沒有檢查「聯絡資訊是否為會議專用」

**後果**：
- 使用官網首頁提取資訊（資訊不完整）
- 使用錯誤的頁面（subcat=17 而非 id=39）

### 漏洞 3：聯絡資訊驗證不足

**問題**：
- SOP 只檢查電話格式（`/^[\d\-\(\)\s#]+$/`）
- 沒有區分「飯店總機」vs「會議專線」
- 沒有檢查 Email 是否為會議專用信箱

**後果**：
- 接受了飯店總機電話（02-2175-7999）
- 接受了通用信箱（events.taipei@marriott.com）

### 漏洞 4：缺少「資料來源 URL」的明確定義

**問題**：
- `images.source` 可以是任何頁面
- 沒有規範應該使用哪個頁面作為「主要來源」
- 沒有記錄「資料提取自哪個頁面」

**後果**：
- images.source 指向 subcat=17（會議室介紹）
- 但聯絡資訊可能來自首頁或其他頁面
- 無法追溯資料來源

---

## ✅ 改進方案

### 改進 1：增加「官網頁面類型」定義

**新增欄位**：
```json
{
  "url": "https://www.taipeimarriott.com.tw/",
  "meetingUrl": "https://www.taipeimarriott.com.tw/websev?cat=page&id=39",
  "venueInfoUrl": "https://www.taipeimarriott.com.tw/websev?cat=page&subcat=17"
}
```

**說明**：
- `url`: 官網首頁（基本資訊）
- `meetingUrl`: 會議&宴會專頁（聯絡資訊、報價）
- `venueInfoUrl`: 會議室詳細介紹頁面（會議室資訊）

### 改進 2：增加「頁面驗證」步驟

**SOP 新增檢查**：
```python
def verify_meeting_page(url, venue_name):
    """驗證是否為會議&宴會頁面"""
    
    # 1. 檢查 URL 是否包含會議相關關鍵字
    meeting_keywords = ['meeting', 'banquet', 'conference', 'event', '會議', '宴會']
    if not any(kw in url.lower() for kw in meeting_keywords):
        return False, "URL 不是會議&宴會頁面"
    
    # 2. 訪問頁面，檢查內容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. 檢查是否包含會議室資訊
    meeting_terms = ['會議', '宴會', '場地', '廳', 'Ballroom', 'Meeting']
    page_text = soup.get_text()
    if not any(term in page_text for term in meeting_terms):
        return False, "頁面不包含會議室資訊"
    
    # 4. 檢查是否有專門的聯絡資訊
    contact_section = soup.find('div', class_=re.compile('contact|聯絡'))
    if not contact_section:
        return False, "頁面沒有專門的聯絡資訊"
    
    return True, "這是會議&宴會頁面"
```

### 改進 3：增加「聯絡資訊驗證」規則

**新增驗證**：
```python
def verify_contact_info(phone, email, source_url):
    """驗證聯絡資訊是否為會議專用"""
    
    warnings = []
    
    # 1. 檢查電話是否為會議專線
    if '總機' in phone or '訂房' in phone:
        warnings.append(f"電話可能是總機而非會議專線: {phone}")
    
    # 2. 檢查 Email 是否為會議專用
    if 'events' not in email.lower() and 'catering' not in email.lower():
        warnings.append(f"Email 可能不是會議專用: {email}")
    
    # 3. 檢查來源頁面是否為會議頁面
    if not verify_meeting_page(source_url)[0]:
        warnings.append(f"聯絡資訊來源不是會議頁面: {source_url}")
    
    return warnings
```

### 改進 4：增加「資料來源追溯」機制

**新增欄位**：
```json
{
  "contactInfo": {
    "phone": "(02)8502-3899",
    "email": "catering@taipeimarriott.com.tw",
    "sourceUrl": "https://www.taipeimarriott.com.tw/websev?cat=page&id=39",
    "extractedAt": "2026-03-17T08:27:00Z"
  },
  "venueInfo": {
    "sourceUrl": "https://www.taipeimarriott.com.tw/websev?cat=page&subcat=17",
    "extractedAt": "2026-03-17T07:55:00Z"
  }
}
```

---

## 📊 改進後的驗證流程

```
┌─────────────────────┐
│ 1. 識別官網首頁      │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│ 2. 尋找會議&宴會頁面  │
│ - 檢查 URL 關鍵字    │
│ - 檢查頁面內容       │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│ 3. 提取聯絡資訊       │
│ - 會議專線電話       │
│ - 會議專用 Email     │
│ - 記錄來源 URL       │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│ 4. 驗證聯絡資訊       │
│ - 不是總機電話       │
│ - 是會議專用信箱     │
│ - 來源是會議頁面     │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│ 5. 提取會議室資訊    │
│ - 從會議室介紹頁面   │
│ - 記錄來源 URL       │
└─────────────────────┘
```

---

## 🎯 核心問題解答

### Q: 為什麼說「源頭就應該正確」，但還是會發生錯誤？

**A: 因為 SOP 沒有定義「什麼是正確的源頭」**

1. **「官網」vs「會議&宴會頁面」**
   - SOP 只說要訪問官網
   - 沒有說明應該訪問「會議&宴會」專頁
   - 導致提取了錯誤的聯絡資訊

2. **「總機」vs「會議專線」**
   - SOP 沒有區分這兩種電話
   - 導致接受了飯店總機電話

3. **「通用信箱」vs「會議專用信箱」**
   - SOP 沒有檢查 Email 是否為會議專用
   - 導致接受了通用信箱

### Q: 為什麼清理時用了錯誤的頁面？

**A: 因為沒有「頁面驗證」機制**

1. **沒有檢查 URL 是否為會議頁面**
   - 直接接受任何官網 URL
   - 沒有驗證頁面內容

2. **沒有追溯資料來源**
   - images.source 可以是任何頁面
   - 無法知道聯絡資訊來自哪裡

### Q: 為什麼沒有驗證「這是不是正確的頁面」？

**A: 因為 SOP 缺少「頁面類型識別」步驟**

1. **沒有定義頁面類型**
   - 首頁、會議頁面、會議室介紹頁面、PDF 文件
   - 每個頁面的用途不同

2. **沒有檢查頁面內容**
   - 沒有檢查是否包含「會議」、「宴會」關鍵字
   - 沒有檢查是否有專門的聯絡資訊區塊

---

## 🔧 具體改進建議

### 1. 更新 DATA_EXTRACTION_SOP.md

**新增章節**：「官網頁面類型識別」

```markdown
## 官網頁面類型

### 頁面分類
1. **官網首頁** (`url`)
   - 用途：基本資訊（地址、營業時間）
   - 不適合提取：會議專線、會議室詳細資訊

2. **會議&宴會頁面** (`meetingUrl`)
   - 用途：會議專線、會議專用 Email、報價
   - 必須驗證：URL 包含 meeting/banquet/會議/宴會

3. **會議室介紹頁面** (`venueInfoUrl`)
   - 用途：會議室詳細資訊、照片
   - 必須驗證：頁面包含會議室列表

### 驗證規則
- 聯絡資訊必須來自「會議&宴會頁面」
- 會議室資訊必須來自「會議室介紹頁面」
- 所有資料必須記錄來源 URL
```

### 2. 更新驗證腳本

**新增函數**：
```python
def validate_venue_source(venue):
    """驗證場地資料來源"""
    
    errors = []
    warnings = []
    
    # 1. 檢查是否有 meetingUrl
    if not venue.get('meetingUrl'):
        warnings.append("缺少 meetingUrl（會議&宴會頁面）")
    
    # 2. 檢查聯絡資訊來源
    contact_source = venue.get('contactInfo', {}).get('sourceUrl')
    if contact_source:
        if not verify_meeting_page(contact_source)[0]:
            errors.append("聯絡資訊來源不是會議頁面")
    else:
        warnings.append("沒有記錄聯絡資訊來源")
    
    # 3. 檢查會議室資訊來源
    venue_source = venue.get('venueInfo', {}).get('sourceUrl')
    if venue_source:
        if 'meeting' not in venue_source.lower() and 'venue' not in venue_source.lower():
            warnings.append("會議室資訊來源可能不是會議頁面")
    
    return errors, warnings
```

### 3. 建立頁面識別工具

**新增腳本**：`identify_meeting_page.py`

```python
#!/usr/bin/env python3
"""識別官網中的會議&宴會頁面"""

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def find_meeting_pages(base_url):
    """從官網尋找會議&宴會頁面"""
    
    meeting_pages = []
    
    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尋找包含會議關鍵字的連結
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().lower()
            
            # 檢查 URL
            if any(kw in href.lower() for kw in ['meeting', 'banquet', 'event', '會議', '宴會']):
                full_url = urljoin(base_url, href)
                meeting_pages.append({
                    'url': full_url,
                    'text': text,
                    'type': 'url_keyword'
                })
            
            # 檢查連結文字
            elif any(kw in text for kw in ['會議', '宴會', '場地', 'meeting', 'banquet']):
                full_url = urljoin(base_url, href)
                meeting_pages.append({
                    'url': full_url,
                    'text': text,
                    'type': 'text_keyword'
                })
        
        return meeting_pages
    
    except Exception as e:
        print(f"錯誤: {e}")
        return []

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方式: python identify_meeting_page.py <官網URL>")
        sys.exit(1)
    
    base_url = sys.argv[1]
    pages = find_meeting_pages(base_url)
    
    print(f"找到 {len(pages)} 個會議&宴會相關頁面:")
    for page in pages:
        print(f"  - {page['url']} ({page['type']}: {page['text']})")
```

---

## 📝 總結

### 核心問題

1. **SOP 沒有定義「什麼是正確的源頭」**
   - 只說要訪問官網，沒有說要訪問會議&宴會頁面

2. **缺少「頁面驗證」機制**
   - 沒有檢查 URL 是否為會議頁面
   - 沒有檢查頁面內容是否包含會議資訊

3. **缺少「聯絡資訊驗證」規則**
   - 沒有區分總機 vs 會議專線
   - 沒有檢查 Email 是否為會議專用

4. **缺少「資料來源追溯」**
   - 沒有記錄資料來自哪個頁面
   - 無法驗證資料來源是否正確

### 改進方向

1. **明確定義頁面類型**
   - url（官網首頁）
   - meetingUrl（會議&宴會頁面）
   - venueInfoUrl（會議室介紹頁面）

2. **增加頁面驗證步驟**
   - 檢查 URL 關鍵字
   - 檢查頁面內容
   - 檢查聯絡資訊區塊

3. **增加聯絡資訊驗證**
   - 不是總機電話
   - 是會議專用信箱
   - 來源是會議頁面

4. **增加資料來源追溯**
   - 記錄每個欄位的來源 URL
   - 記錄提取時間

---

**維護者**: Jobs (Global CTO)  
**日期**: 2026-03-17
