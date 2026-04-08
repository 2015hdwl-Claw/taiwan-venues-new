#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讀取南港展覽館官方 PDF 並提取正確的會議室資料
"""
import sys
import PyPDF2


def read_pdf_local():
    """讀取本地 PDF 檔案"""
    # 用戶提供的路徑
    pdf_path = r"C:\Users\le202\Downloads\外貿協會台北南港展覽館1館會議室租用收費基準.pdf"

    print("="*80)
    print("讀取南港展覽館官方 PDF")
    print("="*80)
    print(f"路徑: {pdf_path}")
    print()

    try:
        # 開啟 PDF
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            print(f"[OK] PDF 頁數: {len(reader.pages)}")
            print()

            # 提取所有頁面的文字
            all_text = ""

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                all_text += f"\n=== 第 {page_num + 1} 頁 ===\n"
                all_text += text

            # 儲存文字內容
            with open('nangang_pdf_text.txt', 'w', encoding='utf-8') as f:
                f.write(all_text)

            print(f"[OK] 已儲存文字內容: nangang_pdf_text.txt")
            print()

            # 分析會議室資料
            analyze_pdf_rooms(all_text)

    except FileNotFoundError:
        print(f"[ERROR] 找不到檔案: {pdf_path}")
        print()
        print("請確認檔案路徑是否正確")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def analyze_pdf_rooms(text):
    """分析 PDF 中的會議室資料"""
    import re

    print("="*80)
    print("分析會議室資料")
    print("="*80)
    print()

    # 尋找會議室名稱
    # 常見模式：尋找包含數字或特定名稱的會議室

    # 模式1: 尋找表格中的會議室資料
    lines = text.split('\n')

    rooms = []
    current_floor = None

    for i, line in enumerate(lines):
        line = line.strip()

        # 跳過空行
        if not line:
            continue

        # 尋找樓層
        if '樓' in line and ('會議室' in line or '會議' in line):
            if '3樓' in line:
                current_floor = '3樓'
            elif '4樓' in line:
                current_floor = '4樓'
            elif '5樓' in line:
                current_floor = '5樓'

        # 尋找會議室名稱
        # 常見模式: 純數字（401, 402等）或特定名稱（福軒、宴會廳等）
        if re.match(r'^\d{3}$', line) or re.match(r'^(福軒|宴會廳|貴賓室)', line):
            room_name = line
            rooms.append({
                'name': room_name,
                'floor': current_floor,
                'line_number': i
            })

    # 顯示找到的會議室
    print(f"找到 {len(rooms)} 個會議室:")
    print()

    for room in rooms:
        print(f"  - {room['name']} ({room['floor']})")

    print()

    # 尋找價格資料
    print("="*80)
    print("價格資料")
    print("="*80)
    print()

    # 尋找 $ 或 NT$
    price_pattern = r'\$[\d,]+|NT\$[\d,]+|[\d,]+ 元'
    prices = re.findall(price_pattern, text)

    if prices:
        print(f"找到 {len(prices)} 個價格資料:")
        for price in prices[:20]:  # 只顯示前20個
            print(f"  - {price}")

    print()

    # 儲存會議室清單
    with open('nangang_pdf_rooms.txt', 'w', encoding='utf-8') as f:
        f.write("從 PDF 提取的會議室清單\n")
        f.write("="*80 + "\n\n")

        for room in rooms:
            f.write(f"{room['name']} ({room['floor']})\n")

        f.write(f"\n總計: {len(rooms)} 個會議室\n")

    print(f"[OK] 已儲存會議室清單: nangang_pdf_rooms.txt")


def main():
    success = read_pdf_local()

    if success:
        print()
        print("="*80)
        print("完成")
        print("="*80)
        print()
        print("下一步:")
        print("  1. 檢視 nangang_pdf_text.txt (完整文字)")
        print("  2. 檢視 nangang_pdf_rooms.txt (會議室清單)")
        print("  3. 對比 venues.json 中的資料")
        print("  4. 更新正確的會議室數量和資料")


if __name__ == '__main__':
    main()
