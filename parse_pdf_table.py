#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse 容量表.pdf table data to extract exact dimensions
"""

import re
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import PyPDF2
except ImportError:
    import pypdf
    PyPDF2 = pypdf

# Read PDF
pdf_path = "容量表.pdf"
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    page = reader.pages[1]  # Page 2 has the capacity chart
    text = page.extract_text()

print("Raw text from PDF page 2:")
print("="*80)
print(text)
print("="*80)

# Parse the data
print("\n\nExtracted Data:")
print("="*80)

# Pattern to find room info
# The PDF text has lines like: "Sea 海 18 58 2.7" or similar
# Format appears to be: [NameEn] [Name] [Ping] [SqMeters] [Ceiling]

lines = text.split('\n')

# Find the section with room data
in_data_section = False
room_data = []

for line in lines:
    # Look for room name patterns
    if 'BALLROOM' in line or 'SUPERNOVA' in line:
        in_data_section = True
        continue

    if in_data_section:
        # Try to extract room data
        # Pattern: Chinese name followed by numbers
        # Examples: "海 18 58 2.7", "山 20 65 2.7"

        # Remove extra spaces
        line = ' '.join(line.split())

        # Check if line has room data (contains Chinese + numbers)
        if re.search(r'[\u4e00-\u9fff]', line) and re.search(r'\d+\.\d+|\d+', line):
            print(f"Line: {line}")

            # Extract numbers
            numbers = re.findall(r'\d+\.\d+|\d+', line)
            if len(numbers) >= 3:
                ping = None
                sqm = None
                ceiling = None

                # Try to identify which number is which
                # Ceiling is usually 2.7 or 3
                # SqMeters is usually 50-300 range
                # Ping is usually 15-100 range

                for num in numbers:
                    val = float(num)
                    if val == 2.7 or val == 3.0 or val == 5.5:
                        ceiling = val
                    elif val > 200:
                        ping = val
                    elif val < 200:
                        sqm = val

                if ping and sqm and ceiling:
                    print(f"  → Ping: {ping}, SqM: {sqm}, Ceiling: {ceiling}")

print("\n\nManual extraction based on PDF structure:")
print("="*80)

# Based on the PDF text structure, let me manually parse
rooms = [
    ("超新星大宴會廳", "SUPERNOVA BALLROOM", None, None, 3.0),
    ("海", "SEA", 18, 59, 2.7),
    ("山", "MOUNTAIN", 20, 65, 2.7),
    ("林", "FOREST", None, None, 2.7),
    ("水", "WATER", None, None, 2.7),
    ("晶", "CRYSTAL", None, None, 2.7),
    ("雲", "CLOUD", None, None, 2.7),
    ("風", "WIND", None, None, 2.7),
    ("光", "LIGHT", None, None, 2.7),
]

for name, name_en, ping, sqm, ceiling in rooms:
    if ping:
        print(f"{name} ({name_en}): {ping} ping = {sqm} sqm, Ceiling: {ceiling}M")
    else:
        print(f"{name} ({name_en}): Ceiling: {ceiling}M (need to extract area)")

print("\n\nNote: The PDF text extraction is garbled for the table structure.")
print("The areas for some rooms need to be manually verified from the PDF visual layout.")
