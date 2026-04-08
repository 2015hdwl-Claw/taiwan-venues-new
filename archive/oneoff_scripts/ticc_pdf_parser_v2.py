#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF 解析器 V2 - 精確解析表格格式
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


class TICCpdfParserV2:
    def __init__(self):
        self.rooms = []

    def parse(self, pdf_url):
        """解析 TICC PDF"""
        print("="*80)
        print("TICC PDF 解析器 V2")
        print("="*80)
        print()

        try:
            # 下載 PDF
            print(f"[1/3] 下載 PDF...")
            response = requests.get(pdf_url, timeout=30, verify=False)
            if response.status_code != 200:
                print(f"❌ 下載失敗: HTTP {response.status_code}")
                return []

            print(f"✅ 下載成功")

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

            # 儲存原始文字
            with open('ticc_pdf_raw.txt', 'w', encoding='utf-8') as f:
                f.write(all_text)

            # 解析表格
            print("[3/3] 解析會議室資料...")
            self.rooms = self._parse_ticc_table(all_text)

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

    def _parse_ticc_table(self, text):
        """精確解析 TICC 表格"""
        rooms = []
        lines = text.split('\n')

        # 找到資料起始位置
        start_idx = -1
        for i, line in enumerate(lines):
            if '大會堂全場' in line:
                start_idx = i
                break

        if start_idx == -1:
            print("❌ 找不到資料起始位置")
            return []

        # 處理每一行
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()

            # 停止條件
            if '備註' in line:
                break

            # 跳過空行
            if not line:
                i += 1
                continue

            # 嘗試解析這一行
            room = self._parse_line(lines, i)
            if room:
                rooms.append(room)

            i += 1

        return rooms

    def _parse_line(self, lines, idx):
        """解析單一行"""
        line = lines[idx].strip()

        # 特殊處理跨行的會議室（如101 全室）
        # 檢查下一行是否是數字開頭（容量）
        if idx + 1 < len(lines):
            next_line = lines[idx + 1].strip()
            # 如果下一行是純數字或包含彈射椅，則是同一個會議室的續行
            if next_line and (next_line.split()[0].replace(',', '').replace('—', '').replace('-', '').isdigit() or '彈射椅' in next_line):
                line = line + " " + next_line

        # 使用正則表達式提取會議室名稱和所有數字
        # 先識別會議室名稱
        room_name = None

        # 嘗試各種會議室名稱格式
        if '大會堂全場' in line:
            room_name = '大會堂全場'
        elif '大會堂半場' in line:
            room_name = '大會堂半場'
        elif re.match(r'^\d+\s+全室', line):
            match = re.match(r'^(\d+)\s+全室', line)
            room_name = f"{match.group(1)} 全室"
        elif re.match(r'^\d+[A-Z]', line):
            match = re.match(r'^(\d+[A-Z]+(?:/[A-Z]+\d*)?)', line)
            room_name = match.group(1)
        elif re.match(r'^\d+', line):
            match = re.match(r'^(\d+)', line)
            room_name = match.group(1)
        elif '樓' in line and ('軒' in line or '廳' in line):
            match = re.match(r'^(\d+樓[^實例手續費]+?軒|\d+樓[^實例手續費]+?廳)', line)
            if match:
                room_name = match.group(1)
            else:
                # 嘗試其他模式
                if '3樓南' in line or '3樓北' in line:
                    room_name = '3樓南/北軒'
                elif '3樓宴會廳' in line:
                    room_name = '3樓宴會廳'
                elif '4樓雅' in line or '4樓悅' in line:
                    room_name = '4樓雅/悅軒'
                elif '4樓鳳凰廳' in line:
                    room_name = '4樓鳳凰廳'

        if not room_name:
            return None

        # 移除會議室名稱，提取剩餘數據
        data_part = line
        for name_prefix in [room_name, '大會堂全場', '大會堂半場']:
            if name_prefix in data_part:
                data_part = data_part.replace(name_prefix, '', 1).strip()
                break

        # 提取所有數字（包含逗號）
        numbers = re.findall(r'([—\-]?\d{1,4}[，,\d\s]*(?:坪|元|公尺|m²|㎡)?|[—\-])', data_part)

        # 更好的方法：分割並分析每個欄位
        # 格式：會議室名稱 | 劇院型 | 教室型 | U型 | 洽談 | 攤位 | 面積 | 尺寸 | 平日價 | 假日價 | 展覽價

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
            'price_exhibition': None
        }

        # 使用智能解析
        # 1. 提取尺寸（格式：xx.x×xx.x×x.x）
        dim_match = re.search(r'(\d+\.?\d*)×(\d+\.?\d*)×(\d+\.?\d*)', data_part)
        if dim_match:
            room_data['dimensions'] = f"{dim_match.group(1)}×{dim_match.group(2)}×{dim_match.group(3)}"

        # 2. 提取面積（格式：640/193）
        area_match = re.search(r'(\d{1,5})/(\d{1,4})(?!\s*×)', data_part)
        if area_match:
            room_data['area_sqm'] = int(area_match.group(1))
            room_data['area_ping'] = int(area_match.group(2))

        # 3. 提取容量（最大的數字通常是劇院型容量）
        # 找所有純數字（不含逗號和單位）
        clean_numbers = []
        for match in re.finditer(r'\b([—\-]?\d{1,4})\b', data_part):
            num_str = match.group(1).replace(',', '').replace('—', '').replace('-', '')
            if num_str.isdigit():
                num = int(num_str)
                # 過濾掉面積和尺寸相關的數字
                if num < 5000:  # 容量通常小於5000
                    clean_numbers.append(num)

        # 4. 提取價格（格式：xx,xxx）
        prices = re.findall(r'(\d{1,3},\d{3}|\d{5,6})', data_part)
        prices = [int(p.replace(',', '')) for p in prices]

        # 5. 智能分配數值
        if clean_numbers:
            # 最大的數字通常是劇院型容量
            if len(clean_numbers) >= 1:
                room_data['capacity_theater'] = max(clean_numbers)

            # 其他數字可能是教室型、U型、洽談型容量
            if len(clean_numbers) >= 2:
                # 找第二大的數字
                sorted_nums = sorted([n for n in clean_numbers if n < room_data['capacity_theater']], reverse=True)
                if len(sorted_nums) >= 1:
                    room_data['capacity_classroom'] = sorted_nums[0]
                if len(sorted_nums) >= 2:
                    room_data['capacity_u'] = sorted_nums[1]
                if len(sorted_nums) >= 3:
                    room_data['capacity_negotiation'] = sorted_nums[2]

        # 6. 分配價格
        if len(prices) >= 1:
            room_data['price_weekday'] = prices[0]
        if len(prices) >= 2:
            room_data['price_weekend'] = prices[1]
        if len(prices) >= 3:
            room_data['price_exhibition'] = prices[2]

        return room_data

    def _display_results(self):
        """顯示解析結果"""
        print("="*80)
        print("解析結果")
        print("="*80)
        print()

        for i, room in enumerate(self.rooms[:15], 1):  # 只顯示前15個
            print(f"{i}. {room['name']}")
            print(f"   容量: 劇院型 {room['capacity_theater'] or 'N/A'} 人")
            if room['capacity_classroom']:
                print(f"       教室型 {room['capacity_classroom']} 人")
            if room['capacity_u']:
                print(f"       U型 {room['capacity_u']} 人")
            print(f"   面積: {room['area_sqm'] or 'N/A'} 平方公尺 / {room['area_ping'] or 'N/A'} 坪")
            print(f"   尺寸: {room['dimensions'] or 'N/A'}")
            price_weekday = f"${room['price_weekday']:,}" if room['price_weekday'] else 'N/A'
            price_weekend = f"${room['price_weekend']:,}" if room['price_weekend'] else 'N/A'
            print(f"   價格: 平日 {price_weekday} / 假日 {price_weekend}")
            if room['price_exhibition']:
                price_exhibition = f"${room['price_exhibition']:,}" if room['price_exhibition'] else 'N/A'
                print(f"   展覽: {price_exhibition}")
            print()

        if len(self.rooms) > 15:
            print(f"... 還有 {len(self.rooms) - 15} 個會議室")
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
    parser = TICCpdfParserV2()
    pdf_url = "https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf"

    rooms = parser.parse(pdf_url)

    if rooms:
        parser.save_to_json('ticc_rooms_parsed_v2.json')

        print("="*80)
        print("完成！")
        print("="*80)


if __name__ == '__main__':
    main()
