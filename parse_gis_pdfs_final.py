#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析集思 PDF 並更新到 venues.json
"""
import json
import re


def parse_gis_ntu_pdf():
    """解析集思台大 PDF"""
    rooms = []

    # 從文字文件讀取
    with open('gis_ntu_2025_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    # 尋找會議室資料
    # 模式: 會議室名稱 + 容量/面積
    # 例如: "400人/253.6坪"

    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        # 尋找包含容量和面積的行
        if re.search(r'\d+人/\d+(?:\.\d+)?坪', line):
            # 提取容量
            cap_match = re.search(r'(\d+)人/', line)
            # 提取面積
            area_match = re.search(r'/([\d.]+)坪', line)

            # 找會議室名稱（在上一行或前幾行）
            # 通常格式是: "會議室名稱  會議室型態"
            room_name = None

            # 檢查這個會議室是否已經記錄
            # 如果 line 不是開頭，可能會議室名稱在前面

            if cap_match and area_match:
                capacity = int(cap_match.group(1))
                area = float(area_match.group(1))

                # 尋找會議室名稱（從之前的行）
                for i in range(max(0, lines.index(line) - 5), lines.index(line)):
                    prev_line = lines[i].strip()
                    # 常見會議室名稱模式
                    if re.match(r'^[\u4e00-\u9fff]{2,}$|^[^\d\s]{2,}$', prev_line) and '廳' in prev_line:
                        room_name = prev_line
                        break

                if room_name:
                    rooms.append({
                        'id': f"1128-{room_name}",
                        'name': room_name,
                        'nameEn': room_name,
                        'area': area,
                        'areaUnit': '坪',
                        'capacity': {
                            'standard': capacity
                        },
                        'source': 'gis_official_pdf'
                    })

    print(f"NTUCC: Found {len(rooms)} rooms")
    return rooms


def parse_gis_motc_pdf():
    """解析集思交通部 PDF"""
    rooms = []

    with open('gis_motc_2025_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        # 尋找包含容量和面積的行
        if re.search(r'\d+人/\d+(?:\.\d+)?坪', line):
            cap_match = re.search(r'(\d+)人/', line)
            area_match = re.search(r'/([\d.]+)坪', line)

            if cap_match and area_match:
                capacity = int(cap_match.group(1))
                area = float(area_match.group(1))

                # 尋找會議室名稱
                room_name = None
                for i in range(max(0, lines.index(line) - 3), lines.index(line)):
                    prev_line = lines[i].strip()
                    if re.match(r'^[\u4e00-\u9fff\d]+', prev_line) and '會議室' in prev_line:
                        room_name = prev_line.replace('會議室', '').strip()
                        break

                if room_name:
                    rooms.append({
                        'id': f"1494-{room_name}",
                        'name': f"{room_name}會議室",
                        'nameEn': f"{room_name} Meeting Room",
                        'area': area,
                        'areaUnit': '坪',
                        'capacity': {
                            'standard': capacity
                        },
                        'source': 'gis_official_pdf'
                    })

    print(f"MOTC: Found {len(rooms)} rooms")
    return rooms


def parse_gis_tc_pdf():
    """解析集思中國醫 PDF"""
    rooms = []

    with open('gis_tc_2025_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')

    current_room = None

    for line in lines:
        line = line.strip()

        # 尋找會議室名稱行
        # 例如: "201 會議室  容納人數  63  坪數  63  樓層  2樓"
        if re.match(r'^\d+\s+會議室', line):
            parts = line.split()
            if len(parts) >= 6:
                room_num = parts[0]
                capacity = int(parts[2]) if parts[2].isdigit() else None
                area = float(parts[3]) if parts[3].replace('.', '').isdigit() else None
                floor = parts[5].strip()

                if capacity and area:
                    rooms.append({
                        'id': f"1497-{room_num}",
                        'name': f"{room_num}會議室",
                        'nameEn': f"Room {room_num}",
                        'area': area,
                        'areaUnit': '坪',
                        'floor': floor,
                        'capacity': {
                            'standard': capacity
                        },
                        'source': 'gis_official_pdf'
                    })

    print(f"TC: Found {len(rooms)} rooms")
    return rooms


def update_venues_with_pdf_data():
    """使用 PDF 資料更新 venues.json"""
    # 解析所有 PDF
    all_rooms = []

    print("="*80)
    print("Parse GIS PDFs")
    print("="*80)
    print()

    # 集思台大
    ntucc_rooms = parse_gis_ntu_pdf()
    all_rooms.extend(ntucc_rooms)

    # 集思交通部
    motc_rooms = parse_gis_motc_pdf()
    all_rooms.extend(motc_rooms)

    # 集思中國醫
    tc_rooms = parse_gis_tc_pdf()
    all_rooms.extend(tc_rooms)

    print()
    print(f"Total: {len(all_rooms)} rooms")
    print()

    # 更新 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    updated_count = 0

    for venue in venues:
        venue_id = venue.get('id')

        # 根據 venue_id 分配會議室
        if venue_id == 1128:  # 集思台大
            venue['rooms'] = ntucc_rooms
            if ntucc_rooms:
                max_cap = max([r['capacity']['standard'] for r in ntucc_rooms])
                venue['capacity'] = {'standard': max_cap}
            updated_count += 1

        elif venue_id == 1494:  # 集思交通部
            venue['rooms'] = motc_rooms
            if motc_rooms:
                max_cap = max([r['capacity']['standard'] for r in motc_rooms])
                venue['capacity'] = {'standard': max_cap}
            updated_count += 1

        elif venue_id == 1497:  # 集思中國醫
            venue['rooms'] = tc_rooms
            if tc_rooms:
                max_cap = max([r['capacity']['standard'] for r in tc_rooms])
                venue['capacity'] = {'standard': max_cap}
            updated_count += 1

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f"Updated: {updated_count} venues")
    print()

    # 顯示摘要
    print("="*80)
    print("Summary")
    print("="*80)
    print()

    print(f"NTUCC: {len(ntucc_rooms)} rooms")
    for room in ntucc_rooms:
        print(f"  - {room['name']}: {room['capacity']['standard']} people, {room['area']} ping")

    print()
    print(f"MOTC: {len(motc_rooms)} rooms")
    for room in motc_rooms:
        print(f"  - {room['name']}: {room['capacity']['standard']} people, {room['area']} ping")

    print()
    print(f"TC: {len(tc_rooms)} rooms")
    for room in tc_rooms[:5]:
        print(f"  - {room['name']}: {room['capacity']['standard']} people, {room['area']} ping")


if __name__ == '__main__':
    update_venues_with_pdf_data()
