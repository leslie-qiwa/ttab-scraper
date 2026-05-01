#!/usr/bin/env python3
"""Test script to understand pagination structure"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://ttabvue.uspto.gov/ttabvue/v?qt=adv&procstatus=All&pno=&propno=&qs=project+management&propnameop=&propname=&pop=&pn=&pop2=&pn2=&cop=&cn="

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.content, 'lxml')

# Find all links on the page
print("All links with href containing numbers:")
print("=" * 70)
all_links = soup.find_all('a')
for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)

    # Look for pagination-related links
    if any(keyword in text.lower() for keyword in ['next', 'previous', 'page']) or re.search(r'\d', href):
        print(f"Text: '{text}' | Href: '{href}'")

print("\n" + "=" * 70)
print("Looking for 'Go to page' section:")
print("=" * 70)

# Get the full text around "Go to page"
page_text = soup.get_text()
# Find the section with "Go to page"
go_to_match = re.search(r'Page #\d+\..*?Go to page:\s*(.*?)(?:Next|Previous|Results)', page_text, re.DOTALL)
if go_to_match:
    print(f"Found: {go_to_match.group(0)}")

# Look for numbered page links (1, 2, 3, 4, etc.)
page_links = soup.find_all('a', string=re.compile(r'^\d+$'))
print(f"\nFound {len(page_links)} numbered page links:")
for link in page_links[:10]:
    print(f"  {link.get_text()} -> {link.get('href')}")
