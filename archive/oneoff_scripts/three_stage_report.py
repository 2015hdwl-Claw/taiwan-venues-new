#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Three-Stage Technical Detection Report
"""

import json
from datetime import datetime

print("=" * 100)
print("三階段技術檢測報告")
print("=" * 100)
print(f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Target venues
report_data = [
    {
        'id': 1499,
        'name': '高雄國際會議中心',
        'url': 'https://www.meeting.com.tw/khh/',
        'stage1_result': 'HTTP 404',
        'can_proceed': False,
        'issue': '網頁不存在',
        'action_required': '確認正確網址'
    },
    {
        'id': 1501,
        'name': '安順文旅',
        'url': 'https://www.amforahotel.com.tw/ambanew/',
        'stage1_result': 'DNS解析失敗',
        'can_proceed': False,
        'issue': '域名無法解析',
        'action_required': '確認正確網址'
    },
    {
        'id': 1502,
        'name': '台灣晶豐酒店',
        'url': 'https://www.chinapalace.com.tw/',
        'stage1_result': 'DNS解析失敗',
        'can_proceed': False,
        'issue': '域名無法解析',
        'action_required': '確認正確網址'
    },
    {
        'id': 1503,
        'name': '裕珍花園酒店',
        'url': 'https://www.yuzenhotel.com.tw/',
        'stage1_result': 'DNS解析失敗',
        'can_proceed': False,
        'issue': '域名無法解析',
        'action_required': '確認正確網址'
    },
    {
        'id': 1505,
        'name': '漢來大飯店',
        'url': 'https://www.hanlai-hotel.com.tw/',
        'stage1_result': 'DNS解析失敗',
        'can_proceed': False,
        'issue': '域名無法解析',
        'action_required': '確認正確網址'
    },
    {
        'id': 1526,
        'name': '蓮潭國際會館',
        'url': 'TBD',
        'stage1_result': 'URL TBD',
        'can_proceed': False,
        'issue': '缺少網址',
        'action_required': '提供官網網址'
    },
    {
        'id': 1529,
        'name': '福客來南北樓',
        'url': 'TBD',
        'stage1_result': 'URL TBD',
        'can_proceed': False,
        'issue': '缺少網址',
        'action_required': '提供官網網址'
    },
    {
        'id': 1530,
        'name': '富苑喜宴會館',
        'url': 'TBD',
        'stage1_result': 'URL TBD',
        'can_proceed': False,
        'issue': '缺少網址',
        'action_required': '提供官網網址'
    },
    {
        'id': 1536,
        'name': '高雄國際會議中心 (ICCK)',
        'url': 'https://www.icck.com.tw/',
        'stage1_result': 'HTTP 410 (Gone)',
        'can_proceed': False,
        'issue': '網頁已永久移除',
        'action_required': '確認新網址'
    },
    {
        'id': 1539,
        'name': '震大金鬱金香酒店',
        'url': 'https://www.goldentulip-zendahotel.com/',
        'stage1_result': 'DNS解析失敗',
        'can_proceed': False,
        'issue': '域名無法解析',
        'action_required': '確認正確網址'
    },
]

print("階段1技術檢測結果\n")
print("-" * 100)

for item in report_data:
    print(f"\nID {item['id']}: {item['name']}")
    print(f"  當前網址: {item['url']}")
    print(f"  檢測結果: {item['stage1_result']}")
    print(f"  問題: {item['issue']}")
    print(f"  需要動作: {item['action_required']}")

# Statistics
total = len(report_data)
dns_failures = sum(1 for item in report_data if 'DNS' in item['stage1_result'])
http_errors = sum(1 for item in report_data if 'HTTP' in item['stage1_result'])
tbd_urls = sum(1 for item in report_data if item['url'] == 'TBD')

print("\n" + "=" * 100)
print("統計摘要")
print("=" * 100)
print(f"總共處理: {total} 個場地")
print(f"DNS解析失敗: {dns_failures} 個")
print(f"HTTP錯誤 (404/410): {http_errors} 個")
print(f"缺少網址 (TBD): {tbd_urls} 個")
print(f"階段1通過: 0 個")
print(f"階段2無法執行: 是（全部卡在階段1）")
print(f"階段3無法執行: 是（全部卡在階段1）")

print("\n" + "=" * 100)
print("結論")
print("=" * 100)
print("所有10個場地都無法通過階段1技術檢測，無法進入階段2深度爬蟲和階段3驗證寫入。")
print("\n需要用戶提供正確的官網網址才能繼續處理這些場地。")
print("\n建議：")
print("1. 確認這些場地是否仍在營業")
print("2. 查詢並提供正確的官網網址")
print("3. 對於已關閉的場地（如HTTP 410），考慮從資料庫中移除")

print("\n" + "=" * 100)
print("DONE!")
print("=" * 100)
