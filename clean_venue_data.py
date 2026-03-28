#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理場地資料
1. 會議室去重
2. 清理 HTML 標籤
3. 標準化容量格式
"""
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import io

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class VenueDataCleaner:
    def __init__(self):
        self.stats = {
            'venues_processed': 0,
            'rooms_before': 0,
            'rooms_after': 0,
            'duplicates_removed': 0,
            'html_cleaned': 0
        }

    def clean_html(self, text):
        """清理 HTML 標籤"""
        if not text or not isinstance(text, str):
            return text

        # 移除 HTML 標籤
        soup = BeautifulSoup(text, 'html.parser')
        cleaned = soup.get_text().strip()

        # 移除多餘空白
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned if cleaned else text

    def standardize_capacity(self, capacity):
        """標準化容量格式"""
        if not capacity:
            return None

        if isinstance(capacity, (int, float)):
            return int(capacity)

        if isinstance(capacity, str):
            # 移除非數字字符
            cleaned = re.sub(r'[^\d]', '', capacity)
            if cleaned:
                return int(cleaned)

        return None

    def deduplicate_rooms(self, rooms):
        """會議室去重，使用 name + floor 作為唯一鍵"""
        if not rooms:
            return rooms

        seen = {}
        unique_rooms = []

        for room in rooms:
            # 建立唯一鍵
            name = room.get('name', '').strip()
            floor = room.get('floor', '').strip()

            # 如果 name 和 floor 都為空，跳過
            if not name and not floor:
                continue

            unique_key = f"{name}|{floor}"

            # 如果沒看過，加入
            if unique_key not in seen:
                seen[unique_key] = True
                unique_rooms.append(room)
            else:
                self.stats['duplicates_removed'] += 1

        return unique_rooms

    def clean_venue(self, venue):
        """清理單個場地資料"""
        self.stats['venues_processed'] += 1

        vid = venue.get('id')
        name = venue.get('name', 'Unknown')

        print(f'清理場地 ID {vid}: {name}')

        # 1. 會議室去重
        if 'rooms' in venue:
            rooms_before = len(venue.get('rooms', []))
            venue['rooms'] = self.deduplicate_rooms(venue['rooms'])
            rooms_after = len(venue['rooms'])

            self.stats['rooms_before'] += rooms_before
            self.stats['rooms_after'] += rooms_after

            if rooms_before != rooms_after:
                print(f'  會議室去重: {rooms_before} -> {rooms_after} (移除 {rooms_before - rooms_after} 個重複)')

            # 2. 標準化會議室資料
            for room in venue.get('rooms', []):
                # 清理 HTML
                for field in ['name', 'equipment']:
                    if field in room and room[field]:
                        cleaned = self.clean_html(room[field])
                        if cleaned != room[field]:
                            room[field] = cleaned
                            self.stats['html_cleaned'] += 1

                # 標準化容量
                if 'capacity' in room:
                    room['capacity'] = self.standardize_capacity(room['capacity'])

        # 3. 清理 rules 和 accessInfo 的 HTML
        if 'rules' in venue:
            for rule_type, rule_value in venue['rules'].items():
                if rule_value:
                    cleaned = self.clean_html(rule_value)
                    if cleaned != rule_value:
                        venue['rules'][rule_type] = cleaned
                        self.stats['html_cleaned'] += 1

        if 'accessInfo' in venue:
            for access_type, access_value in venue['accessInfo'].items():
                if access_value:
                    cleaned = self.clean_html(access_value)
                    if cleaned != access_value:
                        venue['accessInfo'][access_type] = cleaned
                        self.stats['html_cleaned'] += 1

        # 4. 新增清理時間戳
        venue['cleanedAt'] = datetime.now().isoformat()
        venue['cleanVersion'] = 'v1'

        return venue

    def clean_all_venues(self, input_file, output_file=None):
        """清理所有場地資料"""
        print('='*80)
        print('場地資料清理工具')
        print('='*80)
        print()

        # 讀取資料
        print(f'讀取 {input_file}...')
        with open(input_file, 'r', encoding='utf-8') as f:
            venues = json.load(f)

        print(f'總共 {len(venues)} 個場地')
        print()

        # 只清理爬取過的場地
        scraped_venues = [v for v in venues if v.get('scrape_version') == 'v2_complete']
        print(f'需要清理的場地: {len(scraped_venues)} 個')
        print()

        # 清理每個場地
        cleaned_venues = []
        for venue in venues:
            if venue.get('scrape_version') == 'v2_complete':
                cleaned_venue = self.clean_venue(venue)
                cleaned_venues.append(cleaned_venue)
            else:
                cleaned_venues.append(venue)

        # 儲存結果
        output_file = output_file or input_file
        backup_file = f'{input_file}.before_clean_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

        print()
        print('='*80)
        print('清理統計')
        print('='*80)
        print(f'處理場地數: {self.stats["venues_processed"]}')
        print(f'會議室去重前: {self.stats["rooms_before"]} 個')
        print(f'會議室去重後: {self.stats["rooms_after"]} 個')
        print(f'移除重複會議室: {self.stats["duplicates_removed"]} 個')
        print(f'清理 HTML 標籤: {self.stats["html_cleaned"]} 處')
        print()

        # 備份
        import shutil
        shutil.copy(input_file, backup_file)
        print(f'備份: {backup_file}')

        # 儲存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_venues, f, ensure_ascii=False, indent=2)
        print(f'已儲存: {output_file}')

        # 生成報告
        report = {
            'cleanedAt': datetime.now().isoformat(),
            'statistics': self.stats,
            'venues_summary': [
                {
                    'id': v['id'],
                    'name': v['name'],
                    'rooms_count': len(v.get('rooms', [])),
                    'has_pricing': bool(v.get('pricing', {}).get('prices')),
                    'has_rules': bool(v.get('rules')),
                    'has_access': bool(v.get('accessInfo'))
                }
                for v in cleaned_venues
                if v.get('scrape_version') == 'v2_complete'
            ]
        }

        report_file = input_file.replace('.json', '_clean_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f'報告: {report_file}')

        print()
        print('='*80)
        print('清理完成！')
        print('='*80)


def main():
    cleaner = VenueDataCleaner()
    cleaner.clean_all_venues('venues.json')


if __name__ == '__main__':
    main()
