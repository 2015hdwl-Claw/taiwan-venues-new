#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北喜瑞飯店 - 解析完整 Sitemap
"""

import requests
import xml.etree.ElementTree as ET
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北喜瑞飯店 - 完整 Sitemap 解析")
print("=" * 100)

base_url = 'https://www.ambiencehotel.com.tw'
sitemap_url = f"{base_url}/wp-sitemap.xml"

print(f"解析: {sitemap_url}\n")

try:
    # 獲取主 sitemap 索引
    r = requests.get(sitemap_url, timeout=20, verify=False)
    print(f"主 Sitemap 狀態: {r.status_code}")

    if r.status_code == 200:
        # 解析 XML
        root = ET.fromstring(r.content)

        # 尋找所有 sitemap 子項
        namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemaps = root.findall('.//sm:sitemap/sm:loc', namespaces)

        print(f"發現 {len(sitemaps)} 個子 sitemap\n")

        all_urls = []

        # 處理每個子 sitemap
        for i, sm in enumerate(sitemaps):
            sub_sitemap_url = sm.text
            print(f"[{i+1}/{len(sitemaps)}] 處理: {sub_sitemap_url}")

            try:
                sr = requests.get(sub_sitemap_url, timeout=15, verify=False)

                if sr.status_code == 200:
                    sub_root = ET.fromstring(sr.content)
                    urls = sub_root.findall('.//sm:url/sm:loc', namespaces)
                    print(f"  發現 {len(urls)} 個 URL")

                    for url in urls:
                        url_text = url.text
                        # 只保留 ambiencehotel 的 URL
                        if 'ambiencehotel.com.tw' in url_text:
                            all_urls.append(url_text)

            except Exception as e:
                print(f"  錯誤: {e}")

        # 去重並排序
        all_urls = sorted(list(set(all_urls)))

        print(f"\n{'=' * 100}")
        print(f"總共找到 {len(all_urls)} 個唯一 URL\n")

        # 分類顯示
        print("【所有 URL 列表】\n")

        for url in all_urls:
            print(f"  {url}")

        # 檢查是否有會議/宴會相關的 URL
        print(f"\n{'=' * 100}")
        print("【可能包含會議/宴會資訊的 URL】\n")

        meeting_keywords = ['meeting', 'conference', 'banquet', 'event', 'wedding',
                          'function', '會議', '宴會', '婚宴', '活動', 'mice']

        for url in all_urls:
            url_lower = url.lower()
            if any(kw in url_lower for kw in meeting_keywords):
                print(f"  ✓ {url}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
