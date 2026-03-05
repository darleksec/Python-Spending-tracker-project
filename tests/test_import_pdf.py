"""Integration tests for ExpenseTracker.importPDF() and importPDFBatch()."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from ExpenseTracker import ExpenseTracker


def _make_mock_pdf(rows):
    """Create a mock pdfplumber PDF with given table rows."""
    mock_page = MagicMock()
    mock_page.extract_table.return_value = rows
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = lambda s: s
    mock_pdf.__exit__ = MagicMock(return_value=False)
    return mock_pdf


def _make_detect_and_parse_pdfs(rows, bank_text="Chase UK Statement"):
    """Return a side_effect list for two pdfplumber.open calls (detect + parse)."""
    mock_page_detect = MagicMock()
    mock_page_detect.extract_text.return_value = bank_text

    mock_pdf_detect = MagicMock()
    mock_pdf_detect.pages = [mock_page_detect]
    mock_pdf_detect.__enter__ = lambda s: s
    mock_pdf_detect.__exit__ = MagicMock(return_value=False)

    mock_pdf_parse = _make_mock_pdf(rows)

    return [mock_pdf_detect, mock_pdf_parse]


class TestImportPDF:
    """Integration tests for importPDF method."""

    def _make_tracker(self, tmp_path):
        """Create an ExpenseTracker with a temp JSON file."""
        json_file = os.path.join(str(tmp_path), "test_expenses.json")
        return ExpenseTracker(filename=json_file)

    @patch("bank_parser.pdfplumber.open")
    def test_import_pdf_creates_expenses(self, mock_open, tmp_path):
        """importPDF with a valid Chase PDF creates expenses in a temp JSON file."""
        rows = [
            ["15 Mar 25", "Tesco Stores", "45.67", ""],
            ["16 Mar 25", "Deliveroo London", "18.50", ""],
            ["17 Mar 25", "TFL Travel", "2.80", ""],
        ]
        mock_open.side_effect = _make_detect_and_parse_pdfs(rows)

        tracker = self._make_tracker(tmp_path)
        count = tracker.importPDF("fake_chase.pdf")

        assert count == 3
        # Verify data persisted to JSON
        with open(tracker.filename, "r") as f:
            data = json.load(f)
        assert len(data["expenses"]) > 0

    @patch("bank_parser.pdfplumber.open")
    def test_dedup_returns_zero(self, mock_open, tmp_path):
        """Re-importing the same PDF returns 0 (dedup works)."""
        rows = [
            ["15 Mar 25", "Tesco Stores", "45.67", ""],
        ]

        tracker = self._make_tracker(tmp_path)

        # First import
        mock_open.side_effect = _make_detect_and_parse_pdfs(rows)
        count1 = tracker.importPDF("fake.pdf")
        assert count1 == 1

        # Second import of same data
        mock_open.side_effect = _make_detect_and_parse_pdfs(rows)
        count2 = tracker.importPDF("fake.pdf")
        assert count2 == 0

    @patch("bank_parser.pdfplumber.open")
    def test_imported_expenses_have_correct_fields(self, mock_open, tmp_path):
        """Imported expenses have all required fields with correct values."""
        rows = [
            ["20 Apr 25", "Tesco Express", "12.99", ""],
        ]
        mock_open.side_effect = _make_detect_and_parse_pdfs(rows)

        tracker = self._make_tracker(tmp_path)
        tracker.importPDF("fake.pdf")

        expense = list(tracker.expenses.values())[0]
        assert expense.date == "20/04/2025"
        assert expense.category == "Groceries"
        assert expense.amount == 12.99
        assert expense.payment_method == "Chase"
        assert expense.merchant == "Tesco Express"
        assert expense.rebate == 0.0
        assert expense.hash_value is not None and len(expense.hash_value) > 0


class TestImportPDFBatch:
    """Integration tests for importPDFBatch method."""

    @patch("bank_parser.pdfplumber.open")
    def test_batch_imports_all_pdfs(self, mock_open, tmp_path):
        """importPDFBatch on a directory imports from all PDFs."""
        pdf_dir = os.path.join(str(tmp_path), "pdfs")
        os.makedirs(pdf_dir)
        for name in ["stmt1.pdf", "stmt2.pdf", "stmt3.pdf"]:
            open(os.path.join(pdf_dir, name), "w").close()
        # Non-PDF file should be ignored
        open(os.path.join(pdf_dir, "readme.txt"), "w").close()

        rows1 = [["1 Jan 25", "Aldi Shop", "30.00", ""]]
        rows2 = [["2 Jan 25", "Netflix Monthly", "15.99", ""]]
        rows3 = [["3 Jan 25", "Uber Trip", "8.50", ""]]

        # Each importPDF call triggers 2 pdfplumber.open calls (detect + parse)
        mock_open.side_effect = (
            _make_detect_and_parse_pdfs(rows1)
            + _make_detect_and_parse_pdfs(rows2)
            + _make_detect_and_parse_pdfs(rows3)
        )

        json_file = os.path.join(str(tmp_path), "test_expenses.json")
        tracker = ExpenseTracker(filename=json_file)
        count = tracker.importPDFBatch(pdf_dir)

        assert count == 3
        # Verify JSON file was written
        with open(tracker.filename, "r") as f:
            data = json.load(f)
        assert len(data["expenses"]) > 0


class TestImportCSVRegression:
    """Verify existing importCSV still works after PDF import changes."""

    def test_import_csv_still_works(self, tmp_path):
        """importCSV continues to work correctly (no regression)."""
        csv_content = (
            "Date,Category,Amount,Bank,Merchant,Rebate\n"
            "01/01/2025,Groceries,25.00,Chase,Tesco,0.00\n"
        )
        csv_file = os.path.join(str(tmp_path), "test.csv")
        with open(csv_file, "w", encoding="utf-8-sig") as f:
            f.write(csv_content)

        json_file = os.path.join(str(tmp_path), "test_expenses.json")
        tracker = ExpenseTracker(filename=json_file)
        count = tracker.importCSV(csv_file)

        assert count == 1
        # Check that expenses were persisted
        with open(json_file, "r") as f:
            data = json.load(f)
        assert len(data["expenses"]) == 1

        exp = data["expenses"][0]
        assert exp["date"] == "01/01/2025"
        assert exp["category"] == "Groceries"
        assert exp["amount"] == 25.00
        assert exp["payment_method"] == "Chase"
        assert exp["merchant"] == "Tesco"
        assert exp["rebate"] == 0.00
        assert "hash_value" in exp
