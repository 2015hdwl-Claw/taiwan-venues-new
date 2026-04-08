# Quick Reference Guide
# 快速參考指南 - Taiwan Venues Project

**Last Updated:** 2026-03-28
**Status:** Ready for Handover ✅

---

## 🚀 Quick Start (5 minutes)

### 1. Verify Database (驗證資料庫)

```bash
python -c "import json; venues = json.load(open('venues.json')); print(f'Venues: {len(venues)}, Avg Quality: {sum(v.get(\"metadata\", {}).get(\"qualityScore\", 0) for v in venues)/len(venues):.1f}')"
```

**Expected Output:** `Venues: 80, Avg Quality: 72.2`

---

## 📊 Current Stats (當前統計)

| Metric | Value |
|--------|-------|
| Total Venues | 80 |
| With Room Data | 69 (86.2%) |
| Average Quality | 72.2/100 |
| Total Meeting Rooms | 392 |

---

## ⚠️ MANDATORY Workflow (強制性工作流程)

### Three-Stage Scraping (三階段爬蟲)

```
階段1: 技術檢測 → 階段2: 深度爬蟲 → 階段3: 驗證寫入
```

**⚠️ DO NOT SKIP ANY STAGE!**

**See:** `memory/three_stage_mandatory.md`

---

## 📁 Critical Files (關鍵檔案)

### Must Copy (必須複製)

| File | Size | Description |
|------|------|-------------|
| venues.json | 535K | Main database |
| CLAUDE.md | 13K | Project config |
| KNOWLEDGE_BASE.md | 33K | Knowledge base |
| HANDOVER_REPORT.md | 19K | Handover report |
| memory/ | 4.1K | All memories |

---

## 🎯 Success Metrics (成功指標)

✅ 80 venues - ACHIEVED
✅ 86.2% completeness - ACHIEVED
✅ 72.2 average quality - ACHIEVED
✅ 0% low quality venues - ACHIEVED

---

**Ready for handover! ✅**
