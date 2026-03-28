#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
階段2：深度爬蟲 - 文華東方
三級爬取：主頁→會議室頁→PDF
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def level_1_homepage(base_url):
    """第一級：主頁分析"""

    print('=' * 80)
    print('第一級：主頁分析')
    print('=' * 80)
    print(f'URL: {base_url}')
    print()

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(base_url, timeout=15, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 尋找會議室相關連結
        print('[1/3] 尋找會議室相關連結...')

        meeting_links = []

        # 檢查所有連結
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True)

            # 會議室關鍵詞
            meeting_keywords = [
                'meeting', 'ballroom', 'function', 'event', 'conference',
                '會議', '宴會', '會議室', '場地'
            ]

            # URL 關鍵詞
            if any(keyword in href.lower() for keyword in meeting_keywords) or \
               any(keyword in link_text.lower() for keyword in meeting_keywords):
                full_url = urljoin(base_url, href)
                meeting_links.append({
                    'url': full_url,
                    'text': link_text,
                    'type': 'meeting_page'
                })

        # 去重
        seen_urls = set()
        unique_links = []
        for link in meeting_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)

        if unique_links:
            print(f'✅ 找到 {len(unique_links)} 個會議室相關連結:')
            for i, link in enumerate(unique_links[:10], 1):
                print(f'  {i}. {link["text"][:50]}')
                print(f'     {link["url"]}')
        else:
            print('⚠️  未找到會議室連結')

        print()

        # 2. 尋找 PDF 連結
        print('[2/3] 尋找 PDF 連結...')

        pdf_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(base_url, href)
                link_text = link.get_text(strip=True)
                pdf_links.append({
                    'url': full_url,
                    'text': link_text
                })

        if pdf_links:
            print(f'✅ 找到 {len(pdf_links)} 個 PDF:')
            for pdf in pdf_links:
                print(f'  - {pdf["text"][:50]}')
                print(f'    {pdf["url"]}')
        else:
            print('⚠️  未找到 PDF 連結')

        print()

        # 3. 尋找圖片連結（會議室照片）
        print('[3/3] 尋找會議室照片...')

        room_images = []

        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')

            # 會議室關鍵詞
            if any(keyword in alt.lower() for keyword in ['meeting', 'ballroom', 'conference', '會議', '宴會']):
                full_url = urljoin(base_url, src)
                room_images.append({
                    'url': full_url,
                    'alt': alt
                })

        if room_images:
            print(f'✅ 找到 {len(room_images)} 張會議室照片:')
            for img in room_images[:5]:
                print(f'  - {img["alt"][:40]}')
                print(f'    {img["url"][:80]}')
        else:
            print('⚠️  未找到會議室照片')

        print()

        return {
            'meeting_links': unique_links[:10],
            'pdf_links': pdf_links,
            'room_images': room_images[:10]
        }

    except Exception as e:
        print(f'❌ 主頁分析失敗: {e}')
        import traceback
        traceback.print_exc()
        return None


def level_2_meeting_page(meeting_url):
    """第二級：會議室頁面深度提取"""

    print('=' * 80)
    print('第二級：會議室頁面深度提取')
    print('=' * 80)
    print(f'URL: {meeting_url}')
    print()

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(meeting_url, timeout=15, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 1. 提取會議室名稱
        print('[1/4] 提取會議室名稱...')

        room_names = []

        # 方法1: 從標題提取
        for tag in ['h1', 'h2', 'h3']:
            for elem in soup.find_all(tag):
                text = elem.get_text(strip=True)
                if text and any(keyword in text.lower() for keyword in ['room', 'ballroom', 'hall', '會議', '宴會']):
                    room_names.append(text)

        # 方法2: 從 class/id 提取
        for elem in soup.find_all(class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['room', 'meeting', 'ballroom', 'venue']
        )):
            text = elem.get_text(strip=True)
            if text and len(text) < 100:  # 避免太長的文字
                room_names.append(text)

        if room_names:
            unique_rooms = list(set(room_names))[:10]
            print(f'✅ 可能的會議室名稱:')
            for room in unique_rooms:
                print(f'  - {room}')
        else:
            print('⚠️  未找到會議室名稱')

        print()

        # 2. 提取容量資訊
        print('[2/4] 提取容量資訊...')

        capacity_patterns = [
            r'capacity[：:]\s*(\d+)',
            r'(\d+)\s*(?:people|guests|pax|人)',
            r'up to\s*(\d+)',
            r'最大(?:容量)?[：:]\s*(\d+)'
        ]

        capacities = []
        for pattern in capacity_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            capacities.extend([int(m) for m in matches if m.isdigit()])

        if capacities:
            unique_caps = sorted(set(capacities))[:10]
            print(f'✅ 可能的容量資訊:')
            for cap in unique_caps:
                print(f'  - {cap} 人')
        else:
            print('⚠️  未找到容量資訊')

        print()

        # 3. 提取尺寸/面積
        print('[3/4] 提取尺寸/面積...')

        dimension_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:sqm|sq|m²|㎡|square meters)',
            r'(\d+(?:\.\d+)?)\s*(?:ping|坪)',
            r'dimension[：:]\s*(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)'
        ]

        areas = []
        for pattern in dimension_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            areas.extend(matches)

        if areas:
            print(f'✅ 可能的面積資訊:')
            for area in areas[:10]:
                print(f'  - {area}')
        else:
            print('⚠️  未找到面積資訊')

        print()

        # 4. 提取 PDF 連結
        print('[4/4] 提取 PDF 連結...')

        pdf_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(meeting_url, href)
                link_text = link.get_text(strip=True)
                pdf_links.append({
                    'url': full_url,
                    'text': link_text
                })

        # 檢查 iframe 或 object 標籤中的 PDF
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if '.pdf' in src.lower():
                full_url = urljoin(meeting_url, src)
                pdf_links.append({
                    'url': full_url,
                    'text': 'PDF (iframe)',
                    'source': 'iframe'
                })

        if pdf_links:
            print(f'✅ 找到 {len(pdf_links)} 個 PDF:')
            for pdf in pdf_links:
                print(f'  - {pdf.get("text", "")[:50]}')
                print(f'    {pdf["url"]}')
        else:
            print('⚠️  未找到 PDF 連結')

        print()

        return {
            'room_names': list(set(room_names))[:10],
            'capacities': list(set(capacities))[:10],
            'areas': areas[:10],
            'pdf_links': pdf_links
        }

    except Exception as e:
        print(f'❌ 會議室頁面提取失敗: {e}')
        import traceback
        traceback.print_exc()
        return None


def level_3_pdf_analysis(pdf_url):
    """第三級：PDF 分析"""

    print('=' * 80)
    print('第三級：PDF 分析')
    print('=' * 80)
    print(f'URL: {pdf_url}')
    print()

    try:
        # 下載 PDF
        print('[1/2] 下載 PDF...')
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, timeout=30, headers=headers)
        response.raise_for_status()

        filename = 'mandarin_meeting_rooms.pdf'
        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f'✅ 下載完成: {filename}')
        print(f'大小: {len(response.content)} bytes')
        print()

        # 使用 pdfplumber 解析
        print('[2/2] 解析 PDF...')

        try:
            import pdfplumber

            with pdfplumber.open(filename) as pdf:
                print(f'頁數: {len(pdf.pages)}')
                print()

                all_tables = []

                for page_num, page in enumerate(pdf.pages[:3], 1):  # 只看前3頁
                    print(f'--- 頁面 {page_num} ---')

                    text = page.extract_text()
                    if text:
                        # 顯示前 500 字符
                        print(f'文字預覽:')
                        print(text[:500])
                        print()

                    # 提取表格
                    tables = page.extract_tables({
                        'vertical_strategy': 'text',
                        'horizontal_strategy': 'text'
                    })

                    if tables:
                        print(f'找到 {len(tables)} 個表格')
                        for table_num, table in enumerate(tables, 1):
                            print(f'\\n表格 {table_num}:')
                            for row_num, row in enumerate(table[:5], 1):
                                if row:
                                    display_row = [str(cell)[:30] if cell else '' for cell in row[:6]]
                                    print(f'  Row {row_num}: {display_row}')

                            all_tables.append({
                                'page': page_num,
                                'table_num': table_num,
                                'data': table
                            })

                return {
                    'pdf_url': pdf_url,
                    'filename': filename,
                    'total_pages': len(pdf.pages),
                    'tables': all_tables
                }

        except ImportError:
            print('⚠️  pdfplumber 未安裝，無法解析 PDF')
            return {
                'pdf_url': pdf_url,
                'filename': filename,
                'error': 'pdfplumber not installed'
            }

    except Exception as e:
        print(f'❌ PDF 分析失敗: {e}')
        import traceback
        traceback.print_exc()
        return None


def main():
    print('=' * 80)
    print('深度爬蟲 - 文華東方（三級爬取）')
    print('=' * 80)
    print()

    # 第一級：主頁
    level1_result = level_1_homepage('https://www.mandarinoriental.com/zh-hk/taipei/songshan/meet')

    # 第二級：會議室頁面
    if level1_result and level1_result.get('meeting_links'):
        # 使用第一個會議室連結
        meeting_url = level1_result['meeting_links'][0]['url']
        level2_result = level_2_meeting_page(meeting_url)

        # 第三級：PDF
        if level2_result and level2_result.get('pdf_links'):
            # 使用用戶提供的 PDF URL
            pdf_url = 'https://cdn-assets-dynamic.frontify.com/4001946/eyJhc3NldF9pZCI6NTk4NzIsInNjb3BlIjoiYXNzZXQ6dmlldyJ9:mandarin-oriental-hotel-group:DPQPeMI4kSiRw7PDc5axDqPeG3bMRlvOUH4Pu1hby18'
            level3_result = level_3_pdf_analysis(pdf_url)

            # 儲存所有結果
            all_results = {
                'level1_homepage': level1_result,
                'level2_meeting_page': level2_result,
                'level3_pdf': level3_result
            }

            with open('mandarin_deep_scrape.json', 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)

            print()
            print('=' * 80)
            print('✅ 深度爬蟲完成')
            print('=' * 80)
            print()
            print('結果已儲存到 mandarin_deep_scrape.json')

    else:
        print()
        print('⚠️  無法進行深度爬蟲（未找到會議室連結）')


if __name__ == '__main__':
    main()
