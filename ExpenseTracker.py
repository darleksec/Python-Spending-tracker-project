import json
import os
from expense import Expense
class ExpenseTracker:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = []
        self.load()

    # -----------------
    # Add
    # -----------------
    def add_expense(self, date, category, amount, payment_method, rebate=0.0):
        expense = Expense(date, category, amount, payment_method, rebate)
        self.expenses.append(expense)
        self.save()
        return expense.id

    # -----------------
    # Delete
    # -----------------
    def delete_expense(self, expense_id):
        self.expenses = [
            e for e in self.expenses if e.id != expense_id
        ]
        self.save()

    # -----------------
    # Edit
    # -----------------
    def edit_expense(self, expense_id, **kwargs):
        for expense in self.expenses:
            if expense.id == expense_id:
                for key, value in kwargs.items():
                    if hasattr(expense, key):
                        setattr(expense, key, value)
                self.save()
                return True
        return False

    # -----------------
    # Save
    # -----------------
    def save(self):
        with open(self.filename, "w") as f:
            json.dump(
                [e.to_dict() for e in self.expenses],
                f,
                indent=4
            )

    # -----------------
    # Load
    # -----------------
    def load(self):
        if not os.path.exists(self.filename):
            return

        with open(self.filename, "r") as f:
            data = json.load(f)
            self.expenses = [Expense.from_dict(d) for d in data]
