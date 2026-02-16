import json
import os
from expense import Expense
class ExpenseTracker:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = {}
        self.next_id =1
        self.load()

    #ID
    def get_next_id(self):
        current_id = self.next_id
        self.next_id += 1
        return current_id

    # -----------------
    # Add
    # -----------------
    def add_expense(self, date, category, amount, payment_method, rebate=0.0):
        expense_id = self.get_next_id()
        
        
        expense = Expense(expense_id, date, category, amount, payment_method, rebate)
         
        self.expenses[expense_id] = expense
        self.save()
        return expense.id

    # -----------------
    # Delete
    # -----------------
    def delete_expense(self, expense_id):
        if expense_id not in self.expenses:
            return False
        
        self.expenses.pop(expense_id)
        self.save()
        return True

    # -----------------
    # Edit
    # -----------------
    def edit_expense(self, expense_id, **kwargs):
        expense = self.expenses.get(expense_id)

        if not expense:
            return False

        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)

        expense.hash_value = expense.generate_hash()

        self.save()
        return True
        

    # -----------------
    # Save
    # -----------------
    def save(self):
        data = {
            "next_id": self.next_id,
            "expenses":[exp.to_dict() for exp in self.expenses.values()]
        }
        with open(self.filename, "w") as f:
            json.dump(
                data,
                f,
                indent=4
            )

    # -----------------
    # Load
    # -----------------
    def load(self):
        if not os.path.exists(self.filename):
            return
        
        if os.path.getsize(self.filename) == 0:
            self.expenses = {}
            self.next_id = 1
            return
        
        try:

            with open(self.filename, "r") as f:
                data = json.load(f)
                
            self.next_id = data.get("next_id",1 )
            self.expenses = {}
            
            for item in data.get("expenses", []):
                expense = Expense.from_dict(item)
                self.expenses[expense.id] = expense
        except json.JSONDecodeError:
            print("JSON file corrupted, resetting storage")
            self.expenses = {}
            self.next_id = 1
            
    def get_all_expenses(self):
        return sorted(
            self.expenses.values(),
            key=lambda e: e.date
        )

    
            
            
            
            
            
            
