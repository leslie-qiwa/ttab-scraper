# Live Demonstration: Claude Driving the TTAB Scraper

**Date:** 2026-05-01
**Query:** "artificial intelligence"
**Method:** Claude-driven (natural language modifications)

---

## Demonstration Flow

### Initial Request
```
User: Search TTAB for "artificial intelligence" from last 60 days
```

### What Claude Did

**1. Loaded the skill**
- Read `ttab-scraper-skill/SKILL.md`
- Understood requirements: date filtering, party extraction, Excel output

**2. Updated the scraper**
- Changed query from "project management" to "artificial intelligence"
- Set `DAYS_BACK = 60`
- Updated query_url with proper URL encoding

**3. Ran the scraper**
```bash
python3 scraper_enhanced.py
```

**4. Results obtained**
- Pages scraped: 2
- Cases found: 31 total
- Cases within 60 days: **4 cases**

---

## Results (60-Day Filter)

**Output file:** `output/ttab_cases_filtered_20260501_223236.csv`

| Case Number | Filing Date | Defendant | Plaintiff |
|-------------|-------------|-----------|-----------|
| 99495281 | 04/02/2026 | Sidus Space, Inc. | Ubiquiti Inc. |
| 91306088 | 03/24/2026 | UNORTHODOX RESEARCH & DEVELOPMENT, LLC | Hangzhou DeepSeek Artificial Intelligence Co., Ltd. |
| 99294598 | 03/19/2026 | Epoch Artificial Intelligence, Inc. | Frontiers Media SA |
| 91083792 | - | ARTIFICIAL INTELLIGENCE LIMITED | STRAND LIGHTING, INC. |

**Correspondence data extracted:**
- Defendant marks and serial numbers
- Plaintiff marks and serial numbers

---

## Iteration: Extended to 90 Days

### Request
```
User: Extend to 90 days
```

### What Claude Did

**1. Updated configuration**
- Changed `DAYS_BACK = 60` to `DAYS_BACK = 90`
- Added comment: "Extended to 90 days as per user request"

**2. Re-ran scraper**
```bash
python3 scraper_enhanced.py
```

**3. New results**
- Same pages (2)
- Cases within 90 days: **4 cases** (same as 60-day)

**Insight:** All "artificial intelligence" cases were filed within 60 days, so extending to 90 days didn't add more results.

---

## Demonstration Summary

### What This Shows

**Natural Language Control:**
- ✅ "Search for X" → Claude updates query
- ✅ "Extend to Y days" → Claude updates date filter
- ✅ "Change to Z" → Claude modifies and re-runs

**Automatic Handling:**
- ✅ URL encoding (spaces → +)
- ✅ File paths
- ✅ Error handling
- ✅ Result reporting

**No Manual Work:**
- ❌ No Python editing by user
- ❌ No file path hunting
- ❌ No URL formatting

### Time Comparison

**With Claude (Development):**
- Total time: ~10 seconds per iteration
- User effort: Natural language prompt
- Code changes: Automatic
- Result: Iterative refinement

**Without Claude (Production):**
- Total time: ~5 seconds per run
- User effort: None (automated)
- Code changes: Manual editing required
- Result: Repeated execution

---

## Token Usage for Demonstration

| Action | Tokens |
|--------|--------|
| Load skill (read SKILL.md) | ~2,500 |
| Update query to "AI" | ~500 |
| Run scraper | ~1,000 |
| Change to 90 days | ~300 |
| Re-run scraper | ~1,000 |
| **Total demonstration** | **~5,300 tokens** |

**Cost:** ~$0.01 USD (at typical API pricing)
**Value:** No manual Python editing, instant iteration

---

## Real-World Scenario

### Week 1: Development with Claude

**Monday - Exploration:**
```
Search TTAB for "blockchain"
→ Found 12 cases

Change to "cryptocurrency"
→ Found 8 cases

Combine both searches
→ Found 20 cases

Extend to 90 days
→ Found 35 cases

Perfect! Email to legal@company.com
→ Sent
```

**Tuesday - Refinement:**
```
Only show opposition cases
Filter out defendant "ABC Corp"
→ Found 22 relevant cases

This is what we need weekly!
```

### Week 2+: Production without Claude

**Automated weekly run:**
```bash
# crontab entry
0 9 * * 1 cd /path/to/ttab/ttab-scraper && python3 scraper_enhanced.py && \
  python3 email_reporter.py send output/ttab_cases_filtered_*.csv legal@company.com
```

**No Claude needed** - runs automatically every Monday at 9am!

### When Issues Arise: Return to Claude

**Month 3 - TTABVUE changed:**
```
User: The scraper is returning empty results

Claude: [Debugs]
        The TTAB website changed their HTML structure.
        I'll update the selectors...

        [Updates field-map.md]
        [Fixes scraper]

        ✓ Scraper fixed and working
        ✓ Documentation updated
```

---

## Recommendation

### Use Claude When:
- ✅ Exploring new search terms
- ✅ First time using the scraper
- ✅ Modifying queries or filters
- ✅ Troubleshooting issues
- ✅ Adding new features
- ✅ Learning how it works

### Run Directly When:
- ✅ Query is finalized and stable
- ✅ Running on a schedule (cron)
- ✅ Part of automated pipeline
- ✅ Same search every time
- ✅ No modifications needed
- ✅ Production environment

### Best Practice

**Start:** Use Claude to develop and refine
**Middle:** Test production runs directly
**Ongoing:** Automate direct runs, return to Claude for changes

---

**This demonstration shows:**
- Claude successfully updated query from "project management" to "artificial intelligence"
- Extended date filter from 60 to 90 days
- Ran scraper automatically
- Found 4 cases with full party information
- No manual Python editing required
- Total iteration time: ~20 seconds

**Conclusion:** Let Claude drive during development, then automate for production! 🚀
