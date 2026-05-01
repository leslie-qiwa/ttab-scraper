# TTAB Scraper - Usage Guide

## Quick Start

Run the enhanced scraper with date filtering and party extraction:

```bash
python3 scraper_enhanced.py
```

## Features

✅ **Date Filtering** - Only extracts cases filed within the last 60 days  
✅ **Party Extraction** - Extracts defendant and plaintiff names with correspondence  
✅ **Excel-Ready** - CSV formatted with UTF-8 BOM for easy Excel import  
✅ **Pagination** - Automatically scrapes all pages of results  

## Output Format

The CSV file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Case_Number` | USPTO case identifier | 92090439 |
| `Detail_URL` | Direct link to case | https://ttabvue.uspto.gov/... |
| `Filing_Date` | Date case was filed | 12/22/2025 |
| `Defendant_Name` | Defendant/Respondent name | Construction Management Institute... |
| `Defendant_Correspondence` | Defendant mark & serial #s | Mark: CMI-FSP, S#: 98514586 |
| `Plaintiff_Name` | Plaintiff/Petitioner name | Project Management Institute, Inc. |
| `Plaintiff_Correspondence` | Plaintiff mark & serial #s | Mark: PMI-SP, S#: 77409410 |

## Customizing the Date Range

Edit `scraper_enhanced.py` line 17:

```python
DAYS_BACK = 60  # Change to 30, 90, 180, etc.
```

## Customizing the Query

Edit `scraper_enhanced.py` line 306:

```python
query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&qs=YOUR_SEARCH_TERM&..."
```

## Importing to Excel

1. Open Microsoft Excel
2. Go to **Data** > **Get Data** > **From File** > **From Text/CSV**
3. Select the generated CSV file
4. Excel will auto-detect the UTF-8 encoding and import cleanly
5. Click **Load**

The file is formatted with:
- UTF-8 BOM for proper character encoding
- Proper CSV escaping for commas in data
- Headers in the first row

## Output Files

- **CSV**: `output/ttab_cases_filtered_YYYYMMDD_HHMMSS.csv`
- **Log**: `logs/scraper_log_filtered_YYYYMMDD_HHMMSS.txt`

## Sample Output

```csv
Case_Number,Detail_URL,Filing_Date,Defendant_Name,Defendant_Correspondence,Plaintiff_Name,Plaintiff_Correspondence
92090439,https://ttabvue.uspto.gov/ttabvue/v?pno=92090439&pty=CAN,12/22/2025,Construction Management Institute of the United States of America Inc,"Mark: CMI-FSP, S#: 98514586","Project Management Institute, Inc.","Mark: PMI-SP, S#: 77409410"
```

## Notes

- The scraper respects TTABVUE's server with 1-second delays between pages
- Only cases within the specified date range are included
- Duplicate cases are automatically removed
- The output is sorted by case number

