#!/usr/bin/env python3
"""
每日自動執行排程
功能：每日自動驗證、修正、同步
作者：Jobs (Global CTO)
日期：2026-03-17
"""

import schedule
import time
import logging
from datetime import datetime
import random
from auto_master import AutoMaster
import json

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DailyScheduler:
    """每日自動執行排程"""
    
    def __init__(self):
        self.master = AutoMaster()
        self.all_venue_ids = self.load_all_venue_ids()
    
    def load_all_venue_ids(self):
        """載入所有場地 ID"""
        with open('venues.json', 'r', encoding='utf-8') as f:
            venues = json.load(f)
        return [v['id'] for v in venues]
    
    def daily_verification(self):
        """每日驗證（隨機抽取 10%）"""
        logger.info("="*60)
        logger.info("開始每日驗證")
        logger.info("="*60)
        
        # 隨機抽取 10% 場地
        sample_size = max(1, len(self.all_venue_ids) // 10)
        sampled_ids = random.sample(self.all_venue_ids, sample_size)
        
        logger.info(f"隨機抽取 {sample_size} 個場地進行驗證")
        
        # 執行驗證
        results = self.master.verify_only(venue_ids=sampled_ids)
        
        # 檢查是否有差異
        has_differences = any(r.get('differences') for r in results)
        
        if has_differences:
            logger.info("發現差異，執行自動修正...")
            # 執行完整週期
            self.master.run_full_cycle(venue_ids=sampled_ids)
        else:
            logger.info("資料一致，無需修正")
    
    def weekly_deep_verification(self):
        """每週深度驗證（所有場地）"""
        logger.info("="*60)
        logger.info("開始每週深度驗證")
        logger.info("="*60)
        
        # 分批處理，每次 20 個
        batch_size = 20
        total = len(self.all_venue_ids)
        
        for i in range(0, total, batch_size):
            batch = self.all_venue_ids[i:i+batch_size]
            logger.info(f"處理批次 {i//batch_size + 1}/{(total-1)//batch_size + 1}")
            
            # 執行完整週期
            self.master.run_full_cycle(venue_ids=batch)
            
            # 避免過度請求
            time.sleep(10)
        
        logger.info("每週深度驗證完成")
    
    def monthly_full_sync(self):
        """每月完整同步"""
        logger.info("="*60)
        logger.info("開始每月完整同步")
        logger.info("="*60)
        
        # 強制同步所有資料
        self.master.sync_only()
        
        logger.info("每月完整同步完成")


def main():
    """主程式"""
    scheduler = DailyScheduler()
    
    # 設定排程
    # 每天凌晨 2:00 執行
    schedule.every().day.at("02:00").do(scheduler.daily_verification)
    
    # 每週日凌晨 3:00 執行
    schedule.every().sunday.at("03:00").do(scheduler.weekly_deep_verification)
    
    # 每月 1 日凌晨 4:00 執行
    schedule.every().monday.at("04:00").do(scheduler.monthly_full_sync)
    
    logger.info("排程系統已啟動")
    logger.info("每日驗證: 每天 02:00")
    logger.info("每週深度驗證: 每週日 03:00")
    logger.info("每月完整同步: 每月 1 日 04:00")
    
    # 持續運行
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
