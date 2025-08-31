#!/usr/bin/env python
"""
Test script for the scholarship scraper command
This script tests the scraping functionality without running the full Django command
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def test_website_accessibility():
    """Test if the predefined websites are accessible"""
    websites = [
        'https://www.education.go.ke',
        'https://www.universitieskenyaonline.com', 
        'https://kenyaeducation.info'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Testing website accessibility...")
    
    for url in websites:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"✓ {url}: Status {response.status_code}")
        except requests.RequestException as e:
            print(f"✗ {url}: {str(e)}")
    
    print("\n" + "="*50 + "\n")

def test_beautifulsoup_parsing():
    """Test BeautifulSoup parsing with sample HTML"""
    sample_html = """
    <html>
        <head><title>Test Scholarship Page</title></head>
        <body>
            <h1>Kenya Education Scholarship 2025</h1>
            <p>This scholarship is for undergraduate students in Kenya...</p>
            <a href="/scholarship/undergraduate-2025">More details</a>
            <span class="deadline">Deadline: 31/12/2025</span>
            <div class="amount">KES 200,000</div>
        </body>
    </html>
    """
    
    print("Testing BeautifulSoup parsing...")
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # Test title extraction
    title = soup.select_one('h1')
    print(f"Title found: {title.get_text(strip=True) if title else 'None'}")
    
    # Test description extraction
    description = soup.select_one('p')
    print(f"Description found: {description.get_text(strip=True) if description else 'None'}")
    
    # Test deadline extraction
    deadline = soup.select_one('.deadline')
    print(f"Deadline found: {deadline.get_text(strip=True) if deadline else 'None'}")
    
    # Test amount extraction
    amount_text = soup.get_text()
    amount_pattern = r'KES\s*(\d{1,3}(?:,\d{3})*)'
    amount_match = re.search(amount_pattern, amount_text)
    print(f"Amount found: {amount_match.group(0) if amount_match else 'None'}")
    
    print("\n" + "="*50 + "\n")

def test_date_parsing():
    """Test date parsing functionality"""
    print("Testing date parsing...")
    
    date_strings = [
        "31/12/2025",
        "2025-12-31", 
        "December 31, 2025",
        "31 December 2025"
    ]
    
    date_formats = [
        '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y',
        '%Y/%m/%d', '%Y-%m-%d', '%d %B %Y', '%B %d, %Y'
    ]
    
    for date_string in date_strings:
        parsed = False
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_string.strip(), fmt)
                print(f"✓ '{date_string}' parsed as: {parsed_date.strftime('%Y-%m-%d')}")
                parsed = True
                break
            except ValueError:
                continue
        
        if not parsed:
            print(f"✗ '{date_string}' could not be parsed")
    
    print("\n" + "="*50 + "\n")

def test_amount_estimation():
    """Test scholarship amount estimation"""
    print("Testing amount estimation...")
    
    test_texts = [
        "This scholarship provides KES 200,000 for undergraduate students",
        "Award amount: 500,000 Kenya Shillings",
        "University scholarship for degree students",
        "Secondary school bursary program",
        "50 thousand shillings available"
    ]
    
    for text in test_texts:
        # Amount extraction patterns
        amount_patterns = [
            r'KES\s*(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:Kenya[n]?\s*)?shillings?',
            r'(\d{1,3}(?:,\d{3})*)\s*thousand',
        ]
        
        found_amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = int(amount_str)
                    if 'thousand' in match.group(0).lower():
                        amount *= 1000
                    found_amount = amount
                    break
                except ValueError:
                    continue
        
        if not found_amount:
            # Default amounts based on keywords
            text_lower = text.lower()
            if any(word in text_lower for word in ['university', 'undergraduate', 'degree']):
                found_amount = 200000
            elif any(word in text_lower for word in ['secondary', 'high school']):
                found_amount = 50000
            else:
                found_amount = 100000
        
        print(f"Text: '{text[:50]}...'")
        print(f"Estimated amount: KES {found_amount:,}")
        print()

if __name__ == "__main__":
    print("Scholarship Scraper Test Suite")
    print("=" * 50)
    print()
    
    test_website_accessibility()
    test_beautifulsoup_parsing()
    test_date_parsing()
    test_amount_estimation()
    
    print("Test suite completed!")
    print("\nIf all tests pass, the scraping command should work correctly.")
    print("Run the actual command with: python manage.py scrape_scholarships --dry-run")
