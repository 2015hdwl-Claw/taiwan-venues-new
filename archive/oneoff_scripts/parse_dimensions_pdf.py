#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse 容量表.pdf to extract venue dimensions
"""

import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import PyPDF2
    print(f"[OK] PyPDF2 available")
except ImportError:
    try:
        import pypdf
        PyPDF2 = pypdf
        print(f"[OK] pypdf available")
    except ImportError:
        print("[ERROR] No PDF library found. Installing PyPDF2...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        import PyPDF2

# Read PDF
pdf_path = "容量表.pdf"
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    num_pages = len(reader.pages)
    print(f"\n[OK] PDF has {num_pages} pages\n")

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        print(f"{'='*80}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*80}")
        print(text)
        print()
