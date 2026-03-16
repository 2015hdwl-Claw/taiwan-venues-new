#!/usr/bin/env python3
"""
自動化主控制系統
功能：整合驗證、修正、同步流程
作者：Jobs (Global CTO)
日期：2026-03-17
"""

import json
import sys
from datetime import datetime
import logging
from typing import List, Dict
import argparse

# 導入子系統
from auto_verification_engine import DataVerificationEngine
from auto_correction_system import DataCorrectionSystem
from auto_sync_system import AutoSyncSystem

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_master.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoMaster:
    """自動化主控制系統"""
    
    def __init__(self):
        self.verification_engine = DataVerificationEngine()
        self.correction_system = DataCorrectionSystem()
        self.sync_system = AutoSyncSystem()
        self.session_log = {
            'start_time': datetime.now().isoformat(),
            'steps': []
        }
    
    def run_full_cycle(self, venue_ids: List[int] = None, city: str = None, limit: int = None):
        """執行完整週期：驗證 → 修正 → 同步"""
        logger.info("="*60)
        logger.info("開始自動化完整週期")
        logger.info("="*60)
        
        # Step 1: 驗證
        logger.info("\n[Step 1/3] 資料驗證")
        logger.info("-"*60)
        
        verification_results = self.verification_engine.verify_batch(
            venue_ids=venue_ids,
            city=city,
            limit=limit
        )
        
        verification_summary = self.verification_engine.get_summary()
        self.session_log['steps'].append({
            'name': 'verification',
            'summary': verification_summary
        })
        
        # Step 2: 修正
        logger.info("\n[Step 2/3] 資料修正")
        logger.info("-"*60)
        
        corrections_count = 0
        for result in verification_results:
            if result.get('differences'):
                venue_id = result['venue_id']
                differences = result['differences']
                
                if self.correction_system.auto_correct(venue_id, differences):
                    corrections_count += 1
        
        logger.info(f"修正完成: {corrections_count} 個場地")
        
        self.session_log['steps'].append({
            'name': 'correction',
            'count': corrections_count
        })
        
        # Step 3: 同步
        logger.info("\n[Step 3/3] 同步到生產環境")
        logger.info("-"*60)
        
        sync_success = self.sync_system.sync_to_production(
            changes=[{
                'type': 'venue_update',
                'count': corrections_count
            }]
        )
        
        self.session_log['steps'].append({
            'name': 'sync',
            'success': sync_success
        })
        
        # 完成
        self.session_log['end_time'] = datetime.now().isoformat()
        self.session_log['success'] = sync_success
        
        self.save_session_log()
        self.print_final_report()
        
        return sync_success
    
    def verify_only(self, venue_ids: List[int] = None, city: str = None, limit: int = None):
        """只執行驗證"""
        logger.info("執行驗證...")
        
        results = self.verification_engine.verify_batch(
            venue_ids=venue_ids,
            city=city,
            limit=limit
        )
        
        summary = self.verification_engine.get_summary()
        
        print("\n" + "="*60)
        print("驗證結果")
        print("="*60)
        print(f"總計: {summary['total']}")
        print(f"成功: {summary['success']}")
        print(f"失敗: {summary['failed']}")
        print(f"無 URL: {summary['no_url']}")
        print(f"有差異: {summary['with_differences']}")
        print(f"準確率: {summary['accuracy_rate']:.1f}%")
        print("="*60)
        
        return results
    
    def correct_only(self, venue_ids: List[int] = None):
        """只執行修正"""
        logger.info("執行修正...")
        
        count = 0
        for venue_id in venue_ids or []:
            if self.correction_system.fill_missing_data(venue_id):
                count += 1
        
        print(f"\n修正完成: {count} 個場地")
        return count
    
    def sync_only(self):
        """只執行同步"""
        logger.info("執行同步...")
        
        success = self.sync_system.sync_to_production()
        
        print(f"\n同步結果: {'成功' if success else '失敗'}")
        return success
    
    def save_session_log(self):
        """儲存會話日誌"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'logs/session_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.session_log, f, ensure_ascii=False, indent=2)
        
        logger.info(f"會話日誌已儲存: {filename}")
    
    def print_final_report(self):
        """列印最終報告"""
        print("\n" + "="*60)
        print("自動化執行報告")
        print("="*60)
        print(f"開始時間: {self.session_log['start_time']}")
        print(f"結束時間: {self.session_log['end_time']}")
        print(f"執行結果: {'成功' if self.session_log['success'] else '失敗'}")
        print("\n執行步驟:")
        
        for i, step in enumerate(self.session_log['steps'], 1):
            print(f"  {i}. {step['name']}: {step}")
        
        print("="*60)


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='自動化主控制系統')
    
    # 操作模式
    parser.add_argument('--full', action='store_true', help='執行完整週期（驗證→修正→同步）')
    parser.add_argument('--verify', action='store_true', help='只執行驗證')
    parser.add_argument('--correct', action='store_true', help='只執行修正')
    parser.add_argument('--sync', action='store_true', help='只執行同步')
    
    # 篩選條件
    parser.add_argument('--city', type=str, help='只處理特定縣市')
    parser.add_argument('--limit', type=int, help='限制處理數量')
    parser.add_argument('--venue-ids', type=int, nargs='+', help='指定場地 ID')
    
    args = parser.parse_args()
    
    # 建立必要目錄
    import os
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp/photos', exist_ok=True)
    
    # 執行
    master = AutoMaster()
    
    if args.full:
        success = master.run_full_cycle(
            venue_ids=args.venue_ids,
            city=args.city,
            limit=args.limit
        )
        sys.exit(0 if success else 1)
    
    elif args.verify:
        master.verify_only(
            venue_ids=args.venue_ids,
            city=args.city,
            limit=args.limit
        )
    
    elif args.correct:
        master.correct_only(venue_ids=args.venue_ids)
    
    elif args.sync:
        master.sync_only()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
