#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 TICC PDF 結構
"""
import requests
import PyPDF2
import io
import re
import sys
import json
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == 'win32':
    import io as sys_io
    sys.stdout = sys_io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def analyze_ticc_pdf():
    """分析 TICC PDF"""
    pdf_url = "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf"

    print("="*80)
    print("TICC PDF 結構分析")
    print("="*80)
    print()
    print(f"PDF URL: {pdf_url}")
    print()

    try:
        # 下載 PDF
        print("[1/4] 下載 PDF...")
        response = requests.get(pdf_url, timeout=30, verify=False)
        if response.status_code != 200:
            print(f"❌ 下載失敗: HTTP {response.status_code}")
            return

        print(f"✅ 下載成功: {len(response.content)} bytes")

        # 解析 PDF
        print("[2/4] 解析 PDF...")
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        print(f"✅ 頁數: {len(pdf_reader.pages)}")
        print()

        # 提取所有文字
        print("[3/4] 提取文字內容...")
        all_text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text = page.extract_text()
            all_text += f"\n--- 第 {page_num} 頁 ---\n{text}\n"

        # 儲存原始文字
        with open('ticc_pdf_text.txt', 'w', encoding='utf-8') as f:
            f.write(all_text)
        print(f"✅ 原始文字已儲存至 ticc_pdf_text.txt")
        print()

        # 分析結構
        print("[4/4] 分析資料結構...")
        print("-"*80)

        # 尋找會議室相關的模式
        lines = all_text.split('\n')

        rooms = []
        current_room = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 嘗試識別會議室名稱
            # TICC 常見格式: "第一會議室", "A+會議室", "國際會議廳" 等
            room_patterns = [
                r'^(第[一二三四五六七八九十]+會議室)',
                r'^([A-Z]\+?會議室)',
                r'^(國際會議廳)',
                r'^(.*?會議室)',
            ]

            matched = False
            for pattern in room_patterns:
                match = re.match(pattern, line)
                if match:
                    # 儲存前一個會議室
                    if current_room:
                        rooms.append(current_room)

                    # 新會議室
                    current_room = {
                        'name': match.group(1),
                        'raw_lines': [line]
                    }
                    matched = True
                    break

            if not matched and current_room:
                # 加入當前會議室的資料
                current_room['raw_lines'].append(line)

        # 儲存最後一個會議室
        if current_room:
            rooms.append(current_room)

        print(f"✅ 找到 {len(rooms)} 個可能的會議室")
        print()

        # 顯示前幾個會議室的原始資料
        print("【前 5 個會議室的原始資料】")
        for i, room in enumerate(rooms[:5], 1):
            print(f"\n{i}. {room['name']}")
            print("   原始資料:")
            for line in room['raw_lines'][:10]:
                print(f"     {line}")

        # 嘗試解析欄位
        print()
        print("-"*80)
        print("【嘗試自動解析欄位】")
        print()

        parsed_rooms = []

        for room in rooms:
            room_data = {
                'name': room['name'],
                'capacity': None,
                'area': None,
                'price': None
            }

            # 合併所有文字
            full_text = ' '.join(room['raw_lines'])

            # 容量 (常見格式: 容量: 100人, 100人, etc.)
            capacity_patterns = [
                r'容[纳量量]*[:：]\s*(\d+)\s*人',
                r'(\d+)\s*人',
            ]
            for pattern in capacity_patterns:
                match = re.search(pattern, full_text)
                if match:
                    room_data['capacity'] = match.group(1)
                    break

            # 面積 (常見格式: 面積: 50坪, 50坪, 100m², etc.)
            area_patterns = [
                r'面積[:：]\s*([\d.]+\s*(?:坪|m²|㎡|平方公尺|平方米))',
                r'([\d.]+\s*(?:坪|m²|㎡|平方公尺|平方米))',
            ]
            for pattern in area_patterns:
                match = re.search(pattern, full_text)
                if match:
                    room_data['area'] = match.group(1)
                    break

            # 價格 (常見格式: $10,000, NT$10,000, 10000元, etc.)
            price_patterns = [
                r'(?:NT\$|\$)?\s*([\d,]+)\s*元',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, full_text)
                if match:
                    room_data['price'] = match.group(1)
                    break

            parsed_rooms.append(room_data)

        # 顯示解析結果
        print("【解析結果】")
        for i, room in enumerate(parsed_rooms[:10], 1):
            print(f"\n{i}. {room['name']}")
            print(f"   容量: {room['capacity'] or '未找到'}")
            print(f"   面積: {room['area'] or '未找到'}")
            print(f"   價格: {room['price'] or '未找到'}")

        # 儲存結果
        result = {
            'pdf_url': pdf_url,
            'total_pages': len(pdf_reader.pages),
            'rooms_found': len(parsed_rooms),
            'rooms': parsed_rooms
        }

        with open('ticc_pdf_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print()
        print("="*80)
        print("分析完成")
        print("="*80)
        print(f"結果已儲存至:")
        print(f"  - ticc_pdf_text.txt (原始文字)")
        print(f"  - ticc_pdf_analysis.json (解析結果)")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    analyze_ticc_pdf()
