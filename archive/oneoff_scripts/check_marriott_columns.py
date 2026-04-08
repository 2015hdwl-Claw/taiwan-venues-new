#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

data = json.load(open('marriott_pdf_extraction.json', encoding='utf-8'))
row = data['pdfs'][0]['tables'][0]['data'][4]  # Spring

print('Row 4 (Spring 春) columns 11-24:')
for i in range(11, min(25, len(row))):
    print(f'  [{i}]: {repr(row[i])[:60]}')
