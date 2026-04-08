#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scraper - 統一場地爬蟲

Usage:
    python -m scraper --test 1043
    python -m scraper --batch --sample 5
    python -m scraper --fix-rooms
    python -m scraper --report
"""

from .scraper import main

if __name__ == '__main__':
    main()
