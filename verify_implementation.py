#!/usr/bin/env python
"""
Simple verification script to check all chart methods exist and are callable
Does not require GUI - just checks code structure
"""

import ast
import sys

def verify_implementation():
    """Verify all required methods exist in visual_page.py"""

    print("=" * 60)
    print("IMPLEMENTATION VERIFICATION")
    print("=" * 60)

    with open('./gui/visual_page.py', 'r') as f:
        tree = ast.parse(f.read())

    # Find all method definitions
    methods = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            methods[node.name] = node.lineno

    # Required new chart methods
    required_new_methods = [
        'plot_category_horizontal_bar',
        'plot_weekly_pattern',
        'plot_top_merchants',
        'plot_cashback_analysis',
        'plot_payment_method_spend',
        'plot_budget_vs_actual'
    ]

    # Required existing methods (regression check)
    required_existing_methods = [
        'monthly_overview',
        'Category_Sum',
        'monthly_pie',
        'plot_category_trend',
        'plot_cum_spend'
    ]

    # Other required methods
    required_core_methods = [
        'build_dataframe',
        'create_sidebar',
        'clear_and_get_axis'
    ]

    all_pass = True

    # Check new methods
    print("\n📊 NEW CHART METHODS:")
    for method in required_new_methods:
        if method in methods:
            print(f"  ✅ {method} (line {methods[method]})")
        else:
            print(f"  ❌ {method} - NOT FOUND")
            all_pass = False

    # Check existing methods (regression)
    print("\n📈 EXISTING CHART METHODS (Regression):")
    for method in required_existing_methods:
        if method in methods:
            print(f"  ✅ {method} (line {methods[method]})")
        else:
            print(f"  ❌ {method} - MISSING (REGRESSION BUG!)")
            all_pass = False

    # Check core methods
    print("\n🔧 CORE METHODS:")
    for method in required_core_methods:
        if method in methods:
            print(f"  ✅ {method} (line {methods[method]})")
        else:
            print(f"  ❌ {method} - NOT FOUND")
            all_pass = False

    # Check DataFrame columns in build_dataframe
    print("\n📋 DATAFRAME COLUMNS:")
    with open('./gui/visual_page.py', 'r') as f:
        content = f.read()

    required_columns = ['Merchant', 'PaymentMethod', 'Rebate', 'DayOfWeek']
    for col in required_columns:
        if f'"{col}"' in content or f"'{col}'" in content:
            print(f"  ✅ {col} column present")
        else:
            print(f"  ❌ {col} column - NOT FOUND")
            all_pass = False

    # Check button creation
    print("\n🔘 SIDEBAR BUTTONS:")
    button_names = [
        'cat_bar_h_btn',
        'weekly_pattern_btn',
        'top_merchants_btn',
        'cashback_btn',
        'payment_method_btn',
        'budget_btn'
    ]

    for btn in button_names:
        if f'self.{btn}' in content:
            print(f"  ✅ {btn} created")
        else:
            print(f"  ❌ {btn} - NOT FOUND")
            all_pass = False

    # Check for debug print statements
    print("\n🐛 CODE QUALITY CHECKS:")
    build_df_start = content.find('def build_dataframe(self):')
    build_df_end = content.find('def ', build_df_start + 1)
    build_df_code = content[build_df_start:build_df_end]

    if 'print(' in build_df_code:
        print("  ⚠️  WARNING: print() statements found in build_dataframe()")
        # Check if they are the specific debug prints
        if 'print(df.columns)' in build_df_code or 'print(df.head())' in build_df_code:
            print("     Debug prints should be removed")
    else:
        print("  ✅ No debug print statements in build_dataframe()")

    # Summary
    print("\n" + "=" * 60)
    if all_pass:
        print("✅ ALL CHECKS PASSED - Implementation Complete")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("  1. Run manual GUI test: python gui/app.py")
        print("  2. Click through all 11 charts (5 old + 6 new)")
        print("  3. Verify charts render correctly")
        print("  4. Test edge cases (empty data, chart switching)")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Review Errors Above")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = verify_implementation()
    sys.exit(exit_code)
