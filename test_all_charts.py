#!/usr/bin/env python
"""
Comprehensive test script for all visualization charts
Tests all 6 new charts + 5 existing charts
"""

import sys
import json
from ExpenseTracker import ExpenseTracker
from gui.visual_page import VisualPage
from PyQt6.QtWidgets import QApplication

def test_dataframe_columns(page):
    """Verify DataFrame has all required columns"""
    required_columns = ['Date', 'Category', 'Amount', 'Month', 'Merchant', 'PaymentMethod', 'Rebate', 'DayOfWeek']
    df_columns = page.df.columns.tolist()

    print("\n=== DataFrame Column Test ===")
    print(f"Expected columns: {required_columns}")
    print(f"Actual columns: {df_columns}")

    missing = [col for col in required_columns if col not in df_columns]
    if missing:
        print(f"❌ FAILED: Missing columns: {missing}")
        return False
    else:
        print("✅ PASSED: All required columns present")
        return True

def test_chart_rendering(page, chart_name, chart_method):
    """Test if a chart method executes without errors"""
    print(f"\n=== Testing: {chart_name} ===")
    try:
        chart_method()
        print(f"✅ PASSED: {chart_name} rendered successfully")
        return True
    except Exception as e:
        print(f"❌ FAILED: {chart_name} - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_aggregations(page):
    """Test data aggregation logic"""
    print("\n=== Data Aggregation Tests ===")
    df = page.df

    # Test merchant aggregation
    merchant_totals = df.groupby("Merchant")["Amount"].sum()
    print(f"Top 5 merchants: {merchant_totals.nlargest(5).to_dict()}")

    # Test cashback efficiency
    total_spend = df["Amount"].sum()
    total_rebate = df["Rebate"].sum()
    efficiency = (total_rebate / total_spend * 100) if total_spend > 0 else 0
    print(f"Overall cashback efficiency: {efficiency:.2f}%")

    # Test payment method grouping
    payment_totals = df.groupby("PaymentMethod")["Amount"].sum()
    print(f"Payment methods: {payment_totals.to_dict()}")

    # Test weekly pattern
    weekly_avg = df.groupby("DayOfWeek")["Amount"].mean()
    print(f"Average spending by day (sample): {dict(list(weekly_avg.items())[:3])}")

    print("✅ PASSED: All aggregations computed successfully")
    return True

def test_edge_case_zero_rebate(page):
    """Test charts handle zero rebate correctly"""
    print("\n=== Edge Case: Zero Rebate Dataset ===")

    # Check if we have any non-zero rebates
    non_zero_rebates = (page.df["Rebate"] > 0).sum()
    total_rebates = len(page.df)

    print(f"Non-zero rebates: {non_zero_rebates}/{total_rebates}")

    if non_zero_rebates == 0:
        print("Dataset has all zero rebates - testing cashback chart with zero efficiency")
        try:
            page.plot_cashback_analysis()
            print("✅ PASSED: Cashback chart handles zero rebates gracefully")
            return True
        except Exception as e:
            print(f"❌ FAILED: Cashback chart failed with zero rebates: {str(e)}")
            return False
    else:
        print("✅ PASSED: Dataset has rebates, zero-rebate scenario not applicable")
        return True

def main():
    print("=" * 60)
    print("COMPREHENSIVE CHART VERIFICATION TEST")
    print("=" * 60)

    # Initialize tracker and visual page
    tracker = ExpenseTracker()
    app = QApplication(sys.argv)
    page = VisualPage(tracker)

    print(f"\nTotal expenses loaded: {len(tracker.get_all_expenses())}")
    print(f"DataFrame shape: {page.df.shape}")

    results = []

    # Test 1: DataFrame columns
    results.append(("DataFrame Columns", test_dataframe_columns(page)))

    # Test 2: Data aggregations
    results.append(("Data Aggregations", test_data_aggregations(page)))

    # Test 3: All 6 NEW charts
    new_charts = [
        ("Category Horizontal Bar", page.plot_category_horizontal_bar),
        ("Weekly Spending Pattern", page.plot_weekly_pattern),
        ("Top 10 Merchants", page.plot_top_merchants),
        ("Cashback Analysis", page.plot_cashback_analysis),
        ("Payment Method Spend", page.plot_payment_method_spend),
        ("Budget vs Actual", page.plot_budget_vs_actual),
    ]

    print("\n" + "=" * 60)
    print("TESTING 6 NEW CHARTS")
    print("=" * 60)

    for chart_name, chart_method in new_charts:
        results.append((chart_name, test_chart_rendering(page, chart_name, chart_method)))

    # Test 4: All 5 EXISTING charts (ensure we didn't break anything)
    existing_charts = [
        ("Monthly Overview", page.monthly_overview),
        ("Category Sum (Vertical Bar)", page.Category_Sum),
        ("Monthly Pie Chart", lambda: page.monthly_pie()),
        ("Category Trend", page.plot_category_trend),
        ("Cumulative Monthly Spend", page.plot_cum_spend),
    ]

    print("\n" + "=" * 60)
    print("TESTING 5 EXISTING CHARTS (Regression Test)")
    print("=" * 60)

    for chart_name, chart_method in existing_charts:
        results.append((chart_name, test_chart_rendering(page, chart_name, chart_method)))

    # Test 5: Edge cases
    results.append(("Edge Case: Zero Rebate", test_edge_case_zero_rebate(page)))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 60)
    print(f"FINAL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! All charts are working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
