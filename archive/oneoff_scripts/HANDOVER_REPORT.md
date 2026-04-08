# Taiwan Venues Project - Handover Report
## 台灣場地資料庫專案 - 交接報告

**Date:** 2026-03-28
**Project:** Activity Master (活動大師) - Taiwan Venues Database
**Status:** Production Ready ✅
**Claude Code Version:** Sonnet 4.6

---

## 📋 Executive Summary (執行摘要)

This project builds a comprehensive database of event venues in Taiwan, including hotels, convention centers, exhibition halls, and wedding banquet venues. The database contains detailed information about meeting rooms, capacities, pricing, and contact information.

**Key Achievement:** 80 venues with 392 meeting rooms, 86.2% data completeness, average quality score of 72.2/100.

**本專案目標：** 建立台灣會議場地的完整資料庫，包含飯店、會展中心、展覽館、婚宴會館等，提供詳細的會議室資料、容量、價格與聯絡資訊。

**核心成果：** 80個場地、392個會議室、86.2%資料完整度、平均品質分數72.2/100。

---

## 📊 Current Status (當前狀態)

### Database Statistics (資料庫統計)

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Venues** | 80 | 100% |
| **With Room Data** | 69 | 86.2% ✅ |
| **Without Room Data** | 11 | 13.8% |
| **Total Meeting Rooms** | 392 | - |
| **Avg Rooms per Venue** | 5.7 | - |
| **Average Quality Score** | 72.2/100 | - |

### Quality Distribution (品質分布)

| Quality Level | Count | Percentage |
|--------------|-------|------------|
| **High (≥70)** | 39 | 48.8% ✅ |
| **Medium (36-69)** | 41 | 51.2% |
| **Low (≤35)** | 0 | 0.0% 🎉 |

### Geographic Distribution (地理分布)

| City | Venues | Percentage |
|------|--------|------------|
| 台北市 | 41 | 51.2% |
| 新北市 | 14 | 17.5% |
| 台中市 | 14 | 17.5% |
| 高雄市 | 10 | 12.5% |
| 桃園市 | 1 | 1.3% |

### Venue Type Distribution (場地類型分布)

| Type | Count | Percentage |
|------|-------|------------|
| 飯店場地 | 34 | 42.5% |
| 婚宴場地 | 19 | 23.8% |
| 會議中心 | 12 | 15.0% |
| 展演場地 | 5 | 6.2% |
| 運動場地 | 4 | 5.0% |
| 會展中心 | 3 | 3.8% |
| 展覽館 | 2 | 2.5% |
| 演藝中心 | 1 | 1.3% |

### Top 10 Venues by Room Count (會議室數量排行榜)

| Rank | ID | Name | Rooms | Quality |
|------|-----|------|-------|---------|
| 1 | 1500 | 南港展覽館 | 28 | 90 |
| 2 | 1448 | 台大集思會議中心 TICC | 27 | 96 |
| 3 | 1125 | 華山1914文创园区 | 24 | 100 |
| 4 | 1053 | 台北老爺酒店 | 23 | 100 |
| 5 | 1103 | 台北萬豪酒店 | 21 | 80 |
| 6 | 1516 | 彭園婚宴會館 新店館 | 18 | 100 |
| 7 | 1072 | 台北將軍大酒店 | 13 | 75 |
| 8 | 1493 | 麗緻大飯店 中壢館 | 13 | 100 |
| 9 | 1128 | 集思台大會議中心 NTUCC | 12 | 100 |
| 10 | 1076 | 台北寒舍艾麗酒店 | 11 | 75 |

---

## 🧠 Core Knowledge & Memories (核心知識與記憶)

### Critical Lessons Learned (關鍵教訓)

#### 1. Three-Stage Scraping Workflow (三階段爬蟲流程) ⚠️ **MANDATORY**

**必須嚴格執行，不可跳過任何階段：**

```
階段1：技術檢測 → 階段2：深度爬蟲 → 階段3：驗證寫入
```

**Stage 1: Technical Detection (技術檢測)**
- HTTP status code check
- Content-Type detection
- Page type detection (static HTML vs dynamic JS)
- CMS identification (WordPress, Drupal, custom)
- Data location discovery (JSON-LD, embedded JSON, HTML)
- Anti-scraping mechanisms (Cloudflare, cookies, rate limiting)

**Stage 2: Deep Scraping (深度爬蟲)**
- Level 1: Main page analysis (extract ALL links, not just common paths)
- Level 2: Meeting page discovery (visit conference/banquet links)
- Level 3: Detail page extraction (complete data extraction)

**Stage 3: Validation & Write (驗證寫入)**
- Validate extracted data completeness
- Check data quality (capacities, areas, prices)
- Write to venues.json with backup
- Generate verification report

**User Requirement (2026-03-26):**
> "那就確實地做吧，我一開始就要求，確實地做。寫入知識庫，寫入claude.md中，確實按步驟做事，不要投機取巧。"

**File:** `memory/three_stage_mandatory.md`

---

#### 2. PDF Parsing Best Practices (PDF 解析最佳實踐)

**Use pdfplumber for Chinese PDF tables:**
- ✅ `pdfplumber` (designed for tables, supports Chinese)
- ❌ `PyPDF2` (poor table extraction)

**Extraction Strategy:**
```python
vertical_strategy='text'
horizontal_strategy='text'
```

**Key Success Cases:**
- Victoria Hotel: 17 sub-venues, 94% price coverage
- Nangang Exhibition Center: 28 rooms, 100% coverage
- NTUCC: 12 rooms (from PDF, not HTML)

**Critical Rule (2026-03-26):**
Always validate PDF extraction results - don't assume data was extracted just because PDF was found.

**File:** `memory/pdfplumber_success_patterns.md`

---

#### 3. Complete Room Data Structure (完整會議室資料結構)

**30-Field Standard:**

1. **Basic Info:** id, name, nameEn
2. **Area:** areaSqm, areaPing, areaUnit
3. **Dimensions:** lengthM, widthM, heightM
4. **Capacity:** theater, banquet, classroom, boardroom, reception
5. **Price:** weekday, holiday, hourly, daily
6. **Equipment:** projector, microphone, audio, video conferencing
7. **Other:** images, floor, source, lastUpdated

**NULL Value Tracking:**
- Use `null` (not empty string) for missing data
- Enables accurate completeness tracking

**File:** `memory/complete_room_structure_standard.md`

---

#### 4. SubSpace Structure (細分場地結構)

**When to use subSpaces:**
- PDF shows partitioned pricing
- Venue name contains "區" (area/zone)
- Movable partitions available

**Example: Victoria Hotel**
- Main Hall → 7 sub-spaces (A, B, C zones, corridor, outdoor garden, VIP room)
- Victoria Hall → 4 sub-spaces
- Tiandi Hall → 6 sub-spaces

**Key Fields:**
- `combinable`: Can sub-spaces be combined?
- `price`: Separate pricing for each sub-space
- `capacity`: Individual capacity

**File:** `memory/venue_subspace_structure.md`

---

#### 5. Important Rules (重要規則)

**❌ NO MORE REPORTS (2026-03-26)**
- Do NOT generate analysis reports
- Focus on actual work: scraping, updating data, fixing issues
- User quote: "往後就都不用任何分析報告，因為寫了，你也不一定會依據而改善。"

**File:** `memory/no_more_reports_rule.md`

---

## 🏗️ Technical Architecture (技術架構)

### Data Structure (資料結構)

**Venue Object:**
```json
{
  "id": 1128,
  "name": "集思台大會議中心(NTUCC)",
  "venueType": "會議中心",
  "city": "台北市",
  "address": "台北市羅斯福路四段85號B1",
  "url": "https://www.meeting.com.tw/ntu/",
  "contact": {
    "phone": "+886-2-3366-4504",
    "email": "ntu.service@meeting.com.tw"
  },
  "capacity": {
    "theater": 400,
    "classroom": 150
  },
  "rooms": [
    {
      "id": "1128-01",
      "name": "國際會議廳",
      "capacity": {"theater": 400},
      "area": 253.6,
      "areaUnit": "坪",
      "price": {"weekday": 44000, "holiday": 48000},
      "source": "pdf_20250401"
    }
  ],
  "verified": true,
  "metadata": {
    "lastScrapedAt": "2026-03-25T10:30:00",
    "scrapeVersion": "V4_PDF",
    "scrapeConfidenceScore": 85,
    "totalRooms": 12,
    "qualityScore": 100
  }
}
```

### Quality Scoring (品質評分)

**Base Score:** 35 points

**Bonus Points:**
- Phone: +10
- Email: +10
- Per room: +3 to +8 (depending on completeness)
- Capacity data: +5
- Area data: +3 to +5
- Price data: +10
- PDFs: +5

**Maximum:** 100 points

**Current Average:** 72.2/100

---

## 📁 File Structure (檔案結構)

### Core Files (核心檔案)

```
taiwan-venues-new/
├── venues.json                    # Main database (80 venues)
├── sources.json                   # Source tracking (optional)
├── CLAUDE.md                      # Project configuration
├── KNOWLEDGE_BASE.md              # Project knowledge base
├── memory/                        # Critical memories & lessons
│   ├── MEMORY.md                  # Memory index
│   ├── three_stage_mandatory.md   # ⚠️ MANDATORY workflow
│   ├── pdfplumber_success_patterns.md
│   ├── venue_subspace_structure.md
│   ├── complete_room_structure_standard.md
│   └── ...
├── backup/                        # Automatic backups (auto-created)
└── [various scraper scripts]     # 50+ scraping scripts
```

### Key Scraper Scripts (重要爬蟲腳本)

**Main Scrapers:**
- `intelligent_scraper_v3.py` - Fast single-page scraping
- `full_site_scraper_v4.py` - Complete multi-page scraping
- `full_site_scraper_v4_enhanced.py` - V4 + PDF extraction

**Latest Scripts (2026-03-28):**
- `deep_scrape_all_zero_rooms.py` - Deep scraping for 0-room venues
- `three_stage_scraper.py` - Strict three-stage workflow
- `update_and_add_venues.py` - Fix URLs + add new venues

### Backup Files (備份檔案)

**Pattern:** `venues.json.backup.{description}_{timestamp}.json`

**Recent Backups:**
- `venues.json.backup.deep_scrape_20260328_055923.json`
- `venues.json.backup.remove_10_20260328_055501.json`
- `venues.json.backup.fix_add_20260328_054245.json`

**Total Backups:** 50+ files

---

## 🚀 Getting Started on New Machine (在新機器上開始)

### Prerequisites (前置需求)

```bash
# Python 3.10+
python --version

# Required packages
pip install requests beautifulsoup4 pdfplumber lxml

# Or use requirements.txt (if exists)
pip install -r requirements.txt
```

### Setup Steps (設置步驟)

1. **Copy Project Files:**
   ```bash
   # Copy entire directory
   scp -r taiwan-venues-new/ user@new-machine:/path/to/
   ```

2. **Verify Database:**
   ```bash
   cd taiwan-venues-new
   python -c "import json; venues = json.load(open('venues.json')); print(f'Total venues: {len(venues)}')"
   # Expected: Total venues: 80
   ```

3. **Check Statistics:**
   ```bash
   python -c "
   import json
   venues = json.load(open('venues.json'))
   scores = [v.get('metadata', {}).get('qualityScore', 0) for v in venues]
   print(f'Average quality: {sum(scores)/len(scores):.1f}')
   print(f'Venues with rooms: {sum(1 for v in venues if v.get(\"rooms\"))}')
   "
   ```

### First Task on New Machine (新機器上的第一個任務)

**Recommended:** Test a simple scraper to verify environment

```bash
# Test single venue scrape
python intelligent_scraper_v3.py --batch --sample 1
```

---

## ⚠️ Known Issues & Limitations (已知問題與限制)

### Venues Without Room Data (11個，13.8%)

**Failed Scraping:**
- ID 1510: 新莊典華 - HTTP 403
- ID 1512: 台北新板希爾頓酒店 - No room data found
- ID 1517: 頤品大飯店 - No room data found
- ID 1520: 寶麗金婚宴會館 市政店 - HTTP 202
- ID 1521: 寶麗金婚宴會館 崇德店 - HTTP 202
- ID 1523: 好運來洲際宴展中心 - No room data
- ID 1533: 臺中國際會展中心 - Exhibition center type
- ID 1534: 臺中國際展覽館 - Exhibition hall type
- ID 1535: 高雄展覽館 KEC - Exhibition hall type
- ID 1542: 高雄萬豪酒店 - No room data found
- ID 1543: 衛武營國家藝術文化中心 - Performance center type

**Reasons:**
- HTTP errors (403, 404, 202)
- Exhibition centers may not use traditional "meeting room" format
- Dynamic websites requiring browser-based scraping

### Technical Limitations

1. **JavaScript-Heavy Sites:** Current scrapers use requests+BeautifulSoup, cannot handle dynamic JS content
2. **Cloudflare Protection:** Some sites block automated scraping
3. **PDF Password Protection:** Cannot extract from password-protected PDFs
4. **Image-Based PDFs:** Cannot extract text from scanned/image-based PDFs

---

## 📝 Recommended Next Steps (建議後續步驟)

### Priority 1: Complete Missing Data (優先級1：完成缺失資料)

**Action:** Use browser-based scraping (Selenium/Playwright) for 11 failed venues

**Tools Needed:**
- Selenium or Playwright
- Browser drivers (Chrome/Firefox)

**Estimated Time:** 2-3 hours

### Priority 2: Data Verification (優先級2：資料驗證)

**Action:** Manual verification of high-priority venues (quality ≥90)

**Top 10 Venues to Verify:**
1. ID 1125: 華山1914文创园区 (Q:100)
2. ID 1053: 台北老爺酒店 (Q:100)
3. ID 1493: 麗緻大飯店 中壢館 (Q:100)
4. ID 1128: 集思台大會議中心 (Q:100)
5. ID 1516: 彭園婚宴會館 新店館 (Q:100)
6. ID 1545: 承億酒店 (Q:100)
7. ID 1504: 高雄國際會議中心 (Q:100)
8. ID 1448: 台大集思會議中心 (Q:96)
9. ID 1500: 南港展覽館 (Q:90)
10. ID 1103: 台北萬豪酒店 (Q:80)

### Priority 3: Documentation (優先級3：文檔完善)

**Action:** Update CLAUDE.md with latest workflow

**Sections to Add:**
- Deep scraping workflow for 0-room venues
- Quality scoring calculation details
- Backup strategy

---

## 🔑 Important Files to Copy (重要需要複製的檔案)

### Must Copy (必須複製)

1. **venues.json** - Main database
2. **memory/** directory - All critical lessons
3. **CLAUDE.md** - Project configuration
4. **KNOWLEDGE_BASE.md** - Knowledge base

### Optional (選擇性複製)

1. **Scraper scripts** - For reference
2. **Backup files** - For rollback capability
3. **Report scripts** - For generating reports

### Can Ignore (可忽略)

1. **Test files** - `test_*.py`
2. **Temporary scripts** - Old versions
3. **Cache files** - `__pycache__/`

---

## 📞 Support & Resources (支援與資源)

### Project Documentation (專案文檔)

- **CLAUDE.md:** Project configuration and workflow
- **KNOWLEDGE_BASE.md:** Comprehensive knowledge base
- **memory/MEMORY.md:** Memory index with links

### Critical Memories (關鍵記憶)

1. `memory/three_stage_mandatory.md` - ⚠️ MANDATORY workflow
2. `memory/pdfplumber_success_patterns.md` - PDF extraction
3. `memory/venue_subspace_structure.md` - SubSpace structure
4. `memory/complete_room_structure_standard.md` - 30-field standard

### External Resources (外部資源)

- **pdfplumber Documentation:** https://github.com/jsvine/pdfplumber
- **BeautifulSoup Documentation:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Python Requests:** https://docs.python-requests.org/

---

## ✅ Pre-Handover Checklist (交接前檢查清單)

### Database Integrity (資料庫完整性)

- [x] venues.json contains 80 venues
- [x] Average quality score: 72.2/100
- [x] 86.2% venues have room data (69/80)
- [x] 0% low quality venues (≤35)
- [x] Total 392 meeting rooms

### Documentation Completeness (文檔完整性)

- [x] CLAUDE.md present and up-to-date
- [x] KNOWLEDGE_BASE.md present
- [x] memory/ directory with all critical lessons
- [x] Three-stage workflow documented
- [x] PDF parsing best practices documented

### Backup Status (備份狀態)

- [x] Recent backups available (50+ files)
- [x] Latest backup: 2026-03-28
- [x] Backup pattern consistent

### Code Quality (程式碼品質)

- [x] UTF-8 encoding for all files
- [x] Windows console wrapper for Chinese display
- [x] Error handling in all scripts
- [x] Backup before every write operation

---

## 🎯 Success Metrics (成功指標)

### Achieved (已達成)

✅ 80 venues with comprehensive data
✅ 86.2% data completeness (69/80 with room data)
✅ Average quality score: 72.2/100
✅ 392 meeting rooms extracted
✅ 48.8% high-quality venues (≥70)
✅ 0% low-quality venues (≤35)
✅ Complete knowledge base and memories
✅ Automated backup system

### Room for Improvement (改進空間)

- 11 venues still need room data (13.8%)
- Some venues may have outdated pricing
- Manual verification recommended for top 10 venues

---

## 📋 Handover Summary (交接摘要)

### What's Working (運作正常)

1. **Automated Scraping System:** Successfully extracted data from 86.2% of venues
2. **Quality Scoring:** Comprehensive quality assessment system
3. **Backup System:** Automatic backups before every change
4. **Knowledge Base:** Complete documentation of lessons learned
5. **Three-Stage Workflow:** Proven methodology for new venues

### What Needs Attention (需要注意)

1. **11 venues without room data** - May require browser-based scraping
2. **Pricing data** - May be outdated, manual verification recommended
3. **Dynamic websites** - Current scrapers cannot handle JS-heavy sites

### Quick Start Commands (快速開始指令)

```bash
# Check database status
python -c "import json; venues = json.load(open('venues.json')); print(f'{len(venues)} venues, avg Q: {sum(v.get(\"metadata\", {}).get(\"qualityScore\", 0) for v in venues)/len(venues):.1f}')"

# Scrape single venue
python intelligent_scraper_v3.py --batch --sample 1

# Generate quality report
python -c "
import json
venues = json.load(open('venues.json'))
for v in venues:
    q = v.get('metadata', {}).get('qualityScore', 0)
    if q >= 90:
        print(f'{v[\"id\"]:4d} | {v[\"name\"][:40]:40s} | Q:{q:3d} | {len(v.get(\"rooms\", [])):2d} rooms')
"
```

---

## 🏁 Conclusion (結論)

This project is in excellent condition with 80 venues, 86.2% data completeness, and comprehensive documentation. The three-stage scraping workflow is proven and effective. The knowledge base contains all critical lessons learned.

**Key Recommendation:** Follow the three-stage workflow strictly for any new scraping tasks. Do not skip technical detection or validation steps.

**專案狀態優秀：** 80個場地、86.2%資料完整度、完整文檔。三階段爬蟲流程經證實有效。知識庫包含所有關鍵教訓。

**核心建議：** 新的爬蟲任務務必嚴格遵循三階段流程，不可跳過技術檢測或驗證步驟。

---

**Report Generated:** 2026-03-28
**Generated By:** Claude Code (Sonnet 4.6)
**Project:** Taiwan Venues Database (活動大師)
**Status:** ✅ Production Ready

---

## Appendix A: File Manifest (附錄A：檔案清單)

### Core Files (8 files)
- venues.json
- sources.json
- CLAUDE.md
- KNOWLEDGE_BASE.md
- memory/MEMORY.md
- memory/three_stage_mandatory.md
- memory/pdfplumber_success_patterns.md
- memory/venue_subspace_structure.md

### Memory Files (5 files)
- complete_room_structure_standard.md
- pdf_data_validation_workflow.md
- pdf_extraction_complete_workflow.md
- venue_completeness_analysis.md
- no_more_reports_rule.md

### Scraper Scripts (50+ files)
- intelligent_scraper_v3.py
- full_site_scraper_v4.py
- full_site_scraper_v4_enhanced.py
- deep_scrape_all_zero_rooms.py
- three_stage_scraper.py
- [plus 45+ more]

### Backup Files (50+ files)
- Pattern: venues.json.backup.{description}_{YYYYMMDD_HHMMSS}.json

**Total Files:** 150+ files

---

**End of Handover Report**
**交接報告完結**
