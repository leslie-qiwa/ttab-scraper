#!/usr/bin/env python3
"""
TTAB Scraper - Extract case data from TTABVUE using requests
"""
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
    import requests
    from bs4 import BeautifulSoup

# Configuration
OUTPUT_DIR = Path("./output")
LOG_DIR = Path("./logs")

def scrape_results_page(url):
    """Fetch and parse the search results page"""
    print(f"Fetching: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Save the raw HTML for inspection
        with open(OUTPUT_DIR / 'page_source.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("  Saved page source to output/page_source.html for inspection")

        results = []

        # Find all tables
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} table(s)")

        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"  Table {table_idx + 1}: {len(rows)} rows")

            for row_idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])

                if len(cells) == 0:
                    continue

                # Extract cell text
                row_data = [cell.get_text(strip=True) for cell in cells]

                # Find any links in the first cell
                detail_url = None
                first_cell = cells[0] if cells else None
                if first_cell:
                    link = first_cell.find('a')
                    if link and link.get('href'):
                        href = link['href']
                        detail_url = f"https://ttabvue.uspto.gov{href}" if href.startswith('/') else href

                result = {
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'cells': row_data,
                    'detail_url': detail_url,
                    'is_header': row_idx == 0 and all(cell.name == 'th' for cell in cells)
                }
                results.append(result)

        return results

    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []
    except Exception as e:
        print(f"Error parsing page: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Main scraper function"""

    # The query URL provided by user
    query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&pno=&propno=&qs=project+management&propnameop=&propname=&pop=&pn=&pop2=&pn2=&cop=&cn="

    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"ttab_results_{timestamp}.csv"
    log_file = LOG_DIR / f"scraper_log_{timestamp}.txt"

    # Scrape the results page
    results = scrape_results_page(query_url)

    print(f"\nExtracted {len(results)} rows total")

    if not results:
        print("No results found!")
        return None

    # Write to CSV
    print(f"\nWriting results to CSV...")

    # Determine max number of columns
    max_cols = max(len(r['cells']) for r in results if r['cells'])

    # Create header
    headers = [f"Column_{i+1}" for i in range(max_cols)]
    headers.extend(["Detail_URL", "Table_Index", "Row_Index", "Is_Header"])

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for result in results:
            row = result['cells'] + [''] * (max_cols - len(result['cells']))
            row.extend([
                result['detail_url'] or '',
                result['table_index'],
                result['row_index'],
                result['is_header']
            ])
            writer.writerow(row)

    print(f"✓ Results saved to: {csv_file}")
    print(f"✓ Total records: {len(results)}")

    # Write log
    with open(log_file, 'w') as f:
        f.write(f"TTAB Scraper Run\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Query URL: {query_url}\n")
        f.write(f"Records extracted: {len(results)}\n")
        f.write(f"Output file: {csv_file}\n")
        f.write(f"Max columns: {max_cols}\n")

    print(f"✓ Log saved to: {log_file}")

    # Print sample of first few results
    print(f"\n{'='*60}")
    print("Sample of first 3 rows:")
    for i, result in enumerate(results[:3]):
        print(f"\nRow {i+1}: {result['cells']}")
    print(f"{'='*60}")

    return csv_file

if __name__ == "__main__":
    csv_output = main()
    if csv_output:
        print(f"\nScraping complete! Output: {csv_output}")
        print("\nCheck output/page_source.html to see the HTML structure")
    else:
        print("\nScraping failed!")
