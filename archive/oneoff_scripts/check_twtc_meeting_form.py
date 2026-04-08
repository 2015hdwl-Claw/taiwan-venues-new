#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查台北世貿會議室表單頁面
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import json
import re

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    print('=' * 80)
    print('檢查台北世貿會議室表單頁面')
    print('=' * 80)
    print()

    url = 'https://www.twtc.com.tw/meeting_form'

    print(f'[1/3] 訪問頁面: {url}')
    print()

    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        print(f'✅ 成功訪問 (HTTP {response.status_code})')
        print(f'   頁面大小: {len(response.text):,} 字元')
        print()

        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找所有表格
        print('[2/3] 分析頁面結構...')
        print()

        # 檢查是否有表格
        tables = soup.find_all('table')
        print(f'找到 {len(tables)} 個表格')

        if tables:
            for i, table in enumerate(tables[:5], 1):
                rows = table.find_all('tr')
                print(f'  表格 {i}: {len(rows)} 行')

                # 顯示前幾行
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    text = ' | '.join([cell.get_text(strip=True)[:30] for cell in cells])
                    print(f'    Row {j}: {text}')
                print()

        # 檢查是否有選項（select）
        print('[尋找表單選項]')
        selects = soup.find_all('select')
        print(f'找到 {len(selects)} 個下拉選單:')

        for i, select in enumerate(selects[:10], 1):
            name = select.get('name', '無名稱')
            options = select.find_all('option')
            print(f'  {i}. {name} ({len(options)} 個選項)')

            # 顯示前 5 個選項
            for j, option in enumerate(options[:5], 1):
                value = option.get('value', '')
                text = option.get_text(strip=True)
                print(f'     {j}. {text} (value: {value})')

            if len(options) > 5:
                print(f'     ... 還有 {len(options) - 5} 個選項')
            print()

        # 尋找會議室相關的選項
        print('[3/3] 尋找會議室相關資訊...')
        print()

        page_text = soup.get_text()

        # 尋找會議室名稱
        room_keywords = ['第一會議室', '第二會議室', '第三會議室', 'A+會議室', '第四會議室', '第五會議室']
        found_rooms = []

        for keyword in room_keywords:
            if keyword in page_text:
                found_rooms.append(keyword)

        if found_rooms:
            print(f'✅ 找到會議室名稱: {", ".join(found_rooms)}')
        else:
            print('⚠️  未找到會議室名稱')

        # 尋找價格資訊
        price_patterns = [
            r'NT\$?\s*[\d,]+',
            r'[\d,]+\s*元',
            r'[\d,]+\s*元/\s*天',
            r'[\d,]+\s*元/\s*小時'
        ]

        all_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            all_prices.extend(matches)

        if all_prices:
            # 去重
            unique_prices = list(set(all_prices))[:10]
            print(f'✅ 找到價格資訊: {", ".join(unique_prices)}')
        else:
            print('⚠️  未找到價格資訊')

        # 尋找容量資訊
        capacity_pattern = r'\d+\s*人'
        capacities = re.findall(capacity_pattern, page_text)

        if capacities:
            unique_capacities = list(set(capacities))[:10]
            print(f'✅ 找到容量資訊: {", ".join(unique_capacities)}')

        # 尋找隱藏欄位（可能有 JSON 資料）
        print()
        print('[尋找隱藏欄位和 JavaScript]')

        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        print(f'找到 {len(hidden_inputs)} 個隱藏欄位')

        useful_data = {}
        for hidden in hidden_inputs:
            name = hidden.get('name', '')
            value = hidden.get('value', '')
            if name and value:
                useful_data[name] = value

        if useful_data:
            print(f'可能包含資料的欄位:')
            for name, value in useful_data.items():
                print(f'  - {name}: {value[:50]}...' if len(value) > 50 else f'  - {name}: {value}')

        # 尋找 script 標籤中的 JSON
        scripts = soup.find_all('script')
        print()
        print(f'找到 {len(scripts)} 個 script 標籤')

        for i, script in enumerate(scripts):
            script_text = script.string or ''

            # 尋找 JSON 物件
            if '{' in script_text and '}' in script_text:
                # 嘗試提取 JSON
                try:
                    # 尋找可能的 JSON
                    json_pattern = r'\{[^{}]*"[^"]*"[^{}]*:[^{}]*\}'
                    json_matches = re.findall(json_pattern, script_text)

                    if json_matches:
                        print(f'Script {i} 可能包含 JSON 資料:')
                        for match in json_matches[:3]:
                            print(f'  {match[:100]}...')
                        break
                except:
                    pass

        # 儲存完整頁面供分析
        with open('twtc_meeting_form.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print()
        print('✅ 完整頁面已儲存到 twtc_meeting_form.html')

        # 儲存分析結果
        result = {
            'url': url,
            'tables_count': len(tables),
            'selects_count': len(selects),
            'found_rooms': found_rooms,
            'found_prices': list(set(all_prices))[:20],
            'found_capacities': list(set(capacities))[:20],
            'hidden_fields': useful_data
        }

        with open('twtc_meeting_form_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print('✅ 分析結果已儲存到 twtc_meeting_form_analysis.json')

    except Exception as e:
        print(f'❌ 錯誤: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
