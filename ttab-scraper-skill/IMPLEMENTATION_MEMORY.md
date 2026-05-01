# TTAB Scraper - Implementation Memory

**Project:** TTAB Web Scraper for USPTO Trademark Trial and Appeal Board
**Date:** 2026-05-01
**Status:** ✅ Enhanced with date filtering and party extraction
**Version:** 2.0 (Enhanced)

---

## Summary

Built a Python web scraper that extracts trademark case data from TTABVUE (USPTO database) with:
- **Date filtering** - Only cases from last 60 days (configurable)
- **Party extraction** - Defendant and plaintiff names with correspondence
- **Excel-ready output** - CSV with UTF-8 BOM for seamless Excel import
- **Full pagination** - Automatically scrapes all result pages

**Evolution:**
- v1.0: Basic scraper with pagination (122 cases, basic fields)
- v2.0: Enhanced with date filtering + party extraction (Excel-ready output)

### Version Comparison

| Feature | v1.0 (scraper_final.py) | v2.0 (scraper_enhanced.py) |
|---------|-------------------------|----------------------------|
| Pagination | ✅ Yes | ✅ Yes |
| Date filtering | ❌ No | ✅ Yes (configurable) |
| Case number | ✅ Yes | ✅ Yes |
| Filing date | ✅ Yes | ✅ Yes |
| Detail URL | ✅ Yes | ✅ Yes |
| Proceeding type | ✅ Yes | ❌ No (removed for simplicity) |
| Defendant name | ❌ No | ✅ Yes |
| Defendant correspondence | ❌ No | ✅ Yes (mark + serial #) |
| Plaintiff name | ❌ No | ✅ Yes |
| Plaintiff correspondence | ❌ No | ✅ Yes (mark + serial #) |
| CSV format | UTF-8 | UTF-8 BOM (Excel-ready) |
| Output filename | `ttab_cases_*.csv` | `ttab_cases_filtered_*.csv` |
| Use case | All cases, basic info | Recent cases, full party details |

**Recommendation:** Use v2.0 for most use cases. Use v1.0 only if you need proceeding type or want all historical cases without filtering.

---

## What Was Built

### Core Scraper (`scraper_final.py`)
- **Language:** Python 3
- **Libraries:** requests, BeautifulSoup4, lxml
- **Features:**
  - Automatic pagination detection and traversal
  - Smart deduplication by proceeding number
  - Rate limiting (1-second delay between pages)
  - Timestamped output files
  - Detailed logging with run statistics

### File Structure
```
ttab-scraper/
├── scraper_enhanced.py           # CURRENT: Enhanced scraper with filtering & party extraction
├── scraper_final.py              # LEGACY: Basic scraper (11KB, 231 lines)
├── README.md                      # Basic documentation (4.2KB)
├── USAGE.md                       # Enhanced scraper guide (NEW)
├── debug_structure.py             # Debug tool for HTML analysis
├── output/
│   ├── ttab_cases_filtered_*.csv          # Enhanced output with party data
│   ├── ttab_cases_20260501_103539.csv     # Legacy output (13KB, 122 cases)
│   └── page_source.html                   # Saved for debugging (130KB)
└── logs/
    └── scraper_log_filtered_*.txt         # Enhanced run logs
```

---

## Key Implementation Decisions

### 1. Requests + BeautifulSoup instead of Playwright
**Reason:** TTABVUE returns full HTML without JavaScript rendering. This makes the scraper:
- Faster (no browser overhead)
- More reliable (fewer dependencies)
- Easier to deploy (no browser binary needed)
- Lower resource usage

**Original plan:** Use Playwright
**Actual implementation:** requests + BeautifulSoup4
**Result:** Works perfectly, confirmed with live testing

### 2. List-Page-Only Data Extraction
**What was extracted:**
- Proceeding Number
- Proceeding Type (CAN/OPP/EXT/EXA)
- Filing Date
- Detail URL

**What was NOT extracted:**
- Plaintiff/Defendant names (visible but not cleanly parsed)
- Mark names
- Attorney information (requires detail page scraping)
- Trial dates (requires detail page scraping)

**Reason:** List page data sufficient for initial use case. Detail page scraping can be added later if needed.

### 3. Pagination Implementation
**Detection method:**
- Parses page text for "Go to page: 2 3 4 5"
- Extracts page numbers with regex
- Determines max page automatically

**URL format discovered:**
- ✅ Correct: `&page=2`
- ❌ Wrong: `&p=2` (tried first, didn't work)

**Result:** Successfully scraped all 5 pages (122 cases vs 25 from page 1 only)

### 4. Deduplication Strategy
- Collects all cases from all pages
- Removes duplicates based on unique proceeding number
- Ensures each case appears only once in output

---

## Technical Details

### URL Pattern (Confirmed Working)
```
https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&qs=project+management&page=N
```

### Data Extraction Pattern
```python
# Find proceeding links
proc_links = soup.find_all('a', href=re.compile(r'v\?pno=(\d+)&pty='))

for link in proc_links:
    # Extract from link
    proceeding_number = link.get_text(strip=True)
    proc_type = extract_from_url(link['href'], r'pty=(\w+)')

    # Extract from parent row
    parent_row = link.find_parent('tr')
    filing_date = extract_date_from_text(parent_row)
```

### Pagination Detection
```python
def get_pagination_info(soup):
    page_text = soup.get_text()
    page_match = re.search(r'Go to page:\s*([\d\s]+)', page_text)
    if page_match:
        page_numbers = re.findall(r'\d+', page_match.group(1))
        return max(int(p) for p in page_numbers)
    return 1
```

---

## Test Results

### Query: "project management"

| Metric | Value |
|--------|-------|
| Total pages detected | 5 |
| Cases per page | ~25 |
| Total cases scraped | 125 (before dedup) |
| Unique cases | 122 |
| Duplicates removed | 3 |
| Scraping time | ~5 seconds |
| Date range of results | 2002-2025 |

### Sample Cases
```csv
Proceeding_Number,Proceeding_Type,Filing_Date,Detail_URL
92090439,CAN,12/22/2025,https://ttabvue.uspto.gov/ttabvue/v?pno=92090439&pty=CAN
99075242,EXT,10/14/2025,https://ttabvue.uspto.gov/ttabvue/v?pno=99075242&pty=EXT
98429281,EXA,05/09/2025,https://ttabvue.uspto.gov/ttabvue/v?pno=98429281&pty=EXA
```

### Proceeding Types Found
- **CAN** - Cancellation
- **OPP** - Opposition
- **EXT** - Extension
- **EXA** - Extension Appeal

---

## Iterations & Debugging

### Iteration 1: Playwright Attempt
- **File:** `scraper.py`
- **Issue:** Missing system library (libnspr4.so) in WSL environment
- **Abandoned:** Switched to simpler approach

### Iteration 2: Basic Requests
- **File:** `scraper_simple.py`
- **Result:** Successfully fetched page, but extracted 515 rows (too much noise)
- **Issue:** Captured all tables including navigation, not just results

### Iteration 3: Refined Parsing
- **File:** `scraper_refined.py`
- **Result:** Clean extraction of 25 cases from page 1
- **Issue:** No pagination support yet

### Iteration 4: Final with Pagination
- **File:** `scraper_final.py`
- **Result:** ✅ Full pagination support, 122 cases across 5 pages
- **Status:** Production v1.0 (now legacy)

### Iteration 5: Enhanced with Date Filtering & Party Extraction
- **File:** `scraper_enhanced.py`
- **New Requirements:**
  - Filter to last 60 days only
  - Extract defendant name and correspondence
  - Extract plaintiff name and correspondence
  - Excel-ready CSV format
- **Challenges:**
  1. Understanding table structure (nested tables, 3-level TD hierarchy)
  2. Date filtering logic (comparison with cutoff date)
  3. Party extraction (finding correct parent TR, then sibling TDs)
  4. Correspondence parsing (regex for Mark: and S#: fields)
- **Solutions:**
  1. Created debug script to analyze HTML structure
  2. Discovered TR > TD[0,1,2] pattern for proceeding/defendant/plaintiff
  3. Implemented navigation: link → table → td → tr → all_tds[1,2]
  4. Used regex patterns for mark/serial extraction
- **Result:** ✅ Full party extraction with date filtering
- **Status:** Production v2.0 (CURRENT)

**Key Breakthrough:** Realizing party data is in sibling TDs, not nested within the proceeding cell. Required navigating up to parent TR, then accessing all_tds[1] and all_tds[2].

---

## Code Quality & Best Practices

### ✅ Implemented (v2.0)
- Rate limiting (1 sec delay between pages)
- Error handling for network requests
- Timestamped output files (no overwrites)
- Detailed logging with date filter info
- Progress indicators during execution
- Excel-ready CSV with UTF-8 BOM encoding
- Deduplication logic
- **Date filtering** (last N days, configurable)
- **Party extraction** (defendant/plaintiff from table structure)
- **Correspondence parsing** (mark names and serial numbers)

### 🔧 Could Be Enhanced
- CLI arguments for query customization
- Config file for settings
- Detail page scraping
- Better plaintiff/defendant parsing
- Excel output option
- Email notifications on completion
- Scheduled runs via cron

---

## Usage Instructions

### Run the Enhanced Scraper (v2.0 - RECOMMENDED)
```bash
python3 scraper_enhanced.py
```

**Features:**
- Filters to last 60 days
- Extracts defendant/plaintiff with correspondence
- Excel-ready CSV output

### Run the Legacy Scraper (v1.0)
```bash
python3 scraper_final.py
```

**Note:** Use legacy version only if you need all cases without date filtering or party details.

### Customize Date Range (v2.0)
Edit line 17 in `scraper_enhanced.py`:
```python
DAYS_BACK = 60  # Change to 30, 90, 180, etc.
```

### Customize Query (Both Versions)
Edit the query_url:
- v2.0: Line 306 in `scraper_enhanced.py`
- v1.0: Line 161 in `scraper_final.py`

```python
query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&qs=YOUR_SEARCH_TERM&..."
```

### Limit Pages (Testing)
Edit the `scrape_all_pages()` call:
- v2.0: Line 311 in `scraper_enhanced.py`
- v1.0: Line 175 in `scraper_final.py`

```python
cases = scrape_all_pages(query_url, max_pages=3)  # First 3 pages only
```

### Output Locations

**v2.0 Enhanced:**
- CSV: `output/ttab_cases_filtered_YYYYMMDD_HHMMSS.csv`
- Log: `logs/scraper_log_filtered_YYYYMMDD_HHMMSS.txt`

**v1.0 Legacy:**
- CSV: `output/ttab_cases_YYYYMMDD_HHMMSS.csv`
- Log: `logs/scraper_log_YYYYMMDD_HHMMSS.txt`

---

## Performance Characteristics

### Speed
- Page 1: ~2 seconds (includes network + parsing)
- Additional pages: ~1 second each (rate limited)
- Total for 5 pages: ~5 seconds

### Resource Usage
- Memory: Minimal (< 50MB)
- CPU: Low (text parsing only)
- Network: ~130KB per page download

### Scalability
- Tested: 5 pages, 122 cases
- Expected max: 100+ pages, 2500+ cases
- Bottleneck: Network latency and rate limiting
- Estimated time for 100 pages: ~100 seconds

---

## Version 2.0 Enhancements (May 1, 2026)

### New Requirements

User requested:
1. Filter cases to **last 60 days only**
2. Extract **defendant name and correspondence**
3. Extract **plaintiff name and correspondence**
4. Output formatted for **easy Excel import**

### Implementation Approach

#### 1. Date Filtering

**Challenge:** Filter cases by filing date before processing

**Solution:**
```python
from datetime import datetime, timedelta

DAYS_BACK = 60
cutoff_date = datetime.now() - timedelta(days=DAYS_BACK)

def is_within_date_range(date_str, days_back=60):
    case_date = datetime.strptime(date_str, "%m/%d/%Y")
    return case_date >= cutoff_date
```

**Implementation:**
- Extract filing date from proceeding cell
- Compare with cutoff date
- Skip processing if outside range
- Apply filter before party extraction (efficiency)

#### 2. Party Extraction

**Challenge:** Extract defendant and plaintiff from complex table structure

**HTML Structure Discovery:**
```html
<tr>  <!-- Main row -->
  <td>  <!-- Column 0: Proceeding + Date -->
    <table><tr><td>
      <a href="v?pno=92090439">92090439</a><br/>12/22/2025
    </td></tr></table>
  </td>

  <td>  <!-- Column 1: Defendant -->
    <table><tr><td>
      <a href="v?pnam=...">Construction Management Institute...</a><br/>
      Mark: CMI-FSP<br/>S#: 98514586
    </td></tr></table>
  </td>

  <td>  <!-- Column 2: Plaintiff -->
    <table><tr><td>
      <a href="v?pnam=...">Project Management Institute, Inc.</a><br/>
      Mark: PMI-SP<br/>S#: 77409410
    </td></tr></table>
  </td>
</tr>
```

**Navigation Algorithm:**
```python
# Start from proceeding link
proc_link = soup.find('a', href=re.compile(r'v\?pno='))

# Navigate up to main row
parent_table = proc_link.find_parent('table')  # Inner table
parent_td = parent_table.find_parent('td')     # TD column 0
parent_tr = parent_td.find_parent('tr')        # Main row

# Get all direct-child TDs (critical: recursive=False)
all_tds = parent_tr.find_all('td', recursive=False)

# Extract from TD[1] (defendant) and TD[2] (plaintiff)
defendant_td = all_tds[1]
plaintiff_td = all_tds[2]
```

**Critical Discovery:** Must use `recursive=False` to get only the 3 top-level TDs, not all nested TDs within the inner tables.

#### 3. Correspondence Extraction

**Challenge:** Parse mark names and serial numbers from plain text

**Solution:**
```python
cell_text = defendant_td.get_text(strip=True)

# Extract mark name (everything after "Mark:" until "S#:" or end)
marks = re.findall(r'Mark:\s*([^\n]+?)(?:\s+S#:|$)', cell_text)

# Extract serial number (digits after "S#:")
serials = re.findall(r'S#:\s*(\d+)', cell_text)

# Combine
correspondence = f"Mark: {marks[0]}, S#: {serials[0]}"
```

#### 4. Excel-Ready Output

**Challenge:** Ensure CSV imports cleanly into Excel

**Solution:**
```python
# Use UTF-8 with BOM encoding
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cases)
```

**Why UTF-8 BOM:**
- Excel on Windows needs BOM to detect UTF-8
- Without it, special characters display incorrectly
- The `utf-8-sig` encoding adds BOM automatically

### Testing Results

**Test with 180-day filter:**
- Query: "project management"
- Result: 1 case found (92090439, filed 12/22/2025)
- Defendant: Construction Management Institute of the United States of America Inc
- Plaintiff: Project Management Institute, Inc.
- Correspondence: Successfully extracted marks and serial numbers

**CSV Output (verified):**
```csv
Case_Number,Detail_URL,Filing_Date,Defendant_Name,Defendant_Correspondence,Plaintiff_Name,Plaintiff_Correspondence
92090439,https://ttabvue.uspto.gov/ttabvue/v?pno=92090439&pty=CAN,12/22/2025,Construction Management Institute of the United States of America Inc,"Mark: CMI-FSP, S#: 98514586","Project Management Institute, Inc.","Mark: PMI-SP, S#: 77409410"
```

**Production setting:** DAYS_BACK = 60 (as requested)

### New Output Fields

| Field | Description | Example |
|-------|-------------|---------|
| Case_Number | Case identifier | 92090439 |
| Detail_URL | Link to case | https://ttabvue.uspto.gov/... |
| Filing_Date | MM/DD/YYYY | 12/22/2025 |
| Defendant_Name | Full party name | Construction Management Institute... |
| Defendant_Correspondence | Mark & serial # | Mark: CMI-FSP, S#: 98514586 |
| Plaintiff_Name | Full party name | Project Management Institute, Inc. |
| Plaintiff_Correspondence | Mark & serial # | Mark: PMI-SP, S#: 77409410 |

---

## Known Limitations (v2.0)

1. **No detail page scraping** - Only extracts data visible on list pages
2. **Hardcoded query** - No CLI args yet
3. **CSV only** - No native Excel (XLSX) export, but CSV is Excel-ready with UTF-8 BOM
4. **Single query at a time** - No batch processing
5. **Correspondence parsing** - May include extra characters (R#) in some cases

---

## Future Enhancements (Backlog)

### Completed in v2.0 ✅
- [x] Parse plaintiff/defendant names cleanly
- [x] Excel-ready CSV output (UTF-8 BOM)
- [x] Date filtering
- [x] Correspondence extraction (marks & serial numbers)

### High Priority
- [ ] Add CLI arguments for query, date_range, max_pages, output_dir
- [ ] Add config file (YAML or JSON)
- [ ] Clean up correspondence parsing (remove extra R# characters)
- [ ] Add multiple query support (batch processing)

### Medium Priority
- [ ] Implement detail page scraping for full case data
- [ ] Add native Excel (XLSX) output format
- [ ] Email notification on completion
- [ ] Error recovery and retry logic
- [ ] Scheduled runs via cron

### Low Priority
- [ ] Database storage option
- [ ] Web UI for monitoring
- [ ] API endpoints
- [ ] Real-time updates / webhooks

---

## Dependencies

```
Python 3.6+
├── requests (HTTP library)
├── beautifulsoup4 (HTML parsing)
└── lxml (XML/HTML parser for BeautifulSoup)
```

Auto-installed on first run if missing.

---

## File Locations

```
Working directory: $(pwd) -> ttab-scraper/
Project root: ../  (parent directory)

Skill files (../ttab-scraper-skill/):
  SKILL.md                                        # Updated with v2.0 implementation
  references/field-map.md                         # Updated with confirmed selectors & party extraction
  IMPLEMENTATION_MEMORY.md                        # This file - complete project history

Scraper files (current directory):
  scraper_enhanced.py                             # v2.0 - CURRENT production (date filter + party extraction)
  scraper_final.py                                # v1.0 - LEGACY (basic pagination)
  scraper_refined.py                              # Development iteration
  scraper_simple.py                               # Development iteration
  scraper.py                                      # Initial Playwright attempt
  debug_structure.py                              # HTML analysis tool
  test_pagination.py                              # Pagination testing tool
  README.md                                       # Basic user documentation
  USAGE.md                                        # Enhanced scraper usage guide
  output/
    ttab_cases_filtered_*.csv                     # v2.0 output with party data
    ttab_cases_*.csv                              # v1.0 output (legacy)
    page_source.html                              # Saved HTML for debugging
  logs/
    scraper_log_filtered_*.txt                    # v2.0 run logs
    scraper_log_*.txt                             # v1.0 run logs
```

**Quick reference:**
- Current scraper: `./scraper_enhanced.py`
- Latest output: `./output/ttab_cases_filtered_<timestamp>.csv`
- Usage guide: `./USAGE.md`
- Skill docs: `../ttab-scraper-skill/`

---

## Token Usage

Total tokens consumed: **~113,051 tokens** (11.3% of 1M budget)

Breakdown:
- Initial exploration & design: ~10K tokens
- Implementation v1.0 (basic + pagination): ~40K tokens
- Implementation v2.0 (date filter + party extraction): ~35K tokens
- Testing & debugging v2.0: ~13K tokens
- Documentation & skill updates: ~15K tokens

---

## Success Metrics

### v1.0 Achievements ✅
- Scrapes TTABVUE search results
- Handles pagination automatically
- Exports to CSV
- No manual intervention needed
- Fast execution (< 10 seconds for typical queries)
- Reliable (tested multiple times)

### v2.0 Achievements ✅
- Date filtering (last 60 days)
- Defendant name & correspondence extraction
- Plaintiff name & correspondence extraction
- Excel-ready CSV format (UTF-8 BOM)
- Complex table structure parsing (nested TDs)
- Efficient filtering (date check before party extraction)

### Quality Attributes ✅
- Clean, readable code
- Well-commented for maintainability
- Proper error handling
- Rate limiting (respectful to server)
- Reproducible results
- Comprehensive documentation

---

## Lessons Learned

### v1.0 Lessons
1. **Simplicity wins** - Requests+BeautifulSoup was better than Playwright for this use case
2. **Inspect first, code second** - Saved time by analyzing HTML structure before coding
3. **Test pagination early** - Pagination logic was trickier than expected (page vs p parameter)
4. **Deduplication is essential** - Same cases can appear on multiple pages
5. **Progressive enhancement** - Built basic version first, then added pagination

### v2.0 Lessons
6. **Nested table structures need careful navigation** - Must navigate up multiple levels (link → table → td → tr) to find sibling cells
7. **recursive=False is critical** - Without it, you get all nested TDs instead of just top-level ones
8. **Debug scripts save time** - Creating `debug_structure.py` helped understand complex HTML faster
9. **UTF-8 BOM essential for Excel** - Regular UTF-8 doesn't work well in Excel on Windows
10. **Date filtering before party extraction** - More efficient to filter early rather than extract all then filter

---

## Maintenance Notes

### If the scraper breaks:

1. **Check URL structure** - TTAB may have changed their URL parameters
2. **Inspect HTML** - Run `test_pagination.py` to see current page structure
3. **Check selectors** - Proceeding links may have different href format
4. **Verify pagination** - May change from `&page=N` to different format
5. **Look at saved HTML** - `output/page_source.html` shows what was fetched

### Where to update (v2.0 - scraper_enhanced.py):

- Date range: Line 17 (`DAYS_BACK = 60`)
- URL format: Line 306 (query_url)
- Selectors: Line 117 (proceeding links regex)
- Pagination: Line 88 (get_pagination_info function)
- Party extraction: Lines 164-219 (TD navigation and parsing)
- Output fields: Lines 328-335 (fieldnames)

### Where to update (v1.0 - scraper_final.py):

- URL format: Line 161
- Selectors: Line 100 (proceeding links regex)
- Pagination: Line 25 (get_pagination_info function)
- Output fields: Lines 197-200 (priority_fields)

---

## Contact & Support

For issues or questions about this implementation:

**User Documentation:**
- `USAGE.md` - Enhanced scraper usage guide
- `README.md` - Basic scraper documentation

**Technical Documentation:**
- `../ttab-scraper-skill/SKILL.md` - Skill guide
- `../ttab-scraper-skill/references/field-map.md` - Selector details
- `../ttab-scraper-skill/IMPLEMENTATION_MEMORY.md` - This file

**Code:**
- `scraper_enhanced.py` - v2.0 source code (well-commented)
- `scraper_final.py` - v1.0 source code

**Debug Tools:**
- `debug_structure.py` - Analyze HTML structure
- `test_pagination.py` - Test pagination detection
- `output/page_source.html` - Saved HTML for inspection

---

**End of Implementation Memory**
**Status:** Production Ready v2.0 ✅
**Last Updated:** 2026-05-01 19:10
**Current Version:** Enhanced scraper with date filtering and party extraction
