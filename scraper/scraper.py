#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/scraper.py - 統一爬蟲主程式
流程：技術偵測 → 頁面發現 → 資料提取 → 驗證 → 合併寫入
"""

import argparse
import json
import os
import re
import sys
import io
from datetime import datetime
from shutil import copy2

# Windows UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')

import requests as req_module
from .config import QUALITY_LEVELS
from .detectors import TechnicalDetector
from .discoverers import PageDiscoverer
from .extractors import PDFExtractor, extract_venue_data
from .spa_extractor import SPExtractor
from .validators import (
    is_meeting_room, calculate_room_quality, get_quality_level,
    validate_capacity, merge_room,
)


class UnifiedScraper:
    """統一爬蟲"""

    def __init__(self):
        self.detector = TechnicalDetector()
        self.discoverer = PageDiscoverer()
        self.pdf_extractor = PDFExtractor()
        self.data = None

    def load_venues(self) -> list:
        """載入 venues.json"""
        if not os.path.exists(VENUES_FILE):
            print(f'[錯誤] 找不到 {VENUES_FILE}')
            return []

        with open(VENUES_FILE, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f'[載入] {len(self.data)} 個場地')
        return self.data

    def save_venues(self):
        """儲存 venues.json"""
        with open(VENUES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f'[儲存] 已寫入 {VENUES_FILE}')

    def backup_venues(self):
        """備份 venues.json"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'{VENUES_FILE}.backup.{timestamp}'
        copy2(VENUES_FILE, backup_path)
        print(f'[備份] {backup_path}')

    def find_venue(self, venue_id) -> dict:
        """根據 ID 尋找場地"""
        if not self.data:
            return None
        vid = int(venue_id) if isinstance(venue_id, str) else venue_id
        for v in self.data:
            if v.get('id') == vid:
                return v
        return None

    # === 核心：處理單一場地 ===

    def process_venue(self, venue: dict) -> dict:
        """
        處理單一場地的完整流程

        返回結果 dict：
        {
            'venueId': int,
            'venueName': str,
            'success': bool,
            'techReport': dict,
            'discoveredPages': list,
            'rooms': list,
            'qualityReport': dict,
            'errors': list,
        }
        """
        result = {
            'venueId': venue.get('id'),
            'venueName': venue.get('name', ''),
            'success': False,
            'techReport': None,
            'discoveredPages': [],
            'rooms': [],
            'qualityReport': {},
            'errors': [],
        }

        url = venue.get('url', '')
        if not url or url == 'TBD':
            result['errors'].append('無 URL 或 URL 為 TBD')
            return result

        print(f'\n{"="*60}')
        print(f'處理場地: {venue.get("name")} (ID: {venue.get("id")})')
        print(f'URL: {url}')
        print(f'{"="*60}')

        # Stage 1: 技術偵測
        print('\n--- Stage 1: 技術偵測 ---')
        tech_report = self.detector.detect(url)
        result['techReport'] = tech_report

        print(f'  HTTP: {tech_report["httpStatus"]}')
        print(f'  策略: {tech_report["extractionStrategy"]}')
        print(f'  動態: {tech_report["isDynamic"]}')
        print(f'  框架: {tech_report["jsFrameworks"]}')
        print(f'  靜態內容: {tech_report["staticContentLength"]} chars')

        # 即使首頁 404，仍嘗試頁面發現（URL 模式可能找到會議頁面）
        homepage_ok = tech_report['extractionStrategy'] != 'failed'
        if not homepage_ok:
            print(f'  [注意] 首頁失敗，仍嘗試 URL 模式發現...')

        # Stage 2: 多層頁面發現
        print('\n--- Stage 2: 頁面發現 ---')
        final_url = tech_report.get('finalUrl') or url
        discovered = self.discoverer.discover_all(final_url)
        result['discoveredPages'] = discovered

        meeting_pages = [p for p in discovered if p['pageType'] in ('meeting_list', 'meeting_detail')]
        pdf_pages = [p for p in discovered if p['pageType'] == 'pdf']
        print(f'  發現頁面: {len(discovered)} 個')
        print(f'  會議頁面: {len(meeting_pages)} 個')
        print(f'  PDF: {len(pdf_pages)} 個')

        # Stage 3: 資料提取
        print('\n--- Stage 3: 資料提取 ---')
        all_rooms = []
        venue_images = []  # 收集場地主圖片

        # 收集所有 PDF URL（從頁面發現 + 已有 floorPlan + 會議頁面中的 PDF 連結）
        all_pdf_urls = set()
        for p in pdf_pages:
            all_pdf_urls.add(p['url'])

        # 利用 venues.json 已有的 floorPlan
        existing_floorplan = venue.get('floorPlan')
        if existing_floorplan and existing_floorplan.startswith('http'):
            all_pdf_urls.add(existing_floorplan)
            print(f'  [PDF] 使用已有 floorPlan: {existing_floorplan}')

        # 從已發現的會議頁面中找 PDF 連結
        for page in meeting_pages:
            if page.get('httpStatus') not in (200, 202):
                continue
            try:
                r = req_module.get(page['url'], timeout=20, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }, verify=False)
                if r.status_code != 200:
                    continue
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '.pdf' in href.lower():
                        from urllib.parse import urljoin
                        abs_url = urljoin(page['url'], href)
                        all_pdf_urls.add(abs_url)
            except Exception:
                pass

        # 提取 PDF
        if all_pdf_urls:
            print(f'\n  [PDF] 嘗試提取 {len(all_pdf_urls)} 個 PDF...')
            for pdf_url in all_pdf_urls:
                pdf_rooms = self.pdf_extractor.extract(pdf_url)
                all_rooms.extend(pdf_rooms)
                print(f'  [PDF] {pdf_url}: {len(pdf_rooms)} 個會議室')

        # HTML 提取（從所有會議頁面）
        spa_extractor = None
        if meeting_pages:
            for page in meeting_pages:
                if page['httpStatus'] not in (200, 202):
                    continue
                strategy = tech_report.get('extractionStrategy', 'static_html')

                # SPA 網站：使用 Playwright 渲染
                if strategy == 'dynamic_js':
                    try:
                        if spa_extractor is None:
                            spa_extractor = SPExtractor()
                        spa_rooms = spa_extractor.extract(page['url'])
                        all_rooms.extend(spa_rooms)
                        # 收集場地主圖片 (從第一個頁面)
                        if not venue_images and len(all_rooms) > 0:
                            from bs4 import BeautifulSoup
                            from .extractors import HTMLExtractor
                            # 重新渲染一次以取得圖片
                            result = spa_extractor.render_page(page['url'])
                            if result.get('html'):
                                soup = BeautifulSoup(result['html'], 'html.parser')
                                html_ext = HTMLExtractor()
                                imgs = html_ext.extract_images(soup, page['url'])
                                if imgs:
                                    venue_images = imgs[:10]  # 最多 10 張
                                    print(f'  [場地圖片] 收集 {len(venue_images)} 張')
                    except Exception as e:
                        print(f'  [SPA] 提取失敗 {page["url"]}: {e}')
                    continue

                # 靜態網站：使用 requests + BeautifulSoup
                try:
                    r = req_module.get(page['url'], timeout=20, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    }, verify=False)
                    if r.status_code != 200:
                        continue

                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(r.text, 'html.parser')
                    html_rooms = extract_venue_data(soup, page['url'], strategy)
                    all_rooms.extend(html_rooms)

                    # 收集場地主圖片 (從第一個頁面)
                    if not venue_images:
                        from .extractors import HTMLExtractor
                        html_ext = HTMLExtractor()
                        imgs = html_ext.extract_images(soup, page['url'])
                        if imgs:
                            venue_images = imgs[:10]  # 最多 10 張
                            print(f'  [場地圖片] 收集 {len(venue_images)} 張')

                except Exception as e:
                    print(f'  [HTML] 頁面提取失敗 {page["url"]}: {e}')

        # 關閉 SPA 瀏覽器
        if spa_extractor:
            spa_extractor.close()

        result['rooms'] = all_rooms
        print(f'\n  總計提取: {len(all_rooms)} 個會議室')

        # Stage 4: 驗證 + 去重
        print('\n--- Stage 4: 驗證 + 去重 ---')
        valid_rooms = []
        for room in all_rooms:
            name = room.get('name', '')
            if not is_meeting_room(name, room):
                print(f'  [排除] {name} (非會議室)')
                continue

            cap = room.get('capacity')
            if cap and not validate_capacity(cap):
                print(f'  [警告] {name} 容量不合理: {cap}')

            score = calculate_room_quality(room)
            room['qualityScore'] = score
            room['qualityLevel'] = get_quality_level(score)

            # 去重：檢查是否已有同名/相似房間
            merged = False
            for existing in valid_rooms:
                if self._is_same_room(existing, room):
                    # 合併資料（補充缺少的欄位）
                    for key in ['price', 'capacity', 'area', 'areaUnit', 'areaSqm',
                                'areaPing', 'floor', 'images', 'equipment', 'dimensions']:
                        new_val = room.get(key)
                        old_val = existing.get(key)
                        if new_val and (not old_val or old_val == '' or old_val == {} or old_val == []):
                            existing[key] = new_val
                        elif isinstance(new_val, dict) and isinstance(old_val, dict):
                            for k, v in new_val.items():
                                if v and not old_val.get(k):
                                    old_val[k] = v
                    # 保留較長的名稱
                    if len(name) > len(existing.get('name', '')):
                        existing['name'] = name
                    # 重新計算分數
                    existing['qualityScore'] = calculate_room_quality(existing)
                    existing['qualityLevel'] = get_quality_level(existing['qualityScore'])
                    print(f'  [合併] {name} → {existing["name"]}')
                    merged = True
                    break

            if not merged:
                valid_rooms.append(room)
                print(f'  [{room["qualityLevel"].upper():6s}] {name} (分數: {score})')

        result['rooms'] = valid_rooms
        result['success'] = len(valid_rooms) > 0

        # Stage 5: 合併到 venues.json
        if valid_rooms:
            print(f'\n--- Stage 5: 合併 ---')
            self._merge_rooms(venue, valid_rooms, tech_report, venue_images)

        return result

    def _merge_rooms(self, venue: dict, new_rooms: list, tech_report: dict, venue_images: list = None):
        """合併新會議室到場地資料"""
        existing_rooms = venue.get('rooms', [])

        for new_room in new_rooms:
            # 嘗試匹配已有的會議室
            matched = False
            for i, existing in enumerate(existing_rooms):
                if self._is_same_room(existing, new_room):
                    existing_rooms[i] = merge_room(existing, new_room)
                    print(f'  [合併] {new_room.get("name")} → 更新現有')
                    matched = True
                    break

            if not matched:
                # 新增會議室
                if not new_room.get('id'):
                    new_room['id'] = f"{venue.get('id')}-{len(existing_rooms)+1:02d}"
                existing_rooms.append(new_room)
                print(f'  [新增] {new_room.get("name")} (ID: {new_room["id"]})')

        venue['rooms'] = existing_rooms

        # 保存場地主圖片
        if venue_images and len(venue_images) > 0:
            venue['images'] = {
                'main': venue_images[0],
                'gallery': venue_images[:10],
                'verified': True,
                'verifiedAt': datetime.now().strftime('%Y-%m-%d'),
                'lastUpdated': datetime.now().strftime('%Y-%m-%d')
            }
            print(f'  [場地圖片] 已更新 {len(venue_images)} 張')

        # 更新 metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}
        venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
        venue['metadata']['scrapeVersion'] = 'unified_v1'
        venue['metadata']['totalRooms'] = len(existing_rooms)

        # 記錄技術報告
        if 'technicalReport' not in venue:
            venue['technicalReport'] = {}
        venue['technicalReport']['homepage'] = {
            'url': tech_report.get('finalUrl', ''),
            'httpStatus': tech_report.get('httpStatus'),
            'isDynamic': tech_report.get('isDynamic'),
            'jsFrameworks': tech_report.get('jsFrameworks'),
            'extractionStrategy': tech_report.get('extractionStrategy'),
        }

    def _is_same_room(self, existing: dict, new_room: dict) -> bool:
        """
        判斷兩個會議室是否為同一個（支援模糊匹配）
        """
        e_name = existing.get('name', '').strip()
        n_name = new_room.get('name', '').strip()

        # ID 匹配
        e_id = existing.get('id', '')
        n_id = new_room.get('id', '')
        if e_id and n_id and e_id == n_id:
            return True

        if not e_name or not n_name:
            return False

        e_lower = e_name.lower()
        n_lower = n_name.lower()

        # 完全相同
        if e_lower == n_lower:
            return True

        # 一個包含另一個
        if e_lower in n_lower or n_lower in e_lower:
            return True

        # 移除樓層前綴後比較
        e_clean = re.sub(r'^\d+\s*[F樓]\s*', '', e_lower).strip()
        n_clean = re.sub(r'^\d+\s*[F樓]\s*', '', n_lower).strip()
        if e_clean and n_clean and (e_clean in n_clean or n_clean in e_clean):
            return True

        # 中文關鍵字重疊率
        cn_e = set(re.findall(r'[\u4e00-\u9fff]', e_name))
        cn_n = set(re.findall(r'[\u4e00-\u9fff]', n_name))
        if cn_e and cn_n:
            overlap = cn_e & cn_n
            total = cn_e | cn_n
            if total and len(overlap) / len(total) >= 0.6:
                return True

        # 英文關鍵字重疊
        en_e = set(w.lower() for w in re.findall(r'[A-Za-z]{2,}', e_name))
        en_n = set(w.lower() for w in re.findall(r'[A-Za-z]{2,}', n_name))
        if en_e and en_n and (en_e & en_n):
            return True

        return False

    # === CLI 指令 ===

    def cmd_test(self, venue_id):
        """測試單一場地"""
        self.load_venues()
        venue = self.find_venue(venue_id)
        if not venue:
            print(f'[錯誤] 找不到場地 ID: {venue_id}')
            return

        self.backup_venues()
        result = self.process_venue(venue)

        if result['success']:
            self.save_venues()
            print(f'\n✓ 成功！提取 {len(result["rooms"])} 個會議室')
        else:
            print(f'\n✗ 失敗: {", ".join(result["errors"])}')

        return result

    def cmd_batch(self, sample: int = 5):
        """批次處理"""
        self.load_venues()
        self.backup_venues()

        # 篩選有 URL 的場地
        candidates = [v for v in self.data if v.get('url') and v['url'] != 'TBD']
        print(f'[批次] 符合條件: {len(candidates)} 個場地，處理前 {sample} 個')

        results = []
        for venue in candidates[:sample]:
            result = self.process_venue(venue)
            results.append(result)

        self.save_venues()

        # 統計
        success = sum(1 for r in results if r['success'])
        total_rooms = sum(len(r['rooms']) for r in results)
        print(f'\n{"="*60}')
        print(f'批次結果: {success}/{len(results)} 成功, 共 {total_rooms} 個會議室')
        print(f'{"="*60}')

        return results

    def cmd_fix_rooms(self):
        """修正客房誤判"""
        self.load_venues()
        self.backup_venues()

        fixed_count = 0
        removed_rooms = []

        for venue in self.data:
            rooms = venue.get('rooms', [])
            original_count = len(rooms)
            valid_rooms = []

            for room in rooms:
                name = room.get('name', '')
                if is_meeting_room(name, room):
                    valid_rooms.append(room)
                else:
                    removed_rooms.append({
                        'venue': venue.get('name'),
                        'venueId': venue.get('id'),
                        'room': name,
                    })
                    print(f'  [排除] {venue.get("name")}: {name}')

            if len(valid_rooms) < original_count:
                venue['rooms'] = valid_rooms
                venue['metadata']['totalRooms'] = len(valid_rooms)
                fixed_count += original_count - len(valid_rooms)

        self.save_venues()

        print(f'\n[修正] 排除 {fixed_count} 個客房:')
        for r in removed_rooms:
            print(f'  - {r["venue"]}: {r["room"]}')

        return removed_rooms

    def cmd_report(self):
        """品質報告"""
        self.load_venues()

        total_venues = len(self.data)
        total_rooms = sum(len(v.get('rooms', [])) for v in self.data)
        rooms_with_data = {'name': 0, 'capacity': 0, 'area': 0, 'price': 0, 'image': 0}

        quality_dist = {'high': 0, 'medium': 0, 'low': 0, 'empty': 0}

        for venue in self.data:
            for room in venue.get('rooms', []):
                if room.get('name'):
                    rooms_with_data['name'] += 1
                cap = room.get('capacity')
                if isinstance(cap, dict) and cap.get('theater'):
                    rooms_with_data['capacity'] += 1
                if room.get('area') or room.get('areaSqm') or room.get('areaPing'):
                    rooms_with_data['area'] += 1
                price = room.get('price')
                if isinstance(price, dict) and (price.get('weekday') or price.get('note')):
                    rooms_with_data['price'] += 1
                images = room.get('images')
                if isinstance(images, dict) and images.get('main'):
                    rooms_with_data['image'] += 1

                score = calculate_room_quality(room)
                level = get_quality_level(score)
                quality_dist[level] += 1

        # 無會議室的場地
        venues_no_rooms = [v.get('name') for v in self.data if not v.get('rooms')]

        print(f'\n{"="*60}')
        print(f'品質報告')
        print(f'{"="*60}')
        print(f'場地總數: {total_venues}')
        print(f'會議室總數: {total_rooms}')
        print(f'')
        print(f'欄位填充率:')
        for field, count in rooms_with_data.items():
            pct = (count / total_rooms * 100) if total_rooms > 0 else 0
            print(f'  {field:12s}: {count:4d} / {total_rooms} ({pct:.0f}%)')
        print(f'')
        print(f'品質分佈:')
        print(f'  高品質 (≥70): {quality_dist["high"]:4d} ({quality_dist["high"]/total_rooms*100:.0f}%)')
        print(f'  中品質 (≥40): {quality_dist["medium"]:4d} ({quality_dist["medium"]/total_rooms*100:.0f}%)')
        print(f'  低品質 (<40): {quality_dist["low"]:4d} ({quality_dist["low"]/total_rooms*100:.0f}%)')
        print(f'  空白:         {quality_dist["empty"]:4d}')

        if venues_no_rooms:
            print(f'\n無會議室的場地 ({len(venues_no_rooms)}):')
            for name in venues_no_rooms:
                print(f'  - {name}')

        # 客房檢查
        hotel_rooms = []
        for venue in self.data:
            for room in venue.get('rooms', []):
                name = room.get('name', '')
                if not is_meeting_room(name, room):
                    hotel_rooms.append(f'{venue.get("name")}: {name}')

        if hotel_rooms:
            print(f'\n疑似客房 ({len(hotel_rooms)}):')
            for hr in hotel_rooms:
                print(f'  ! {hr}')

        print(f'{"="*60}')

    def cmd_fix_low_quality(self):
        """重新爬取低品質場地"""
        self.load_venues()
        self.backup_venues()

        low_quality_venues = []
        for venue in self.data:
            rooms = venue.get('rooms', [])
            if not rooms:
                continue
            avg_score = sum(calculate_room_quality(r) for r in rooms) / len(rooms)
            if avg_score < QUALITY_LEVELS['medium']:
                low_quality_venues.append(venue)

        print(f'[低品質] 找到 {len(low_quality_venues)} 個場地需要重新爬取')

        results = []
        for venue in low_quality_venues[:5]:
            result = self.process_venue(venue)
            results.append(result)

        self.save_venues()
        return results


def main():
    parser = argparse.ArgumentParser(description='統一場地爬蟲')
    parser.add_argument('--test', type=int, help='測試單一場地 (ID)')
    parser.add_argument('--batch', action='store_true', help='批次處理')
    parser.add_argument('--sample', type=int, default=5, help='批次處理數量 (預設 5)')
    parser.add_argument('--fix-rooms', action='store_true', help='修正客房誤判')
    parser.add_argument('--fix-low-quality', action='store_true', help='重新爬取低品質場地')
    parser.add_argument('--report', action='store_true', help='品質報告')

    args = parser.parse_args()
    scraper = UnifiedScraper()

    if args.test:
        scraper.cmd_test(args.test)
    elif args.batch:
        scraper.cmd_batch(args.sample)
    elif args.fix_rooms:
        scraper.cmd_fix_rooms()
    elif args.fix_low_quality:
        scraper.cmd_fix_low_quality()
    elif args.report:
        scraper.cmd_report()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
