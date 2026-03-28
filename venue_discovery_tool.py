#!/usr/bin/env python3
"""
場地發現工具 - 從各種來源找新場地
支援: Google Maps API, 手動清單, CSV匯入
"""
import json
import requests
from datetime import datetime
from typing import List, Dict

class VenueDiscovery:
    def __init__(self):
        self.session = requests.Session()

    def load_existing_venues(self, filepath='venues.json'):
        """載入現有場地"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def add_venue_from_list(self, venues_list: List[Dict]):
        """從清單新增場地"""
        existing = self.load_existing_venues()
        existing_ids = {v['id'] for v in existing}

        new_venues = []
        next_id = max(existing_ids) + 1 if existing_ids else 1000

        for venue_data in venues_list:
            # 檢查是否已存在 (根據URL或名稱)
            exists = any(
                v.get('url') == venue_data.get('url') or
                v.get('name') == venue_data.get('name')
                for v in existing
            )

            if exists:
                print(f'跳過重複: {venue_data.get("name")}')
                continue

            # 建立新場地
            new_venue = {
                'id': next_id,
                'name': venue_data['name'],
 'url': venue_data['url'],
                'status': 'active',
                'metadata': {
                    'createdAt': datetime.now().isoformat(),
                    'scrapeVersion': 'new',
                    'pagesDiscovered': 0
                }
            }

            # 可選欄位
            for field in ['address', 'contactPhone', 'contactEmail', 'district', 'city']:
                if field in venue_data:
                    new_venue[field] = venue_data[field]

            new_venues.append(new_venue)
            existing.append(new_venue)
            next_id += 1
            print(f'新增: {new_venue["name"]} (ID: {new_venue["id"]})')

        return new_venues, existing

    def save_venues(self, venues, filepath='venues.json'):
        """儲存場地"""
        # 備份
        backup_file = f'venues.json.backup.discovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)

        # 儲存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)

        print(f'已備份到: {backup_file}')
        print(f'已更新: {filepath}')

def demo_venues():
    """示範新場地資料"""
    return [
        {
            'name': '台北君悅酒店',
            'url': 'https://www.grandhyatttaipei.com/',
            'address': '台北市信義區松壽路2號',
            'district': '信義區',
            'city': '台北市'
        },
        {
            'name': '寒舍艾麗酒店',
            'url': 'https://www.hotel-elixir.com.tw/',
            'address': '台北市信義區松仁路18號',
            'district': '信義區',
            'city': '台北市'
        },
        {
            'name': '台北W酒店',
            'url': 'https://www.marriott.com/hotels/travel/tpewh-w-taipei/',
            'address': '台北市信義區忠孝東路五段10號',
            'district': '信義區',
            'city': '台北市'
        },
        {
            'name': '三猿創意基地',
            'url': 'https://3monkeys.asia/',
            'address': '台北市中正區重慶南路一段122號',
            'district': '中正區',
            'city': '台北市'
        },
        {
            'name': '台灣創新快遞基地',
            'url': 'https://www.tixbase.com/',
            'address': '台北市中正區重慶南路一段122號4樓',
            'district': '中正區',
            'city': '台北市'
        },
        {
            'name': '台灣會議展覽中心',
            'url': 'https://www.tcec.com.tw/',
            'address': '台北市信義區松壽路12號',
            'district': '信義區',
            'city': '台北市'
        },
        {
            'name': '松山文創園區',
            'url': 'https://www.songshanculturalpark.org/',
            'address': '台北市信義區光復南路133號',
            'district': '信義區',
            'city': '台北市'
        },
        {
            'name': '花博爭豐館',
            'url': 'https://www.tfam.museum/',
            'address': '台北市中正區中山南路3-1號',
            'district': '中正區',
            'city': '台北市'
        },
        {
            'name': '華山1914文創園區',
            'url': 'https://www.huashan1914.com/',
            'address': '台北市中正區八德路一段1號',
            'district': '中正區',
            'city': '台北市'
        },
        {
            'name': '台大醫院國際會議中心',
            'url': 'https://www.ntuh.gov.tw/',
            'address': '台北市中正區常德街1號',
            'district': '中正區',
            'city': '台北市'
        }
    ]

def main():
    print('場地發現工具')
    print('='*60)
    print('\n選擇來源:')
    print('1. 使用示範資料 (10個新場地)')
    print('2. 從JSON檔案匯入')
    print('3. 手動輸入')

    choice = input('\n請選擇 (1-3): ').strip()

    discovery = VenueDiscovery()

    if choice == '1':
        print('\n使用示範資料...')
        new_venues, updated_data = discovery.add_venue_from_list(demo_venues())
        discovery.save_venues(updated_data)
        print(f'\n新增了 {len(new_venues)} 個場地')

    elif choice == '2':
        filepath = input('請輸入JSON檔案路徑: ').strip()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                venues_list = json.load(f)
            new_venues, updated_data = discovery.add_venue_from_list(venues_list)
            discovery.save_venues(updated_data)
            print(f'\n新增了 {len(new_venues)} 個場地')
        except Exception as e:
            print(f'錯誤: {e}')

    elif choice == '3':
        print('\n手動輸入場地 (輸入空白結束)')
        venues_list = []
        while True:
            name = input('場地名稱: ').strip()
            if not name:
                break
            url = input('網站URL: ').strip()
            address = input('地址 (選填): ').strip()

            venue = {'name': name, 'url': url}
            if address:
                venue['address'] = address

            venues_list.append(venue)
            print()

        if venues_list:
            new_venues, updated_data = discovery.add_venue_from_list(venues_list)
            discovery.save_venues(updated_data)
            print(f'\n新增了 {len(new_venues)} 個場地')

    print('\n下一步: 執行 python parallel_venue_scraper.py 爬取新場地')

if __name__ == '__main__':
    main()
