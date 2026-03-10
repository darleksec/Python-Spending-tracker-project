"""Unit tests for bank_parser module."""

import pytest
from unittest.mock import patch, MagicMock

from bank_parser import (
    format_date_4digit,
    format_date_2digit,
    clean_to_float,
    get_category,
    _is_noise,
    parse_chase_statement,
    parse_hsbc_statement,
    parse_statement,
    detect_bank_format,
)


# ---------------------
# format_date_4digit
# ---------------------

class TestFormatDate4Digit:
    def test_standard(self):
        assert format_date_4digit("26 Mar 2025") == "26/03/2025"

    def test_single_digit_day(self):
        assert format_date_4digit("1 Jan 2024") == "01/01/2024"

    def test_december(self):
        assert format_date_4digit("31 Dec 2023") == "31/12/2023"


# ---------------------
# format_date_2digit
# ---------------------

class TestFormatDate2Digit:
    def test_standard(self):
        assert format_date_2digit("27 Feb 25") == "27/02/2025"

    def test_single_digit_day(self):
        assert format_date_2digit("5 Aug 24") == "05/08/2024"

    def test_old_year(self):
        assert format_date_2digit("10 Jun 99") == "10/06/1999"


# ---------------------
# get_category
# ---------------------

class TestGetCategory:
    def test_tesco_groceries(self):
        assert get_category("TESCO STORES 1234") == "Groceries"

    def test_deliveroo_dining(self):
        assert get_category("Deliveroo London") == "Dining"

    def test_amazon_shopping(self):
        assert get_category("AMAZON.CO.UK") == "Shopping"

    def test_amazon_prime_bill(self):
        assert get_category("AMAZON PRIME") == "Bill"

    def test_unknown_merchant(self):
        assert get_category("RANDOM UNKNOWN SHOP XYZ") == "Flag"


# ---------------------
# Fuzzy matching
# ---------------------

class TestFuzzyMatching:
    """Test fuzzy matching for OCR typos, special characters, and edge cases."""

    def test_ocr_typo_tesco(self):
        assert get_category("TESC0 STORES") == "Groceries"

    def test_ocr_typo_starbucks(self):
        assert get_category("STARBVCKS LONDON") == "Dining"

    def test_special_char_m_and_s(self):
        assert get_category("M&S FOOD HALL") == "Groceries"

    def test_special_char_coop(self):
        assert get_category("CO-OP GROUP") == "Groceries"

    def test_special_char_h_and_m(self):
        assert get_category("H&M ONLINE") == "Shopping"

    def test_short_merchant_kfc(self):
        assert get_category("KFC DRIVE THRU") == "Dining"

    def test_short_merchant_uber(self):
        assert get_category("UBER TRIP") == "Transport"

    def test_unknown_returns_flag(self):
        assert get_category("XYZZYPLUGH SERVICES LTD") == "Flag"

    def test_empty_description(self):
        assert get_category("") == "Flag"

    def test_none_description(self):
        assert get_category(None) == "Flag"

    def test_amazon_prime_before_amazon(self):
        """AMAZON PRIME should match Bill, not Shopping."""
        assert get_category("AMAZON PRIME MEMBERSHIP") == "Bill"

    def test_amazon_without_prime(self):
        """Plain AMAZON should match Shopping."""
        assert get_category("AMAZON MARKETPLACE") == "Shopping"


# ---------------------
# clean_to_float
# ---------------------

class TestCleanToFloat:
    def test_plain_number(self):
        assert clean_to_float("12.50") == 12.50

    def test_with_pound_sign(self):
        assert clean_to_float("£1,234.56") == 1234.56

    def test_negative_returns_abs(self):
        assert clean_to_float("-9.99") == 9.99

    def test_empty_string(self):
        assert clean_to_float("") is None

    def test_none(self):
        assert clean_to_float(None) is None

    def test_dash(self):
        assert clean_to_float("-") is None

    def test_double_dash(self):
        assert clean_to_float("--") is None

    def test_spaces(self):
        assert clean_to_float("  42.00  ") == 42.00


# ---------------------
# Noise filtering
# ---------------------

class TestNoiseFiltering:
    def test_round_up(self):
        assert _is_noise("Round up to nearest pound")

    def test_opening_balance(self):
        assert _is_noise("Opening balance")

    def test_savings_transfer(self):
        assert _is_noise("Chase savings goal")

    def test_normal_merchant(self):
        assert not _is_noise("Tesco stores")


# ---------------------
# Regex noise patterns
# ---------------------

class TestRegexNoisePatterns:
    def test_p2p_transfer_to(self):
        assert _is_noise("To John")

    def test_p2p_transfer_from(self):
        assert _is_noise("From Sarah")

    def test_reference_number(self):
        assert _is_noise("123456")

    def test_balance_bf(self):
        assert _is_noise("Balance b/f")

    def test_bf_shorthand(self):
        assert _is_noise("b/f")

    def test_false_positive_toffee(self):
        assert not _is_noise("Toffee Shop")

    def test_false_positive_fromage(self):
        assert not _is_noise("Fromage Bistro")

    def test_empty_string(self):
        assert not _is_noise("")


# ---------------------
# parse_chase_statement (mocked PDF)
# ---------------------

def _make_mock_pdf(rows):
    """Create a mock pdfplumber PDF with given table rows."""
    mock_page = MagicMock()
    mock_page.extract_table.return_value = rows
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = lambda s: s
    mock_pdf.__exit__ = MagicMock(return_value=False)
    return mock_pdf


class TestParseChaseStatement:
    @patch("bank_parser.pdfplumber.open")
    def test_basic_transaction(self, mock_open):
        rows = [
            ["15 Mar 25", "Tesco Stores", "45.67", ""],
        ]
        mock_open.return_value = _make_mock_pdf(rows)

        result = parse_chase_statement("fake.pdf")

        assert len(result) == 1
        txn = result[0]
        assert txn["date"] == "15/03/2025"
        assert isinstance(txn["amount"], float)
        assert txn["amount"] == 45.67
        assert txn["category"] == "Groceries"
        assert txn["bank"] == "Chase"
        assert txn["merchant"] == "Tesco Stores"
        assert txn["rebate"] == 0.0

    @patch("bank_parser.pdfplumber.open")
    def test_4digit_year(self, mock_open):
        rows = [
            ["26 Mar 2025", "Amazon Purchase", "19.99", ""],
        ]
        mock_open.return_value = _make_mock_pdf(rows)

        result = parse_chase_statement("fake.pdf")
        assert len(result) == 1
        assert result[0]["date"] == "26/03/2025"

    @patch("bank_parser.pdfplumber.open")
    def test_noise_filtered(self, mock_open):
        rows = [
            ["10 Jan 25", "Round up", "0.50", ""],
            ["10 Jan 25", "Opening balance", "100.00", ""],
            ["10 Jan 25", "Chase savings transfer", "50.00", ""],
            ["10 Jan 25", "Tesco", "12.00", ""],
        ]
        mock_open.return_value = _make_mock_pdf(rows)

        result = parse_chase_statement("fake.pdf")
        assert len(result) == 1
        assert result[0]["merchant"] == "Tesco"

    @patch("bank_parser.pdfplumber.open")
    def test_no_bill_category_leak(self, mock_open):
        """Categories should not all be 'Bill' — verify diverse categories."""
        rows = [
            ["1 Feb 25", "Tesco", "10.00", ""],
            ["2 Feb 25", "Deliveroo", "15.00", ""],
            ["3 Feb 25", "Amazon order", "25.00", ""],
        ]
        mock_open.return_value = _make_mock_pdf(rows)

        result = parse_chase_statement("fake.pdf")
        categories = {t["category"] for t in result}
        assert "Bill" not in categories
        assert "Groceries" in categories
        assert "Dining" in categories
        assert "Shopping" in categories


# ---------------------
# parse_statement auto-detection
# ---------------------

class TestParseStatementAutoDetect:
    @patch("bank_parser.pdfplumber.open")
    def test_chase_auto_detect(self, mock_open):
        """parse_statement should detect Chase and delegate correctly."""
        # First call: detect_bank_format reads first page text
        # Second call: parse_chase_statement reads tables
        mock_page_detect = MagicMock()
        mock_page_detect.extract_text.return_value = "Chase UK Statement"

        mock_page_parse = MagicMock()
        mock_page_parse.extract_table.return_value = [
            ["5 Apr 25", "Starbucks", "4.50", ""],
        ]

        mock_pdf_detect = MagicMock()
        mock_pdf_detect.pages = [mock_page_detect]
        mock_pdf_detect.__enter__ = lambda s: s
        mock_pdf_detect.__exit__ = MagicMock(return_value=False)

        mock_pdf_parse = MagicMock()
        mock_pdf_parse.pages = [mock_page_parse]
        mock_pdf_parse.__enter__ = lambda s: s
        mock_pdf_parse.__exit__ = MagicMock(return_value=False)

        mock_open.side_effect = [mock_pdf_detect, mock_pdf_parse]

        result = parse_statement("fake.pdf")
        assert len(result) == 1
        assert result[0]["category"] == "Dining"


# ---------------------
# Integration tests
# ---------------------

class TestParsingIntegration:
    @patch("bank_parser.pdfplumber.open")
    def test_chase_filters_person_transfers(self, mock_open):
        """Chase parser should filter out personal transfers and savings noise."""
        rows = [
            ["10 Jan 25", "personal transfer", "50.00", ""],
            ["10 Jan 25", "Chase savings goal", "25.00", ""],
            ["10 Jan 25", "Tesco Stores", "12.50", ""],
        ]
        mock_open.return_value = _make_mock_pdf(rows)

        result = parse_chase_statement("fake.pdf")
        assert len(result) == 1
        assert result[0]["merchant"] == "Tesco Stores"
        assert result[0]["category"] == "Groceries"

    @patch("bank_parser.pdfplumber.open")
    def test_chase_fuzzy_categorizes_ocr_typo(self, mock_open):
        """Chase parser should fuzzy-match OCR-typo merchants to correct categories."""
        rows = [
            ["5 Feb 25", "TESC0 STORES", "30.00", ""],
            ["5 Feb 25", "STARBVCKS LONDON", "4.50", ""],
        ]
        mock_open.return_value = _make_mock_pdf(rows)

        result = parse_chase_statement("fake.pdf")
        assert len(result) == 2
        assert result[0]["category"] == "Groceries"
        assert result[1]["category"] == "Dining"

    @patch("bank_parser.pdfplumber.open")
    def test_hsbc_filters_balance_bf(self, mock_open):
        """HSBC parser should filter out 'Balance b/f' rows."""
        rows = [
            ["1 Mar 25", "Balance b/f", "", "", "1000.00"],
            ["1 Mar 25", "b/f", "", "", "1000.00"],
            ["2 Mar 25", "Sainsburys", "45.00", "", "955.00"],
        ]
        mock_open.return_value = _make_mock_pdf(rows)

        result = parse_hsbc_statement("fake.pdf")
        assert len(result) == 1
        assert result[0]["merchant"] == "Sainsburys"
        assert result[0]["bank"] == "HSBC"
