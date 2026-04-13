#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成 new-taipei-event-venue.html 頁面
從 venues.json 讀取場地圖片，替換佔位圖片
"""

import json
import sys
import os
from bs4 import BeautifulSoup

# Windows UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

# 專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'new-taipei-event-venue.html')

# 新北場地 ID 列表（按 HTML 頁面順序）
NEW_TAIPEI_IDS = [1506, 1507, 1508, 1509, 1511, 1513, 1514, 1515, 1516, 1532]

# 預設圖片（如果場地沒有圖片）
DEFAULT_IMAGE = 'https://taiwan-venues-new-indol.vercel.app/favicon.svg'


def load_venues():
    """載入 venues.json"""
    with open(VENUES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_venue_image(venue):
    """取得場地主圖片"""
    images = venue.get('images', {})
    if isinstance(images, dict):
        main = images.get('main') or images.get('image')
        if main and main.startswith('http'):
            return main
    # 如果沒有 images 欄位，嘗試舊格式
    old_image = venue.get('image')
    if old_image and old_image.startswith('http'):
        return old_image
    return DEFAULT_IMAGE


def regenerate_html():
    """重新生成 HTML 頁面"""
    venues = load_venues()

    # 讀取現有 HTML
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # 使用 BeautifulSoup 解析
    soup = BeautifulSoup(html, 'html.parser')

    # 找到所有連到 /venues/{id} 的連結
    for vid in NEW_TAIPEI_IDS:
        venue = next((v for v in venues if v['id'] == vid), None)
        if not venue:
            print(f'[跳過] 找不到場地 ID {vid}')
            continue

        venue_name = venue.get('name', 'UNKNOWN')
        new_image = get_venue_image(venue)

        # 找到該 venue 的連結
        link = soup.find('a', href=f'/venues/{vid}')
        if not link:
            print(f'[跳過] ID {vid} {venue_name}: 找不到連結')
            continue

        # 找到連結內的 img 標籤
        img = link.find('img')
        if not img:
            print(f'[跳過] ID {vid} {venue_name}: 找不到 img 標籤')
            continue

        # 替換 src
        old_src = img.get('src', '')
        img['src'] = new_image
        print(f'[OK] ID {vid} {venue_name}: {old_src[:50]}... -> {new_image[:50]}...')

    # 寫回檔案
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    print(f'\n[完成] 已更新 {OUTPUT_FILE}')


if __name__ == '__main__':
    regenerate_html()
