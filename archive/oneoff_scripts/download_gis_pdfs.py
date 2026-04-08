#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並解析集思會議中心官方 PDF
"""
import asyncio
import requests
import PyPDF2
import re
import json
from datetime import datetime


# 所有集思 PDF 連結
GIS_PDFS = [
    {
        "venue_id": 1128,
        "name": "集思台大會議中心(NTUCC)",
        "url": "https://www.meeting.com.tw/ntu/download/%E5%8F%B0%E5%A4%A7_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8_20250401.pdf",
        "filename": "gis_ntu_2025.pdf"
    },
    {
        "venue_id": 1494,
        "name": "集思交通部會議中心(MOTC)",
        "url": "https://www.meeting.com.tw/motc/download/%E4%BA%A4%E9%80%9A%E9%83%A8_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8_20250401.pdf",
        "filename": "gis_motc_2025.pdf"
    },
    {
        "venue_id": 1496,
        "name": "集思台師大会議中心(HSPH)",
        "url": "https://www.meeting.com.tw/wenxin/download/%E5%8F%B0%E4%B8%AD%E6%96%87%E5%BF%83_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8_20260102.pdf",
        "filename": "gis_hsp_2026.pdf"
    },
    {
        "venue_id": 1498,
        "name": "集思烏日會議中心(WURI)",
        "url": "https://www.meeting.com.tw/xinwuri/download/%E5%8F%B0%E4%B8%AD%E6%96%B0%E7%83%8F%E6%97%A5_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E5%80%9F%E7%94%B3%E8%AB%8B%E8%A1%A8_20260102.pdf",
        "filename": "gis_wuri_2026.pdf"
    },
    {
        "venue_id": 1495,
        "name": "集思北科技會議中心(Tech)",
        "url": "https://www.meeting.com.tw/ntut/download/%E5%8C%97%E7%A7%91%E5%A4%A7_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8_20250401.pdf",
        "filename": "gis_ntut_2025.pdf"
    },
    {
        "venue_id": 1497,
        "name": "集思中國醫會議中心(TC)",
        "url": "https://www.meeting.com.tw/hsp/download/%E7%AB%B9%E7%A7%91-%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8-20250402.pdf",
        "filename": "gis_tc_2025.pdf"
    },
]


def download_pdf(pdf_info):
    """Download single PDF"""
    url = pdf_info["url"]
    filename = pdf_info["filename"]
    name = pdf_info["name"]

    print(f"Downloading: {filename}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            content = response.content

            with open(filename, 'wb') as f:
                f.write(content)

            print(f"  [OK] Size: {len(content):,} bytes")
            return True
        else:
            print(f"  [ERROR] HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def parse_pdf_rooms(pdf_info):
    """Parse rooms from PDF"""
    filename = pdf_info["filename"]
    venue_id = pdf_info["venue_id"]

    print()
    print(f"Parsing: {filename}")

    try:
        with open(filename, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            print(f"  Pages: {len(reader.pages)}")

            # Extract all text
            all_text = ""
            for page in reader.pages:
                text = page.extract_text()
                all_text += text + "\n"

            # Save text content
            text_filename = filename.replace('.pdf', '_text.txt')
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(all_text)

            print(f"  [OK] Saved text: {text_filename}")

            # Parse rooms
            rooms = extract_rooms_from_text(all_text, venue_id, pdf_info["name"])

            return rooms

    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_rooms_from_text(text, venue_id, venue_name):
    """從 PDF 文字中提取會議室資料"""
    rooms = []

    # 按行分割
    lines = text.split('\n')

    # 尋找會議室資料行
    # 常見格式：
    # 1. 會議室名稱 + 容量 + 面積
    # 2. 表格格式

    current_room = None

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            continue

        # 尋找會議室名稱
        # 常見模式: 以數字開頭（如 201, 202）或特殊名稱（如 國際會議廳）
        if re.match(r'^(\d{3}|[國國際際會議廳].*|全場|A室|B室|C室)', line):
            # 這可能是會議室名稱
            room_name = line.split()[0] if ' ' in line else line
            current_room = {
                'name': room_name,
                'nameEn': room_name,
                'venue_id': venue_id,
                'capacity': {},
                'area': None,
                'source': 'gis_official_pdf'
            }

        # 尋找容量資料
        # 常見格式: "容納 XX 人" 或 "容量 XX"
        elif re.search(r'容納?\s*容量?\s*(\d+)\s*人', line):
            cap_match = re.search(r'(\d+)\s*人', line)
            if cap_match and current_room:
                capacity = int(cap_match.group(1))
                current_room['capacity']['standard'] = capacity

        # 尋找面積資料
        # 常見格式: "XX 坪" 或 "XX 平方公尺"
        elif re.search(r'(\d+(?:\.\d+)?)\s*坪', line):
            area_match = re.search(r'(\d+(?:\.\d+)?)\s*坪', line)
            if area_match and current_room:
                area = float(area_match.group(1))
                current_room['area'] = area
                current_room['areaUnit'] = '坪'

        # 如果會議室資料完整，加入列表
        if current_room and current_room.get('name') and (current_room.get('capacity') or current_room.get('area')):
            # 生成 ID
            room_name_base = current_room['name'].replace(' ', '_').replace('-', '_')
            current_room['id'] = f"{venue_id}-{room_name_base}"

            rooms.append(current_room)
            current_room = None

    # 如果沒有找到資料，嘗試其他模式
    if not rooms:
        # 嘗試尋找表格格式
        rooms = extract_table_format(text, venue_id)

    print(f"  [OK] Found {len(rooms)} rooms")

    return rooms


def extract_table_format(text, venue_id):
    """提取表格格式的會議室資料"""
    rooms = []

    # 尋找包含會議室資料的行
    lines = text.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()

        # 尋找看起來像會議室資料的行
        # 通常包含：會議室名稱、容量、面積
        if any(keyword in line for keyword in ['會議室', '會議廳', '坪', '人']):
            # 嘗試解析這一行
            parts = line.split()

            if len(parts) >= 3:
                # 第一部分可能是會議室名稱
                room_name = parts[0]

                # 尋找數字（可能是容量或面積）
                numbers = re.findall(r'(\d+(?:\.\d+)?)', line)

                if len(numbers) >= 1:
                    room = {
                        'id': f"{venue_id}_{room_name}",
                        'name': room_name,
                        'nameEn': room_name,
                        'capacity': {},
                        'area': None,
                        'source': 'gis_official_pdf'
                    }

                    # 第一個數字可能是容量
                    if len(numbers) >= 1:
                        try:
                            cap = int(float(numbers[0]))
                            if cap < 1000:  # 合理的容量範圍
                                room['capacity']['standard'] = cap
                        except:
                            pass

                    # 第二個數字可能是面積（坪）
                    if len(numbers) >= 2:
                        try:
                            area = float(numbers[1])
                            if area < 1000:  # 合理的面積範圍
                                room['area'] = area
                                room['areaUnit'] = '坪'
                        except:
                            pass

                    rooms.append(room)

    return rooms


def main():
    print("="*80)
    print("GIS Meeting Centers - Official PDF Download")
    print("="*80)
    print()

    all_results = []

    # Download all PDFs
    print("Step 1: Download PDFs")
    print("-"*80)

    downloaded = []
    for pdf_info in GIS_PDFS:
        success = download_pdf(pdf_info)
        if success:
            downloaded.append(pdf_info)
        print()

    print()
    print(f"Downloaded: {len(downloaded)}/{len(GIS_PDFS)} PDFs")
    print()

    # Parse PDFs
    print("Step 2: Parse PDFs")
    print("-"*80)

    for pdf_info in downloaded:
        rooms = parse_pdf_rooms(pdf_info)

        if rooms:
            all_results.append({
                'venue_id': pdf_info['venue_id'],
                'venue_name': pdf_info['name'],
                'filename': pdf_info['filename'],
                'rooms': rooms,
                'total': len(rooms)
            })

        print()

    # Save results
    print("Step 3: Save Results")
    print("-"*80)

    with open('gis_pdf_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved: gis_pdf_results.json")
    print()

    # Show summary
    print("="*80)
    print("Summary")
    print("="*80)
    print()

    total_rooms = 0
    for result in all_results:
        venue_name = result['venue_name']
        count = result['total']
        total_rooms += count

        print(f"{venue_name}: {count} rooms")

        for room in result['rooms'][:5]:
            cap = room.get('capacity', {}).get('standard', 'N/A')
            area = room.get('area', 'N/A')
            print(f"  - {room['name']}: {cap} people, {area} ping")

        if count > 5:
            print(f"  ... and {count - 5} more")

        print()

    print(f"Total: {total_rooms} rooms from {len(all_results)} venues")
    print()

    print("Next step: Update venues.json")


if __name__ == '__main__':
    main()
