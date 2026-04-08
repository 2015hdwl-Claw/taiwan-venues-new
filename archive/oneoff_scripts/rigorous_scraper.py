#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最嚴謹的三階段爬蟲流程
不跳過任何步驟，完全記錄檢測結果
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def stage1_technical_detection(url):
    """
    階段1：技術檢測（必須先執行）
    """
    print("\n" + "=" * 100)
    print("階段1：技術檢測")
    print("=" * 100)
    print(f"目標 URL: {url}\n")

    result = {
        'url': url,
        'timestamp': datetime.now().isoformat()
    }

    # 1. HTTP 狀態碼
    print("1.1 檢測 HTTP 狀態碼...")
    try:
        response = requests.get(url, timeout=15, allow_redirects=True, verify=False)
        result['http_status'] = response.status_code
        result['final_url'] = response.url
        print(f"    HTTP 狀態: {response.status_code}")
        print(f"    最終 URL: {response.url}")

        if response.status_code != 200:
            print(f"    ⚠️ HTTP 狀態碼異常，但繼續檢測")

    except Exception as e:
        result['http_error'] = str(e)
        print(f"    ❌ HTTP 請求失敗: {e}")
        return result, None, None

    # 2. Content-Type 檢測
    print("\n1.2 檢測 Content-Type...")
    content_type = response.headers.get('Content-Type', '')
    result['content_type'] = content_type
    print(f"    Content-Type: {content_type}")

    if 'text/html' in content_type:
        result['page_type'] = 'HTML'
        print(f"    頁面類型: HTML")
    elif 'application/json' in content_type:
        result['page_type'] = 'JSON'
        print(f"    頁面類型: JSON API")
    else:
        result['page_type'] = 'Other'
        print(f"    頁面類型: 其他")

    # 3. 網頁載入方式檢測
    print("\n1.3 檢測網頁載入方式...")
    soup = BeautifulSoup(response.text, 'html.parser')

    # 檢查是否有 JavaScript 框架
    scripts = soup.find_all('script')
    js_frameworks = []

    for script in scripts:
        script_content = script.string or ''
        if any(fw in script_content for fw in ['react', 'vue', 'angular', 'jquery', 'next.js', 'nuxt.js']):
            js_frameworks.append(script_content[:50])

    if js_frameworks:
        result['js_frameworks'] = js_frameworks
        print(f"    發現 JS 框架: {len(js_frameworks)} 個")
        for fw in js_frameworks[:3]:
            print(f"      - {fw}")
    else:
        result['js_frameworks'] = []
        print(f"    JS 框架: 無（靜態 HTML）")

    # 判斷載入方式
    if result['js_frameworks']:
        result['loading_method'] = 'Dynamic/SPA'
        print(f"    載入方式: 動態/SPA")
    else:
        result['loading_method'] = 'Static/SSR'
        print(f"    載入方式: 靜態/SSR")

    # 4. 資料位置檢測
    print("\n1.4 檢測資料位置...")

    # 檢查 JSON-LD
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    if json_ld_scripts:
        result['json_ld_count'] = len(json_ld_scripts)
        print(f"    JSON-LD: {len(json_ld_scripts)} 個")

    # 檢查內嵌 JSON
    inline_scripts = soup.find_all('script')
    inline_json = []
    for script in inline_scripts:
        if script.string and ('{' in script.string or 'data =' in script.string):
            inline_json.append(True)

    if inline_json:
        result['inline_json_count'] = len(inline_json)
        print(f"    內嵌 JSON: {len(inline_json)} 個")

    # 檢查 HTML 結構
    meeting_keywords = ['meeting', 'conference', 'room', '會議', '場地', '會議室']
    found_keywords = []

    page_text = soup.get_text().lower()
    for keyword in meeting_keywords:
        if keyword in page_text:
            found_keywords.append(keyword)

    if found_keywords:
        result['html_keywords'] = found_keywords
        print(f"    HTML 關鍵字: {', '.join(found_keywords)}")

    result['data_location'] = 'HTML_structure'
    print(f"    資料位置: HTML 結構")

    # 5. 反爬蟲機制檢測
    print("\n1.5 檢測反爬蟲機制...")

    # 檢查 Cookies
    cookies = response.cookies
    if cookies:
        result['cookies'] = len(cookies)
        print(f"    Cookies: {len(cookies)} 個")

    # 檢查 Cloudflare
    server = response.headers.get('Server', '')
    if 'cloudflare' in server.lower():
        result['anti_scraping'] = 'Cloudflare'
        print(f"    ⚠️ 發現 Cloudflare")

    # 檢查 rate limiting headers
    rate_limit_headers = ['X-RateLimit', 'X-RateLimit-Remaining', 'Retry-After']
    found_rate_limit = [h for h in rate_limit_headers if h in response.headers]

    if found_rate_limit:
        result['rate_limit_headers'] = found_rate_limit
        print(f"    ⚠️ 發現 Rate Limiting: {', '.join(found_rate_limit)}")
    else:
        print(f"    反爬蟲: 無明顯機制")

    return result, soup, response


def stage2_deep_scraping(base_url, soup, response):
    """
    階段2：深度爬蟲（三級爬取）
    """
    print("\n" + "=" * 100)
    print("階段2：深度爬蟲（三級爬取）")
    print("=" * 100)

    result = {
        'base_url': base_url,
        'timestamp': datetime.now().isoformat()
    }

    # === 第一級：主頁分析 ===
    print("\n2.1 第一級：主頁分析")
    print("    尋找會議/宴會相關連結...")

    meeting_links = []
    all_links = soup.find_all('a', href=True)

    for a in all_links:
        href = a['href']
        text = a.get_text(strip=True).lower()
        href_lower = href.lower()

        # 尋找包含會議/宴議關鍵字的連結
        if any(kw in href_lower or kw in text for kw in
               ['meet', 'mice', 'banquet', 'event', 'conference',
                '會議', '宴會', '活動', '場地', '會議室', '聯絡']):
            # 排除無效連結
            if not href_lower.startswith('mailto:') and not href_lower.startswith('tel:'):
                full_url = urljoin(base_url, href)
                meeting_links.append({
                    'text': a.get_text(strip=True)[:100],
                    'href': full_url
                })

    result['meeting_links_count'] = len(meeting_links)
    print(f"    找到相關連結: {len(meeting_links)} 個")

    if meeting_links:
        print(f"    前 5 個連結:")
        for link in meeting_links[:5]:
            print(f"      - {link['text']}")
            print(f"        {link['href']}")

    # === 第二級：會議室頁面發現 ===
    print("\n2.2 第二級：會議室頁面發現")

    # 尋找 PDF 連結
    pdf_links = []
    for a in all_links:
        href = a['href'].lower()
        if '.pdf' in href or 'download' in href or '場租' in a.get_text() or '價格' in a.get_text():
            full_url = urljoin(base_url, a['href'])
            pdf_links.append({
                'text': a.get_text(strip=True)[:100],
                'href': full_url
            })

    result['pdf_links_count'] = len(pdf_links)
    print(f"    PDF 連結: {len(pdf_links)} 個")

    if pdf_links:
        print(f"    PDF 列表:")
        for pdf in pdf_links:
            print(f"      - {pdf['text']}")
            print(f"        {pdf['href']}")

    # === 第三級：頁面內容提取 ===
    print("\n2.3 第三級：頁面內容提取")

    # 提取所有文字
    page_text = soup.get_text()
    result['page_text_length'] = len(page_text)
    print(f"    頁面文字量: {len(page_text)} 字元")

    # 尋找可能的會議室名稱
    print("\n    尋找會議室資訊...")

    # 常見會議室命名模式
    room_patterns = [
        r'\d+[F樓]?\s*[會室廳]',
        r'[ABCD]\s*區',
        r'\d+\s*會議室',
        r'宴會廳',
        r'會議室'
    ]

    found_rooms = []
    for pattern in room_patterns:
        matches = re.findall(pattern, page_text)
        found_rooms.extend(matches)

    if found_rooms:
        result['potential_rooms'] = list(set(found_rooms))
        print(f"    可能的會議室: {len(result['potential_rooms'])} 個")
        print(f"    {result['potential_rooms'][:10]}")

    # 尋找聯絡資訊
    print("\n    尋找聯絡資訊...")

    phone_pattern = r'0\d[\d-]{7,9}'
    phones = re.findall(phone_pattern, page_text)

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, page_text)

    if phones:
        result['phones'] = phones[:5]
        print(f"    電話: {len(phones)} 個")
        for phone in phones[:3]:
            print(f"      - {phone}")

    if emails:
        result['emails'] = emails[:5]
        print(f"    Email: {len(emails)} 個")
        for email in emails[:3]:
            print(f"      - {email}")

    return result


def stage3_validation_and_summary(venue_id, venue_name, stage1_result, stage2_result):
    """
    階段3：驗證與總結
    """
    print("\n" + "=" * 100)
    print("階段3：驗證與總結")
    print("=" * 100)

    print(f"\n場地: {venue_name} (ID: {venue_id})")
    print(f"檢測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n【技術檢測結果】")
    print(f"  HTTP 狀態: {stage1_result.get('http_status', 'N/A')}")
    print(f"  頁面類型: {stage1_result.get('page_type', 'N/A')}")
    print(f"  載入方式: {stage1_result.get('loading_method', 'N/A')}")
    print(f"  資料位置: {stage1_result.get('data_location', 'N/A')}")
    print(f"  反爬蟲: {stage1_result.get('anti_scraping', '無') or '無明顯機制'}")

    print("\n【深度爬取結果】")
    print(f"  會議連結: {stage2_result.get('meeting_links_count', 0)} 個")
    print(f"  PDF 連結: {stage2_result.get('pdf_links_count', 0)} 個")
    print(f"  可能的會議室: {len(stage2_result.get('potential_rooms', []))} 個")

    print("\n【下一步建議】")

    if stage1_result.get('http_status') != 200:
        print("  ❌ HTTP 錯誤，無法爬取")
        print("  → 建議: 檢查 URL 或嘗試其他 URL")

    elif stage2_result.get('pdf_links_count', 0) > 0:
        print("  ✅ 發現 PDF，優先解析")
        print(f"  → 建議: 下載並解析 {stage2_result['pdf_links_count']} 個 PDF")

    elif stage2_result.get('meeting_links_count', 0) > 0:
        print("  ✅ 發現會議頁面，深度爬取")
        print(f"  → 建議: 爬取 {stage2_result['meeting_links_count']} 個連結")

    elif stage2_result.get('potential_rooms'):
        print("  ⚠️ 主頁有資訊，但需要手動提取")
        print("  → 建議: 手動提取會議室資料")

    else:
        print("  ❌ 未發現會議室資訊")
        print("  → 建議: 檢查是否有其他 URL 或直接聯繫")

    return {
        'venue_id': venue_id,
        'venue_name': venue_name,
        'stage1': stage1_result,
        'stage2': stage2_result,
        'timestamp': datetime.now().isoformat()
    }


def scrape_venue_rigorous(venue_id, venue_name, url):
    """
    完整的三階段爬蟲流程
    """
    print("\n" + "=" * 100)
    print(f"開始爬取: {venue_name}")
    print("=" * 100)
    print(f"ID: {venue_id}")
    print(f"URL: {url}")

    # 階段1：技術檢測
    try:
        stage1_result, soup, response = stage1_technical_detection(url)
    except Exception as e:
        print(f"\n❌ 階段1失敗: {e}")
        return None

    # 階段2：深度爬蟲
    try:
        stage2_result = stage2_deep_scraping(url, soup, response)
    except Exception as e:
        print(f"\n❌ 階段2失敗: {e}")
        stage2_result = {'error': str(e), 'stage2_failed': True}

    # 階段3：驗證與總結
    try:
        final_result = stage3_validation_and_summary(venue_id, venue_name, stage1_result, stage2_result)
    except Exception as e:
        print(f"\n❌ 階段3失敗: {e}")
        final_result = {'error': str(e), 'stage3_failed': True}

    return final_result


if __name__ == '__main__':
    # 測試單一場地
    venue_id = 1042
    venue_name = "公務人力發展學院"
    url = "https://www.hrd.gov.tw/"  # 修正正確 URL

    result = scrape_venue_rigorous(venue_id, venue_name, url)

    if result:
        # 儲存結果
        with open(f'scrape_result_{venue_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                  'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 結果已儲存")
