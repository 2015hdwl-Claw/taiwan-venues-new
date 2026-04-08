#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試華山1914爬蟲 - 使用真實瀏覽器
"""
from scrapling import Fetcher
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "https://www.huashan1914.com"

print("="*100)
print(f"測試爬取: {url}")
print("="*100)
print()

# 嘗試不同的 URL
urls_to_try = [
    "https://www.huashan1914.com",
    "https://www.huashan1914.com/w/huashan1914/index",
    "https://huashan1914.com",
]

fetcher = Fetcher()

for test_url in urls_to_try:
    print(f"嘗試: {test_url}")
    try:
        page = fetcher.get(test_url)
        print(f"  狀態碼: {page.status}")
        print(f"  頁面長度: {len(page.text)} 字元")
        print(f"  Content-Type: {page.headers.get('Content-Type', 'N/A')}")
        
        if len(page.text) > 0:
            print(f"  ✅ 成功取得內容")
            
            # 顯示前 1000 字
            preview = page.text[:1000]
            print(f"\n前 1000 字預覽:")
            print("-"*100)
            print(preview)
            print("-"*100)
            break
        else:
            print(f"  ❌ 頁面空白")
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
    print()

print()
print("="*100)
print("使用 mcp__web_reader 工具嘗試")
print("="*100)
