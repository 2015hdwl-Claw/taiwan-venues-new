#!/usr/bin/env python3
"""
驗證會議中心和展演場地的資料擷取
檢測網頁技術類型並擷取完整資料
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urljoin
import time

class VenueTypeVerifier:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def detect_page_type(self, url):
        """檢測網頁技術類型"""
        result = {
            'url': url,
            'detected_at': datetime.now().isoformat()
        }

        try:
            # 測試1: 檢查原始碼是否包含內容
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # 檢查關鍵字
            text = soup.get_text().lower()
            keywords = ['會議', 'meeting', '宴會', 'banquet', '會議室', '場地']
            has_content = sum(1 for kw in keywords if kw in text)

            # 測試2: 檢查是否有 WordPress API
            api_url = urljoin(url, '/wp-json/wp/v2/pages')
            try:
                api_response = self.session.get(api_url, timeout=3)
                if api_response.status_code == 200:
                    result['type'] = 'WordPress API'
                    result['confidence'] = 'high'
                    result['api_endpoint'] = api_url
                    return result
            except:
                pass

            # 判斷類型
            if has_content >= 3:
                # 原始碼有內容 → 靜態/SSR
                result['type'] = 'Static/SSR'
                result['confidence'] = 'high'
                result['has_content_in_source'] = True
            else:
                # 原始碼沒有內容 → 可能是 JS 渲染
                result['type'] = 'JavaScript (CSR)'
                result['confidence'] = 'medium'
                result['has_content_in_source'] = False
                result['note'] = '需要用 Playwright 驗證'

        except Exception as e:
            result['type'] = 'Unknown'
            result['error'] = str(e)

        return result

    def extract_venue_data(self, url, venue_id, venue_name):
        """擷取場地資料"""
        print(f'\n擷取 ID {venue_id}: {venue_name[:40]}')
        print(f'URL: {url}')
        print('='*60)

        result = {
            'id': venue_id,
            'name': venue_name,
            'url': url,
            'extracted_at': datetime.now().isoformat(),
            'extraction_result': {}
        }

        try:
            # 步驟1: 檢測網頁類型
            print('[步驟1] 檢測網頁技術類型...')
            page_type = self.detect_page_type(url)
            result['page_type'] = page_type

            print(f"  類型: {page_type.get('type', 'Unknown')}")
            print(f"  信心度: {page_type.get('confidence', 'N/A')}")

            # 步驟2: 擷取基本資料
            print('\n[步驟2] 擷取基本資料...')
            response = self.session.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')

            basic_data = self._extract_basic_info(soup)
            result['basic_info'] = basic_data
            print(f"  名稱: {basic_data.get('name', 'N/A')}")
            print(f"  類型: {basic_data.get('venueType', 'N/A')}")
            print(f"  電話: {basic_data.get('contactPhone', 'N/A')}")
            print(f"  Email: {basic_data.get('contactEmail', 'N/A')}")

            # 步驟3: 尋找會議室頁面
            print('\n[步驟3] 尋找會議室頁面...')
            meeting_links = self._find_meeting_pages(soup, url)
            result['meeting_pages'] = meeting_links
            print(f"  找到 {len(meeting_links)} 個會議相關頁面")

            if meeting_links:
                for link in meeting_links[:3]:
                    print(f"    - {link['text'][:40]}")

            # 步驟4: 尋找聯絡頁面
            print('\n[步驟4] 尋找聯絡頁面...')
            contact_links = self._find_contact_pages(soup, url)
            result['contact_pages'] = contact_links
            print(f"  找到 {len(contact_links)} 個聯絡頁面")

            # 步驟5: 尋找交通頁面
            print('\n[步驟5] 尋找交通頁面...')
            access_links = self._find_access_pages(soup, url)
            result['access_pages'] = access_links
            print(f"  找到 {len(access_links)} 個交通頁面")

            # 步驟6: 統計頁面數
            print('\n[步驟6] 統計頁面數...')
            all_links = soup.find_all('a', href=True)
            result['total_links'] = len(all_links)
            print(f"  總連結數: {len(all_links)}")

            result['success'] = True

        except Exception as e:
            print(f'\n❌ 錯誤: {e}')
            result['success'] = False
            result['error'] = str(e)

        return result

    def _extract_basic_info(self, soup):
        """提取基本資料"""
        data = {}

        # 名稱
        for tag in ['h1', 'h2']:
            elem = soup.find(tag)
            if elem:
                data['name'] = elem.get_text().strip()[:100]
                break

        # 電話
        import re
        phones = re.findall(r'0\d-\d{4}-\d{4}', soup.get_text())
        if phones:
            data['contactPhone'] = phones[0]

        # Email
        emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', soup.get_text())
        if emails:
            data['contactEmail'] = emails[0]

        return data

    def _find_meeting_pages(self, soup, base_url):
        """尋找會議室頁面"""
        keywords = ['會議', 'meeting', '宴會', 'banquet', '會議室', '場地租借']
        links = []

        for a in soup.find_all('a', href=True):
            text = a.get_text().strip().lower()
            href = a['href'].lower()

            if any(kw in text or kw in href for kw in keywords):
                full_url = urljoin(base_url, a['href'])
                links.append({
                    'text': a.get_text().strip(),
                    'url': full_url
                })

        return links[:10]

    def _find_contact_pages(self, soup, base_url):
        """尋找聯絡頁面"""
        keywords = ['聯絡', 'contact', '聯絡我們', '電話']
        links = []

        for a in soup.find_all('a', href=True):
            text = a.get_text().strip().lower()
            href = a['href'].lower()

            if any(kw in text or kw in href for kw in keywords):
                full_url = urljoin(base_url, a['href'])
                links.append({
                    'text': a.get_text().strip(),
                    'url': full_url
                })

        return links[:5]

    def _find_access_pages(self, soup, base_url):
        """尋找交通頁面"""
        keywords = ['交通', 'access', '位置', 'location', '怎麼去', 'direction']
        links = []

        for a in soup.find_all('a', href=True):
            text = a.get_text().strip().lower()
            href = a['href'].lower()

            if any(kw in text or kw in href for kw in keywords):
                full_url = urljoin(base_url, a['href'])
                links.append({
                    'text': a.get_text().strip(),
                    'url': full_url
                })

        return links[:5]


def main():
    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 篩選會議中心和展演場地
    conference_centers = []
    exhibition_venues = []

    for v in venues:
        if v.get('status') == 'discontinued':
            continue

        venue_type = v.get('venueType', '').lower()

        if '會議中心' in venue_type or 'conference' in venue_type:
            conference_centers.append(v)

        if '展演' in venue_type or '展覽' in venue_type:
            exhibition_venues.append(v)

    verifier = VenueTypeVerifier()

    print('='*80)
    print('驗證會議中心和展演場地的資料擷取')
    print('='*80)

    all_results = []

    # 測試會議中心（前3個）
    print('\n### 會議中心 ###\n')
    for i, venue in enumerate(conference_centers[:3], 1):
        print(f'\n[{i}/{min(3, len(conference_centers))}]')
        result = verifier.extract_venue_data(
            venue['url'],
            venue['id'],
            venue.get('name', '')
        )
        all_results.append(result)
        time.sleep(1)  # 避免請求過快

    # 測試展演場地（全部）
    print('\n\n### 展演場地 ###\n')
    for i, venue in enumerate(exhibition_venues, 1):
        print(f'\n[{i}/{len(exhibition_venues)}]')
        result = verifier.extract_venue_data(
            venue['url'],
            venue['id'],
            venue.get('name', '')
        )
        all_results.append(result)
        time.sleep(1)

    # 儲存結果
    report = {
        'tested_at': datetime.now().isoformat(),
        'conference_centers_tested': min(3, len(conference_centers)),
        'exhibition_venues_tested': len(exhibition_venues),
        'total_tested': len(all_results),
        'results': all_results
    }

    with open('venue_type_verification_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('\n' + '='*80)
    print(f'測試完成！共 {len(all_results)} 個場地')
    print('詳細結果已儲存到 venue_type_verification_report.json')

    # 統計
    static_count = sum(1 for r in all_results if r.get('page_type', {}).get('type') == 'Static/SSR')
    api_count = sum(1 for r in all_results if 'API' in r.get('page_type', {}).get('type', ''))
    js_count = sum(1 for r in all_results if 'JavaScript' in r.get('page_type', {}).get('type', ''))

    print('\n網頁技術分佈:')
    print(f'  Static/SSR: {static_count}')
    print(f'  API: {api_count}')
    print(f'  JavaScript: {js_count}')
    print(f'  Unknown: {len(all_results) - static_count - api_count - js_count}')


if __name__ == '__main__':
    main()
