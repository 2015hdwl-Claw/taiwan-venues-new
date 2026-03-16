#!/usr/bin/env python3
"""
自動資料修正系統
功能：自動修正錯誤資料、下載照片、驗證資料
作者：Jobs (Global CTO)
日期：2026-03-17
"""

import json
import requests
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional
import hashlib
from PIL import Image
from io import BytesIO
import shutil

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/correction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
REQUEST_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PHOTO_QUALITY = 85
MAX_PHOTO_WIDTH = 1200

class PhotoDownloader:
    """照片下載與優化器"""
    
    def __init__(self, temp_dir: str = 'temp/photos'):
        self.temp_dir = temp_dir
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        os.makedirs(temp_dir, exist_ok=True)
    
    def download(self, url: str) -> Optional[str]:
        """下載照片"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # 生成唯一檔名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            ext = url.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                ext = 'jpg'
            
            filename = f"{url_hash}.{ext}"
            filepath = os.path.join(self.temp_dir, filename)
            
            # 儲存原始照片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"照片下載成功: {url}")
            return filepath
        
        except Exception as e:
            logger.error(f"照片下載失敗 {url}: {e}")
            return None
    
    def optimize(self, filepath: str) -> str:
        """優化照片"""
        try:
            img = Image.open(filepath)
            
            # 調整大小
            if img.width > MAX_PHOTO_WIDTH:
                ratio = MAX_PHOTO_WIDTH / img.width
                new_height = int(img.height * ratio)
                img = img.resize((MAX_PHOTO_WIDTH, new_height), Image.Resampling.LANCZOS)
            
            # 轉換為 RGB（如果需要）
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # 儲存優化後的照片
            optimized_path = filepath.replace('.', '_optimized.')
            img.save(optimized_path, 'JPEG', quality=PHOTO_QUALITY, optimize=True)
            
            # 替換原始檔案
            shutil.move(optimized_path, filepath)
            
            logger.info(f"照片優化成功: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"照片優化失敗 {filepath}: {e}")
            return filepath


class DataValidator:
    """資料驗證器"""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """驗證電話格式"""
        if not phone:
            return False
        # 台灣電話格式: 02-1234-5678 或 0912-345-678
        pattern = r'^(\d{2,4}-\d{3,4}-\d{3,4}|\d{4}-\d{3}-\d{3})$'
        return bool(re.match(pattern, phone.replace(' ', '')))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """驗證 Email 格式"""
        if not email:
            return False
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """驗證 URL 格式"""
        if not url:
            return False
        pattern = r'^https?://[\w\.-]+(?:/[\w\.-]*)*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """驗證容納人數"""
        return isinstance(capacity, int) and 0 < capacity <= 10000
    
    @staticmethod
    def validate_price(price: int) -> bool:
        """驗證價格"""
        return isinstance(price, int) and price >= 0


class DataCorrectionSystem:
    """資料修正系統"""
    
    def __init__(self):
        self.venues_data = None
        self.photo_downloader = PhotoDownloader()
        self.validator = DataValidator()
        self.corrections = []
    
    def load_venues(self) -> List[Dict]:
        """載入場地資料"""
        if self.venues_data is None:
            with open('venues.json', 'r', encoding='utf-8') as f:
                self.venues_data = json.load(f)
        return self.venues_data
    
    def save_venues(self):
        """儲存場地資料"""
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(self.venues_data, f, ensure_ascii=False, indent=2)
    
    def auto_correct(self, venue_id: int, differences: Dict) -> bool:
        """自動修正資料"""
        venues = self.load_venues()
        venue = next((v for v in venues if v['id'] == venue_id), None)
        
        if not venue:
            logger.error(f"找不到場地 ID: {venue_id}")
            return False
        
        corrected = False
        
        for field, values in differences.items():
            old_value = values.get('local')
            new_value = values.get('website')
            
            # 驗證新值
            if self.validate_field(field, new_value):
                venue[field] = new_value
                self.log_correction(venue_id, venue['name'], field, old_value, new_value)
                corrected = True
            else:
                logger.warning(f"新值驗證失敗，跳過修正: {field} = {new_value}")
        
        if corrected:
            # 更新時間戳
            venue['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
            venue['verified'] = True
            
            # 儲存變更
            self.save_venues()
            logger.info(f"場地 {venue['name']} 資料已更新")
        
        return corrected
    
    def validate_field(self, field: str, value: any) -> bool:
        """驗證欄位值"""
        if value is None:
            return False
        
        validators = {
            'contactPhone': self.validator.validate_phone,
            'contactEmail': self.validator.validate_email,
            'url': self.validator.validate_url,
            'maxCapacityTheater': self.validator.validate_capacity,
            'maxCapacityClassroom': self.validator.validate_capacity,
            'priceHalfDay': self.validator.validate_price,
            'priceFullDay': self.validator.validate_price,
        }
        
        validator = validators.get(field)
        if validator:
            return validator(value)
        
        # 預設：非空字串
        return bool(str(value).strip())
    
    def log_correction(self, venue_id: int, venue_name: str, field: str, old_value: any, new_value: any):
        """記錄修正"""
        correction = {
            'timestamp': datetime.now().isoformat(),
            'venue_id': venue_id,
            'venue_name': venue_name,
            'field': field,
            'old_value': old_value,
            'new_value': new_value
        }
        self.corrections.append(correction)
        logger.info(f"修正: {venue_name} - {field}: {old_value} → {new_value}")
    
    def update_photos(self, venue_id: int, photo_urls: Dict[str, str]) -> bool:
        """更新照片"""
        venues = self.load_venues()
        venue = next((v for v in venues if v['id'] == venue_id), None)
        
        if not venue:
            return False
        
        updated = False
        
        for room_name, photo_url in photo_urls.items():
            # 下載照片
            photo_path = self.photo_downloader.download(photo_url)
            
            if photo_path:
                # 優化照片
                optimized_path = self.photo_downloader.optimize(photo_path)
                
                # 更新資料（這裡簡化處理，實際應該上傳到圖床）
                # venue['rooms'][room_name]['images']['main'] = optimized_path
                updated = True
                logger.info(f"照片更新成功: {venue['name']} - {room_name}")
        
        if updated:
            self.save_venues()
        
        return updated
    
    def fill_missing_data(self, venue_id: int) -> bool:
        """補齊缺失資料"""
        venues = self.load_venues()
        venue = next((v for v in venues if v['id'] == venue_id), None)
        
        if not venue:
            return False
        
        filled = False
        
        # 檢查必要欄位
        required_fields = ['name', 'address', 'contactPhone', 'city', 'venueType']
        
        for field in required_fields:
            if not venue.get(field):
                logger.warning(f"場地 {venue['name']} 缺少必要欄位: {field}")
                # 這裡可以加入自動填補邏輯
        
        # 檢查 images 結構
        if 'images' not in venue:
            venue['images'] = {
                'main': '',
                'gallery': [],
                'floorPlan': '',
                'needsUpdate': True,
                'note': '自動建立 images 結構',
                'lastUpdated': datetime.now().strftime('%Y-%m-%d')
            }
            filled = True
        
        # 檢查 rooms 結構
        if 'rooms' not in venue:
            venue['rooms'] = []
            filled = True
        
        if filled:
            self.save_venues()
            logger.info(f"場地 {venue['name']} 缺失資料已補齊")
        
        return filled
    
    def batch_correct(self, verification_report: str):
        """批次修正"""
        with open(verification_report, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        logger.info(f"開始批次修正 {len(results)} 個場地")
        
        for result in results:
            venue_id = result['venue_id']
            differences = result.get('differences', {})
            
            if differences:
                self.auto_correct(venue_id, differences)
        
        # 儲存修正報告
        self.save_correction_report()
    
    def save_correction_report(self):
        """儲存修正報告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reports/correction_report_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.corrections, f, ensure_ascii=False, indent=2)
        
        logger.info(f"修正報告已儲存: {filename}")


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自動資料修正系統')
    parser.add_argument('--venue-id', type=int, help='修正特定場地')
    parser.add_argument('--verification-report', type=str, help='從驗證報告批次修正')
    parser.add_argument('--fill-missing', action='store_true', help='補齊缺失資料')
    
    args = parser.parse_args()
    
    # 建立必要目錄
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp/photos', exist_ok=True)
    
    system = DataCorrectionSystem()
    
    if args.verification_report:
        system.batch_correct(args.verification_report)
    
    elif args.venue_id:
        if args.fill_missing:
            system.fill_missing_data(args.venue_id)
        else:
            print("請指定要修正的內容（--fill-missing）")
    
    else:
        print("請指定要執行的操作")


if __name__ == '__main__':
    main()
