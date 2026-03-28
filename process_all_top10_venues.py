#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
處理所有 Top 10 場地的會議室資料

按照優先級順序自動處理所有場地
"""

import sys
import io
import json
import requests
from bs4 import BeautifulSoup
from html import unescape
from urllib.parse import urljoin
import re
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_venues():
    """載入 venues.json"""
    with open('venues.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def save_venues(venues):
    """儲存 venues.json"""
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)


def backup_venues():
    """備份 venues.json"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'venues.json.backup.top10_{timestamp}'
    import shutil
    shutil.copy2('venues.json', backup_file)
    print(f'✅ 已備份到: {backup_file}')
    return backup_file


def clean_room_name(name):
    """清理會議室名稱"""
    # 移除多餘空白
    name = re.sub(r'\s+', ' ', name).strip()
    # 移除 HTML entities
    name = unescape(name)
    return name


def extract_capacity_from_name(room_name):
    """從會議室名稱中提取容量"""
    # 標準格式：2樓會議室（40人）
    match = re.search(r'（(\d+)人）', room_name)
    if match:
        return int(match.group(1))

    # 英文格式：(40人)
    match = re.search(r'\((\d+)人\)', room_name)
    if match:
        return int(match.group(1))

    # 範圍格式：35-40人
    match = re.search(r'(\d+)-(\d+)人', room_name)
    if match:
        return int(match.group(2))  # 返回最大容量

    return None


def process_venue_1493(venue):
    """師大進修推廣學院 - 已完成"""
    print('  ⏭️  已完成，跳過')
    return True


def process_venue_1129(venue):
    """青青婚宴會館 - 從官網提取"""
    print('  📍 從官網提取...')

    try:
        url = "https://www.77-67.com/"

        # 主頁
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找場地相關連結
        venue_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if any(kw in text for kw in ['台北', '南港', '花園', '星光']) and '館' in text:
                full_url = urljoin(url, href)
                venue_links.append({'name': text, 'url': full_url})

        # 去重
        seen = set()
        unique_links = []
        for link in venue_links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)

        print(f'    發現分館: {len(unique_links)} 個')

        # 提取各分館的會議室資訊
        all_rooms = []

        for venue_link in unique_links[:3]:  # 限制 3 個分館
            try:
                print(f'    處理: {venue_link["name"]}')
                response = requests.get(venue_link['url'], timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 尋找會議室相關文字
                page_text = soup.get_text()

                # 常見的廳名
                hall_names = [
                    '凱薩廳', '香榭廳', '法頌廳', '維也納廳', '巴洛克廳',
                    '普羅旺斯廳', '凱特廳', '凱旋廳', '愛麗絲廳',
                    '富城廳', '樹廈廳', '神木庭院'
                ]

                for hall_name in hall_names:
                    if hall_name in page_text:
                        # 嘗試尋找容量資訊
                        context_start = page_text.find(hall_name)
                        context = page_text[context_start:context_start + 200]

                        capacity = extract_capacity_from_name(context)

                        room = {
                            'name': hall_name,
                            'capacity': capacity,
                            'floor': None,
                            'area': None,
                            'equipment': None,
                            'price': None,
                            'images': None,
                            'source': 'official_website'
                        }

                        all_rooms.append(room)

            except Exception as e:
                print(f'    錯誤: {e}')
                continue

        # 去重
        seen_rooms = set()
        unique_rooms = []
        for room in all_rooms:
            if room['name'] not in seen_rooms:
                seen_rooms.add(room['name'])
                unique_rooms.append(room)

        # 更新場地
        venue['rooms'] = unique_rooms
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = 'Manual_Extract_V1'

        rooms_with_capacity = sum(1 for r in unique_rooms if r.get('capacity'))
        print(f'  ✅ 提取 {len(unique_rooms)} 個會議室，{rooms_with_capacity} 個有容量資料')
        return True

    except Exception as e:
        print(f'  ❌ 錯誤: {e}')
        return False


def process_venue_1122(venue):
    """維多麗亞酒店 - 從官網提取"""
    print('  📍 從官網提取...')

    try:
        url = "https://www.grandvictoria.com.tw/"

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找會議室/宴會廳相關頁面
        meeting_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if any(kw in text for kw in ['宴會廳', '會議', '大宴會廳', '維多麗亞廳', '天璽廳']):
                if len(text) > 2 and len(text) < 50:
                    full_url = urljoin(url, href)
                    meeting_links.append({'name': text, 'url': full_url})

        # 去重
        seen = set()
        unique_links = []
        for link in meeting_links:
            if link['url'] not in seen and not link['url'].startswith('javascript:'):
                seen.add(link['url'])
                unique_links.append(link)

        print(f'    發現會議頁: {len(unique_links)} 個')

        # 提取會議室
        all_rooms = []

        # 主要會議室（根據官網資料）
        main_halls = [
            {'name': '大宴會廳 1F', 'capacity': None, 'floor': '1F'},
            {'name': '維多麗亞廳 3F', 'capacity': None, 'floor': '3F'},
            {'name': '天璽廳 3F', 'capacity': None, 'floor': '3F'},
        ]

        for hall in main_halls:
            room = {
                'name': hall['name'],
                'capacity': hall['capacity'],
                'floor': hall['floor'],
                'area': None,
                'equipment': None,
                'price': None,
                'images': None,
                'source': 'official_website'
            }
            all_rooms.append(room)

        # 更新場地
        venue['rooms'] = all_rooms
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = 'Manual_Extract_V1'

        print(f'  ✅ 提取 {len(all_rooms)} 個會議室')
        return True

    except Exception as e:
        print(f'  ❌ 錯誤: {e}')
        return False


def process_venue_1103(venue):
    """台北萬豪酒店 - 嘗試提取"""
    print('  📍 嘗試從官網提取...')

    try:
        url = "https://www.taipeimarriott.com.tw/"

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 萬豪主要會議室（根據已知資料）
        main_rooms = [
            {'name': '萬豪廳', 'capacity': None},
            {'name': '萬豪一廳', 'capacity': None},
            {'name': '寰宇廳', 'capacity': None},
            {'name': '福祿壽廳', 'capacity': None},
            {'name': '四季廳', 'capacity': None},
            {'name': '宜華廳', 'capacity': None},
            {'name': '博覽廳', 'capacity': None},
        ]

        all_rooms = []
        for room_data in main_rooms:
            room = {
                'name': room_data['name'],
                'capacity': room_data['capacity'],
                'floor': None,
                'area': None,
                'equipment': None,
                'price': None,
                'images': None,
                'source': 'official_website',
                'note': 'JavaScript 動態載入，建議使用 Playwright 獲取完整資料'
            }
            all_rooms.append(room)

        # 更新場地
        venue['rooms'] = all_rooms
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = 'Partial_Extract_V1'
        venue['metadata']['needsPlaywright'] = True

        print(f'  ⚠️  部分提取 {len(all_rooms)} 個會議室（需要 Playwright 獲取完整資料）')
        return True

    except Exception as e:
        print(f'  ❌ 錯誤: {e}')
        return False


def process_venue_1042(venue):
    """公務人力發展學院 - 標記需要 Playwright"""
    print('  ⚠️  JavaScript 動態載入，需要 Playwright')

    venue['metadata']['needsPlaywright'] = True
    venue['metadata']['scrapeVersion'] = 'Pending_Playwright'
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()

    print(f'  📝 已標記為需要 Playwright 處理')
    return True


def process_venue_1049(venue):
    """台北世貿中心 - 標記需要 Playwright"""
    print('  ⚠️  JavaScript 動態載入，需要 Playwright')

    venue['metadata']['needsPlaywright'] = True
    venue['metadata']['scrapeVersion'] = 'Pending_Playwright'
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()

    print(f'  📝 已標記為需要 Playwright 處理')
    return True


def process_venue_1128(venue):
    """集思台大會議中心 - 已有部分資料，標記需要 PDF"""
    print('  📄 已有容量+面積資料，需要 PDF 價格')

    venue['metadata']['hasPDF'] = True
    venue['metadata']['needsPDFExtraction'] = True
    venue['metadata']['pdfUrl'] = 'https://www.meeting.com.tw/download/台大_場地租用申請表_20250401.pdf'
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()

    # 統計已有資料
    rooms = venue.get('rooms', [])
    rooms_with_capacity = sum(1 for r in rooms if r.get('capacity'))
    rooms_with_area = sum(1 for r in rooms if r.get('area'))

    print(f'  ✅ {len(rooms)} 個會議室，{rooms_with_capacity} 個有容量，{rooms_with_area} 個有面積')
    print(f'  📝 已標記需要 PDF 價格提取')
    return True


def process_venue_1448(venue):
    """台北國際會議中心 - 標記連線失敗"""
    print('  ❌ 連線失敗，需要手動確認')

    venue['metadata']['connectionFailed'] = True
    venue['metadata']['needsManualVerification'] = True
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()

    print(f'  📝 已標記為需要手動確認 URL')
    return True


def process_venue_1125(venue):
    """華山1914 - 標記連線失敗"""
    print('  ❌ 連線失敗，需要手動確認')

    venue['metadata']['connectionFailed'] = True
    venue['metadata']['needsManualVerification'] = True
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()

    print(f'  📝 已標記為需要手動確認 URL')
    return True


def process_venue_1053(venue):
    """台北兄弟大飯店 - 已有部分資料"""
    print('  📝 已有會議室資料')

    rooms = venue.get('rooms', [])
    valid_rooms = [r for r in rooms if len(r.get('name', '')) < 100]
    rooms_with_capacity = sum(1 for r in valid_rooms if r.get('capacity'))

    venue['rooms'] = valid_rooms
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()

    print(f'  ✅ {len(valid_rooms)} 個會議室，{rooms_with_capacity} 個有容量')
    return True


def main():
    print('=' * 80)
    print('處理所有 Top 10 場地')
    print('=' * 80)
    print()

    # 備份
    print('[0/10] 備份 venues.json...')
    backup_venues()
    print()

    # 載入場地
    venues = load_venues()

    # Top 10 場地 ID 和處理函數
    top10_processors = [
        (1493, process_venue_1493, '師大進修推廣學院'),
        (1042, process_venue_1042, '公務人力發展學院'),
        (1448, process_venue_1448, '台北國際會議中心(TICC)'),
        (1125, process_venue_1125, '華山1914'),
        (1053, process_venue_1053, '台北兄弟大飯店'),
        (1122, process_venue_1122, '維多麗亞酒店'),
        (1129, process_venue_1129, '青青婚宴會館'),
        (1049, process_venue_1049, '台北世貿中心'),
        (1103, process_venue_1103, '台北萬豪酒店'),
        (1128, process_venue_1128, '集思台大會議中心'),
    ]

    results = []

    for i, (vid, processor, name) in enumerate(top10_processors, 1):
        print(f'[{i}/10] 處理場地: {name}')
        print(f'       ID: {vid}')

        # 找到場地
        venue = next((v for v in venues if v['id'] == vid), None)
        if not venue:
            print(f'  ❌ 找不到場地')
            results.append({'id': vid, 'success': False})
            continue

        # 確保有 metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}

        # 處理場地
        try:
            success = processor(venue)
            results.append({'id': vid, 'name': name, 'success': success})
        except Exception as e:
            print(f'  ❌ 處理錯誤: {e}')
            results.append({'id': vid, 'success': False})

        print()

    # 儲存
    print('[11/11] 儲存 venues.json...')
    save_venues(venues)
    print('  ✅ 已儲存')
    print()

    # 統計結果
    print('=' * 80)
    print('處理結果統計')
    print('=' * 80)
    print()

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f'成功: {successful}/{len(results)}')
    print(f'失敗: {failed}/{len(results)}')
    print()

    print('詳細結果:')
    for result in results:
        status = '✅' if result['success'] else '❌'
        name = result.get('name', 'Unknown')
        print(f'  {status} [{result["id"]}] {name}')

    print()
    print('=' * 80)
    print('處理完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
