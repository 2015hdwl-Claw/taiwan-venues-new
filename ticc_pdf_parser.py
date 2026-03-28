#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF 解析器 - 專門處理 TICC 的價目表 PDF
"""
import requests
import PyPDF2
import io
import re
import sys
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == 'win32':
    import io as sys_io
    sys.stdout = sys_io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class TICCpdfParser:
    def __init__(self):
        self.rooms = []

    def parse(self, pdf_url):
        """解析 TICC PDF"""
        print("="*80)
        print("TICC PDF 解析器")
        print("="*80)
        print()

        try:
            # 下載 PDF
            print(f"[1/3] 下載 PDF: {pdf_url}")
            response = requests.get(pdf_url, timeout=30, verify=False)
            if response.status_code != 200:
                print(f"❌ 下載失敗: HTTP {response.status_code}")
                return []

            print(f"✅ 下載成功: {len(response.content)} bytes")

            # 解析 PDF
            print("[2/3] 解析 PDF...")
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            print(f"✅ 頁數: {len(pdf_reader.pages)}")

            # 提取文字
            all_text = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                all_text += text + "\n"

            # 解析表格
            print("[3/3] 解析會議室資料...")
            self.rooms = self._parse_table(all_text)

            print(f"✅ 解析完成: 找到 {len(self.rooms)} 個會議室")
            print()

            # 顯示結果
            self._display_results()

            return self.rooms

        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_table(self, text):
        """解析表格格式的會議室資料"""
        rooms = []
        lines = text.split('\n')

        # 跳過標題
        start_idx = -1
        for i, line in enumerate(lines):
            if '大會堂全場' in line:
                start_idx = i
                break

        if start_idx == -1:
            print("❌ 找不到資料起始位置")
            return []

        # 解析每一行
        current_room = None
        i = start_idx

        while i < len(lines):
            line = lines[i].strip()

            # 跳過空行和標題
            if not line or '會議室名稱' in line or '標準容量' in line:
                i += 1
                continue

            # 停止條件
            if '備註' in line:
                break

            # 嘗試解析會議室
            room = self._parse_room_line(lines, i)
            if room:
                rooms.append(room)
                i += 1
            else:
                i += 1

        return rooms

    def _parse_room_line(self, lines, idx):
        """解析單一會議室資料"""
        # 合併接下來幾行以獲得完整資料
        combined = ""
        for i in range(idx, min(idx + 5, len(lines))):
            line = lines[i].strip()
            if not line or '備註' in line:
                break
            combined += line + " "

        # 移除多餘空白
        combined = ' '.join(combined.split())

        # 嘗試識別會議室名稱
        room_patterns = [
            r'^(大會堂全場)',
            r'^(大會堂半場)',
            r'^(\d+)\s+全室',
            r'^(\d+[A-Z]+/[A-Z]+\d*)',  # 101A/D, 201AB/EF 等
            r'^(\d+)[A-Z/\d]*',  # 102, 103 等
            r'^(\d+樓[南北雅悅宴鳳凰軒]+[軒廳])',  # 3樓南/北軒, 3樓宴會廳, 4樓雅/悅軒, 4樓鳳凰廳
            r'^(\d+樓宴會廳)',
            r'^(\d+樓雅軒)',
            r'^(\d+樓悅軒)',
            r'^(\d+樓南北軒)',
            r'^(4樓鳳凰廳)',
        ]

        room_name = None
        for pattern in room_patterns:
            match = re.match(pattern, combined)
            if match:
                room_name = match.group(1)
                break

        if not room_name:
            return None

        # 提取數據
        room_data = {
            'name': room_name,
            'capacity_theater': None,
            'capacity_classroom': None,
            'capacity_u': None,
            'capacity_negotiation': None,
            'area_sqm': None,
            'area_ping': None,
            'dimensions': None,
            'price_weekday': None,
            'price_weekend': None,
            'price_exhibition': None,
            'booths_3x2': None
        }

        # 容量（劇院型）
        theater_match = re.search(r'(\d{1,4})\s+(?:\d{1,4}\s+)?(?:\d{1,4}\s+)?(?:\d{1,4}\s+)?', combined)
        if theater_match:
            room_data['capacity_theater'] = int(theater_match.group(1))

        # 面積（平方公尺/坪）
        area_match = re.search(r'(\d{1,5})/(\d{1,4})', combined)
        if area_match:
            room_data['area_sqm'] = int(area_match.group(1))
            room_data['area_ping'] = int(area_match.group(2))

        # 尺寸（寬x長x高）
        dim_match = re.search(r'([\d.]+)×([\d.]+)×([\d.]+)', combined)
        if dim_match:
            room_data['dimensions'] = f"{dim_match.group(1)}×{dim_match.group(2)}×{dim_match.group(3)}"

        # 價格（平日、假日、展覽）
        prices = re.findall(r'(\d{2,6}(?:,\d{3})*)', combined)
        if len(prices) >= 2:
            room_data['price_weekday'] = int(prices[0].replace(',', ''))
            room_data['price_weekend'] = int(prices[1].replace(',', ''))
        if len(prices) >= 3:
            room_data['price_exhibition'] = int(prices[2].replace(',', ''))

        # 攤位
        booth_match = re.search(r'(\d+)\s+攤位', combined)
        if booth_match:
            room_data['booths_3x2'] = int(booth_match.group(1))

        return room_data

    def _display_results(self):
        """顯示解析結果"""
        print("="*80)
        print("解析結果")
        print("="*80)
        print()

        for i, room in enumerate(self.rooms, 1):
            print(f"{i}. {room['name']}")
            print(f"   容量（劇院型）: {room['capacity_theater'] or 'N/A'} 人")
            print(f"   面積: {room['area_sqm'] or 'N/A'} 平方公尺 / {room['area_ping'] or 'N/A'} 坪")
            print(f"   尺寸: {room['dimensions'] or 'N/A'}")
            print(f"   價格: 平日 ${room['price_weekday'] or 'N/A':,} / 假日 ${room['price_weekend'] or 'N/A':,}")
            if room['price_exhibition']:
                print(f"   展覽: ${room['price_exhibition']:,}")
            print()

    def save_to_json(self, filename):
        """儲存結果為 JSON"""
        result = {
            'source': 'TICC PDF',
            'total_rooms': len(self.rooms),
            'rooms': self.rooms
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ 結果已儲存至: {filename}")


def main():
    parser = TICCpdfParser()

    # TICC PDF URL
    pdf_url = "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf"

    # 解析
    rooms = parser.parse(pdf_url)

    if rooms:
        # 儲存
        parser.save_to_json('ticc_rooms_parsed.json')

        print("="*80)
        print("完成！")
        print("="*80)


if __name__ == '__main__':
    main()
