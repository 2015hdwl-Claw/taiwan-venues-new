#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC - 階段2：測試找到的連結
基於階段1技術檢測結果
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - 階段2：測試階段1找到的連結")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 從主頁開始
base_url = "https://www.ticc.com.tw/"

print("步驟 1：重新訪問主頁，提取所有連結...")
response = requests.get(base_url, timeout=15, verify=False)
print(f"主頁 HTTP 狀態: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# 尋找所有會議相關連結
print("\n步驟 2：尋找會議相關連結...")
meeting_links = []

for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)
    href_lower = href.lower()

    # 尋找包含會議/場地關鍵字的連結
    if any(kw in href_lower or kw in text for kw in
           ['meet', 'room', 'floor', '會議', '場地', '會議室', '宴會']):
        if not href_lower.startswith('mailto:') and not href_lower.startswith('tel:'):
            # 轉換為完整 URL
            if not href.startswith('http'):
                if href.startswith('/'):
                    href = 'https://www.ticc.com.tw' + href
                else:
                    href = 'https://www.ticc.com.tw/' + href

            meeting_links.append({
                'text': text[:100],
                'href': href
            })

print(f"找到 {len(meeting_links)} 個會議相關連結\n")

# 測試每個連結
print("步驟 3：測試每個連結的可用性...")
print("=" * 100)

working_links = []
failed_links = []

for i, link in enumerate(meeting_links, 1):
    print(f"\n連結 {i}/{len(meeting_links)}")
    print(f"  文字: {link['text']}")
    print(f"  URL: {link['href']}")

    try:
        test_response = requests.get(link['href'], timeout=10, verify=False)
        print(f"  HTTP 狀態: {test_response.status_code}")

        if test_response.status_code == 200:
            print(f"  ✅ 可用")

            # 檢查頁面內容
            test_soup = BeautifulSoup(test_response.text, 'html.parser')
            page_text = test_soup.get_text()

            # 檢查是否包含會議室資訊
            if any(kw in page_text for kw in ['會議室', '會議廳', '宴會廳', '樓層', '坪']):
                print(f"  📄 包含會議室資訊")
                working_links.append(link)
            else:
                print(f"  ⚠️  可能不是會議室頁面")

            # 儲存可用的頁面
            if len(working_links) <= 3:  # 只儲存前3個
                filename = f"ticc_link_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(test_soup.prettify()))
                print(f"  💾 已儲存: {filename}")

        else:
            print(f"  ❌ 不可用")
            failed_links.append({**link, 'status': test_response.status_code})

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        failed_links.append({**link, 'error': str(e)})

    # 延遲避免被封
    time.sleep(1)

# 總結
print("\n" + "=" * 100)
print("測試結果總結")
print("=" * 100)
print(f"總連結數: {len(meeting_links)}")
print(f"可用連結: {len(working_links)}")
print(f"失敗連結: {len(failed_links)}")

if working_links:
    print(f"\n✅ 可用連結列表:")
    for link in working_links:
        print(f"  - {link['text']}")
        print(f"    {link['href']}")

if failed_links:
    print(f"\n❌ 失敗連結列表:")
    for link in failed_links[:5]:
        status = link.get('status', link.get('error', 'Unknown'))
        print(f"  - {link['text']}")
        print(f"    {link['href']}")
        print(f"    原因: {status}")

# 儲存結果
result = {
    'venue': 'TICC',
    'venue_id': 1448,
    'test_date': datetime.now().isoformat(),
    'total_links': len(meeting_links),
    'working_links': working_links,
    'failed_links': failed_links,
    'success_rate': f"{len(working_links)}/{len(meeting_links)}"
}

result_file = f'ticc_stage2_link_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 測試結果已儲存: {result_file}")

# 下一步建議
print("\n" + "=" * 100)
print("下一步建議")
print("=" * 100)

if working_links:
    print(f"✅ 找到 {len(working_links)} 個可用連結")
    print(f"建議：深度爬取這些可用連結，提取會議室資料")
else:
    print(f"❌ 所有連結都不可用")
    print(f"建議：")
    print(f"  1. 檢查是否需要特殊的 session/cookie")
    print(f"  2. 嘗試使用模擬瀏覽器（Selenium）")
    print(f"  3. 手動訪問網站確認正確的 URL")
    print(f"  4. 直接聯繫 TICC 索取會議室資料")
