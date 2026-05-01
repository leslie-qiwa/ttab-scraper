#!/usr/bin/env python3
"""
TTAB Scraper - Enhanced version with date filtering and detailed party extraction
Filters cases to last 60 days and extracts defendant/plaintiff with correspondence info
"""
import csv
import re
import time
from datetime import datetime, timedelta
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
DAYS_BACK = 90  # Extended to 90 days as per user request

def parse_date(date_str):
    """Parse MM/DD/YYYY date string to datetime object"""
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except:
        return None

def is_within_date_range(date_str, days_back=60):
    """Check if date is within the last N days"""
    case_date = parse_date(date_str)
    if not case_date:
        return False

    cutoff_date = datetime.now() - timedelta(days=days_back)
    return case_date >= cutoff_date

def extract_party_info(soup, table_index=0):
    """
    Extract defendant and plaintiff information from table cells.
    TTAB results have alternating columns: Defendant | Plaintiff
    """
    # Find all tables in the row
    tables = soup.find_all('table')

    parties = {
        'defendant_name': '',
        'defendant_correspondence': '',
        'plaintiff_name': '',
        'plaintiff_correspondence': ''
    }

    # Look for party name links
    party_links = soup.find_all('a', href=re.compile(r'pnam='))

    if len(party_links) >= 1:
        # First link is typically defendant
        parties['defendant_name'] = party_links[0].get_text(strip=True)

        # Try to find correspondence info near defendant
        def_parent = party_links[0].find_parent('td')
        if def_parent:
            # Look for email or address info
            text = def_parent.get_text(strip=True)
            # Extract mark/serial info as correspondence identifier
            mark_match = re.search(r'Mark:\s*([^\s]+)', text)
            serial_match = re.search(r'S#:\s*(\d+)', text)
            if mark_match:
                parties['defendant_correspondence'] = f"Mark: {mark_match.group(1)}"
            if serial_match:
                if parties['defendant_correspondence']:
                    parties['defendant_correspondence'] += f", S#: {serial_match.group(1)}"
                else:
                    parties['defendant_correspondence'] = f"S#: {serial_match.group(1)}"

    if len(party_links) >= 2:
        # Second link is typically plaintiff
        parties['plaintiff_name'] = party_links[1].get_text(strip=True)

        # Try to find correspondence info near plaintiff
        plt_parent = party_links[1].find_parent('td')
        if plt_parent:
            text = plt_parent.get_text(strip=True)
            mark_match = re.search(r'Mark:\s*([^\s]+)', text)
            serial_match = re.search(r'S#:\s*(\d+)', text)
            if mark_match:
                parties['plaintiff_correspondence'] = f"Mark: {mark_match.group(1)}"
            if serial_match:
                if parties['plaintiff_correspondence']:
                    parties['plaintiff_correspondence'] += f", S#: {serial_match.group(1)}"
                else:
                    parties['plaintiff_correspondence'] = f"S#: {serial_match.group(1)}"

    return parties

def get_pagination_info(soup):
    """Extract pagination information from the page"""
    page_text = soup.get_text()
    page_match = re.search(r'Go to page:\s*([\d\s]+)', page_text)
    if page_match:
        page_numbers = re.findall(r'\d+', page_match.group(1))
        if page_numbers:
            max_page = max(int(p) for p in page_numbers)
            return max_page

    next_link = soup.find('a', string=re.compile(r'Next', re.IGNORECASE))
    if next_link:
        return 2

    return 1

def scrape_results_page(url, page_num=1, days_back=60):
    """Fetch and parse a single search results page"""
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
        all_cases = []

        # Get all proceeding links
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
                'Case_Number': proceeding_number,
                'Detail_URL': detail_url,
                'Proceeding_Type': proc_type,
                'Filing_Date': '',
                'Defendant_Name': '',
                'Defendant_Correspondence': '',
                'Plaintiff_Name': '',
                'Plaintiff_Correspondence': ''
            }

            if parent_row:
                # Get filing date from the proceeding cell
                row_text = parent_row.get_text(separator=' ', strip=True)
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', row_text)
                if date_match:
                    case['Filing_Date'] = date_match.group(1)

                    # Filter by date
                    if not is_within_date_range(case['Filing_Date'], days_back):
                        continue  # Skip cases outside date range

            # Extract party information from sibling TDs
            # The structure is: TR > TD (proceeding) | TD (defendant) | TD (plaintiff)
            # Need to go up to the parent TR of the table that contains the proceeding link
            parent_table = link.find_parent('table')
            if parent_table:
                parent_td = parent_table.find_parent('td')
                if parent_td:
                    parent_tr = parent_td.find_parent('tr')
                    if parent_tr:
                        # Get all TD cells in this main row
                        all_tds = parent_tr.find_all('td', recursive=False)

                        # TD 0: Proceeding number
                        # TD 1: Defendant info
                        # TD 2: Plaintiff info
                        if len(all_tds) >= 2:
                            # Extract defendant from TD 1
                            defendant_td = all_tds[1]
                            def_link = defendant_td.find('a', href=re.compile(r'pnam='))
                            if def_link:
                                case['Defendant_Name'] = def_link.get_text(strip=True)

                                # Extract correspondence (Mark and S#)
                                cell_text = defendant_td.get_text(strip=True)
                                marks = re.findall(r'Mark:\s*([^\n]+?)(?:\s+S#:|$)', cell_text)
                                serials = re.findall(r'S#:\s*(\d+)', cell_text)
                                corr_parts = []
                                if marks:
                                    corr_parts.append(f"Mark: {marks[0].strip()}")
                                if serials:
                                    corr_parts.append(f"S#: {serials[0]}")
                                if corr_parts:
                                    case['Defendant_Correspondence'] = ", ".join(corr_parts)

                        if len(all_tds) >= 3:
                            # Extract plaintiff from TD 2
                            plaintiff_td = all_tds[2]
                            plt_link = plaintiff_td.find('a', href=re.compile(r'pnam='))
                            if plt_link:
                                case['Plaintiff_Name'] = plt_link.get_text(strip=True)

                                # Extract correspondence (Mark and S#)
                                cell_text = plaintiff_td.get_text(strip=True)
                                marks = re.findall(r'Mark:\s*([^\n]+?)(?:\s+S#:|$)', cell_text)
                                serials = re.findall(r'S#:\s*(\d+)', cell_text)
                                corr_parts = []
                                if marks:
                                    corr_parts.append(f"Mark: {marks[0].strip()}")
                                if serials:
                                    corr_parts.append(f"S#: {serials[0]}")
                                if corr_parts:
                                    case['Plaintiff_Correspondence'] = ", ".join(corr_parts)

            all_cases.append(case)

        # Remove duplicates based on case number
        unique_cases = {}
        for case in all_cases:
            case_num = case['Case_Number']
            if case_num not in unique_cases:
                unique_cases[case_num] = case

        filtered_count = len(unique_cases)
        print(f"  Filtered to {filtered_count} cases within last {days_back} days")

        return list(unique_cases.values()), soup

    except requests.RequestException as e:
        print(f"  Error fetching page: {e}")
        return [], None
    except Exception as e:
        print(f"  Error parsing page: {e}")
        import traceback
        traceback.print_exc()
        return [], None

def scrape_all_pages(base_url, max_pages=None, days_back=60):
    """Scrape all pages of results with pagination support and date filtering"""
    print(f"Starting scraper with pagination and date filtering")
    print(f"Filter: Last {days_back} days (since {(datetime.now() - timedelta(days=days_back)).strftime('%m/%d/%Y')})")
    print(f"Base URL: {base_url}\n")

    all_cases = []

    # Scrape first page
    print("=" * 70)
    print("PAGE 1")
    print("=" * 70)
    cases, soup = scrape_results_page(base_url, page_num=1, days_back=days_back)
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

            time.sleep(1)  # Rate limiting

            cases, _ = scrape_results_page(base_url, page_num=page_num, days_back=days_back)
            all_cases.extend(cases)
            print()

    # Remove duplicates across all pages
    unique_cases = {}
    for case in all_cases:
        case_num = case['Case_Number']
        if case_num not in unique_cases:
            unique_cases[case_num] = case

    return list(unique_cases.values())

def main():
    """Main scraper function"""

    query_url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&pno=&propno=&qs=artificial+intelligence&propnameop=&propname=&pop=&pn=&pop2=&pn2=&cop=&cn="

    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"ttab_cases_filtered_{timestamp}.csv"
    log_file = LOG_DIR / f"scraper_log_filtered_{timestamp}.txt"

    # Scrape all pages with date filtering
    cases = scrape_all_pages(query_url, max_pages=None, days_back=DAYS_BACK)

    print("\n" + "=" * 70)
    print(f"SUMMARY: Extracted {len(cases)} unique cases from last {DAYS_BACK} days")
    print("=" * 70 + "\n")

    if not cases:
        print("No cases found within the date range!")
        return None

    # Print sample
    if cases:
        print("Sample cases (first 3):")
        for i, case in enumerate(cases[:3]):
            print(f"\n  Case {i+1}:")
            print(f"    Case Number: {case.get('Case_Number', 'N/A')}")
            print(f"    Filing Date: {case.get('Filing_Date', 'N/A')}")
            print(f"    Defendant: {case.get('Defendant_Name', 'N/A')}")
            print(f"    Plaintiff: {case.get('Plaintiff_Name', 'N/A')}")

    # Write to Excel-friendly CSV
    print(f"\nWriting to Excel-friendly CSV...")

    # Field order for Excel
    fieldnames = [
        'Case_Number',
        'Detail_URL',
        'Filing_Date',
        'Defendant_Name',
        'Defendant_Correspondence',
        'Plaintiff_Name',
        'Plaintiff_Correspondence'
    ]

    # Write CSV with UTF-8 BOM for Excel compatibility
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Write only the specified fields
        for case in cases:
            row = {field: case.get(field, '') for field in fieldnames}
            writer.writerow(row)

    print(f"✓ Results saved to: {csv_file}")
    print(f"✓ Total cases: {len(cases)}")
    print(f"✓ Date range: Last {DAYS_BACK} days")

    # Write log
    with open(log_file, 'w') as f:
        f.write(f"TTAB Scraper Run (Filtered - Last {DAYS_BACK} Days)\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Query URL: {query_url}\n")
        f.write(f"Cases extracted: {len(cases)}\n")
        f.write(f"Output file: {csv_file}\n")
        f.write(f"Date filter: Last {DAYS_BACK} days\n")
        f.write(f"Cutoff date: {(datetime.now() - timedelta(days=DAYS_BACK)).strftime('%m/%d/%Y')}\n")
        f.write(f"Fields: {', '.join(fieldnames)}\n")

    print(f"✓ Log saved to: {log_file}")

    return csv_file

if __name__ == "__main__":
    csv_output = main()
    if csv_output:
        print(f"\n{'='*70}")
        print(f"SUCCESS! Filtered TTAB cases saved to: {csv_output}")
        print(f"File is formatted for Excel import (UTF-8 with BOM)")
        print(f"{'='*70}")
    else:
        print("\nScraping failed or no cases found!")
