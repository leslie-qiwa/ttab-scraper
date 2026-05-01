#!/usr/bin/env python3
"""
TTAB Scraper - Extract case data from TTABVUE
"""
import asyncio
import csv
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
OUTPUT_DIR = Path("./output")
LOG_DIR = Path("./logs")
HEADLESS = True
TIMEOUT = 30000  # 30 seconds

async def scrape_results_page(page, url):
    """Navigate to URL and scrape all results from the page"""
    print(f"Navigating to: {url}")

    try:
        await page.goto(url, wait_until="networkidle", timeout=TIMEOUT)
        await asyncio.sleep(2)  # Give page time to fully render

        # Wait for results table to appear
        await page.wait_for_selector("table", timeout=TIMEOUT)

        results = []

        # Find all table rows (skip header)
        rows = await page.query_selector_all("table tr")
        print(f"Found {len(rows)} rows (including header)")

        for i, row in enumerate(rows):
            if i == 0:  # Skip header row
                continue

            try:
                cells = await row.query_selector_all("td")

                if len(cells) < 3:  # Skip rows without enough data
                    continue

                # Extract text from each cell
                row_data = []
                for cell in cells:
                    text = await cell.inner_text()
                    row_data.append(text.strip())

                # Find the proceeding number link
                link_elem = await cells[0].query_selector("a")
                detail_url = None
                if link_elem:
                    href = await link_elem.get_attribute("href")
                    if href:
                        detail_url = f"https://ttabvue.uspto.gov{href}" if href.startswith("/") else href

                result = {
                    'cells': row_data,
                    'detail_url': detail_url
                }
                results.append(result)
                print(f"  Row {i}: {len(row_data)} cells extracted")

            except Exception as e:
                print(f"  Error parsing row {i}: {e}")
                continue

        return results

    except PlaywrightTimeout:
        print(f"Timeout loading page: {url}")
        return []
    except Exception as e:
        print(f"Error scraping page: {e}")
        return []

async def scrape_detail_page(page, url):
    """Scrape additional details from individual case page"""
    try:
        print(f"  Loading detail page: {url}")
        await page.goto(url, wait_until="networkidle", timeout=TIMEOUT)
        await asyncio.sleep(1)

        # Extract all text content from the page
        # This is a basic extraction - can be refined based on actual page structure
        content = await page.inner_text("body")

        # Try to find specific fields (adjust selectors based on actual page)
        detail_data = {
            'content_length': len(content)
        }

        return detail_data

    except Exception as e:
        print(f"  Error scraping detail page: {e}")
        return {}

async def main():
    """Main scraper function"""

    # The query URL provided by user
    query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&pno=&propno=&qs=project+management&propnameop=&propname=&pop=&pn=&pop2=&pn2=&cop=&cn="

    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"ttab_results_{timestamp}.csv"
    log_file = LOG_DIR / f"scraper_log_{timestamp}.txt"

    all_results = []

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()

        # Scrape the results page
        results = await scrape_results_page(page, query_url)

        print(f"\nExtracted {len(results)} results from search page")

        # Optionally scrape detail pages (disabled by default for speed)
        # Uncomment to enable detail page scraping
        # for idx, result in enumerate(results):
        #     if result['detail_url']:
        #         detail_data = await scrape_detail_page(page, result['detail_url'])
        #         result['detail'] = detail_data
        #         await asyncio.sleep(1)  # Rate limiting

        all_results.extend(results)

        await browser.close()

    # Write to CSV
    if all_results:
        print(f"\nWriting {len(all_results)} results to CSV...")

        # Determine max number of columns
        max_cols = max(len(r['cells']) for r in all_results)

        # Create header
        headers = [f"Column_{i+1}" for i in range(max_cols)]
        headers.append("Detail_URL")

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for result in all_results:
                row = result['cells'] + [''] * (max_cols - len(result['cells']))
                row.append(result['detail_url'] or '')
                writer.writerow(row)

        print(f"✓ Results saved to: {csv_file}")
        print(f"✓ Total records: {len(all_results)}")

        # Write log
        with open(log_file, 'w') as f:
            f.write(f"TTAB Scraper Run\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Query URL: {query_url}\n")
            f.write(f"Records extracted: {len(all_results)}\n")
            f.write(f"Output file: {csv_file}\n")

        print(f"✓ Log saved to: {log_file}")
    else:
        print("No results found!")

    return csv_file

if __name__ == "__main__":
    csv_output = asyncio.run(main())
    print(f"\n{'='*60}")
    print(f"Scraping complete! Output: {csv_output}")
    print(f"{'='*60}")
