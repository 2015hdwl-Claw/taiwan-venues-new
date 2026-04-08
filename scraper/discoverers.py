#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/discoverers.py - 多層頁面發現器
從首頁深入到會議室詳情頁
"""

import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import REQUEST_HEADERS, MEETING_URL_PATTERNS, MEETING_NAV_KEYWORDS, PDF_KEYWORDS


class PageDiscoverer:
    """多層頁面發現器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.session.verify = False
        self.visited = set()

    def discover_all(self, base_url: str, max_depth: int = 3) -> list:
        """
        4 層頁面發現，返回所有找到的頁面

        返回格式：
        [
            {
                'url': str,
                'httpStatus': int,
                'pageType': str,  # homepage, meeting_list, meeting_detail, pdf, other
                'depth': int,
                'discoveredFrom': str,  # navigation, footer, url_pattern, deep_link
                'contentLength': int,
                'title': str,
                'childLinks': [str],  # 子頁面 URL
            }
        ]
        """
        all_pages = []
        soup = None

        # Layer 1: 首頁（可能失敗，仍繼續 URL 模式發現）
        homepage = self._fetch_page(base_url, 'homepage', 1, 'initial')
        if homepage:
            all_pages.append(homepage)
            self.visited.add(base_url)
            soup = homepage.get('_soup')

        # Layer 2: 會議/宴會頁面
        meeting_links = self._discover_meeting_links(soup, base_url) if soup else []
        url_pattern_links = self._discover_by_url_patterns(base_url)
        pdf_links = self._discover_pdfs(soup, base_url) if soup else []

        all_meeting = self._deduplicate(meeting_links + url_pattern_links)

        for link_info in all_meeting[:10]:  # 限制最多 10 個
            url = link_info['url']
            if url in self.visited:
                continue

            page = self._fetch_page(url, 'meeting_list', 2, link_info['source'])
            if page:
                all_pages.append(page)
                self.visited.add(url)

                # Layer 3: 會議室詳情頁
                if page.get('_soup'):
                    detail_links = self._discover_detail_links(page['_soup'], url)
                    for detail_info in detail_links[:8]:
                        detail_url = detail_info['url']
                        if detail_url in self.visited:
                            continue
                        detail_page = self._fetch_page(
                            detail_url, 'meeting_detail', 3, 'deep_link'
                        )
                        if detail_page:
                            all_pages.append(detail_page)
                            self.visited.add(detail_url)

        # PDF 頁面
        for pdf_url in pdf_links[:5]:
            if pdf_url not in self.visited:
                all_pages.append({
                    'url': pdf_url,
                    'httpStatus': 200,
                    'pageType': 'pdf',
                    'depth': 2,
                    'discoveredFrom': 'pdf_link',
                    'contentLength': 0,
                    'title': '',
                    'childLinks': [],
                })
                self.visited.add(pdf_url)

        # 清理：移除內部 _soup 欄位
        for p in all_pages:
            p.pop('_soup', None)

        return all_pages

    def _fetch_page(self, url: str, page_type: str, depth: int, source: str) -> dict:
        """抓取單一頁面"""
        try:
            r = self.session.get(url, timeout=20, allow_redirects=True)
            if r.status_code not in (200, 202):
                return None

            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string.strip()[:80] if soup.title and soup.title.string else ''

            # 收集頁面上的連結
            child_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                    continue
                abs_url = urljoin(url, href)
                if abs_url not in self.visited:
                    child_links.append(abs_url)

            return {
                'url': r.url,
                'httpStatus': r.status_code,
                'pageType': page_type,
                'depth': depth,
                'discoveredFrom': source,
                'contentLength': len(soup.get_text(strip=True)),
                'title': title,
                'childLinks': child_links[:20],
                '_soup': soup,
            }
        except Exception:
            return None

    def _discover_meeting_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Layer 2: 從導航發現會議相關頁面"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)

            if any(kw in text for kw in MEETING_NAV_KEYWORDS) or \
               any(kw in href.lower() for kw in [k.lower() for k in MEETING_NAV_KEYWORDS]):
                abs_url = urljoin(base_url, href)
                if urlparse(abs_url).netloc == urlparse(base_url).netloc:
                    links.append({
                        'url': abs_url,
                        'source': 'navigation',
                        'text': text[:50],
                    })
        return links

    def _discover_by_url_patterns(self, base_url: str) -> list:
        """Layer 2: 嘗試常見 URL 模式"""
        links = []
        # 使用 scheme + netloc 作為根域名
        parsed = urlparse(base_url)
        domain = f'{parsed.scheme}://{parsed.netloc}'
        print(f'  [URL模式] 根域名: {domain}, 嘗試 {len(MEETING_URL_PATTERNS)} 個模式')
        for pattern in MEETING_URL_PATTERNS:
            test_url = domain + pattern
            if test_url not in self.visited:
                try:
                    r = self.session.get(test_url, timeout=5, allow_redirects=True)
                    if r.status_code in (200, 202):
                        print(f'  [URL模式] ✓ {pattern} -> {r.status_code}')
                        links.append({
                            'url': r.url,
                            'source': 'url_pattern',
                            'text': pattern,
                        })
                except Exception:
                    continue
        return links

    def _discover_detail_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Layer 3: 發現會議室詳情頁"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True).lower()

            # 檢查是否為詳情頁
            is_detail = any(kw in text for kw in ['detail', 'more', 'view', '了解更多', '查看'])
            has_id = '?id=' in href or '&id=' in href

            if is_detail or has_id:
                abs_url = urljoin(base_url, href)
                if urlparse(abs_url).netloc == urlparse(base_url).netloc:
                    links.append({
                        'url': abs_url,
                        'source': 'deep_link',
                        'text': a.get_text(strip=True)[:50],
                    })

        return links

    def _discover_pdfs(self, soup: BeautifulSoup, base_url: str) -> list:
        """發現 PDF 連結"""
        pdfs = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True).lower()

            if '.pdf' in href.lower():
                abs_url = urljoin(base_url, href)
                # 優先標記有關鍵字的 PDF
                pdfs.append(abs_url)

        return list(set(pdfs))

    def _deduplicate(self, links: list) -> list:
        """去重"""
        seen = set()
        unique = []
        for link in links:
            url = link['url']
            if url not in seen:
                seen.add(url)
                unique.append(link)
        return unique
