#!/usr/bin/env python3
"""
自動資料驗證引擎
功能：自動訪問官網、提取資料、比對差異
作者：Jobs (Global CTO)
日期：2026-03-17
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import hashlib

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/verification.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
REQUEST_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DELAY_BETWEEN_REQUESTS = 2  # 秒

class DataVerificationEngine:
    """資料驗證引擎"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.venues_data = None
        self.verification_results = []
        
    def load_venues(self) -> List[Dict]:
        """載入場地資料"""
        if self.venues_data is None:
            with open('venues.json', 'r', encoding='utf-8') as f:
                self.venues_data = json.load(f)
        return self.venues_data
    
    def save_venues(self, venues: List[Dict]):
        """儲存場地資料"""
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """獲取網頁內容"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, verify=False)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            logger.error(f"獲取頁面失敗 {url}: {e}")
            return None
    
    def extract_contact_info(self, html: str, base_url: str) -> Dict:
        """從網頁提取聯絡資訊"""
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        info = {}
        
        # 提取電話
        phone_patterns = [
            r'(\d{2,4}-\d{3,4}-\d{3,4})',
            r'(\(\d{2,4}\)\s*\d{3,4}-\d{3,4})',
            r'(電話[：:]\s*[\d\-\(\)\s]+)'
        ]
        
        text = soup.get_text()
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                info['phone'] = match.group(1).strip()
                break
        
        # 提取 Email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, text)
        if emails:
            # 過濾常見的無用 email
            valid_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'domain'])]
            if valid_emails:
                info['email'] = valid_emails[0]
        
        # 提取地址
        address_keywords = ['地址', '住址', 'Address', 'addr']
        for keyword in address_keywords:
            pattern = rf'{keyword}[：:]\s*(.+?)(?=\n|。|$)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['address'] = match.group(1).strip()
                break
        
        return info
    
    def extract_meeting_rooms(self, html: str, base_url: str) -> List[Dict]:
        """從網頁提取會議室資訊"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        rooms = []
        
        # 尋找會議室相關的關鍵字
        keywords = ['會議室', '會議廳', '宴會廳', 'ballroom', 'meeting', 'conference', 'banquet']
        
        # 提取會議室區塊
        for keyword in keywords:
            # 尋找包含關鍵字的元素
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            
            for element in elements:
                parent = element.parent
                
                # 提取會議室名稱
                room_name = element.strip()
                
                # 提取容量
                capacity_text = parent.get_text()
                capacity_match = re.search(r'(\d+)\s*(人|位|席)', capacity_text)
                capacity = int(capacity_match.group(1)) if capacity_match else None
                
                # 提取坪數
                area_match = re.search(r'(\d+(?:\.\d+)?)\s*坪', capacity_text)
                area = area_match.group(1) if area_match else None
                
                # 提取照片
                img = parent.find('img')
                photo_url = urljoin(base_url, img['src']) if img and img.get('src') else None
                
                if room_name and len(room_name) > 2:
                    room = {
                        'name': room_name,
                        'capacity': capacity,
                        'area': area,
                        'photo': photo_url
                    }
                    
                    # 避免重複
                    if not any(r['name'] == room_name for r in rooms):
                        rooms.append(room)
        
        return rooms
    
    def verify_venue(self, venue: Dict) -> Dict:
        """驗證單一場地"""
        venue_id = venue.get('id')
        venue_name = venue.get('name')
        url = venue.get('url')
        
        logger.info(f"驗證場地: {venue_name} (ID: {venue_id})")
        
        result = {
            'venue_id': venue_id,
            'venue_name': venue_name,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'differences': {},
            'website_data': {}
        }
        
        if not url:
            result['status'] = 'no_url'
            logger.warning(f"場地 {venue_name} 沒有官網 URL")
            return result
        
        # 訪問官網
        html = self.fetch_page(url)
        
        if not html:
            result['status'] = 'fetch_failed'
            logger.error(f"無法訪問 {venue_name} 的官網")
            return result
        
        # 提取資料
        website_data = {
            'contact_info': self.extract_contact_info(html, url),
            'meeting_rooms': self.extract_meeting_rooms(html, url)
        }
        
        result['website_data'] = website_data
        result['status'] = 'success'
        
        # 比對差異
        differences = self.compare_data(venue, website_data)
        result['differences'] = differences
        
        if differences:
            logger.info(f"發現 {len(differences)} 處差異")
        else:
            logger.info("資料一致")
        
        return result
    
    def compare_data(self, local_data: Dict, website_data: Dict) -> Dict:
        """比對本地資料與網站資料"""
        differences = {}
        
        # 比對聯絡資訊
        contact_info = website_data.get('contact_info', {})
        
        if 'phone' in contact_info:
            local_phone = local_data.get('contactPhone', '').replace(' ', '').replace('-', '')
            website_phone = contact_info['phone'].replace(' ', '').replace('-', '')
            
            if local_phone and website_phone and local_phone != website_phone:
                differences['contactPhone'] = {
                    'local': local_data.get('contactPhone'),
                    'website': contact_info['phone']
                }
        
        if 'email' in contact_info:
            local_email = local_data.get('contactEmail', '').lower()
            website_email = contact_info['email'].lower()
            
            if local_email and website_email and local_email != website_email:
                differences['contactEmail'] = {
                    'local': local_data.get('contactEmail'),
                    'website': contact_info['email']
                }
        
        # 比對會議室數量
        website_rooms = website_data.get('meeting_rooms', [])
        local_rooms = local_data.get('rooms', [])
        
        if len(website_rooms) > 0 and len(website_rooms) != len(local_rooms):
            differences['roomCount'] = {
                'local': len(local_rooms),
                'website': len(website_rooms)
            }
        
        return differences
    
    def verify_batch(self, venue_ids: List[int] = None, city: str = None, limit: int = None) -> List[Dict]:
        """批次驗證場地"""
        venues = self.load_venues()
        
        # 篩選場地
        if venue_ids:
            venues = [v for v in venues if v.get('id') in venue_ids]
        elif city:
            venues = [v for v in venues if v.get('city') == city]
        
        if limit:
            venues = venues[:limit]
        
        logger.info(f"開始批次驗證 {len(venues)} 個場地")
        
        results = []
        for i, venue in enumerate(venues, 1):
            logger.info(f"進度: {i}/{len(venues)}")
            
            result = self.verify_venue(venue)
            results.append(result)
            self.verification_results.append(result)
            
            # 避免過度請求
            if i < len(venues):
                time.sleep(DELAY_BETWEEN_REQUESTS)
        
        # 儲存結果
        self.save_verification_report(results)
        
        return results
    
    def save_verification_report(self, results: List[Dict]):
        """儲存驗證報告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reports/verification_report_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"驗證報告已儲存: {filename}")
    
    def get_summary(self) -> Dict:
        """獲取驗證摘要"""
        if not self.verification_results:
            return {}
        
        total = len(self.verification_results)
        success = sum(1 for r in self.verification_results if r['status'] == 'success')
        failed = sum(1 for r in self.verification_results if r['status'] == 'fetch_failed')
        no_url = sum(1 for r in self.verification_results if r['status'] == 'no_url')
        with_differences = sum(1 for r in self.verification_results if r['differences'])
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'no_url': no_url,
            'with_differences': with_differences,
            'accuracy_rate': (success / total * 100) if total > 0 else 0
        }


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自動資料驗證引擎')
    parser.add_argument('--city', type=str, help='只驗證特定縣市')
    parser.add_argument('--limit', type=int, help='限制驗證數量')
    parser.add_argument('--venue-ids', type=int, nargs='+', help='指定場地 ID')
    
    args = parser.parse_args()
    
    # 建立必要目錄
    import os
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # 執行驗證
    engine = DataVerificationEngine()
    results = engine.verify_batch(
        venue_ids=args.venue_ids,
        city=args.city,
        limit=args.limit
    )
    
    # 顯示摘要
    summary = engine.get_summary()
    print("\n" + "="*50)
    print("驗證摘要")
    print("="*50)
    print(f"總計: {summary['total']}")
    print(f"成功: {summary['success']}")
    print(f"失敗: {summary['failed']}")
    print(f"無 URL: {summary['no_url']}")
    print(f"有差異: {summary['with_differences']}")
    print(f"準確率: {summary['accuracy_rate']:.1f}%")
    print("="*50)


if __name__ == '__main__':
    main()
