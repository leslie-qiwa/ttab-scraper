# TTAB Scraper

A Python web scraper for extracting case data from TTABVUE (USPTO's Trademark Trial and Appeal Board database).

## Features

- ✅ **Full pagination support** - Automatically scrapes all pages of results
- ✅ **Smart deduplication** - Removes duplicate cases across pages
- ✅ **Rate limiting** - 1-second delay between pages to be polite to the server
- ✅ **CSV export** - Clean, structured output with key fields
- ✅ **Detailed logging** - Tracks each run with timestamps and record counts

## Requirements

- Python 3.6+
- Dependencies (auto-installed on first run):
  - requests
  - beautifulsoup4
  - lxml

## Usage

### Basic Usage

Simply run the scraper:

```bash
python3 scraper_final.py
```

This will:
1. Scrape all pages for the configured query
2. Extract proceeding number, type, filing date, and detail URL
3. Save results to `output/ttab_cases_TIMESTAMP.csv`
4. Create a log file in `logs/scraper_log_TIMESTAMP.txt`

### Customize the Query

Edit `scraper_final.py` and modify the `query_url` variable (around line 161):

```python
query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&pno=&propno=&qs=YOUR_SEARCH_TERM&..."
```

### Limit Pages

To limit scraping to first N pages (for testing), edit line 175:

```python
# Scrape first 3 pages only
cases = scrape_all_pages(query_url, max_pages=3)

# Scrape all pages (default)
cases = scrape_all_pages(query_url, max_pages=None)
```

## Output Format

CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Proceeding_Number` | Unique case identifier | 92090439 |
| `Proceeding_Type` | Type of proceeding | CAN, OPP, EXT, EXA |
| `Filing_Date` | Date case was filed | 12/22/2025 |
| `Detail_URL` | Link to case details | https://ttabvue.uspto.gov/... |

**Proceeding Types:**
- `CAN` - Cancellation
- `OPP` - Opposition
- `EXT` - Extension
- `EXA` - Extension Appeal

## Example Results

For the query "project management":

- **Pages scraped:** 5
- **Total cases:** 122 unique cases
- **Date range:** 2002-2025
- **Processing time:** ~5 seconds (with 1-second delays between pages)

## File Structure

```
ttab-scraper/
├── scraper_final.py         # Main scraper (with pagination)
├── output/                   # CSV output files
│   └── ttab_cases_*.csv
├── logs/                     # Run logs
│   └── scraper_log_*.txt
└── README.md                 # This file
```

## How It Works

1. **Fetch Page 1** - Makes initial request to detect total pages
2. **Detect Pagination** - Parses page links (e.g., "Go to page: 2 3 4 5")
3. **Loop Through Pages** - Fetches each page with `&page=N` parameter
4. **Extract Cases** - Finds all proceeding links (`v?pno=XXXXXX&pty=XXX`)
5. **Parse Details** - Extracts proceeding number, type, filing date from table rows
6. **Deduplicate** - Removes duplicate cases based on proceeding number
7. **Export** - Writes to CSV with sorted fields

## Troubleshooting

**No results found:**
- Check that the query URL is correct
- Verify the website is accessible
- Check for changes in the TTAB website structure

**Only getting 1 page of results:**
- The pagination detection may have failed
- Check the HTML structure hasn't changed
- Look at the debug output for "Detected X total page(s)"

**Rate limiting / Connection errors:**
- Increase the sleep time in `scrape_all_pages()` (currently 1 second)
- The site may be temporarily down

## Advanced Customization

### Add More Fields

To extract additional data from each case, modify the parsing logic in `scrape_results_page()`:

```python
# Example: Extract more cell data
if parent_row:
    cells = parent_row.find_all('td')
    cell_texts = [cell.get_text(strip=True) for cell in cells]

    # Add custom field extraction here
    if len(cell_texts) > 2:
        case['Custom_Field'] = cell_texts[2]
```

### Change Output Format

To export to Excel instead of CSV:

```python
# Install openpyxl: pip install openpyxl
import pandas as pd

df = pd.DataFrame(cases)
df.to_excel(f'output/ttab_cases_{timestamp}.xlsx', index=False)
```

## License

This scraper is for educational and research purposes. Please respect the USPTO's terms of service and rate limits.

## Last Updated

2026-05-01
