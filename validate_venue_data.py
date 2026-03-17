#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
場地資料驗證腳本
用途：在資料匯入前進行完整驗證，確保源頭資料品質

核心原則：資料在源頭就應該正確，不是事後清理

作者：Jobs (Global CTO)
日期：2026-03-17
版本：1.0
"""

import json
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup


class VenueValidator:
    """場地資料驗證器"""
    
    # 必填欄位定義
    REQUIRED_FIELDS = [
        'name', 'venueType', 'city', 'address', 
        'contactPhone', 'url'
    ]
    
    # 建議填寫欄位
    RECOMMENDED_FIELDS = [
        'contactPerson', 'contactEmail', 'priceHalfDay', 
        'priceFullDay', 'maxCapacityTheater', 'maxCapacityClassroom',
        'equipment'
    ]
    
    # 台灣縣市清單
    TAIWAN_CITIES = [
        '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市',
        '基隆市', '新竹市', '嘉義市', '新竹縣', '苗栗縣', '彰化縣',
        '南投縣', '雲林縣', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣',
        '台東縣', '澎湖縣', '金門縣', '連江縣'
    ]
    
    # 場地類型清單
    VENUE_TYPES = [
        '飯店', '會議中心', '咖啡廳', '餐廳', '活動場地',
        '共同工作空間', '學校', '社區中心', '其他'
    ]
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_venue(self, venue: Dict) -> Dict:
        """
        驗證單一場地資料
        
        Args:
            venue: 場地資料字典
        
        Returns:
            驗證結果字典，包含：
            - venue: 原始場地資料
            - errors: 錯誤清單
            - warnings: 警告清單
            - info: 資訊提示
            - qualityScore: 品質評分 (0-100)
            - qualityGrade: 品質等級 (A/B/C)
            - canImport: 是否可匯入
            - status: 狀態 (OK/WARNING/CRITICAL_ERROR)
        """
        
        # 重置記錄
        self.errors = []
        self.warnings = []
        self.info = []
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"驗證場地: {venue.get('name', '未命名')}")
            print(f"{'='*60}")
        
        # 1. 必填欄位檢查
        self._check_required_fields(venue)
        
        # 2. 格式驗證
        self._check_formats(venue)
        
        # 3. 官網驗證（可選）
        if venue.get('url'):
            self._verify_website(venue)
        
        # 4. 照片驗證
        self._check_images(venue)
        
        # 5. 會議室驗證
        if venue.get('rooms'):
            self._check_rooms(venue)
        
        # 6. 計算品質評分
        score = self._calculate_quality_score(venue)
        
        # 7. 組織結果
        result = {
            'venue': venue,
            'venueId': venue.get('id'),
            'venueName': venue.get('name'),
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'qualityScore': score,
            'qualityGrade': self._get_grade(score),
            'canImport': len(self.errors) == 0,
            'status': self._get_status(),
            'validatedAt': datetime.now().isoformat()
        }
        
        if self.verbose:
            self._print_result(result)
        
        return result
    
    def _check_required_fields(self, venue: Dict):
        """檢查必填欄位"""
        
        for field in self.REQUIRED_FIELDS:
            value = venue.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                self.errors.append(f"缺少必填欄位: {field}")
            else:
                if self.verbose:
                    print(f"✓ {field}: {value}")
    
    def _check_formats(self, venue: Dict):
        """檢查格式"""
        
        # 1. 縣市格式
        city = venue.get('city', '')
        if city and city not in self.TAIWAN_CITIES:
            self.warnings.append(f"縣市格式不符: {city}")
        
        # 2. 場地類型
        venue_type = venue.get('venueType', '')
        if venue_type and venue_type not in self.VENUE_TYPES:
            self.info.append(f"場地類型非標準: {venue_type}")
        
        # 3. 電話格式
        phone = venue.get('contactPhone', '')
        if phone:
            # 允許多種格式：02-1234-5678, (02)1234-5678, 0912-345-678
            if not re.match(r'^[\d\-\(\)\s#ext]+$', phone):
                self.warnings.append(f"電話格式非標準: {phone}")
            elif '請洽' in phone or '各分店' in phone:
                self.warnings.append(f"電話非具體號碼: {phone}")
        
        # 4. Email 格式
        email = venue.get('contactEmail', '')
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self.warnings.append(f"Email 格式錯誤: {email}")
        
        # 5. URL 格式
        url = venue.get('url', '')
        if url and not url.startswith(('http://', 'https://')):
            self.errors.append(f"URL 格式錯誤: {url}")
        
        # 6. 價格範圍檢查
        if venue.get('priceHalfDay'):
            price = venue['priceHalfDay']
            if not isinstance(price, (int, float)):
                self.warnings.append(f"半日價格非數字: {price}")
            elif not (500 <= price <= 200000):
                self.warnings.append(f"半日價格異常: {price}")
        
        if venue.get('priceFullDay'):
            price = venue['priceFullDay']
            if not isinstance(price, (int, float)):
                self.warnings.append(f"全日價格非數字: {price}")
            elif not (1000 <= price <= 400000):
                self.warnings.append(f"全日價格異常: {price}")
        
        # 7. 容納人數檢查
        for field in ['maxCapacityTheater', 'maxCapacityClassroom']:
            if venue.get(field):
                capacity = venue[field]
                if not isinstance(capacity, int):
                    self.warnings.append(f"{field} 非整數: {capacity}")
                elif not (5 <= capacity <= 10000):
                    self.warnings.append(f"{field} 異常: {capacity}")
    
    def _verify_website(self, venue: Dict):
        """驗證官網"""
        
        url = venue.get('url', '')
        if not url:
            return
        
        if self.verbose:
            print(f"\n驗證官網: {url}")
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code != 200:
                self.warnings.append(f"官網無法訪問: HTTP {response.status_code}")
                return
            
            # 檢查標題是否包含場地名稱
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            venue_name = venue.get('name', '')
            
            if title and venue_name:
                if venue_name not in title.text:
                    self.info.append("場地名稱與官網標題不完全吻合")
            
            if self.verbose:
                print(f"✓ 官網可訪問")
            
        except requests.exceptions.Timeout:
            self.warnings.append("官網連線逾時")
        except requests.exceptions.ConnectionError:
            self.warnings.append("官網連線失敗")
        except Exception as e:
            self.warnings.append(f"官網驗證失敗: {str(e)}")
    
    def _check_images(self, venue: Dict):
        """檢查照片"""
        
        images = venue.get('images', {})
        
        # 主照片
        if not images.get('main'):
            self.warnings.append("缺少場地主照片")
        else:
            if self.verbose:
                print(f"✓ 主照片: {images['main'][:50]}...")
        
        # 照片來源
        if not images.get('source'):
            self.info.append("缺少照片來源資訊")
    
    def _check_rooms(self, venue: Dict):
        """檢查會議室資料"""
        
        rooms = venue.get('rooms', [])
        
        if self.verbose:
            print(f"\n檢查 {len(rooms)} 個會議室:")
        
        for i, room in enumerate(rooms, 1):
            room_name = room.get('name', f'會議室 {i}')
            
            # 檢查名稱
            if not room.get('name'):
                self.warnings.append(f"會議室 {i} 缺少名稱")
            
            # 檢查照片
            room_images = room.get('images', {})
            # 處理 images 可能是列表的情況
            if isinstance(room_images, list):
                if len(room_images) == 0:
                    self.warnings.append(f"會議室 '{room_name}' 缺少照片")
                else:
                    if self.verbose:
                        print(f"  ✓ {room_name}: 有照片")
            elif not room_images.get('main'):
                self.warnings.append(f"會議室 '{room_name}' 缺少照片")
            else:
                if self.verbose:
                    print(f"  ✓ {room_name}: 有照片")
            
            # 檢查容納人數
            if room.get('capacity'):
                capacity = room['capacity']
                if not isinstance(capacity, int):
                    self.warnings.append(f"會議室 '{room_name}' 容納人數非整數")
    
    def _calculate_quality_score(self, venue: Dict) -> float:
        """計算品質評分"""
        
        score = 0
        
        # 1. 必填欄位完整度 (40分)
        filled_required = sum(1 for f in self.REQUIRED_FIELDS if venue.get(f))
        score += (filled_required / len(self.REQUIRED_FIELDS)) * 40
        
        # 2. 格式正確性 (20分)
        if len(self.errors) == 0:
            score += 20
        elif len(self.errors) <= 2:
            score += 10
        
        # 3. 官網可訪問 (15分)
        url = venue.get('url', '')
        if url.startswith('http'):
            # 簡化驗證，只要 URL 格式正確就給分
            score += 15
        
        # 4. 照片完整度 (15分)
        if venue.get('images', {}).get('main'):
            score += 5
        
        rooms = venue.get('rooms', [])
        if rooms:
            rooms_with_photos = 0
            for r in rooms:
                images = r.get('images', {})
                # 處理 images 可能是列表的情況
                if isinstance(images, list) and len(images) > 0:
                    rooms_with_photos += 1
                elif isinstance(images, dict) and images.get('main'):
                    rooms_with_photos += 1
            
            score += (rooms_with_photos / len(rooms)) * 10
        else:
            # 沒有會議室資料，給一半分數
            score += 5
        
        # 5. 選填欄位完整度 (10分)
        filled_optional = sum(1 for f in self.RECOMMENDED_FIELDS if venue.get(f))
        score += (filled_optional / len(self.RECOMMENDED_FIELDS)) * 10
        
        return round(score, 1)
    
    def _get_grade(self, score: float) -> str:
        """根據評分取得等級"""
        
        if score >= 90:
            return 'A'
        elif score >= 70:
            return 'B'
        else:
            return 'C'
    
    def _get_status(self) -> str:
        """決定狀態"""
        
        if len(self.errors) > 0:
            return 'CRITICAL_ERROR'
        elif len(self.warnings) > 0:
            return 'WARNING'
        else:
            return 'OK'
    
    def _print_result(self, result: Dict):
        """列印驗證結果"""
        
        print(f"\n{'='*60}")
        print(f"驗證結果")
        print(f"{'='*60}")
        print(f"品質評分: {result['qualityScore']} 分")
        print(f"品質等級: {result['qualityGrade']}")
        print(f"狀態: {result['status']}")
        print(f"可匯入: {'是' if result['canImport'] else '否'}")
        
        if result['errors']:
            print(f"\n❌ 錯誤 ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print(f"\n⚠️  警告 ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['info']:
            print(f"\nℹ️  資訊 ({len(result['info'])}):")
            for info in result['info']:
                print(f"  - {info}")
        
        print(f"\n{'='*60}\n")


def validate_single_venue(venue_file: str, verbose: bool = True) -> Dict:
    """驗證單一場地 JSON 檔案"""
    
    try:
        with open(venue_file, 'r', encoding='utf-8') as f:
            venue = json.load(f)
    except FileNotFoundError:
        print(f"❌ 錯誤: 找不到檔案 {venue_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 錯誤: JSON 格式錯誤 - {e}")
        sys.exit(1)
    
    validator = VenueValidator(verbose=verbose)
    return validator.validate_venue(venue)


def validate_all_venues(venues_file: str, verbose: bool = False) -> Dict:
    """驗證所有場地"""
    
    try:
        with open(venues_file, 'r', encoding='utf-8') as f:
            venues = json.load(f)
    except FileNotFoundError:
        print(f"❌ 錯誤: 找不到檔案 {venues_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 錯誤: JSON 格式錯誤 - {e}")
        sys.exit(1)
    
    if not isinstance(venues, list):
        print(f"❌ 錯誤: venues.json 格式錯誤（應為陣列）")
        sys.exit(1)
    
    print(f"\n開始驗證 {len(venues)} 個場地...")
    print(f"{'='*60}\n")
    
    validator = VenueValidator(verbose=False)
    results = []
    
    # 統計資料
    stats = {
        'total': len(venues),
        'grade_a': 0,
        'grade_b': 0,
        'grade_c': 0,
        'can_import': 0,
        'cannot_import': 0,
        'total_errors': 0,
        'total_warnings': 0
    }
    
    for i, venue in enumerate(venues, 1):
        result = validator.validate_venue(venue)
        results.append(result)
        
        # 更新統計
        grade = result['qualityGrade']
        if grade == 'A':
            stats['grade_a'] += 1
        elif grade == 'B':
            stats['grade_b'] += 1
        else:
            stats['grade_c'] += 1
        
        if result['canImport']:
            stats['can_import'] += 1
        else:
            stats['cannot_import'] += 1
        
        stats['total_errors'] += len(result['errors'])
        stats['total_warnings'] += len(result['warnings'])
        
        # 顯示進度
        if i % 10 == 0 or i == len(venues):
            print(f"進度: {i}/{len(venues)} ({i/len(venues)*100:.1f}%)")
    
    # 輸出報告
    print(f"\n{'='*60}")
    print(f"驗證報告")
    print(f"{'='*60}")
    print(f"總場地數: {stats['total']}")
    print(f"\n品質分佈:")
    print(f"  A 級（優質）: {stats['grade_a']} ({stats['grade_a']/stats['total']*100:.1f}%)")
    print(f"  B 級（良好）: {stats['grade_b']} ({stats['grade_b']/stats['total']*100:.1f}%)")
    print(f"  C 級（待補充）: {stats['grade_c']} ({stats['grade_c']/stats['total']*100:.1f}%)")
    print(f"\n匯入狀態:")
    print(f"  可匯入: {stats['can_import']} ({stats['can_import']/stats['total']*100:.1f}%)")
    print(f"  不可匯入: {stats['cannot_import']} ({stats['cannot_import']/stats['total']*100:.1f}%)")
    print(f"\n問題統計:")
    print(f"  總錯誤數: {stats['total_errors']}")
    print(f"  總警告數: {stats['total_warnings']}")
    
    # 列出不可匯入的場地
    if stats['cannot_import'] > 0:
        print(f"\n{'='*60}")
        print(f"不可匯入的場地清單:")
        print(f"{'='*60}")
        for result in results:
            if not result['canImport']:
                print(f"\n{result['venueName']} (ID: {result['venueId']})")
                print(f"  評分: {result['qualityScore']} ({result['qualityGrade']})")
                for error in result['errors']:
                    print(f"  ❌ {error}")
    
    return {
        'results': results,
        'stats': stats,
        'validatedAt': datetime.now().isoformat()
    }


def generate_quality_report(venues_file: str, output_file: str = None):
    """生成品質報告"""
    
    if not output_file:
        output_file = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    results = validate_all_venues(venues_file, verbose=False)
    
    # 保存報告
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 品質報告已保存至: {output_file}")
    
    return results


def main():
    """主程式"""
    
    parser = argparse.ArgumentParser(
        description='場地資料驗證工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 驗證單一場地
  python3 validate_venue_data.py venue.json
  
  # 驗證所有場地
  python3 validate_venue_data.py --all venues.json
  
  # 生成品質報告
  python3 validate_venue_data.py --report venues.json
  
  # 安靜模式（不顯示詳細資訊）
  python3 validate_venue_data.py --quiet venue.json
        """
    )
    
    parser.add_argument(
        'file',
        help='場地資料 JSON 檔案路徑'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='驗證所有場地（檔案應為場地陣列）'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成品質報告並保存為 JSON'
    )
    
    parser.add_argument(
        '--output',
        help='報告輸出檔案路徑（搭配 --report 使用）'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='安靜模式，減少輸出'
    )
    
    parser.add_argument(
        '--check-required',
        action='store_true',
        help='只檢查必填欄位'
    )
    
    parser.add_argument(
        '--check-format',
        action='store_true',
        help='只檢查格式'
    )
    
    parser.add_argument(
        '--verify-website',
        action='store_true',
        help='只驗證官網'
    )
    
    parser.add_argument(
        '--quality-score',
        action='store_true',
        help='只計算品質評分'
    )
    
    args = parser.parse_args()
    
    # 處理不同的驗證模式
    if args.all:
        validate_all_venues(args.file, verbose=not args.quiet)
    elif args.report:
        generate_quality_report(args.file, args.output)
    else:
        # 單一場地驗證
        result = validate_single_venue(args.file, verbose=not args.quiet)
        
        # 根據指定的檢查項目輸出
        if args.check_required:
            print(f"\n必填欄位檢查:")
            print(f"  錯誤: {len([e for e in result['errors'] if '必填' in e])}")
        
        if args.check_format:
            print(f"\n格式驗證:")
            print(f"  錯誤: {len([e for e in result['errors'] if '格式' in e])}")
            print(f"  警告: {len([w for w in result['warnings'] if '格式' in w])}")
        
        if args.verify_website:
            print(f"\n官網驗證:")
            print(f"  警告: {len([w for w in result['warnings'] if '官網' in w])}")
        
        if args.quality_score:
            print(f"\n品質評分: {result['qualityScore']} ({result['qualityGrade']})")
        
        # 如果沒有指定特定檢查，顯示完整結果
        if not any([args.check_required, args.check_format, args.verify_website, args.quality_score]):
            if args.quiet:
                # 安靜模式只顯示摘要
                print(f"{result['venueName']}: {result['qualityScore']}分 ({result['qualityGrade']}) - {result['status']}")
            
            # 返回狀態碼
            sys.exit(0 if result['canImport'] else 1)


if __name__ == '__main__':
    main()
