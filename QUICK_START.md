# TTAB Scraper - Quick Reference Card

## 🚀 Get Started in 30 Seconds

```bash
# 1. Start Claude Code
cd /path/to/ttab
claude code

# 2. Load skill (paste in Claude)
Read the skill file at ttab-scraper-skill/SKILL.md

# 3. Run your first search
Scrape TTAB for "project management" from last 60 days
```

## 📧 Email Your Results

```
Email the results to legal@company.com
```

## 🔧 Common Commands

| What You Want | What To Say |
|---------------|-------------|
| Search | `Search TTAB for "blockchain" cases` |
| Change term | `Change search to "cryptocurrency"` |
| Extend dates | `Extend to 90 days` |
| Email report | `Email results to user@example.com` |
| Update docs | `Update skill and memory files` |
| Get help | `How do I filter to only opposition cases?` |

## 📂 Where Are My Files?

- **Results:** `ttab-scraper/output/ttab_cases_filtered_*.csv`
- **Logs:** `ttab-scraper/logs/scraper_log_filtered_*.txt`
- **Skill:** `ttab-scraper-skill/SKILL.md`
- **Docs:** `README.md` (you are here)

## 💡 Pro Tips

1. **Start broad, refine iteratively**
   ```
   Search for "AI"
   → Narrow to "artificial intelligence"
   → Add date filter: last 30 days
   ```

2. **Use natural language**
   ```
   "Only opposition cases about blockchain filed in April"
   ```

3. **Preview before export**
   ```
   Show me a sample of the results first
   ```

4. **Save successful queries**
   ```
   Update the skill with this query
   ```

## 🐛 Troubleshooting

**No results?**
- Try: `Extend date range to 180 days`

**Email failed?**
- Try: `Configure email settings`
- Check: SMTP credentials

**Skill not loading?**
- Verify: `ls ttab-scraper-skill/SKILL.md`
- Should show: File exists

## 📖 Full Documentation

- `README.md` - Complete guide
- `ttab-scraper/USAGE.md` - Detailed usage
- `ttab-scraper-skill/IMPLEMENTATION_MEMORY.md` - Technical docs

---

**That's it! You're ready to scrape TTAB data with Claude.** 🎉
