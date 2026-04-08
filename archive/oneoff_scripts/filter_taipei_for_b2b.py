#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 B2B 版本過濾台北場地
直接從 venues.json 過濾，不需要重新生成資料
"""

import json
import sys
import io

# 設定 UTF-8 輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def filter_taipei_venues(input_file='venues.json', output_file='venues_taipei.json'):
    """
    過濾出台北市的場地，並按品質排序

    排序優先級：
    1. 有完整照片（main + 3+ gallery）
    2. 有完整會議室資料
    3. 有聯絡資訊
    """
    print('載入場地資料...')

    with open(input_file, 'r', encoding='utf-8') as f:
        venues = json.load(f)

    print(f'原始場地數: {len(venues)}')

    # 過濾台北市
    taipei_venues = [v for v in venues if v.get('city') == '台北市']
    print(f'台北市場地: {len(taipei_venues)}')

    # 計算每個場地的品質分數
    def quality_score(venue):
        score = 0

        # 1. 照片完整性 (最高分 40)
        images = venue.get('images', {})
        if images.get('main'):
            score += 10
        if isinstance(images.get('gallery'), list) and len(images['gallery']) >= 3:
            score += 30

        # 2. 會議室資料 (最高分 30)
        rooms = venue.get('rooms', [])
        if rooms:
            score += 10
            # 檢查會議室照片（處理 images 可能是 list 或 dict）
            rooms_with_photos = 0
            for r in rooms:
                room_images = r.get('images', {})
                if isinstance(room_images, dict):
                    if room_images.get('main'):
                        rooms_with_photos += 1
                elif isinstance(room_images, list) and room_images:
                    rooms_with_photos += 1

            if rooms_with_photos >= len(rooms) * 0.5:
                score += 20

        # 3. 聯絡資訊 (最高分 20)
        contact = venue.get('contact', {})
        if contact.get('phone'):
            score += 10
        if contact.get('email'):
            score += 10

        # 4. 場地類型權重 (最高分 10)
        venue_type = venue.get('venueType', '')
        if venue_type in ['飯店場地', '會議中心']:
            score += 10
        elif venue_type in ['展演場地', '機關場地']:
            score += 5

        return score

    # 計算分數並排序
    for venue in taipei_venues:
        venue['qualityScore'] = quality_score(venue)

    taipei_venues.sort(key=lambda v: v['qualityScore'], reverse=True)

    # 顯示前 10 個場地的分數
    print('\n品質最高的前 10 個場地:')
    print('-' * 60)
    for i, venue in enumerate(taipei_venues[:10], 1):
        has_main_photo = 'Yes' if venue.get('images', {}).get('main') else 'No'
        print(f"{i}. {venue['name'][:30]:30s} - 分數: {venue['qualityScore']}")
        print(f"   照片: {has_main_photo}")
        print(f"   會議室: {len(venue.get('rooms', []))} 個")
        print()

    # 選擇分數 >= 40 的場地（約 15-25 個）
    mvp_venues = [v for v in taipei_venues if v['qualityScore'] >= 40]

    print(f'\n選擇分數 >= 40 的場地: {len(mvp_venues)} 個')
    print(f'這些場地將用於 MVP')

    # 移除 qualityScore 欄位（不儲存）
    for venue in mvp_venues:
        if 'qualityScore' in venue:
            del venue['qualityScore']

    # 儲存結果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mvp_venues, f, ensure_ascii=False, indent=2)

    print(f'\n✓ 已儲存到 {output_file}')

    return mvp_venues

if __name__ == '__main__':
    filter_taipei_venues()
