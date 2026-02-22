import json
import os
import csv
from expense import Expense
from datetime import datetime
import pandas as pd
class ExpenseTracker:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = {}
        self.next_id =1
        self.hash_index = {}
        self.load()

    #ID
    def get_next_id(self):
        current_id = self.next_id
        self.next_id += 1
        
        if self.expenses:
            self.next_id = max(self.expenses.keys()) + 1
        else:
            self.next_id = 1
        return current_id

    # -----------------
    # Add
    # -----------------
    def add_expense(self, date, category, amount, payment_method, merchant, rebate=0.0):
        expense_id = self.get_next_id()

        expense = Expense(
            expense_id,
            date,
            category,
            amount,
            payment_method,
            merchant,
            rebate
        )

        #  check duplicate
        if expense.hash_value in self.hash_index:
            return False  # duplicate detected

        self.expenses[expense_id] = expense
        self.hash_index[expense.hash_value] = expense_id

        self.save()
        return True


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
                self.hash_index[expense.hash_value] = expense.id
                
            
        except json.JSONDecodeError:
            print("JSON file corrupted, resetting storage")
            self.expenses = {}
            self.next_id = 1
            
            
    #getters
    
    def get_expense_by_id(self,expense_id):
        return self.expenses.get(expense_id)
    
    
    def get_all_expenses(self):
        return sorted(
            self.expenses.values(),
            key=lambda e: e.date
        )

    def get_category_total(self):
        totals = {}
        
        for exp in self.expenses.values():  
            print(type(exp))  
            category = exp.category
            amount = exp.amount
            
            if category not in totals:
                totals[category] = 0
                
            totals[category] += amount
            
        return totals
    
    def _clean_money(self, value):

        if not value:
            return 0.0

        # Remove currency symbol and spaces
        value = value.strip().replace("£", "").replace(",", "")

        # Handle weird rebate like "£-   "
        if value == "-" or value == "":
            return 0.0

        return float(value)

    
     #importing            
    def importCSV(self, file_path):    
        count = 0

        with open(file_path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            reader.fieldnames = [field.strip() for field in reader.fieldnames]

            for row in reader:
                try:
                    row = {key.strip(): value for key, value in row.items()}

                    date = row["Date"].strip()
                    category = row["Category"].strip()
                    payment_method = row["Bank"].strip()
                    merchant = row["Merchant"].strip()

                    amount = self._clean_money(row["Amount"])
                    rebate = self._clean_money(row["Rebate"])

                    if self.add_expense(date, category, amount,
                                        payment_method, merchant, rebate):
                        count += 1

                except Exception as e:
                    print(f"Skipping row due to error Row:{row} Error: {e}")
                    continue

        return count
    
    def importXlsx(self, file_path):
        count = 0

        df = pd.read_excel(file_path, sheet_name=0)

        # Clean empty rows
        df = df.dropna(how="all")

        # Strip column names
        df.columns = df.columns.str.strip()
        print(df.columns)

        for _, row in df.iterrows():
            try:
                # Date
                date = row["Date"]
                print(type(row["Date"]), row["Date"])

                if pd.isna(date):
                    raise ValueError("Missing date")
                date = date.strftime("%d/%m/%Y")

                # Other fields
                category = str(row["Category"]).strip()
                amount = float(row["Amount"])
                payment_method = str(row["Bank"]).strip()
                merchant = str(row["Merchant"]).strip()

                rebate = row["Rebate"]
                rebate = 0.0 if pd.isna(rebate) else float(rebate)

                added = self.add_expense(
                    date,
                    category,
                    amount,
                    payment_method,
                    merchant,
                    rebate
                )

                if added:
                    count += 1

            except Exception as e:
                print(f"Skipping row due to error Row:{row} Error: {e}")
                continue

        return count



            
            
            
            
            
