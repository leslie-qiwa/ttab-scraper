#!/usr/bin/env python3
"""Debug script to understand the HTML structure of party information"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&qs=project+management"

headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.content, 'lxml')

# Find the first proceeding link
proc_link = soup.find('a', href=re.compile(r'v\?pno=92090439'))
if proc_link:
    print("Found proceeding 92090439")
    print("=" * 70)

    # Go up to find the main containing element
    parent_tr = proc_link.find_parent('tr')
    if parent_tr:
        print("\nParent TR HTML (first 2000 chars):")
        print(str(parent_tr)[:2000])

        # Try going up to parent table
        parent_table = proc_link.find_parent('table')
        if parent_table:
            print("\n\nParent TABLE HTML (first 3000 chars):")
            print(str(parent_table)[:3000])

        # Find all tables in this row
        tables = parent_tr.find_all('table')
        print(f"\n\nFound {len(tables)} tables in parent TR")

        for idx, table in enumerate(tables):
            print(f"\n--- Table {idx} ---")
            print(str(table)[:500])

        # Look for party links
        party_links = parent_tr.find_all('a', href=re.compile(r'pnam='))
        print(f"\n\nFound {len(party_links)} party name links")

        for idx, link in enumerate(party_links):
            print(f"\nParty {idx}: {link.get_text(strip=True)}")
            parent_td = link.find_parent('td')
            if parent_td:
                print(f"Cell text: {parent_td.get_text(strip=True)[:200]}")
