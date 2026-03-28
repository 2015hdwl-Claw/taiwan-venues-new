#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速入門：場地爬蟲框架使用示範

這個腳本示範如何使用通用場地爬蟲框架
"""

import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*100)
print("通用場地爬蟲框架 - 快速入門")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("🎯 三種使用方式：")
print("-"*100)

print("\n方式 1：抓取單個場地（測試用）")
print("-"*40)
print("指令:")
print("   python enhanced_venue_scraper.py --venue-id 1076")
print("\n說明:")
print("   → 抓取寒舍艾美酒店（ID: 1076）")
print("   → 適合測試和調整配置")
print("   → 結果會顯示在螢幕上")

print("\n" + "-"*100)
print("\n方式 2：批次抓取所有場地")
print("-"*40)
print("指令:")
print("   python enhanced_venue_scraper.py --batch")
print("\n說明:")
print("   → 抓取配置檔案中的所有場地（52 個）")
print("   → 使用並發處理（預設 5 個同時）")
print("   → 結果儲存至 scraped_venues_*.json")

print("\n" + "-"*100)
print("\n方式 3：生成配置檔案")
print("-"*40)
print("指令:")
print("   python universal_venue_scraper.py --generate-config")
print("\n說明:")
print("   → 從 venues.json 自動生成配置")
print("   → 包含所有 52 個場地")
print("   → 可手動編輯進階規則")

print("\n" + "="*100)
print("📁 檔案說明：")
print("="*100)

files = [
    ("enhanced_venue_scraper.py", "主程式 - 使用這個"),
    ("venue_scraper_config.json", "基本配置（52 場地，自動生成）"),
    ("venue_scraper_config_expanded.json", "進階配置（3 場地範例）"),
    ("README_SCRAPER.md", "完整使用說明"),
    ("OPTION_B_COMPLETE_REPORT.md", "框架完成報告")
]

for filename, description in files:
    print(f"   📄 {filename:<45} - {description}")

print("\n" + "="*100)
print("🚀 推薦工作流程：")
print("="*100)

print("\n第 1 步：測試單個場地")
print("   python enhanced_venue_scraper.py --venue-id 1043")
print("   → 測試六福萬怡酒店")

print("\n第 2 步：查看結果")
print("   → 結果會儲存為 scraped_venues_YYYYMMDD_HHMMSS.json")
print("   → 開啟 JSON 檔案查看抓取的資料")

print("\n第 3 步：調整配置（如果需要）")
print("   → 編輯 venue_scraper_config_expanded.json")
print("   → 添加特定場地的提取規則")
print("   → 參考 README_SCRAPER.md 的範例")

print("\n第 4 步：批次執行")
print("   python enhanced_venue_scraper.py --batch")
print("   → 抓取所有 52 個場地")

print("\n第 5 步：驗證和更新")
print("   → 檢查 scraped_venues_*.json")
print("   → 人工驗證關鍵場地")
print("   → 更新 venues.json")

print("\n" + "="*100)
print("💡 提示：")
print("="*100)

tips = [
    "配置驅動：只需編輯 JSON，不需改程式碼",
    "多種提取器：CSS、文字模式、表格提取器",
    "並發處理：預設 5 個場地同時抓取",
    "可擴展：可添加自定義提取器",
    "完整文件：查看 README_SCRAPER.md"
]

for i, tip in enumerate(tips, 1):
    print(f"   {i}. {tip}")

print("\n" + "="*100)
print("✅ 準備就緒！")
print("="*100)

print("\n下一步：")
print("   選擇一個場地 ID 進行測試")
print("   例如: python enhanced_venue_scraper.py --venue-id 1043")
print("\n或直接批次執行：")
print("   python enhanced_venue_scraper.py --batch")

print(f"\n開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
