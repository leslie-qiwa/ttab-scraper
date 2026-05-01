# TTAB Scraper Skill for Claude Code

A Claude Code skill that automates web scraping of USPTO Trademark Trial and Appeal Board (TTABVUE) case data with date filtering, party extraction, and Excel-ready output.

---

## What is a Claude Code Skill?

Skills are reusable instructions that teach Claude Code how to perform specific tasks. When you invoke a skill, Claude automatically follows the documented workflow to complete the task.

This skill enables Claude to:
- ✅ Build and run TTAB web scrapers
- ✅ Extract trademark case data with party information
- ✅ Filter cases by date (last 60 days)
- ✅ Generate Excel-ready CSV output
- ✅ Handle pagination automatically

---

## Installation

### 1. Copy Skill to Claude Code Skills Directory

**Default skill locations:**

- **macOS/Linux:**
  ```bash
  ~/.claude/skills/ttab-scraper/
  ```

- **Windows:**
  ```
  %USERPROFILE%\.claude\skills\ttab-scraper\
  ```

**Install command:**

```bash
# From the project directory
cp -r ttab-scraper-skill ~/.claude/skills/ttab-scraper
```

Or create a symlink (recommended for development):

```bash
ln -s $(pwd)/ttab-scraper-skill ~/.claude/skills/ttab-scraper
```

### 2. Verify Installation

Open Claude Code and check if the skill is loaded:

```bash
claude code
```

In the Claude Code session, type:
```
/help
```

You should see `ttab-scraper` listed in the available skills.

---

## Usage

### Method 1: Direct Skill Invocation (Recommended)

Simply ask Claude to run the TTAB scraper:

```
Run the TTAB scraper for "project management" cases
```

```
Scrape TTABVUE for trademark opposition cases
```

```
Get new TTAB filings from the last 60 days
```

Claude will automatically:
1. Detect the skill trigger
2. Load the skill instructions
3. Build/update the scraper if needed
4. Run the scraper
5. Save results to CSV

### Method 2: Explicit Skill Reference

Reference the skill file directly:

```
Use the ttab-scraper skill to extract trademark cases for "artificial intelligence"
```

### Method 3: Task-Specific Commands

Trigger the skill with specific requests:

```
Update the TTAB data for opposition cases
```

```
Collect USPTO trademark cases into Excel
```

```
Scrape trademark proceedings from the last 30 days
```

---

## Skill Triggers

The skill automatically activates when you mention:

- **Keywords:** TTAB, TTABVUE, trademark proceedings, opposition scraping
- **Actions:** scrape, extract, collect, automate, update
- **Output:** CSV, Excel, trademark data
- **Date ranges:** last 60 days, recent filings, new cases

**Example prompts:**

✅ "Get TTAB opposition cases from the last 60 days"
✅ "Scrape trademark cancellation proceedings"
✅ "Export TTABVUE data to Excel"
✅ "Run the scrape for project management trademarks"
✅ "Update the TTAB database"

---

## What the Skill Does

When invoked, Claude will:

### 1. **Check/Build Scraper**
   - Verify scraper exists at `ttab-scraper/scraper_enhanced.py`
   - Build scraper if needed using the skill template
   - Install dependencies (requests, beautifulsoup4, lxml)

### 2. **Configure Scraper**
   - Set search query from your request
   - Apply date filter (default: last 60 days)
   - Configure pagination settings

### 3. **Run Scraper**
   - Fetch all pages of results
   - Extract case data:
     - Case number
     - Filing date
     - Detail URL
     - Defendant name & correspondence
     - Plaintiff name & correspondence
   - Filter to date range
   - Deduplicate results

### 4. **Generate Output**
   - Save to Excel-ready CSV with UTF-8 BOM
   - Create timestamped filename
   - Generate run log
   - Display summary

---

## Expected Output

### Console Output

```
Starting scraper with pagination and date filtering
Filter: Last 60 days (since 03/02/2026)

======================================================================
PAGE 1
======================================================================
  Fetching page 1: https://ttabvue.uspto.gov/...
  Found 25 proceeding links on page 1
  Filtered to 5 cases within last 60 days

======================================================================
SUMMARY: Extracted 5 unique cases from last 60 days
======================================================================

✓ Results saved to: output/ttab_cases_filtered_20260501_103539.csv
✓ Total cases: 5
✓ Date range: Last 60 days
```

### CSV File

**Location:** `ttab-scraper/output/ttab_cases_filtered_<timestamp>.csv`

**Columns:**
- Case_Number
- Detail_URL
- Filing_Date
- Defendant_Name
- Defendant_Correspondence
- Plaintiff_Name
- Plaintiff_Correspondence

**Sample:**
```csv
Case_Number,Detail_URL,Filing_Date,Defendant_Name,Defendant_Correspondence,Plaintiff_Name,Plaintiff_Correspondence
92090439,https://ttabvue.uspto.gov/ttabvue/v?pno=92090439&pty=CAN,12/22/2025,Construction Management Institute of the United States of America Inc,"Mark: CMI-FSP, S#: 98514586","Project Management Institute, Inc.","Mark: PMI-SP, S#: 77409410"
```

---

## Configuration

### Change Date Range

Ask Claude:
```
Set the TTAB scraper to get cases from the last 90 days
```

Or edit directly:
```
Edit ttab-scraper/scraper_enhanced.py line 17 to set DAYS_BACK = 90
```

### Change Search Query

Ask Claude:
```
Update the scraper query to search for "blockchain" instead
```

### Limit Pages (Testing)

Ask Claude:
```
Run the scraper but only fetch the first 2 pages
```

---

## Import to Excel

The CSV output is formatted for easy Excel import:

### Option 1: Direct Open (Windows)
Double-click the CSV file - Excel will open it automatically with proper encoding.

### Option 2: Import Data (All Platforms)
1. Open Microsoft Excel
2. Go to **Data** > **Get Data** > **From File** > **From Text/CSV**
3. Select the generated CSV file
4. Excel auto-detects UTF-8 encoding
5. Click **Load**

The UTF-8 BOM encoding ensures special characters display correctly in Excel.

---

## Skill Files

```
ttab-scraper-skill/
├── README.md                      # This file - How to use the skill
├── SKILL.md                       # Skill definition and instructions
├── IMPLEMENTATION_MEMORY.md       # Complete implementation history
└── references/
    └── field-map.md              # Technical selectors and patterns
```

**For developers/maintainers:**
- `SKILL.md` - Claude reads this when the skill is invoked
- `IMPLEMENTATION_MEMORY.md` - Complete technical documentation
- `field-map.md` - HTML selectors and parsing logic

---

## Troubleshooting

### Skill Not Found

**Error:** "No skill named 'ttab-scraper' found"

**Solution:**
```bash
# Verify skill directory exists
ls ~/.claude/skills/ttab-scraper/

# Check SKILL.md exists
cat ~/.claude/skills/ttab-scraper/SKILL.md

# Restart Claude Code
```

### Scraper Not Running

**Error:** "Failed to run scraper"

**Solution:**
```
Ask Claude: "Debug the TTAB scraper and show me any errors"
```

Claude will:
- Check if Python is installed
- Verify dependencies
- Test the scraper
- Show error messages

### No Results Found

**Issue:** Scraper runs but returns 0 cases

**Likely causes:**
- No cases filed in the last 60 days for your query
- Try increasing date range: "Set TTAB filter to 180 days"
- Try different search terms

### Wrong Data Extracted

**Issue:** CSV has missing or incorrect party information

**Solution:**
```
Ask Claude: "Inspect the TTAB HTML structure and update the selectors"
```

Claude will:
- Fetch a sample page
- Analyze the current HTML structure
- Update selectors if needed
- Test the extraction

---

## Advanced Usage

### Custom Date Range

```
Scrape TTAB cases from the last 30 days
```

```
Get all trademark cases from the last 6 months
```

### Multiple Queries (Future)

```
Scrape TTAB data for these queries:
1. "project management"
2. "agile methodology"
3. "scrum framework"
```

### Scheduled Runs (Future)

```
Set up a weekly TTAB scraper to run every Monday
```

---

## Example Session

**User:**
```
Run the TTAB scraper for "artificial intelligence" trademark cases from the last 60 days
```

**Claude:**
```
I'll run the TTAB scraper for "artificial intelligence" cases.

[Checks for scraper...]
Found scraper at ttab-scraper/scraper_enhanced.py

[Updates query...]
✓ Set query to: qs=artificial+intelligence

[Runs scraper...]
Starting scraper with pagination and date filtering
Filter: Last 60 days (since 03/02/2026)

PAGE 1: Found 25 cases, filtered to 8 within date range
PAGE 2: Found 25 cases, filtered to 3 within date range
PAGE 3: Found 12 cases, filtered to 2 within date range

SUMMARY: Extracted 13 unique cases from last 60 days

✓ Results saved to: output/ttab_cases_filtered_20260501_154532.csv
✓ Total cases: 13
✓ Date range: Last 60 days

The CSV file contains:
- Case numbers
- Filing dates
- Defendant and plaintiff names
- Trademark correspondence (marks and serial numbers)

Ready to import into Excel!
```

---

## Version Information

**Current Version:** 2.0 (Enhanced)

**Features:**
- ✅ Date filtering (configurable)
- ✅ Party extraction (defendant/plaintiff)
- ✅ Correspondence data (marks & serial #s)
- ✅ Excel-ready CSV (UTF-8 BOM)
- ✅ Full pagination support
- ✅ Automatic deduplication

**Previous Version:** 1.0 (Basic)
- Available as `scraper_final.py`
- No date filtering or party extraction
- Use only if you need all historical cases

---

## Support & Documentation

**Quick Start:**
- This README - How to use the skill

**User Guides:**
- `../ttab-scraper/USAGE.md` - Scraper usage guide
- `../ttab-scraper/README.md` - Basic documentation

**Technical Docs:**
- `SKILL.md` - Skill definition (Claude reads this)
- `IMPLEMENTATION_MEMORY.md` - Complete implementation history
- `references/field-map.md` - HTML selectors and patterns

**Code:**
- `../ttab-scraper/scraper_enhanced.py` - Current scraper (v2.0)
- `../ttab-scraper/scraper_final.py` - Legacy scraper (v1.0)

---

## Contributing

To improve this skill:

1. **Update skill instructions:** Edit `SKILL.md`
2. **Update technical details:** Edit `references/field-map.md`
3. **Document changes:** Update `IMPLEMENTATION_MEMORY.md`
4. **Test thoroughly:** Run with various queries and date ranges

---

## License

This skill is for educational and research purposes. Please respect USPTO's terms of service and rate limits when scraping TTABVUE.

---

**Last Updated:** 2026-05-01
**Version:** 2.0
**Status:** Production Ready ✅
