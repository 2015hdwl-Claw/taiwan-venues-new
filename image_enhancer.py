#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
照片提取增強器
為飯店場地提取官網照片網址
"""

import json
import re
import sys
from datetime import datetime
from urllib.parse import urljoin

# Windows UTF-8 相容
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

import requests
from bs4 import BeautifulSoup


class ImageExtractor:
    """提取場地照片"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch(self, url: str) -> str:
        """抓取網頁"""
        try:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or 'utf-8'
            return resp.text
        except Exception as e:
            print(f"    ❌ Fetch error: {e}")
            return None

    def extract_illumme_images(self, hotel_id: int) -> dict:
        """提取 ILLUME 飯店照片"""
        print(f"\n{'='*70}")
        print(f"提取 ILLUME 照片")
        print(f"{'='*70}")

        room_images = {}

        # ILLUME 的會議場地頁面
        urls_to_try = [
            'https://www.theillumehotel.com/zh/meeting-events',
            'https://www.theillumehotel.com/meeting-events',
            'https://www.theillumehotel.com/zh/',
        ]

        for url in urls_to_try:
            print(f"  嘗試: {url}")
            html = self.fetch(url)
            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')

            # 尋找包含場地照片的區塊
            # ILLUME 使用 WordPress，可能有 gallery 或 slider

            # 方法1: 尋找所有圖片
            all_images = soup.find_all('img')
            print(f"    找到 {len(all_images)} 張圖片")

            # 方法2: 尋找特定場地的圖片
            # ILLUME 的場地：茹曦廳、斯賓諾莎宴會廳、貴賓軒、玉蘭軒
            venue_keywords = {
                '茹曦廳': ['茹曦廳', 'grand', 'ballroom'],
                '斯賓諾莎宴會廳': ['斯賓諾莎', 'spinoza', 'banquet'],
                '貴賓軒': ['貴賓軒', 'vip', 'lounge'],
                '玉蘭軒': ['玉蘭軒', 'yulan', 'room'],
            }

            for venue_name, keywords in venue_keywords.items():
                images = []
                for img in all_images:
                    src = img.get('src', '') or img.get('data-src', '')
                    alt = img.get('alt', '').lower()
                    title = img.get('title', '').lower()

                    # 檢查是否包含場地相關關鍵詞
                    src_lower = src.lower()
                    if any(kw.lower() in src_lower or kw.lower() in alt or kw.lower() in title for kw in keywords):
                        # 過濾掉小圖和圖示
                        if any(x in src_lower for x in ['icon', 'logo', 'svg', 'avatar']):
                            continue

                        full_url = urljoin(url, src)
                        if full_url not in images:
                            images.append(full_url)

                if images:
                    if venue_name not in room_images:
                        room_images[venue_name] = []
                    room_images[venue_name].extend(images)
                    room_images[venue_name] = list(set(room_images[venue_name]))
                    print(f"    ✓ {venue_name}: {len(room_images[venue_name])} 張照片")

            if room_images:
                break

        return room_images

    def extract_victoria_images(self, hotel_id: int) -> dict:
        """提取維多麗亞酒店照片"""
        print(f"\n{'='*70}")
        print(f"提取維多麗亞照片")
        print(f"{'='*70}")

        room_images = {}

        urls_to_try = [
            'https://www.grandvictoria.com.tw/tw/wedding/banquet',
            'https://www.grandvictoria.com.tw/',
        ]

        for url in urls_to_try:
            print(f"  嘗試: {url}")
            html = self.fetch(url)
            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            all_images = soup.find_all('img')

            venue_keywords = {
                '維多利亞宴會廳': ['victoria', 'ballroom', '宴會廳'],
                '皇冠宴會廳': ['crown', '皇冠'],
                '皇家宴會廳': ['royal', '皇家'],
                '貴賓廳': ['vip', '貴賓'],
                '會議室 A': ['meeting', '會議'],
            }

            for venue_name, keywords in venue_keywords.items():
                images = []
                for img in all_images:
                    src = img.get('src', '') or img.get('data-src', '')
                    src_lower = src.lower()

                    if any(kw.lower() in src_lower for kw in keywords):
                        if any(x in src_lower for x in ['icon', 'logo', 'svg', 'avatar']):
                            continue

                        full_url = urljoin(url, src)
                        if full_url not in images:
                            images.append(full_url)

                if images:
                    if venue_name not in room_images:
                        room_images[venue_name] = []
                    room_images[venue_name].extend(images)
                    room_images[venue_name] = list(set(room_images[venue_name]))
                    print(f"    ✓ {venue_name}: {len(room_images[venue_name])} 張照片")

            if room_images:
                break

        return room_images

    def extract_mandarin_images(self, hotel_id: int) -> dict:
        """提取文華東方照片"""
        print(f"\n{'='*70}")
        print(f"提取文華東方照片")
        print(f"{'='*70}")

        room_images = {}

        # 文華東方的圖片通常用 blob: URL 或 JS 動態載入
        # 直接抓取可能困難，先嘗試
        urls_to_try = [
            'https://www.mandarinoriental.com/taipei/hotel-services/event-spaces',
            'https://www.mandarinoriental.com/taipei',
        ]

        for url in urls_to_try:
            print(f"  嘗試: {url}")
            html = self.fetch(url)
            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')

            # 文華東方可能有 JSON-LD 結構化資料
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # 提取圖片
                    if 'image' in data:
                        print(f"    找到 JSON-LD 圖片")
                except:
                    pass

            # 尋找 img 標籤
            all_images = soup.find_all('img')

            venue_keywords = {
                'Grand Ballroom': ['grand', 'ballroom'],
                'Mandarin Ballroom': ['mandarin', 'ballroom'],
                'Crystal Room': ['crystal', 'room'],
                'Jade Room': ['jade', 'room'],
                'Phoenix Room': ['phoenix', 'room'],
            }

            for venue_name, keywords in venue_keywords.items():
                images = []
                for img in all_images:
                    src = img.get('src', '') or img.get('data-src', '')
                    src_lower = src.lower()

                    # 跳過 blob: URL
                    if 'blob:' in src:
                        continue

                    if any(kw.lower() in src_lower for kw in keywords):
                        if any(x in src_lower for x in ['icon', 'logo', 'svg', 'avatar']):
                            continue

                        full_url = urljoin(url, src)
                        if full_url not in images:
                            images.append(full_url)

                if images:
                    if venue_name not in room_images:
                        room_images[venue_name] = []
                    room_images[venue_name].extend(images)
                    room_images[venue_name] = list(set(room_images[venue_name]))
                    print(f"    ✓ {venue_name}: {len(room_images[venue_name])} 張照片")

            if room_images:
                break

        return room_images

    def extract_ambassador_images(self, hotel_id: int) -> dict:
        """提取國賓照片"""
        print(f"\n{'='*70}")
        print(f"提取國賓照片")
        print(f"{'='*70}")

        room_images = {}

        urls_to_try = [
            'https://www.ambassador-hotels.com/tc/taipei/banquet',
            'https://www.ambassador-hotels.com/tc/taipei',
        ]

        for url in urls_to_try:
            print(f"  嘗試: {url}")
            html = self.fetch(url)
            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            all_images = soup.find_all('img')

            venue_keywords = {
                '孔雀宴會廳': ['peacock', '孔雀', 'ballroom'],
                '玫瑰宴會廳': ['rose', '玫瑰', 'ballroom'],
                '會議室 A': ['meeting', '會議'],
                '會議室 B': ['meeting', '會議'],
                '會議室 C': ['meeting', '會議'],
            }

            for venue_name, keywords in venue_keywords.items():
                images = []
                for img in all_images:
                    src = img.get('src', '') or img.get('data-src', '')
                    src_lower = src.lower()

                    if any(kw.lower() in src_lower for kw in keywords):
                        if any(x in src_lower for x in ['icon', 'logo', 'svg', 'avatar']):
                            continue

                        full_url = urljoin(url, src)
                        if full_url not in images:
                            images.append(full_url)

                if images:
                    if venue_name not in room_images:
                        room_images[venue_name] = []
                    room_images[venue_name].extend(images)
                    room_images[venue_name] = list(set(room_images[venue_name]))
                    print(f"    ✓ {venue_name}: {len(room_images[venue_name])} 張照片")

            if room_images:
                break

        return room_images

    def update_venues_with_images(self, hotel_id: int, room_images: dict):
        """更新 venues.json 中的照片"""
        with open('venues.json', 'r', encoding='utf-8') as f:
            venues = json.load(f)

        updated_rooms = 0
        total_photos = 0

        for venue in venues:
            if venue['id'] == hotel_id:
                for room in venue.get('rooms', []):
                    room_name = room['name']

                    # 尋找對應的照片
                    if room_name in room_images:
                        old_count = len(room.get('images', []))
                        room['images'] = room_images[room_name]
                        new_count = len(room['images'])

                        updated_rooms += 1
                        total_photos += new_count
                        print(f"    ✓ {room_name}: {old_count} → {new_count} 張照片")

                venue['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")
                break

        # 備份並儲存
        import shutil
        backup = f'venues.json.backup.images_{hotel_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy('venues.json', backup)

        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)

        print(f"\n  ✅ 更新 {updated_rooms} 個場地，共 {total_photos} 張照片")
        print(f"  📄 備份: {backup}")


def main():
    """主程式"""
    extractor = ImageExtractor()

    # ILLUME (1090)
    print("\n" + "="*70)
    print("處理 ILLUME 酒店")
    print("="*70)
    illumme_images = extractor.extract_illumme_images(1090)
    if illumme_images:
        extractor.update_venues_with_images(1090, illumme_images)

    # Victoria (1122)
    print("\n" + "="*70)
    print("處理維多麗亞酒店")
    print("="*70)
    victoria_images = extractor.extract_victoria_images(1122)
    if victoria_images:
        extractor.update_venues_with_images(1122, victoria_images)

    # Mandarin Oriental (1085)
    print("\n" + "="*70)
    print("處理文華東方酒店")
    print("="*70)
    mandarin_images = extractor.extract_mandarin_images(1085)
    if mandarin_images:
        extractor.update_venues_with_images(1085, mandarin_images)

    # Ambassador (1069)
    print("\n" + "="*70)
    print("處理國賓大飯店")
    print("="*70)
    ambassador_images = extractor.extract_ambassador_images(1069)
    if ambassador_images:
        extractor.update_venues_with_images(1069, ambassador_images)

    print("\n" + "="*70)
    print("✅ 照片提取完成！")
    print("="*70)


if __name__ == '__main__':
    main()
