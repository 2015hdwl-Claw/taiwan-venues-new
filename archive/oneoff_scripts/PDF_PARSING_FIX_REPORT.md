# PDF Parsing Fix Report

**Date**: 2026-03-25
**Issues Fixed**: TICC PDF parsing errors, Nangang Exhibition Center analysis

---

## Summary

Successfully fixed the PDF parsing issues identified by the user:

1. **TICC (ID 1448)**: Fixed PDF parsing with new V5 parser
   - "大會堂全場": Now correctly shows capacity 3100 (was null)
   - "大會堂半場": Correctly parsed from multi-line data
   - "3樓南/北軒": Name no longer truncated to "3", capacity 90 correctly extracted

2. **Nangang Exhibition Center (ID 1500)**: Analyzed webpage technology
   - Site type: Static/SSR (simple)
   - Issue: No meeting room data on homepage
   - Recommendation: Needs subpage exploration or manual data entry

---

## Problem Analysis

### Original Issues

From user feedback:
> "TICC會議室的資料，還是錯誤百出。例如大會堂全場/半場的資料很清楚，卻辨識成空值，會議室：3樓南/北軒，卻辨識只有3。"

**Root Causes**:
1. **PyPDF2 limitations**: Doesn't preserve table structure well
2. **Multi-line data**: "大會堂半場" data split across lines 13-14
3. **Name truncation**: "3樓南 /北軒" parsed as just "3" due to poor regex
4. **Wrong column mapping**: First number interpreted incorrectly

### Example from Raw PDF Text

```
Line 12:      大會堂全場  3,100  — — 2,973/899  — 159,000  170,000  —
Line 13: 大會堂半場
Line 14: (1-27 排) 1,208  — — — — 112,000  123,000  —
Line 43: 3樓南 /北軒  90 70 40 52 6 152/46  18×7.5×3.7  18,500  21,500 23,500
```

---

## Solution: V5 Parser

### Key Improvements

1. **Correct Column Mapping**
   ```
   name | cap_theater | cap_class | cap_u | cap_neg | booth | area | dim | price_wd | price_we | price_ex
   ```

2. **Multi-line Handling**
   - Detects when room name is on one line, data on next
   - Merges lines when next line starts with "("
   - Example: "大會堂半場" + "(1-27 排) 1,208..."

3. **Smart Name Extraction**
   - Uses multiple-space pattern to find name end
   - Preserves special characters: "/", "—", etc.
   - Example: "3樓南 /北軒" extracted correctly

4. **Intelligent Number Classification**
   - Capacity: 10-5000 people
   - Area: Extracts from fraction format (2,973/899)
   - Price: >5000 (sorted ascending)

### Results

| Room | Before | After | Status |
|------|--------|-------|--------|
| 大會堂全場 | Cap: null, Area: null | Cap: 3100, Area: 2973, Price: 159000 | ✅ FIXED |
| 大會堂半場 | Not found | Cap: 1208, Price: 112000 | ✅ FIXED |
| 3樓南/北軒 | Name: "3", Cap: null | Name: "3樓南 /北軒", Cap: 90, Area: 152 | ✅ FIXED |

**Total Rooms**: 26 (down from 31 due to duplicate removal)

---

## Nangang Exhibition Center (ID 1500)

### Analysis Results

```bash
python analyze_tpec.py
```

**Findings**:
- Site: https://www.tcec.com.tw/
- Type: Static/SSR (simple)
- JavaScript: 1 file
- Meeting room links: 0
- PDF links: 0
- Navigation: None on homepage

**Issue**: Homepage has no meeting room information

### Recommendations

1. **Option A**: Manual subpage exploration
   - Look for URLs like /meeting, /venue, /space
   - Check sitemap.xml

2. **Option B**: Manual data entry
   - Contact venue for meeting room specs
   - Enter data manually into venues.json

3. **Option C**: Deeper crawling
   - Use full_site_scraper_v4.py with subpage discovery
   - May need JavaScript handling if data is dynamic

---

## Files Created

1. **analyze_tpec.py** - Nangang webpage technology detector
2. **ticc_parser_v5.py** - Final PDF parser (V5)
3. **update_ticc_final_v5.py** - Update script for venues.json
4. **ticc_v5_final_*.json** - Parsed TICC data

## Files Modified

1. **venues.json** - Updated ID 1448 (TICC)
2. **venues.json.backup.ticc_v5_*** - Backup created

---

## Verification

### TICC (ID 1448)

Check the updated data:
```bash
python check_venue_details.py --id 1448
```

Expected results:
- 26 meeting rooms
- 大會堂全場: 3100 people, 2973 sqm, $159,000
- 3樓南/北軒: 90 people, 152 sqm, $18,500

### Nangang (ID 1500)

Current status:
- 0 meeting rooms
- Needs manual intervention or deeper crawling

---

## Next Steps

### Immediate
1. ✅ TICC PDF parsing - FIXED
2. ⚠️ Nangang Exhibition Center - Needs decision
   - Manual data entry?
   - Deeper crawling?
   - Contact venue?

### Future Improvements
1. **PDF Library Migration**: Consider pdfplumber or tabula-py for better table extraction
2. **Room Name Patterns**: Build regex database for common room naming patterns
3. **Multi-line Detection**: Improve algorithm for detecting continued data
4. **Validation**: Add cross-checks against expected ranges

---

## Lessons Learned

### PDF Scraping Best Practices

1. **Never assume single-line data**
   - PDFs often split data across lines
   - Always look ahead when data seems incomplete

2. **Name extraction is critical**
   - Room names can contain numbers, letters, slashes
   - Use multiple strategies (multi-space, single-space, regex)

3. **Understand the table structure**
   - Map columns before writing parser
   - Use real data samples to test

4. **Validate with known examples**
   - Test parser against user-reported issues
   - Verify critical rooms before deploying

---

**Status**: ✅ TICC Fixed, ⚠️ Nangang Pending
**Updated**: 2026-03-25 20:15
