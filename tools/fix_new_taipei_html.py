#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 new-taipei-event-venue.html 的場地卡片區塊
"""

import json
import sys
import os

# Windows UTF-8 輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'new-taipei-event-venue.html')

# 新北場地 ID 列表（按 HTML 頁面順序）
NEW_TAIPEI_IDS = [1506, 1507, 1508, 1509, 1511, 1513, 1514, 1515, 1516, 1532]

# 預設圖片
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
    old_image = venue.get('image')
    if old_image and old_image.startswith('http'):
        return old_image
    return DEFAULT_IMAGE


def get_venue_capacity(venue):
    """取得場地最大容量"""
    cap = venue.get('maxCapacityTheater') or venue.get('maxCapacity')
    return cap if cap else 0


def get_venue_rooms(venue):
    """取得場地會議室數量"""
    rooms = venue.get('rooms', [])
    return len(rooms)


def generate_venue_card(venue):
    """生成單一場地卡片 HTML"""
    vid = venue['id']
    name = venue.get('name', 'UNKNOWN')
    image = get_venue_image(venue)
    capacity = get_venue_capacity(venue)
    rooms = get_venue_rooms(venue)

    return f'''                <a href="/venues/{vid}" class="bg-surface-container-lowest rounded-xl border border-surface-container-high overflow-hidden hover:border-primary/30 hover:shadow-lg transition-all group">
                    <div class="h-40 overflow-hidden">
                        <img src="{image}" alt="{name}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy">
                    </div>
                    <div class="p-4">
                        <h3 class="font-bold text-on-surface mb-2 line-clamp-1">{name}</h3>
                        <div class="flex gap-3 text-xs text-on-surface-variant">
                            <span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">groups</span>{capacity}人</span>
                            <span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">meeting_room</span>{rooms}間</span>
                        </div>
                    </div>
                </a>'''


def fix_html():
    """修復 HTML 檔案"""
    venues = load_venues()

    # 讀取現有 HTML
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # 找到 Venue Cards 區段的開始和結束
    venue_section_start = '<!-- Venue Cards -->'
    venue_section_end = '<!-- FAQ -->'

    start_idx = html.find(venue_section_start)
    end_idx = html.find(venue_section_end)

    if start_idx == -1 or end_idx == -1:
        print('[錯誤] 找不到 Venue Cards 區段')
        return

    # 找到 grid div 的開始
    grid_start = html.find('<div class="grid grid-cols-1', start_idx)
    if grid_start == -1:
        print('[錯誤] 找不到 grid div')
        return

    # 找到 grid div 的結束（下一個 section 的開始）
    grid_end = html.find('</section>', grid_start)
    if grid_end == -1:
        print('[錯誤] 找不到 grid div 結束')
        return

    # 生成新的場地卡片
    venue_cards_html = '\n'.join([generate_venue_card(next((v for v in venues if v['id'] == vid), None)) for vid in NEW_TAIPEI_IDS])

    # 建構新的 HTML
    new_html = (
        html[:grid_start] +
        '''<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">

''' +
        venue_cards_html +
        '''
            </div>''' +
        html[grid_end + 10:]  # +10 跳過 </section>
    )

    # 寫回檔案
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f'[完成] 已修復 {OUTPUT_FILE}')


if __name__ == '__main__':
    fix_html()
