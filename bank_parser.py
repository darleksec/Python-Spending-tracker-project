"""
Unified bank statement parser module.
Handles Chase (current + credit) and HSBC PDF statement formats.
Outputs standardised transaction dicts for ExpenseTracker ingestion.
"""

import re
import pdfplumber
from datetime import datetime
from rapidfuzz import process, fuzz, utils

# ---------------------
# Category Mapping
# ---------------------
CATEGORY_MAPPING = {
    # Groceries
    'aldi': 'Groceries',
    'asda': 'Groceries',
    'co-op': 'Groceries',
    'coop': 'Groceries',
    'costco': 'Groceries',
    'iceland': 'Groceries',
    'lidl': 'Groceries',
    'marks and spencer': 'Groceries',
    'm&s': 'Groceries',
    'ms': 'Groceries',
    'morrisons': 'Groceries',
    'ocado': 'Groceries',
    'sainsbury': 'Groceries',
    'tesco': 'Groceries',
    'waitrose': 'Groceries',
    'whole foods': 'Groceries',
    'farmfoods': 'Groceries',
    'heron foods': 'Groceries',
    'jack\'s': 'Groceries',
    'jacks': 'Groceries',
    'spar': 'Groceries',
    'nisa': 'Groceries',
    'budgens': 'Groceries',

    # Dining
    'burger king': 'Dining',
    'costa': 'Dining',
    'deliveroo': 'Dining',
    'domino': 'Dining',
    'five guys': 'Dining',
    'greggs': 'Dining',
    'itsu': 'Dining',
    'just eat': 'Dining',
    'kfc': 'Dining',
    'leon': 'Dining',
    'mcdonald': 'Dining',
    'nando': 'Dining',
    'papa john': 'Dining',
    'pizza express': 'Dining',
    'pizza hut': 'Dining',
    'pret': 'Dining',
    'starbucks': 'Dining',
    'subway': 'Dining',
    'uber eats': 'Dining',
    'wagamama': 'Dining',
    'wasabi': 'Dining',
    'wetherspoon': 'Dining',
    'yo sushi': 'Dining',
    'zizzi': 'Dining',
    'cafe': 'Dining',
    'restaurant': 'Dining',
    'eat.': 'Dining',
    'eat': 'Dining',
    'tortilla': 'Dining',
    'franco manca': 'Dining',
    'dishoom': 'Dining',

    # Transport
    'first bus': 'Transport',
    'national express': 'Transport',
    'national rail': 'Transport',
    'northern rail': 'Transport',
    'scotrail': 'Transport',
    'tfl': 'Transport',
    'trainline': 'Transport',
    'uber': 'Transport',
    'bolt': 'Transport',
    'lime': 'Transport',
    'voi': 'Transport',
    'megabus': 'Transport',
    'flixbus': 'Transport',
    'addison lee': 'Transport',
    'oyster': 'Transport',
    'lumo': 'Transport',
    'lner': 'Transport',
    'avanti': 'Transport',
    'gwr': 'Transport',

    # Bills
    'apple': 'Bill',
    'bt group': 'Bill',
    'council tax': 'Bill',
    'ee mobile': 'Bill',
    'giffgaff': 'Bill',
    'google storage': 'Bill',
    'icloud': 'Bill',
    'netflix': 'Bill',
    'o2': 'Bill',
    'sky': 'Bill',
    'spotify': 'Bill',
    'three': 'Bill',
    'virgin media': 'Bill',
    'vodafone': 'Bill',
    'voxi': 'Bill',
    'youtube': 'Bill',
    'disney': 'Bill',
    'amazon prime': 'Bill',
    'now tv': 'Bill',
    'adobe': 'Bill',
    'microsoft': 'Bill',
    'crunchyroll': 'Bill',

    # Shopping
    'amazon': 'Shopping',
    'argos': 'Shopping',
    'asos': 'Shopping',
    'boots': 'Shopping',
    'currys': 'Shopping',
    'ebay': 'Shopping',
    'h&m': 'Shopping',
    'hm': 'Shopping',
    'ikea': 'Shopping',
    'john lewis': 'Shopping',
    'next': 'Shopping',
    'nike': 'Shopping',
    'primark': 'Shopping',
    'superdrug': 'Shopping',
    'tk maxx': 'Shopping',
    'uniqlo': 'Shopping',
    'wilko': 'Shopping',
    'zara': 'Shopping',
    'shein': 'Shopping',
    'wish': 'Shopping',
    'etsy': 'Shopping',

    # Health & Fitness
    'gym': 'Health',
    'puregym': 'Health',
    'the gym': 'Health',
    'david lloyd': 'Health',
    'pharmacy': 'Health',
    'dentist': 'Health',
    'optician': 'Health',
    'specsavers': 'Health',
    'holland and barrett': 'Health',
    'myprotein': 'Health',

    # Entertainment
    'cinema': 'Entertainment',
    'cineworld': 'Entertainment',
    'odeon': 'Entertainment',
    'vue': 'Entertainment',
    'ticketmaster': 'Entertainment',
    'steam': 'Entertainment',
    'playstation': 'Entertainment',
    'xbox': 'Entertainment',
    'nintendo': 'Entertainment',

    # Fuel
    'bp': 'Fuel',
    'esso': 'Fuel',
    'shell': 'Fuel',
    'texaco': 'Fuel',
    'jet': 'Fuel',
    'gulf': 'Fuel',

    # Rent / Housing
    'rent': 'Rent',
    'letting': 'Rent',
    'openrent': 'Rent',

    # Cash
    'atm': 'Cash',
    'cash': 'Cash',
    'withdraw': 'Cash',

    # Travel
    'airbnb': 'Travel',
    'booking.com': 'Travel',
    'bookingcom': 'Travel',
    'easyjet': 'Travel',
    'hotel': 'Travel',
    'hostel': 'Travel',
    'ryanair': 'Travel',
    'skyscanner': 'Travel',
    'wizz air': 'Travel',
    'british airways': 'Travel',
    'jet2': 'Travel',

    # Education
    'university': 'Education',
    'udemy': 'Education',
    'coursera': 'Education',
    'student': 'Education',
    'tuition': 'Education',
}

# Noise keywords to filter out
NOISE_KEYWORDS = [
    'round up',
    'round-up',
    'roundup',
    'opening balance',
    'closing balance',
    'interest',
    'card frozen',
    'chase savings',
    'hsbc savings',
    'lloyds savings',
    'from chun ching tang',
    'from tang',
    'jamdoughnut',
    'jam doughnut',
    'balance',
    'savings goal',
    'autosave',
    'personal transfer',
]

# Noise regex patterns for non-keyword-based filtering
NOISE_PATTERNS = [
    re.compile(r'^(to|from)\s+[A-Z][a-z]+', re.IGNORECASE),   # P2P transfers
    re.compile(r'^\d{4,}$', re.IGNORECASE),                    # Pure reference numbers
    re.compile(r'^(balance b/f|b/f)', re.IGNORECASE),          # Brought-forward balances
]


# ---------------------
# Utility Functions
# ---------------------

MONTH_MAP = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
}


def format_date_4digit(date_str):
    """Convert 'DD Mon YYYY' (e.g. '26 Mar 2025') to 'DD/MM/YYYY'."""
    parts = date_str.strip().split()
    day = parts[0].zfill(2)
    month = MONTH_MAP[parts[1][:3].lower()]
    year = parts[2]
    return f"{day}/{month}/{year}"


def format_date_2digit(date_str):
    """Convert 'DD Mon YY' (e.g. '27 Feb 25') to 'DD/MM/YYYY'."""
    parts = date_str.strip().split()
    day = parts[0].zfill(2)
    month = MONTH_MAP[parts[1][:3].lower()]
    year_2 = parts[2]
    year = f"20{year_2}" if int(year_2) < 80 else f"19{year_2}"
    return f"{day}/{month}/{year}"


def clean_to_float(value):
    """Clean a string amount to float. Returns None if not a valid number."""
    if not value:
        return None
    value = str(value).strip().replace('£', '').replace(',', '').replace(' ', '')
    if value in ('', '-', '--'):
        return None
    try:
        return abs(float(value))
    except ValueError:
        return None


def get_category(description):
    """Map a merchant description to a category using fuzzy matching."""
    if not description or not description.strip():
        return "Flag"
    desc = description.lower()
    # Try exact keyword matching first for speed and precision
    for keyword, category in CATEGORY_MAPPING.items():
        if keyword in desc:
            return category
    # Fall back to fuzzy matching
    choices = list(CATEGORY_MAPPING.keys())
    result = process.extractOne(
        desc,
        choices,
        scorer=fuzz.WRatio,
        processor=utils.default_process,
        score_cutoff=80,
    )
    if result is None:
        return "Flag"
    matched_key = result[0]
    return CATEGORY_MAPPING[matched_key]


def _is_noise(description):
    """Check if a transaction description matches noise keywords."""
    desc = description.lower()
    for keyword in NOISE_KEYWORDS:
        if keyword in desc:
            return True
    for pattern in NOISE_PATTERNS:
        if pattern.search(description):
            return True
    return False


# ---------------------
# Chase Parser
# ---------------------

def parse_chase_statement(pdf_path):
    """
    Parse a Chase bank statement PDF (current or credit).
    Chase Credit uses DD Mon YYYY (4-digit year).
    Chase Current uses DD Mon YY (2-digit year).
    Returns list of transaction dicts.
    """
    all_transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table({
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "snap_tolerance": 5
            })
            if not table:
                continue

            for row in table:
                clean_row = [
                    str(cell).strip() if cell and str(cell).strip() else ""
                    for cell in row
                ]
                if not clean_row or not clean_row[0]:
                    continue

                # Try 4-digit year first (Chase Credit: DD Mon YYYY)
                date_match_4 = re.search(
                    r'(\d{1,2}\s[A-Za-z]{3}\s\d{4})', clean_row[0]
                )
                # Then try 2-digit year (Chase Current: DD Mon YY)
                date_match_2 = re.search(
                    r'(\d{1,2}\s[A-Za-z]{3}\s\d{2})(?!\d)', clean_row[0]
                )

                if not date_match_4 and not date_match_2:
                    continue

                row_text = ' '.join(clean_row)

                # Skip noise rows
                if _is_noise(row_text):
                    continue

                # Determine date format
                if date_match_4:
                    date_str = format_date_4digit(date_match_4.group(1))
                else:
                    date_str = format_date_2digit(date_match_2.group(1))

                # Build description from non-date, non-amount cells
                description_parts = []
                amount = None

                for i, cell in enumerate(clean_row):
                    if i == 0:
                        # Remove the date from the first cell to get remaining text
                        if date_match_4:
                            remainder = clean_row[0].replace(
                                date_match_4.group(0), ''
                            ).strip()
                        else:
                            remainder = clean_row[0].replace(
                                date_match_2.group(0), ''
                            ).strip()
                        if remainder:
                            description_parts.append(remainder)
                        continue

                    # Try to parse as amount
                    val = clean_to_float(cell)
                    if val is not None and '.' in str(cell):
                        if amount is None:
                            amount = val
                    elif cell:
                        description_parts.append(cell)

                if amount is None:
                    continue

                merchant = ' '.join(description_parts).strip()
                if not merchant:
                    continue

                category = get_category(merchant)

                all_transactions.append({
                    'date': date_str,
                    'category': category,
                    'amount': amount,
                    'bank': 'Chase',
                    'merchant': merchant,
                    'rebate': 0.0,
                })

    return all_transactions


# ---------------------
# HSBC Parser
# ---------------------

def parse_hsbc_statement(pdf_path):
    """
    Parse an HSBC bank statement PDF.
    HSBC uses DD Mon YY date format and columns: date, description, paid_out, paid_in, balance.
    Returns list of transaction dicts.
    """
    all_transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table({
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "snap_tolerance": 5
            })
            if not table:
                continue

            for row in table:
                clean_row = [
                    str(cell).strip() if cell and str(cell).strip() else ""
                    for cell in row
                ]
                if not clean_row or not clean_row[0]:
                    continue

                date_match = re.search(
                    r'(\d{1,2}\s[A-Za-z]{3}\s\d{2})(?!\d)', clean_row[0]
                )
                if not date_match:
                    continue

                row_text = ' '.join(clean_row)
                if _is_noise(row_text):
                    continue

                date_str = format_date_2digit(date_match.group(1))

                # HSBC columns: date, description, paid_out, paid_in, balance
                merchant = clean_row[1] if len(clean_row) > 1 else ''
                if not merchant:
                    continue

                paid_out = clean_to_float(
                    clean_row[2] if len(clean_row) > 2 else ''
                )
                paid_in = clean_to_float(
                    clean_row[3] if len(clean_row) > 3 else ''
                )

                # Use paid_out as primary amount (expenses)
                amount = paid_out if paid_out else paid_in
                if amount is None:
                    continue

                category = get_category(merchant)

                all_transactions.append({
                    'date': date_str,
                    'category': category,
                    'amount': amount,
                    'bank': 'HSBC',
                    'merchant': merchant,
                    'rebate': 0.0,
                })

    return all_transactions


# ---------------------
# Bank Auto-Detection
# ---------------------

def detect_bank_format(pdf_path):
    """
    Detect bank format by checking PDF content for bank-specific markers.
    Returns 'HSBC' or 'Chase'.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return 'Chase'
            first_page_text = pdf.pages[0].extract_text() or ''
    except Exception:
        return 'Chase'

    text_lower = first_page_text.lower()

    # HSBC detection: look for HSBC-specific markers
    if 'hsbc' in text_lower or 'paid out' in text_lower or 'paid in' in text_lower:
        return 'HSBC'

    return 'Chase'


# ---------------------
# Unified Entry Point
# ---------------------

def parse_statement(pdf_path):
    """
    Auto-detect bank format and parse the statement.
    Returns list of transaction dicts.
    """
    bank = detect_bank_format(pdf_path)

    try:
        if bank == 'HSBC':
            return parse_hsbc_statement(pdf_path)
        return parse_chase_statement(pdf_path)
    except Exception:
        return []
