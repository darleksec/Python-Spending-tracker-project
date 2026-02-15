from datetime import datetime
import json
import os
from ExpenseTracker import ExpenseTracker
from expense import Expense


def show_menu():
    print("\n=== Personal Spending Tracker ===\n")
    print("1. Add expense")
    print("2. View expenses")
    print("5. edit")
    print("6. delete")
    print("-1. Exit")


def handle_add(tracker):
    date = input("Date: ")
    category = input("Category: ")
    amount = input("Amount: ")
    payment_method = input("Payment method: ")
    rebate = input("Rebate (optional): ") or 0
    expense_id = tracker.add_expense(
                date, category, amount, payment_method, rebate
            )

    print(f"Expense added with ID: {expense_id}")
    
def handle_edit(tracker):
    expense_id = input("Enter Expense ID to edit: ")
    field = input("Field to edit (date/category/amount/payment_method/rebate): ")
    value = input("New value: ")
    success = tracker.edit_expense(expense_id, **{field: value})

    if success:
        print("Expense updated.")
    else:
        print("Expense not found.")
        
def handle_delete(tracker):
    expense_id = input("Enter Expense ID to delete: ")
    tracker.delete_expense(expense_id)
    print("Deleted (if ID existed).")
    

def handle_view(tracker):
    if not tracker.expenses:
        print("No records")
        return
    
    print("\n-- ID |  Date  |category| amount |payment| rebate --")

    for expense in tracker.expenses.values():
        print(expense)
        
def main():
    tracker = ExpenseTracker()
    
    
    while True:
        show_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            handle_add(tracker)
        elif choice == "2":
            handle_view(tracker)
        elif choice == "5":
            handle_edit(tracker)
        elif choice == "6":
            handle_delete(tracker)
        elif choice =="-1":
            print("program end")
            break
        
        
        
if __name__ == "__main__":
    main()








            


