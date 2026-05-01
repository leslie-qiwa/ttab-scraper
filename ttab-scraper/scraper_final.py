#!/usr/bin/env python3
"""
TTAB Scraper - Final version with clean table parsing
"""
import csv
import re
import time
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

def parse_cases_from_table(table):
    """Parse individual cases from a specific table structure"""
    cases = []

    # Find all rows
    rows = table.find_all('tr')

    for row in rows:
        # Find the proceeding number link
        proc_link = row.find('a', href=re.compile(r'v\?pno=\d+&pty='))

        if not proc_link:
            continue

        proceeding_number = proc_link.get_text(strip=True)
        href = proc_link['href']
        detail_url = f"https://ttabvue.uspto.gov/ttabvue/{href}"

        # Get all text from the row
        row_text = row.get_text(separator='|', strip=True)

        # Try to parse the row structure
        # Typical pattern: Proceeding Number | Filing Date | Defendant Info | Plaintiff Info
        cells = row.find_all('td')

        case = {
            'Proceeding_Number': proceeding_number,
            'Detail_URL': detail_url,
            'Row_Text': row_text
        }

        # Extract filing date (looks like MM/DD/YYYY)
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', row_text)
        if date_match:
            case['Filing_Date'] = date_match.group(1)

        # Extract defendant and plaintiff info
        # Split on proceeding number and filing date to separate fields
        parts = row_text.split(proceeding_number)
        if len(parts) > 1:
            remaining = parts[1]

            # Remove filing date if present
            if date_match:
                remaining = remaining.replace(date_match.group(1), '|', 1)

            # Split by | to get fields
            fields = [f.strip() for f in remaining.split('|') if f.strip()]

            if len(fields) >= 1:
                case['Defendant'] = fields[0] if fields else ''
            if len(fields) >= 2:
                case['Plaintiff'] = fields[1] if len(fields) > 1 else ''

        cases.append(case)

    return cases

def get_pagination_info(soup):
    """Extract pagination information from the page"""
    # Look for pagination links or page numbers
    # Pattern: "Page #1.Go to page:2345Next" or similar
    page_text = soup.get_text()

    # Find "Go to page:" followed by numbers
    page_match = re.search(r'Go to page:\s*([\d\s]+)', page_text)
    if page_match:
        # Extract page numbers
        page_numbers = re.findall(r'\d+', page_match.group(1))
        if page_numbers:
            max_page = max(int(p) for p in page_numbers)
            return max_page

    # Alternative: look for "Next" button/link
    next_link = soup.find('a', string=re.compile(r'Next', re.IGNORECASE))
    if next_link:
        # If there's a Next button, there are at least 2 pages
        # Try to find the highest page number mentioned
        page_links = soup.find_all('a', href=re.compile(r'[&?]p=\d+'))
        if page_links:
            page_nums = []
            for link in page_links:
                match = re.search(r'[&?]p=(\d+)', link['href'])
                if match:
                    page_nums.append(int(match.group(1)))
            if page_nums:
                return max(page_nums)
        return 2  # At minimum, if Next exists, there are 2 pages

    return 1  # Only one page

def scrape_results_page(url, page_num=1):
    """Fetch and parse a single search results page"""
    # Add page parameter to URL if not page 1
    if page_num > 1:
        separator = '&' if '?' in url else '?'
        url = f"{url}{separator}page={page_num}"

    print(f"  Fetching page {page_num}: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Find all links with proceeding numbers
        all_cases = []

        # Get all proceeding links directly
        proc_links = soup.find_all('a', href=re.compile(r'v\?pno=(\d+)&pty='))

        print(f"  Found {len(proc_links)} proceeding links on page {page_num}")

        for link in proc_links:
            proceeding_number = link.get_text(strip=True)
            href = link['href']
            detail_url = f"https://ttabvue.uspto.gov/ttabvue/{href}"

            # Extract proceeding type from URL
            proc_type_match = re.search(r'pty=(\w+)', href)
            proc_type = proc_type_match.group(1) if proc_type_match else ''

            # Get the parent row to extract related information
            parent_row = link.find_parent('tr')

            case = {
                'Proceeding_Number': proceeding_number,
                'Proceeding_Type': proc_type,
                'Detail_URL': detail_url
            }

            if parent_row:
                # Get all cell texts
                cells = parent_row.find_all('td')
                cell_texts = [cell.get_text(strip=True) for cell in cells]

                # Try to find filing date (MM/DD/YYYY pattern)
                row_text = ' '.join(cell_texts)
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', row_text)
                if date_match:
                    case['Filing_Date'] = date_match.group(1)

                # Store all cell data for reference
                for idx, text in enumerate(cell_texts):
                    if text and text != proceeding_number:  # Don't duplicate proceeding number
                        case[f'Cell_{idx+1}'] = text

            all_cases.append(case)

        # Remove duplicates based on proceeding number
        unique_cases = {}
        for case in all_cases:
            proc_num = case['Proceeding_Number']
            if proc_num not in unique_cases:
                unique_cases[proc_num] = case

        return list(unique_cases.values()), soup

    except requests.RequestException as e:
        print(f"  Error fetching page: {e}")
        return [], None
    except Exception as e:
        print(f"  Error parsing page: {e}")
        import traceback
        traceback.print_exc()
        return [], None

def scrape_all_pages(base_url, max_pages=None):
    """Scrape all pages of results with pagination support"""
    print(f"Starting scraper with pagination support\n")
    print(f"Base URL: {base_url}\n")

    all_cases = []

    # Scrape first page to determine total pages
    print("=" * 70)
    print("PAGE 1")
    print("=" * 70)
    cases, soup = scrape_results_page(base_url, page_num=1)
    all_cases.extend(cases)

    if not soup:
        print("Failed to fetch first page")
        return all_cases

    # Determine total number of pages
    total_pages = get_pagination_info(soup)
    print(f"\n  Detected {total_pages} total page(s)")

    # Apply max_pages limit if specified
    if max_pages:
        total_pages = min(total_pages, max_pages)
        print(f"  Limited to {total_pages} page(s) as requested")

    # Scrape remaining pages
    if total_pages > 1:
        print(f"\n  Scraping pages 2-{total_pages}...\n")

        for page_num in range(2, total_pages + 1):
            print("=" * 70)
            print(f"PAGE {page_num}")
            print("=" * 70)

            import time
            time.sleep(1)  # Rate limiting - be polite to the server

            cases, _ = scrape_results_page(base_url, page_num=page_num)
            all_cases.extend(cases)
            print()

    # Remove duplicates across all pages
    unique_cases = {}
    for case in all_cases:
        proc_num = case['Proceeding_Number']
        if proc_num not in unique_cases:
            unique_cases[proc_num] = case

    return list(unique_cases.values())

def main():
    """Main scraper function"""

    query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&pno=&propno=&qs=project+management&propnameop=&propname=&pop=&pn=&pop2=&pn2=&cop=&cn="

    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"ttab_cases_{timestamp}.csv"
    log_file = LOG_DIR / f"scraper_log_{timestamp}.txt"

    # Scrape all pages with pagination
    # Set max_pages=None to scrape all pages, or max_pages=3 to limit to first 3 pages
    cases = scrape_all_pages(query_url, max_pages=None)

    print("\n" + "=" * 70)
    print(f"SUMMARY: Extracted {len(cases)} unique cases from all pages")
    print("=" * 70 + "\n")

    if not cases:
        print("No cases found!")
        return None

    # Print sample
    if cases:
        print("Sample cases (first 3):")
        for i, case in enumerate(cases[:3]):
            print(f"\n  Case {i+1}:")
            print(f"    Proceeding #: {case.get('Proceeding_Number', 'N/A')}")
            print(f"    Type: {case.get('Proceeding_Type', 'N/A')}")
            print(f"    Filing Date: {case.get('Filing_Date', 'N/A')}")
            print(f"    URL: {case.get('Detail_URL', 'N/A')}")

    # Write to CSV
    print(f"\nWriting to CSV...")

    # Get all unique field names across all cases
    all_fields = set()
    for case in cases:
        all_fields.update(case.keys())

    # Sort fields to have important ones first
    priority_fields = ['Proceeding_Number', 'Proceeding_Type', 'Filing_Date', 'Detail_URL']
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
        f.write(f"TTAB Scraper Run (with Pagination)\n")
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
        print(f"\n{'='*70}")
        print(f"SUCCESS! TTAB cases saved to: {csv_output}")
        print(f"{'='*70}")
    else:
        print("\nScraping failed!")
