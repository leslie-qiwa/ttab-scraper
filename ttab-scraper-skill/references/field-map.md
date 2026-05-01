# TTAB Field Map — Confirmed Working Selectors

This file tracks confirmed working selectors for the TTAB scraper.
Update after each run if the site changes.

**Last verified:** 2026-05-01

---

## Results List Page

### URL Pattern (Confirmed)

**Advanced search:**
```
https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&qs=SEARCH_TERM&page=N
```

**Date range search:**
```
https://ttabvue.uspto.gov/ttabvue/query?procstatus=ALL&filefrom=MM/DD/YYYY&fileto=MM/DD/YYYY&type=OP&page=N
```

### Confirmed Selectors

| Field | Selector | Notes |
|---|---|---|
| Proceeding links | `a[href*="v?pno="][href*="&pty="]` | Regex: `v\?pno=(\d+)&pty=` |
| Proceeding number | Link text content | Extract from `<a>` tag text |
| Proceeding type | From URL parameter `pty` | CAN, OPP, EXT, EXA |
| Detail URL | `href` attribute | Construct: `https://ttabvue.uspto.gov/ttabvue/{href}` |
| Filing date | Parent `<tr>` cell text | Regex: `(\d{1,2}/\d{1,2}/\d{4})` |
| Pagination links | `a[href*="page="]` | Text: "2", "3", "4", "5", "Next" |

### Pagination Detection (Confirmed)

The page displays: "Page #1.Go to page:2345Next"

**Method 1 - Parse page numbers:**
```python
# Find "Go to page:" followed by numbers
page_match = re.search(r'Go to page:\s*([\d\s]+)', page_text)
page_numbers = re.findall(r'\d+', page_match.group(1))
max_page = max(int(p) for p in page_numbers)
```

**Method 2 - Find numbered links:**
```python
page_links = soup.find_all('a', string=re.compile(r'^\d+$'))
# URLs: v?qs=...&page=2, v?qs=...&page=3, etc.
```

### Pagination URL Format (Confirmed)

```
&page=2   # Correct - tested and working
&p=2      # Wrong - doesn't work
```

---

## Party Information Extraction (Implemented)

**Status:** ✅ Fully implemented in `scraper_enhanced.py`

### Table Structure (Confirmed)

The results page uses a complex nested table structure:

```
<tr>  <!-- Main row -->
  <td class="p1">  <!-- Column 0: Proceeding -->
    <table>
      <tr><td>
        <a href="v?pno=92090439&pty=CAN">92090439</a>
        <br/>12/22/2025
      </td></tr>
    </table>
  </td>

  <td class="p1">  <!-- Column 1: Defendant -->
    <table>
      <tr><td>
        <a href="v?pnam=Construction%20Management%20Institute...">
          Construction Management Institute of the United States of America Inc
        </a>
        <br/>
        Mark: CMI-FSP
        S#: 98514586
        R#: 7661879
      </td></tr>
    </table>
  </td>

  <td class="p1">  <!-- Column 2: Plaintiff -->
    <table>
      <tr><td>
        <a href="v?pnam=Project%20Management%20Institute...">
          Project Management Institute, Inc.
        </a>
        <br/>
        Mark: PMI SCHEDULING PROFESSIONAL (PMI-SP)
        S#: 77409410
        R#: 3562355
      </td></tr>
    </table>
  </td>
</tr>
```

### Extraction Algorithm (Confirmed)

```python
# 1. Find proceeding link
proc_link = soup.find('a', href=re.compile(r'v\?pno=(\d+)&pty='))

# 2. Navigate up: link → table → td → tr (main row)
parent_table = proc_link.find_parent('table')
parent_td = parent_table.find_parent('td')
parent_tr = parent_td.find_parent('tr')

# 3. Get all TDs in main row (non-recursive)
all_tds = parent_tr.find_all('td', recursive=False)

# 4. Extract from TD[1] (defendant)
defendant_td = all_tds[1]
def_link = defendant_td.find('a', href=re.compile(r'pnam='))
defendant_name = def_link.get_text(strip=True)

# 5. Extract correspondence from TD[1]
cell_text = defendant_td.get_text(strip=True)
marks = re.findall(r'Mark:\s*([^\n]+?)(?:\s+S#:|$)', cell_text)
serials = re.findall(r'S#:\s*(\d+)', cell_text)

# 6. Extract from TD[2] (plaintiff) - same pattern
plaintiff_td = all_tds[2]
plt_link = plaintiff_td.find('a', href=re.compile(r'pnam='))
plaintiff_name = plt_link.get_text(strip=True)
```

### Confirmed Selectors for Party Data

| Field | Selector Path | Notes |
|-------|---------------|-------|
| Defendant name | `all_tds[1].find('a', href*='pnam=')` | Party name link in TD 1 |
| Defendant mark | Regex: `Mark:\s*([^\n]+?)` in TD 1 text | May contain spaces |
| Defendant serial | Regex: `S#:\s*(\d+)` in TD 1 text | Numeric only |
| Plaintiff name | `all_tds[2].find('a', href*='pnam=')` | Party name link in TD 2 |
| Plaintiff mark | Regex: `Mark:\s*([^\n]+?)` in TD 2 text | May contain spaces |
| Plaintiff serial | Regex: `S#:\s*(\d+)` in TD 2 text | Numeric only |

**Key insights:**
- Must use `recursive=False` when finding TDs to get only direct children
- Party links have `href*="pnam="` pattern
- Correspondence data (Mark, S#, R#) is in plain text, not in separate elements
- Multiple marks and serials may exist; we extract the first of each

## Detail Page

**Status:** Not yet implemented. Current scraper extracts all data from list pages only.

The detail page URL format:
```
https://ttabvue.uspto.gov/ttabvue/v?pno=92090439&pty=CAN
```

**Future enhancement:** Parse attorney information, trial dates, document counts from detail pages.

---

## Pagination Logic (Implemented)

```python
def get_pagination_info(soup):
    """Extract total pages from page text"""
    page_text = soup.get_text()
    page_match = re.search(r'Go to page:\s*([\d\s]+)', page_text)
    if page_match:
        page_numbers = re.findall(r'\d+', page_match.group(1))
        return max(int(p) for p in page_numbers)
    return 1

def scrape_all_pages(base_url, max_pages=None):
    """Loop through pages with &page=N parameter"""
    for page_num in range(1, total_pages + 1):
        if page_num > 1:
            url = f"{base_url}&page={page_num}"
        cases, soup = scrape_results_page(url, page_num)
        all_cases.extend(cases)
        time.sleep(1)  # Rate limiting
```

---

## Extraction Pattern (Confirmed)

```python
# Find all proceeding links
proc_links = soup.find_all('a', href=re.compile(r'v\?pno=(\d+)&pty='))

for link in proc_links:
    proceeding_number = link.get_text(strip=True)
    href = link['href']

    # Extract type from URL
    proc_type_match = re.search(r'pty=(\w+)', href)
    proc_type = proc_type_match.group(1)

    # Find filing date in parent row
    parent_row = link.find_parent('tr')
    row_text = ' '.join([cell.get_text(strip=True) for cell in parent_row.find_all('td')])
    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', row_text)
```

---

## Performance Notes

| Metric | Value |
|---|---|
| Pages per query | 5 (for "project management" query) |
| Cases per page | ~25 |
| Total unique cases | 122 |
| Scraping time | ~5 seconds (1 sec delay between pages) |
| Rate limiting | 1 second between page requests |
| Duplicates removed | Yes, by proceeding number |

---

## Date Filtering (Implemented)

**Status:** ✅ Fully implemented in `scraper_enhanced.py`

### Date Comparison Logic

```python
from datetime import datetime, timedelta

def parse_date(date_str):
    """Parse MM/DD/YYYY to datetime"""
    return datetime.strptime(date_str, "%m/%d/%Y")

def is_within_date_range(date_str, days_back=60):
    """Check if date is within last N days"""
    case_date = parse_date(date_str)
    cutoff_date = datetime.now() - timedelta(days=days_back)
    return case_date >= cutoff_date
```

**Configuration:**
- Default: 60 days (configurable via `DAYS_BACK` constant)
- Applied before party extraction to skip old cases early
- Reduces processing time for large result sets

---

## Notes Log

| Date | Note |
|---|---|
| 2026-05-01 | Initial implementation completed. Confirmed pagination with `&page=N` parameter. Successfully scraped 122 cases across 5 pages. |
| 2026-05-01 | Verified proceeding type extraction from URL (`pty=CAN/OPP/EXT/EXA`). |
| 2026-05-01 | Filing date extraction via regex pattern on parent row text. |
| 2026-05-01 | Detail page scraping not implemented - all data from list pages. |
| 2026-05-01 | **Enhancement:** Added date filtering (last 60 days configurable). |
| 2026-05-01 | **Enhancement:** Implemented party extraction (defendant/plaintiff names and correspondence). |
| 2026-05-01 | **Enhancement:** Confirmed table structure parsing (TR > 3 TDs for proceeding/defendant/plaintiff). |
| 2026-05-01 | **Enhancement:** Added Excel-ready CSV output with UTF-8 BOM encoding. |
| 2026-05-01 | **Testing:** Verified with 180-day filter, extracted 1 case with full party data. |
