"""Tests for gui/dashboard_page.py — data helpers and chart logic (no Qt required)."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestDashboardDataHelpers:
    """Test data processing logic without requiring PyQt6 or display."""

    def _make_expense(self, date_str, category, amount):
        exp = MagicMock()
        exp.date = date_str
        exp.category = category
        exp.amount = amount
        return exp

    def _build_dataframe(self, expenses):
        """Replicate DashboardPage.build_dataframe logic."""
        data = []
        for exp in expenses:
            data.append({
                "Date": exp.date,
                "Category": exp.category,
                "Amount": exp.amount,
            })
        if not data:
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Month"])
        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
        df["Month"] = df["Date"].dt.to_period("M")
        return df

    def test_build_dataframe_empty(self):
        df = self._build_dataframe([])
        assert len(df) == 0
        assert "Month" in df.columns

    def test_build_dataframe_parses_dates(self):
        expenses = [self._make_expense("15/03/2026", "Food", 25.0)]
        df = self._build_dataframe(expenses)
        assert len(df) == 1
        assert df.iloc[0]["Month"] == pd.Period("2026-03", freq="M")

    def test_build_dataframe_multiple_months(self):
        expenses = [
            self._make_expense("01/01/2026", "Food", 10),
            self._make_expense("15/02/2026", "Transport", 20),
        ]
        df = self._build_dataframe(expenses)
        months = df["Month"].unique()
        assert len(months) == 2

    def test_category_grouping(self):
        expenses = [
            self._make_expense("01/03/2026", "Food", 10),
            self._make_expense("02/03/2026", "Food", 15),
            self._make_expense("03/03/2026", "Transport", 5),
        ]
        df = self._build_dataframe(expenses)
        totals = df.groupby("Category")["Amount"].sum()
        assert totals["Food"] == 25
        assert totals["Transport"] == 5

    def test_top5_other_grouping(self):
        """When more than 5 categories exist, extras should be grouped as 'Other'."""
        categories = ["A", "B", "C", "D", "E", "F", "G"]
        expenses = [
            self._make_expense("01/03/2026", cat, 10 * (i + 1))
            for i, cat in enumerate(categories)
        ]
        df = self._build_dataframe(expenses)
        totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        top_5 = totals.head(5).copy()
        other_total = totals.iloc[5:].sum()
        if other_total > 0:
            top_5["Other"] = other_total
        assert len(top_5) == 6  # 5 + Other
        assert "Other" in top_5.index


class TestPieChartUnpacking:
    """Verify the autopct pie chart returns 3 values (the bug fix)."""

    def test_pie_with_autopct_returns_three(self):
        """matplotlib pie with autopct returns (wedges, texts, autotexts)."""
        matplotlib = pytest.importorskip("matplotlib")
        from matplotlib.figure import Figure

        fig = Figure()
        ax = fig.add_subplot(111)
        result = ax.pie([30, 70], labels=["A", "B"], autopct="%1.1f%%")
        assert len(result) == 3, "pie() with autopct must return 3 values"
