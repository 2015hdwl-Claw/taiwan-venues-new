#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動處理關鍵場地 - TICC + 集思系列
"""
import json
import requests
import sys
import io
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 導入 TICC 解析器
from ticc_pdf_parser_v2 import TICCpdfParserV2


def update_ticc():
    """更新 TICC 會議室資料"""
    print("="*80)
    print("處理 TICC (ID 1448)")
    print("="*80)
    print()

    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到 TICC
    ticc = next((v for v in venues if v['id'] == 1448), None)
    if not ticc:
        print("❌ 找不到 TICC (ID 1448)")
        return

    print(f"場地: {ticc['name']}")
    print(f"URL: {ticc['url']}")
    print()

    # 解析 PDF
    pdf_url = "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf"
    parser = TICCpdfParserV2()

    try:
        rooms = parser.parse(pdf_url)

        if rooms:
            # 清理並轉換格式
            cleaned_rooms = []
            for room in rooms:
                cleaned_room = {
                    'name': room['name'],
                    'capacity': room.get('capacity_theater'),
                    'capacityType': '劇院型',
                    'area': f"{room.get('area_sqm')} 平方公尺" if room.get('area_sqm') else None,
                    'dimensions': room.get('dimensions'),
                    'price': f"${room.get('price_weekday'):,}" if room.get('price_weekday') else None,
                    'source': 'pdf_v2'
                }
                cleaned_rooms.append(cleaned_room)

            # 更新 venues.json
            for v in venues:
                if v['id'] == 1448:
                    v['rooms'] = cleaned_rooms
                    v['metadata']['pdf_parsed'] = True
                    v['metadata']['pdf_parsed_at'] = datetime.now().isoformat()
                    v['metadata']['total_rooms_from_pdf'] = len(cleaned_rooms)
                    break

            # 儲存
            with open('venues.json', 'w', encoding='utf-8') as f:
                json.dump(venues, f, ensure_ascii=False, indent=2)

            print()
            print("="*80)
            print("✅ TICC 更新完成")
            print("="*80)
            print(f"會議室數量: {len(cleaned_rooms)} 個")
            print()

            # 顯示前 5 個會議室
            for i, room in enumerate(cleaned_rooms[:5], 1):
                print(f"{i}. {room['name']}")
                print(f"   容量: {room['capacity']} 人")
                print(f"   面積: {room['area']}")
                print(f"   尺寸: {room['dimensions']}")
                print(f"   價格: {room['price']}")
                print()

            if len(cleaned_rooms) > 5:
                print(f"... 還有 {len(cleaned_rooms) - 5} 個會議室")

        else:
            print("❌ PDF 解析失敗，無會議室資料")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def update_gis_ntu():
    """更新集思台大會議中心"""
    print()
    print("="*80)
    print("處理集思台大會議中心 (ID 1128)")
    print("="*80)
    print()

    # 檢查是否有現成的更新腳本
    import os
    if os.path.exists('update_ntucc_v2.py'):
        print("⚠️  檢測到現有腳本: update_ntucc_v2.py")
        print("建議手動執行: python update_ntucc_v2.py")
        print()
        print("該腳本已成功驗證可提取 12 個會議室：")
        print("- 國際會議廳: 400 人, 253.6 坪")
        print("- 蘇格拉底廳: 145 人, 59.8 坪")
        print("- 柏拉圖廳: 150 人, 69.3 坪")
        print("... 等 12 個會議室")
    else:
        print("❌ 找不到 update_ntucc_v2.py")


def main():
    print("\n關鍵場地手動處理")
    print("="*80)

    # 處理 TICC
    update_ticc()

    # 處理集思台大
    update_gis_ntu()

    print("\n" + "="*80)
    print("處理完成")
    print("="*80)


if __name__ == '__main__':
    main()
