# TTAB Scraper - Quick Start Guide

Extract USPTO Trademark Trial and Appeal Board case data with Claude Code - no installation required!

---

## 🚀 Quick Start (5 Steps)

### Step 1: Start Claude Code

```bash
cd /path/to/ttab
claude code
```

### Step 2: Load the Skill

In Claude Code, paste this prompt:

```
Read the skill file at ttab-scraper-skill/SKILL.md and help me scrape TTABVUE data
```

Claude will read the skill instructions and be ready to help.

### Step 3: Run Your Query

```
Scrape TTAB cases for "project management" from the last 60 days
```

Claude will:
- Build/update the scraper if needed
- Run the scraper with your query
- Save results to CSV

### Step 4: Refine Your Query (Optional)

Use natural language to adjust:

```
Change the search to "artificial intelligence" instead
```

```
Extend the date range to 90 days
```

```
Filter to only opposition cases
```

```
Add cases for "blockchain" to the same search
```

Claude updates the scraper and re-runs automatically!

### Step 5: Update Documentation

When you're happy with the results:

```
Update the skill files and memory with what we just did
```

Claude will document the query, results, and any changes made.

---

## 📧 Email Reports (New Feature)

### First-Time Setup (One Time Only)

Configure email settings once, they persist forever:

```
Configure email for me:
- SMTP: smtp.gmail.com
- Port: 587
- From: your-email@gmail.com
- Password: [app password]
```

Claude will save to `ttab-scraper/config.json` - **configuration persists across sessions!**

### Send Reports (After Configuration)

Simply ask Claude:

```
Email the TTAB results to legal@company.com
```

```
Send the trademark data to user@example.com
```

```
Email this report to my boss
```

Claude will:
- Load saved email configuration from `config.json`
- Generate summary report
- Attach CSV file
- Send email

**No need to reconfigure each time!** ✅

### Configuration File (Persistent)

**Location:** `ttab-scraper/config.json`

**Format:**
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "your-email@gmail.com",
    "password": "your-app-password",
    "default_subject": "TTAB Search Results"
  }
}
```

**Persists across:**
- Claude Code restarts ✅
- Different sessions ✅
- Different queries ✅

**To update configuration:**
```
Update my email password to: [new-password]
```

```
Change SMTP server to: mail.company.com
```

### Email Report Includes

- Summary statistics (total cases, date range)
- Unique defendants/plaintiffs count
- Sample cases preview (first 5)
- Full CSV attachment
- Timestamp
- Direct links to TTABVUE for each case

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** in your Google Account
2. **Generate App Password:**
   - Go to https://myaccount.google.com/security
   - Select "2-Step Verification"
   - Scroll to "App passwords"
   - Generate password for "Mail"
3. **Use app password** (not your regular Gmail password)

---

## 📝 Example Session

```
You: Read ttab-scraper-skill/SKILL.md and help me scrape TTABVUE

Claude: I've loaded the TTAB scraper skill. I can help you extract
        trademark case data with date filtering and party information.
        What would you like to search for?

You: Get opposition cases for "cloud computing" from the last 60 days

Claude: [Runs scraper]
        ✓ Found 8 cases matching "cloud computing"
        ✓ Filtered to last 60 days
        ✓ Extracted defendant and plaintiff information
        ✓ Saved to: output/ttab_cases_filtered_20260501_120000.csv

        Sample results:
        - Case 92090123: Filed 04/15/2026
          Defendant: Cloud Solutions Inc.
          Plaintiff: Microsoft Corporation

You: Change search to "artificial intelligence" and expand to 90 days

Claude: [Updates and re-runs]
        ✓ Found 15 cases for "artificial intelligence"
        ✓ Date range: Last 90 days
        ✓ Saved to: output/ttab_cases_filtered_20260501_120100.csv

You: Email these results to legal@company.com

Claude: [Sends email]
        ✓ Report sent to legal@company.com
        ✓ Subject: TTAB Search Results - "artificial intelligence"
        ✓ Attached: ttab_cases_filtered_20260501_120100.csv
        ✓ 15 cases included

You: Update the skill documentation with this session

Claude: [Updates files]
        ✓ Updated IMPLEMENTATION_MEMORY.md
        ✓ Added query example: "artificial intelligence"
        ✓ Documented 90-day date range usage
        ✓ Added email reporting example
```

---

## 🎯 Common Queries

### Search by Term
```
Search TTAB for "machine learning" cases
Get trademark disputes about "cryptocurrency"
Find cases mentioning "metaverse"
```

### Filter by Date
```
Only cases from the last 30 days
Show me cases filed in the last 3 months
Get all cases from this year
```

### Filter by Type
```
Only opposition cases
Show cancellation proceedings
Extension requests only
```

### Combine Filters
```
Opposition cases for "blockchain" filed in the last 60 days
Cancellation cases about "NFT" from the past 90 days
```

### Export & Share
```
Email the results to legal@company.com
Save as Excel file instead of CSV
Export to JSON format
```

### Modify & Refine
```
Add "web3" to the search
Exclude cases with defendant "ABC Corp"
Only show cases where plaintiff is "Microsoft"
Change date range to 180 days
```

---

## 📊 Output Format

**CSV File:** `ttab-scraper/output/ttab_cases_filtered_<timestamp>.csv`

**Columns:**
- `Case_Number` - USPTO case identifier
- `Detail_URL` - Direct link to case details
- `Filing_Date` - MM/DD/YYYY
- `Defendant_Name` - Full defendant/respondent name
- `Defendant_Correspondence` - Trademark mark & serial numbers
- `Plaintiff_Name` - Full plaintiff/petitioner name
- `Plaintiff_Correspondence` - Trademark mark & serial numbers

**Example Row:**
```csv
92090439,https://ttabvue.uspto.gov/ttabvue/v?pno=92090439&pty=CAN,12/22/2025,
Construction Management Institute of the United States of America Inc,
"Mark: CMI-FSP, S#: 98514586",
"Project Management Institute, Inc.",
"Mark: PMI-SP, S#: 77409410"
```

---

## ⚙️ Configuration

### Change Default Date Range

```
Set default date filter to 90 days instead of 60
```

### Change Output Location

```
Save results to /path/to/custom/directory
```

### Enable/Disable Features

```
Turn off defendant correspondence extraction
Only extract case numbers and dates
Include proceeding type in output
```

---

## 🔧 Configuration Persistence

### Email Configuration (Persistent ✅)

**Stored in:** `ttab-scraper/config.json`

This file is automatically created when you configure email and **persists forever**:

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "your-email@gmail.com",
    "password": "your-app-password",
    "default_subject": "TTAB Search Results"
  },
  "scraper": {
    "days_back": 60,
    "max_pages": null,
    "output_dir": "./output",
    "log_dir": "./logs"
  }
}
```

**Benefits:**
- ✅ Configure once, use forever
- ✅ Survives Claude Code restarts
- ✅ No need to re-enter credentials
- ✅ Shared across all searches

**To check if configured:**
```
Check if email is configured
```

Claude will read `config.json` and report status.

### Manual Configuration

**Option 1: Let Claude create it**
```
Configure email with:
- From: sender@gmail.com
- Password: your-app-password
- Server: smtp.gmail.com
- Port: 587
```

**Option 2: Copy from example**
```bash
cp ttab-scraper/config.json.example ttab-scraper/config.json
# Edit config.json with your settings
```

**Option 3: Use CLI tool**
```bash
cd ttab-scraper
python email_reporter.py config sender@gmail.com
# Will prompt for password and save to config.json
```

### Security Note

**⚠️ The config.json contains your password!**

**Best practices:**
- Use app passwords (not your main password)
- Add `config.json` to `.gitignore`
- Don't commit config.json to git
- Use environment-specific configs for different machines

**Safer option:** Set environment variables instead
```bash
export TTAB_EMAIL="sender@gmail.com"
export TTAB_PASSWORD="app-password"
```

Then Claude can read from environment instead of config file.

---

## 🎯 Development vs Production: Two Ways to Use

### Development Phase: Let Claude Drive (Recommended) ⭐

**When exploring and refining queries:**

```
You: Search TTAB for "blockchain" from last 60 days

Claude: [Updates scraper, runs it]
        ✓ Found 12 cases for "blockchain"
        ✓ Saved to output/ttab_cases_filtered_*.csv

You: Change to "cryptocurrency"

Claude: [Updates query, re-runs]
        ✓ Found 8 cases for "cryptocurrency"

You: Extend to 90 days

Claude: [Updates DAYS_BACK, re-runs]
        ✓ Found 15 cases (90-day range)

You: Perfect! This is what I want.
```

**Advantages:**
- ✅ No Python editing needed
- ✅ Modify queries in natural language
- ✅ Iterate quickly
- ✅ Claude handles errors
- ✅ Auto-documents what works

**Token cost:** ~200-500 tokens per modification

---

### Production Phase: Run Python Directly (Optional)

**Once query is finalized, automate it:**

```bash
# Run directly (no Claude needed)
cd ttab/ttab-scraper
python3 scraper_enhanced.py

# Or schedule via cron
crontab -e
# Add: 0 9 * * 1 cd /path/to/ttab/ttab-scraper && python3 scraper_enhanced.py
```

**Advantages:**
- ✅ Faster (no Claude overhead)
- ✅ Good for automation
- ✅ No token usage
- ✅ Reliable scheduled runs

**Disadvantages:**
- ❌ Must edit Python to change query
- ❌ No natural language interface
- ❌ Manual documentation

---

### Hybrid Approach (Best of Both) 🏆

**1. Development with Claude:**
```
[Use Claude to explore and refine]
Try different search terms
Adjust date ranges
Test email reporting
Find the perfect query
```

**2. Production without Claude:**
```bash
# Query is finalized - now automate it
# Run directly or schedule via cron
python3 scraper_enhanced.py
```

**3. Return to Claude when needed:**
```
[Something changed? Use Claude again]
Update query to add "machine learning"
Change email recipient
Troubleshoot errors
```

**Best practice:**
- Use Claude during development/exploration
- Switch to direct runs for production automation
- Return to Claude for modifications or troubleshooting

### Live Demonstration: Claude vs Direct

**Scenario:** Search for "artificial intelligence" cases

#### With Claude (Just Demonstrated ✅)
```
You: Search TTAB for "artificial intelligence" from last 60 days

Claude: [Edits scraper_enhanced.py line 306]
        [Updates query: "project management" → "artificial intelligence"]
        [Runs: python3 scraper_enhanced.py]

        ✓ Found 4 cases for "artificial intelligence"
        ✓ Filtered to last 60 days
        ✓ Saved to: output/ttab_cases_filtered_20260501_223236.csv

        Sample results:
        - Case 99495281: Sidus Space vs Ubiquiti Inc.
        - Case 91306088: UNORTHODOX R&D vs DeepSeek AI
        - Case 99294598: Epoch AI vs Frontiers Media
        - Case 91083792: AI Limited vs Strand Lighting

You: Extend to 90 days

Claude: [Edits line 17: DAYS_BACK = 60 → 90]
        [Re-runs scraper]

        ✓ Still 4 cases (all within 60 days anyway)
        ✓ Saved to: output/ttab_cases_filtered_20260501_223352.csv
```

**Time:** 20 seconds total (2 iterations)
**User effort:** 2 natural language prompts
**Code edits:** 0 (Claude handled it)

#### Without Claude (Manual)
```bash
# Step 1: Edit Python file
nano scraper_enhanced.py
# Line 17: DAYS_BACK = 60 → 90
# Line 306: qs=project+management → qs=artificial+intelligence
# Save and exit

# Step 2: Run scraper
python3 scraper_enhanced.py

# Step 3: Check results
cat output/ttab_cases_filtered_*.csv

# Step 4: Modify again (repeat manual editing)
nano scraper_enhanced.py
# Edit again...
python3 scraper_enhanced.py
```

**Time:** 2-3 minutes (manual editing)
**User effort:** Open editor, find lines, edit, save
**Code edits:** Manual for each change

### Comparison Table

| Feature | Claude-Driven | Direct Python |
|---------|---------------|---------------|
| **Ease of use** | "Change to X" ⭐ | Edit .py file |
| **Speed per run** | ~10 sec | ~5 sec |
| **Iteration speed** | Very fast ⭐ | Slow (editing) |
| **Learning curve** | None | Python knowledge |
| **Token cost** | ~500 tokens/change | 0 tokens |
| **Documentation** | Automatic ⭐ | Manual |
| **Error handling** | Claude helps ⭐ | Debug yourself |
| **Automation** | Not ideal | Perfect ⭐ |
| **Best for** | Development ⭐ | Production ⭐ |
| **Recommendation** | Use first | Use after |

**Live results:** Claude successfully changed query and ran it twice in ~20 seconds total! ✅

---

## 📂 File Structure

```
ttab/
├── README.md                          # This file - Quick start guide
├── QUICK_START.md                     # Quick reference card
├── FINAL_SUMMARY.md                   # Complete summary
├── .gitignore                         # Protect config.json
├── ttab-scraper-skill/
│   ├── README.md                      # Skill installation (optional)
│   ├── SKILL.md                       # Skill instructions for Claude
│   ├── IMPLEMENTATION_MEMORY.md       # Technical documentation
│   └── references/field-map.md        # HTML selectors
└── ttab-scraper/
    ├── scraper_enhanced.py            # Current scraper (v2.0)
    ├── email_reporter.py              # Email with persistent config
    ├── config.json.example            # Config template
    ├── config.json                    # Your settings (created on first use)
    ├── USAGE.md                       # Detailed usage guide
    └── output/
        └── ttab_cases_filtered_*.csv  # Results
```

---

## 🐛 Troubleshooting

### "Skill file not found"
```
# Make sure you're in the ttab directory
pwd  # Should show: .../ttab

# Verify skill file exists
ls ttab-scraper-skill/SKILL.md
```

### "No results found"
```
Try: Increase the date range to 180 days
Try: Use different search terms
Try: Check TTABVUE website is accessible
```

### "Email send failed"
```
Check: SMTP credentials are correct
Check: Internet connection
Check: Email server allows programmatic access
Try: Use app password instead of regular password
```

### "Scraper not running"
```
Ask Claude: "Debug the scraper and show me any errors"
Ask Claude: "Check if Python dependencies are installed"
```

---

## 🎓 Advanced Usage

### Batch Processing

```
Search for multiple terms:
1. "artificial intelligence"
2. "machine learning"
3. "neural networks"

Combine results into one report
```

### Scheduled Runs

```
Set up weekly scraper for "blockchain" cases
Email results every Monday at 9am
```

### Custom Filtering

```
Only show cases where filing date is exactly 04/15/2026
Exclude cases with defendant containing "LLC"
Filter to cases with more than 2 marks
```

### Integration

```
Export to Google Sheets
Send to Slack channel #legal-alerts
Upload to SharePoint
```

---

## 💡 Tips & Tricks

1. **Be specific:** "Opposition cases for 'cloud computing' filed in April 2026"
2. **Iterate:** Start broad, then narrow down
3. **Check samples:** Ask Claude to show sample results before full export
4. **Save queries:** Ask Claude to save successful queries for reuse
5. **Email summaries:** Get quick email summaries without downloading CSV

---

## 📖 Documentation

**For Users:**
- This README - Start here
- `ttab-scraper/USAGE.md` - Detailed usage

**For Developers:**
- `ttab-scraper-skill/SKILL.md` - Skill definition
- `ttab-scraper-skill/IMPLEMENTATION_MEMORY.md` - Technical docs
- `ttab-scraper-skill/references/field-map.md` - HTML selectors

---

## 🆘 Getting Help

Ask Claude directly:

```
How do I filter to only opposition cases?
Show me examples of email reports
What date formats are supported?
How do I export to Excel?
```

Claude has access to all documentation and can help with:
- Query syntax
- Configuration
- Troubleshooting
- Custom features
- Report formatting

---

## 🔄 Updates

### When to Update Documentation

After successful scraping session:
```
Update the skill memory with this query and results
```

After finding better search terms:
```
Add "blockchain technology" to the skill examples
```

After fixing issues:
```
Document the fix for [issue description]
```

---

## ✨ What Makes This Easy

**No Installation Required**
- No copying files to ~/.claude/skills/
- Works from current directory
- Just read the skill file

**Natural Language Control**
- Modify queries in plain English
- No need to edit Python code
- Claude handles all the details

**Automatic Documentation**
- Claude updates memory files
- Queries are saved for reuse
- Changes are tracked

**Smart Features**
- Email reports
- Excel-ready CSV
- Date filtering
- Party extraction

---

## 📞 Support

**Questions?** Just ask Claude:
```
I need help with [your question]
```

**Bugs?** Report to Claude:
```
The scraper is [describe issue]
Debug and fix the problem
```

**Feature requests?**
```
Can you add [feature description]?
```

---

**Version:** 2.0
**Last Updated:** 2026-05-01
**Status:** Production Ready ✅

---

**Quick Reference:**

| Action | Command |
|--------|---------|
| Load skill | `Read ttab-scraper-skill/SKILL.md` |
| Run search | `Search TTAB for "term" from last 60 days` |
| Email results | `Email results to user@example.com` |
| Modify query | `Change search to "new term"` |
| Update docs | `Update skill and memory files` |
| Get help | `How do I [question]?` |

**That's it! Start scraping trademark data with Claude in seconds.** 🚀
