---
name: ttab-scraper
description: >
  Use this skill whenever the user wants to scrape, extract, collect, or automate
  data from TTABVUE (USPTO Trademark Trial and Appeal Board database). Triggers include:
  any mention of TTAB, TTABVUE, trademark proceedings, opposition scraping, trademark
  appeals data, or collecting USPTO case data into a CSV or Excel file. Also trigger
  when the user says "run the scrape", "update the TTAB data", "get new TTAB results",
  or references date ranges for trademark case collection. Always use this skill even
  if the user only mentions part of the workflow (e.g. just "get the new filings").
---

# TTAB Scraper Skill

This skill guides Claude Code to build, run, and maintain a Python web scraper that
extracts case data from TTABVUE (USPTO's Trademark Trial and Appeal Board search
interface) with date filtering, party extraction, and Excel-ready CSV output.

---

## Context

**Target site:** https://ttabvue.uspto.gov/ttabvue/
**Search entry point:** https://ttabvue.uspto.gov/ttabvue/query

**Key URL parameters:**
- `filefrom` — start date (MM/DD/YYYY)
- `fileto` — end date (MM/DD/YYYY)
- `procstatus` — proceeding status (e.g. PENDING, TERMINATED, ALL)
- `type` — proceeding type (e.g. OP = Opposition, CA = Cancellation, EX = Extension)
- `page` — pagination (starts at 1)

**Example search URL:**
```
https://ttabvue.uspto.gov/ttabvue/query?procstatus=ALL&filefrom=01/01/2024&fileto=12/31/2024&type=OP&page=1
```

---

## Stack

- **Language:** Python 3
- **HTTP Library:** requests + BeautifulSoup4 (lighter than Playwright, works for this site)
- **Output:** CSV via Python `csv` module
- **Scheduling:** cron (Mac/Linux) or Task Scheduler (Windows)

**Install dependencies:**
```bash
pip install requests beautifulsoup4 lxml
```

**Note:** The scraper uses requests/BeautifulSoup instead of Playwright because TTABVUE returns full HTML without requiring JavaScript execution. This makes the scraper faster, more reliable, and easier to deploy.

### Email Reporting (Optional)

**File:** `email_reporter.py`
**Dependencies:** Built-in (smtplib, email)

**Features:**
- Send CSV results via email
- Automatic summary generation
- **Persistent configuration** (survives restarts)
- Gmail and custom SMTP support

**Configuration storage:** `config.json` (created on first use, persists forever)

---

## Data Fields Extracted (Implemented)

### Enhanced Scraper (scraper_enhanced.py) - CURRENT VERSION

Extracts complete party information from list pages:

- **Case Number** - Unique case identifier (e.g., 92090439)
- **Detail URL** - Direct link to full case details on TTABVUE
- **Filing Date** - Date case was filed (MM/DD/YYYY format)
- **Defendant Name** - Full defendant/respondent party name
- **Defendant Correspondence** - Defendant trademark mark name and serial numbers
- **Plaintiff Name** - Full plaintiff/petitioner party name
- **Plaintiff Correspondence** - Plaintiff trademark mark name and serial numbers

**Features:**
- ✅ Date filtering (default: last 60 days, configurable)
- ✅ Excel-ready CSV format (UTF-8 BOM encoding)
- ✅ Full pagination support
- ✅ Automatic party extraction from table structure
- ✅ Deduplication across pages

### Basic Scraper (scraper_final.py) - LEGACY VERSION

Basic extraction without party details:
- Proceeding Number
- Proceeding Type (CAN/OPP/EXT/EXA)
- Filing Date
- Detail URL

### Not yet implemented (future enhancement):
- Attorney information (requires detail page scraping)
- Trial dates (requires detail page scraping)
- Document counts (requires detail page scraping)
- Registration numbers extraction

> See `references/field-map.md` for confirmed working selectors.

---

## Scraper Architecture (Implemented)

**Current implementation structure:**

```
ttab-scraper/
├── scraper_enhanced.py  # CURRENT: Enhanced scraper with date filtering & party extraction
├── scraper_final.py     # LEGACY: Basic scraper with pagination only
├── output/              # CSV files saved here (timestamped)
├── logs/                # Run logs (timestamped)
├── README.md            # Basic documentation
└── USAGE.md             # Enhanced scraper usage guide
```

### scraper_enhanced.py — Enhanced Logic (CURRENT VERSION)

```
1. Configure query URL and date range (DAYS_BACK = 60)
2. Calculate cutoff date (today - 60 days)
3. Fetch page 1 using requests library
4. Auto-detect total pages from pagination links
5. Loop through all pages (page=1, page=2, etc.):
   a. Parse all proceeding links on current page
   b. Extract filing date and check if within date range
   c. If within range: extract party information
      - Navigate table structure: TR > TD[0] (proceeding) | TD[1] (defendant) | TD[2] (plaintiff)
      - Extract defendant name and correspondence (mark, serial #)
      - Extract plaintiff name and correspondence (mark, serial #)
   d. Add 1-second delay between pages (rate limiting)
6. Deduplicate cases by proceeding number
7. Write filtered cases to Excel-ready CSV (UTF-8 BOM)
8. Log run summary with date filter and record count
```

**Key implementation details:**
- Date filtering: only includes cases from last N days (configurable)
- Party extraction: parses defendant and plaintiff from table cell structure
- Excel-ready: CSV with UTF-8 BOM encoding for seamless Excel import
- Table parsing: TR contains 3 TDs (proceeding | defendant | plaintiff)
- Correspondence parsing: extracts "Mark:" and "S#:" data via regex
- Outputs: `ttab_cases_filtered_YYYYMMDD_HHMMSS.csv`

### scraper_final.py — Basic Logic (LEGACY)

Basic pagination scraper without date filtering or party extraction.
See IMPLEMENTATION_MEMORY.md for details.

---

## Periodic Run Setup

Once scraper is confirmed working, Claude Code should:

1. Add a `--from` and `--to` CLI flag to `scraper.py` so dates can be passed at runtime
2. Write a shell script `run_ttab.sh`:
```bash
#!/bin/bash
cd /path/to/ttab-scraper
python scraper.py --from "$(date -v-7d +%m/%d/%Y)" --to "$(date +%m/%d/%Y)"
```
3. Set up a cron job (or Task Scheduler on Windows) to run weekly

---

## Common Issues & Fixes

| Problem | Fix |
|---|---|
| Page loads slowly | Add `await page.wait_for_load_state("networkidle")` |
| Results not appearing | Site may require JS — use Playwright, not requests |
| Pagination breaks | Check if "Next" button selector changes on last page |
| Detail page times out | Add retry logic with `try/except` and `page.reload()` |
| Rate limiting / blocked | Add `await asyncio.sleep(1)` between detail page clicks |
| Selectors change | Re-inspect element in browser, update `field-map.md` |

---

## Claude Code Usage Instructions

### For Claude: Handling User Requests

When user asks to scrape TTABVUE data, follow this workflow:

**1. Check if scraper exists:**
   - Look for `scraper_enhanced.py` (v2.0)
   - If not found, build it based on this skill

**2. Update query if needed:**
   - Extract search terms from user request
   - Update `query_url` variable in scraper
   - Adjust `DAYS_BACK` if user specifies date range

**3. Run the scraper:**
   - Execute: `python3 scraper_enhanced.py`
   - Show progress to user
   - Report results summary

**4. Handle email requests:**
   - Check if `config.json` exists
   - If not configured: prompt user to set up email
   - If configured: use `email_reporter.py` to send
   - Command: `python email_reporter.py send <csv_file> <to_email>`

**5. Update documentation (if requested):**
   - Update `IMPLEMENTATION_MEMORY.md` with new queries
   - Document any issues or improvements
   - Update `field-map.md` if selectors changed

### Email Configuration (Persistent)

**Storage:** `ttab-scraper/config.json`

**First-time setup:**
```python
# Claude should run:
python email_reporter.py config sender@gmail.com

# User will be prompted for password
# Configuration is saved to config.json
```

**Checking configuration:**
```bash
python email_reporter.py check
```

**Important:** Config persists across Claude Code sessions! Once configured, email works immediately.

### Natural Language Examples

User says: `"Search TTAB for 'blockchain' from last 90 days"`

Claude should:
1. Update DAYS_BACK = 90
2. Update query = "blockchain"
3. Run scraper
4. Show results

User says: `"Email results to legal@company.com"`

Claude should:
1. Check if config.json exists
2. If not: help user configure email first
3. If yes: run email_reporter.py send
4. Confirm email sent

User says: `"Change to 'AI' and extend to 6 months"`

Claude should:
1. Update query = "AI"
2. Update DAYS_BACK = 180
3. Re-run scraper
4. Compare results with previous run

---

## Updating This Skill

After each successful scraper run, note any:
- Selector changes on the TTAB site
- New fields discovered on detail pages
- Pagination behavior changes
- Rate limiting encountered
- Successful query patterns
- Email configuration issues

Update `references/field-map.md` with confirmed working selectors.
Update `IMPLEMENTATION_MEMORY.md` with new examples and lessons learned.
