#!/usr/bin/env python3
"""
TTAB Scraper - Refined version targeting actual case data
"""
import csv
import re
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
    import requests
    from bs4 import BeautifulSoup

# Configuration
OUTPUT_DIR = Path("./output")
LOG_DIR = Path("./logs")

def extract_case_data(soup):
    """Extract case data from the parsed HTML"""
    cases = []

    # Find all links that point to case details (pattern: v?pno=XXXXXXXX&pty=XXX)
    case_links = soup.find_all('a', href=re.compile(r'v\?pno=\d+&pty='))

    print(f"Found {len(case_links)} case links")

    for link in case_links:
        proceeding_number = link.get_text(strip=True)
        href = link['href']
        detail_url = f"https://ttabvue.uspto.gov/ttabvue/{href}"

        # Navigate to parent table row to get all related data
        parent_row = link.find_parent('tr')

        if parent_row:
            cells = parent_row.find_all('td')

            # Extract text from all cells
            cell_data = [cell.get_text(strip=True) for cell in cells]

            case = {
                'Proceeding_Number': proceeding_number,
                'Detail_URL': detail_url,
            }

            # Map cells to fields (this may need adjustment based on actual table structure)
            if len(cell_data) >= 1:
                # Try to identify columns by content
                for idx, cell_text in enumerate(cell_data):
                    case[f'Column_{idx+1}'] = cell_text

            cases.append(case)

    return cases

def extract_structured_case_data(soup):
    """Extract structured case data by analyzing the table structure"""
    cases = []

    # Find tables that likely contain case data (they have proceeding number links)
    tables = soup.find_all('table')

    for table in tables:
        # Check if this table contains proceeding links
        has_proceeding = table.find('a', href=re.compile(r'v\?pno=\d+&pty='))
        if not has_proceeding:
            continue

        rows = table.find_all('tr')

        # Try to find header row
        header_row = rows[0] if rows else None
        headers = []

        if header_row:
            header_cells = header_row.find_all(['th', 'td'])
            headers = [cell.get_text(strip=True) for cell in header_cells]

        # If no meaningful headers, use generic names
        if not headers or all(not h for h in headers):
            # Count columns from first data row
            first_data_row = rows[1] if len(rows) > 1 else rows[0] if rows else None
            if first_data_row:
                num_cols = len(first_data_row.find_all('td'))
                headers = [f'Column_{i+1}' for i in range(num_cols)]

        # Process data rows
        for row in rows[1:] if len(rows) > 1 else rows:
            cells = row.find_all('td')

            if not cells:
                continue

            case = {}

            for idx, cell in enumerate(cells):
                header = headers[idx] if idx < len(headers) else f'Column_{idx+1}'

                # Check if cell contains a proceeding number link
                link = cell.find('a', href=re.compile(r'v\?pno=\d+&pty='))
                if link:
                    case['Proceeding_Number'] = link.get_text(strip=True)
                    href = link['href']
                    case['Detail_URL'] = f"https://ttabvue.uspto.gov/ttabvue/{href}"

                # Extract cell text
                cell_text = cell.get_text(strip=True)
                case[header] = cell_text

            # Only add if we found a proceeding number
            if 'Proceeding_Number' in case:
                cases.append(case)

    return cases

def scrape_results_page(url):
    """Fetch and parse the search results page"""
    print(f"Fetching: {url}\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Extract structured case data
        cases = extract_structured_case_data(soup)

        return cases

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

    query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&pno=&propno=&qs=project+management&propnameop=&propname=&pop=&pn=&pop2=&pn2=&cop=&cn="

    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"ttab_cases_{timestamp}.csv"
    log_file = LOG_DIR / f"scraper_log_{timestamp}.txt"

    # Scrape the results page
    cases = scrape_results_page(query_url)

    print(f"\nExtracted {len(cases)} cases")

    if not cases:
        print("No cases found!")
        return None

    # Print sample
    if cases:
        print("\nSample case (first result):")
        for key, value in list(cases[0].items())[:10]:
            print(f"  {key}: {value}")

    # Write to CSV
    print(f"\nWriting to CSV...")

    # Get all unique field names across all cases
    all_fields = set()
    for case in cases:
        all_fields.update(case.keys())

    # Sort fields to have Proceeding_Number and Detail_URL first
    priority_fields = ['Proceeding_Number', 'Detail_URL']
    other_fields = sorted([f for f in all_fields if f not in priority_fields])
    fieldnames = priority_fields + other_fields

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cases)

    print(f"✓ Results saved to: {csv_file}")
    print(f"✓ Total cases: {len(cases)}")

    # Write log
    with open(log_file, 'w') as f:
        f.write(f"TTAB Scraper Run\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Query URL: {query_url}\n")
        f.write(f"Cases extracted: {len(cases)}\n")
        f.write(f"Output file: {csv_file}\n")
        f.write(f"Fields: {', '.join(fieldnames)}\n")

    print(f"✓ Log saved to: {log_file}")

    return csv_file

if __name__ == "__main__":
    csv_output = main()
    if csv_output:
        print(f"\n{'='*60}")
        print(f"SUCCESS! Data saved to: {csv_output}")
        print(f"{'='*60}")
    else:
        print("\nScraping failed!")
