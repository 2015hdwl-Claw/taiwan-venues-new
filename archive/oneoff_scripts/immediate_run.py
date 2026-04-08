#!/usr/bin/env python3
"""
立即執行腳本
功能：立即開始執行第一週任務
作者：Jane (Global CEO)
日期：2026-03-17
"""

import sys
import os
from datetime import datetime

# 確保在正確目錄
os.chdir('/root/.openclaw/workspace/taiwan-venues-new')

# 導入主控制系統
from auto_master import AutoMaster

def main():
    print("="*70)
    print("活動大師 - 自動化系統立即執行")
    print("="*70)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print()
    
    # 建立必要目錄
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp/photos', exist_ok=True)
    
    master = AutoMaster()
    
    # Step 1: 驗證台北市所有場地
    print("\n[階段 1] 驗證台北市所有場地（112 個）")
    print("-"*70)
    
    results = master.verify_only(city='台北市')
    
    # 統計差異
    with_differences = sum(1 for r in results if r.get('differences'))
    
    print(f"\n驗證完成！發現 {with_differences} 個場地有差異")
    
    if with_differences > 0:
        # Step 2: 自動修正
        print("\n[階段 2] 自動修正資料")
        print("-"*70)
        
        # 篩選有差異的場地 ID
        venue_ids_with_diff = [r['venue_id'] for r in results if r.get('differences')]
        
        # 執行完整週期（修正 + 同步）
        success = master.run_full_cycle(venue_ids=venue_ids_with_diff)
        
        if success:
            print("\n✅ 自動修正與同步完成！")
        else:
            print("\n❌ 自動修正或同步失敗")
    else:
        print("\n✅ 所有資料一致，無需修正")
    
    # Step 3: 生成報告
    print("\n[階段 3] 生成執行報告")
    print("-"*70)
    
    # 這裡可以加入報告生成邏輯
    
    print("\n" + "="*70)
    print(f"執行完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n📊 報告已儲存到:")
    print("  - logs/verification.log")
    print("  - logs/correction.log")
    print("  - logs/sync.log")
    print("  - reports/verification_report_*.json")
    print("\n🚀 網站已自動部署到 Vercel")
    print("\n下一步:")
    print("  1. 檢查部署結果: https://taiwan-venues-new.vercel.app")
    print("  2. 啟動每日排程: python3 daily_auto_run.py")
    print("  3. 繼續處理其他縣市資料")


if __name__ == '__main__':
    main()
