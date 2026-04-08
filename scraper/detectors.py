#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scraper/detectors.py - 技術偵測器
進入頁面前先做技術分析，記錄結果，再決定提取策略
"""

import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import REQUEST_HEADERS, JS_FRAMEWORK_SIGNATURES


class TechnicalDetector:
    """技術偵測器 - 分析網頁技術，決定提取策略"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.session.verify = False

    def detect(self, url: str) -> dict:
        """
        完整技術偵測，返回 technicalReport
        """
        report = {
            'url': url,
            'httpStatus': None,
            'finalUrl': None,
            'contentType': None,
            'responseTime': None,
            'staticContentLength': 0,
            'isDynamic': False,
            'jsFrameworks': [],
            'cms': None,
            'hasDataInJs': False,
            'iframeCount': 0,
            'antiScraping': None,
            'extractionStrategy': 'unknown',
            'detectedAt': datetime.now().isoformat(),
        }

        if not url or url == 'TBD':
            report['extractionStrategy'] = 'failed'
            report['failureReason'] = 'No URL or TBD'
            return report

        try:
            start = time.time()
            r = self.session.get(url, timeout=20, allow_redirects=True)
            elapsed = round(time.time() - start, 2)

            report['httpStatus'] = r.status_code
            report['finalUrl'] = r.url
            report['contentType'] = r.headers.get('Content-Type', '')
            report['responseTime'] = elapsed

            if r.status_code not in (200, 202):
                report['extractionStrategy'] = 'failed'
                report['failureReason'] = f'HTTP {r.status_code}'
                return report

            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text(strip=True)
            report['staticContentLength'] = len(page_text)

            # 偵測 JS 框架
            report['jsFrameworks'] = self._detect_js_frameworks(r.text, soup)

            # 偵測 CMS
            report['cms'] = self._detect_cms(r.text, soup)

            # 判斷是否動態渲染
            report['isDynamic'] = self._is_dynamic(page_text, r.text, report['jsFrameworks'])

            # 檢查 JS 變數中有無資料
            report['hasDataInJs'] = self._has_data_in_js(soup)

            # iframe 數量
            report['iframeCount'] = len(soup.find_all('iframe'))

            # 反爬蟲
            report['antiScraping'] = self._detect_anti_scraping(r)

            # 決定策略
            report['extractionStrategy'] = self._decide_strategy(report)

        except requests.exceptions.ConnectionError:
            report['extractionStrategy'] = 'failed'
            report['failureReason'] = 'Connection Error'
        except requests.exceptions.Timeout:
            report['extractionStrategy'] = 'failed'
            report['failureReason'] = 'Timeout'
        except Exception as e:
            report['extractionStrategy'] = 'failed'
            report['failureReason'] = str(e)[:100]

        return report

    def _detect_js_frameworks(self, html: str, soup: BeautifulSoup) -> list:
        """偵測 JS 框架"""
        html_lower = html.lower()
        scripts = [s.get('src', '').lower() for s in soup.find_all('script', src=True)]

        found = []
        for framework, signatures in JS_FRAMEWORK_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in html_lower or any(sig.lower() in s for s in scripts):
                    found.append(framework)
                    break

        return list(set(found))

    def _detect_cms(self, html: str, soup: BeautifulSoup) -> str:
        """偵測 CMS"""
        generator = soup.find('meta', {'name': 'generator'})
        if generator:
            return generator.get('content', 'Unknown')
        return None

    def _is_dynamic(self, text: str, html: str, frameworks: list) -> bool:
        """判斷是否需要 JS 渲染"""
        # 靜態文字很少 → 可能是動態渲染
        if len(text) < 500:
            return True
        # Wix/React/Vue/Angular 且靜態文字 < 2000 → 可能動態
        dynamic_frameworks = {'React', 'Vue', 'Angular', 'Wix'}
        if any(f in frameworks for f in dynamic_frameworks) and len(text) < 2000:
            return True
        return False

    def _has_data_in_js(self, soup: BeautifulSoup) -> bool:
        """檢查 inline JS 中是否有嵌入資料"""
        for script in soup.find_all('script', src=False):
            content = str(script.string or '')
            if any(kw in content for kw in [
                'window.__', 'var data', 'JSON.parse',
                'roomData', 'venueData', 'meetingRoom',
            ]):
                return True
        return False

    def _detect_anti_scraping(self, response) -> str:
        """偵測反爬蟲機制"""
        if 'cloudflare' in response.text.lower():
            return 'Cloudflare'
        return None

    def _decide_strategy(self, report: dict) -> str:
        """根據技術偵測結果決定提取策略"""
        if report['httpStatus'] not in (200, 202):
            return 'failed'
        if report['isDynamic']:
            return 'dynamic_js'
        return 'static_html'
