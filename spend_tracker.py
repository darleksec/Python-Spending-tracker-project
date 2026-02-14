from datetime import datetime
import json
import os
#in mem storage for expenses
expenses = []

def add_expense():
    try: 
        amount = float(input("Enter amount:"))
        
        category = input("Category: ")
        payment = input("payment method: ")
        date = datetime.now().strftime("%y-%m-%d")

        expense = {
            "date" : date,
            "amount" : amount,
            "category" : category,
            "payment" : payment
        }

        expenses.append(expense)
        print("\nexpense added successfully")
        save_expense()
        print("\nexpense save successfully")

    
    
    except ValueError:
        print("ValueError , invalid value")

def view_expenses(category=None, date=None):
    if not expenses:
        print("No expenses recorded yet.\n")    
        return

    shown = False


    print("\n--- Your Expenses ---")
    print("\n-- Date   |category| amount |payment method--")
    for i, exp in enumerate(expenses):

        if category and exp["category"].lower() != category.lower():
            continue
        
        if date and exp["date"]!=date:
            continue

        print(
            f"{i+1}. {exp['date']} | {exp['category']} | "
            f"${exp['amount']:.2f} | {exp['payment']}"
        )
        shown = True
    
    if not shown:
        print("Error:  no matching expenses")
    print()

def delete_expense():#nothing here yet 
    view_expenses()
    
    if not expenses:
        return
    
    try:
        choice = int(input("Choose which entry to delete with index no. :"))
        index = choice - 1
        
        if 0 <= index < len(expenses):
            removed = expenses.pop(index)
            print("Deleted : " ,removed)
            
        else:
            print("invalid number")
            
            
    except ValueError:
        print("Enter a valid number")
        
        
        
    save_expense()
    print("\nexpense save successfully")

def edit_expense():#nothing here yet
    view_expenses()
        
    if not expenses:
        return
    
    try:
        choice = int(input("Choose which entry to edit with index no. :"))
        index = choice - 1
        
        if 0 <= index < len(expenses):
            exp = expenses[index]
            new_date = input(f"New date yy/mm/dd ({exp['date']}): ")
            new_amount = input(f"New amount ({exp['amount']}): ")
            new_category = input(f"New category ({exp['category']}): ")
            new_payment = input(f"New payment ({exp['payment']}): ")
            
            if new_date:
                exp["date"] = new_date
            if new_amount:
                exp["amount"] = float(new_amount)
            if new_category:
                exp["category"]= new_category
            if new_payment:
                exp["payment"] = new_payment
                
            print("entry updated")
        
        else:
            print("invalid number")
            
            
    except ValueError:
        print("Enter a valid number")
        
        
    save_expense()
    print("\nexpense save successfully")


def total_spent(category=None, date=None):
    total = 0
    view_expenses(category=category, date=date)

    for exp in expenses:
        if category and exp["category"].lower() != category.lower():
            continue
        
        if date and exp["date"]!=date:
            continue

        total += exp["amount"]

    return total

    
def category_Sum():
    category = input("Choose a category to check the sum: ")

    total = total_spent(category=category)
    print(f"\nTotal amount for {category}: ${total:.2f}")

def date_Sum():
    date = input("YY-MM-DD to check sum on date: ")
    total = total_spent(date=date)
    print(f"\nTotal amount on {date}: ${total:.2f}")

def show_Total():
    total = total_spent()
    print(f"\nTotal amount: ${total:.2f}")

def show_menu():
    print("\n=== Personal Spending Tracker ===\n")
    print("1. Add expense")
    print("2. View expenses")
    print("3. Sums")
    print("4. cat sum")
    print("5. delete")
    print("6. Edit")


    print("-1. Exit")

def show_Sum_menu():
    print("\nSums menu\n")
    print("1. Total Sum")
    print("2. Category Sum")
    print("3. Date Sum")
    print("-1. Back")
    
def save_expense():
    with open ("expenses.json" , "w")as file:
        json.dump(expenses, file, indent=4)

def load_expense():
    global expenses
    print("DEBUG loaded expenses:", expenses)
    print("DEBUG count:", len(expenses))

    file_path = os.path.abspath("expenses.json")
    print("reading from : ", file_path)

    print("Current working directory:", os.getcwd())

    if not os.path.exists("expenses.json"):
        return []
    try: #try catch prevents crashing from corrupted file
            
        with open("expenses.json", "r") as file:
            expenses = json.load(file)
            print("imported expense from JSON ")
    except json.JSONDecodeError:
        print("Warning, corrupted JSON file, Starting fresh log")
        expenses = []
    


def main():
    load_expense()


    while True:
        show_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_Sum_menu()
            choice = input("Choose an option: ")
            if choice == "1":
                total_spent()
                show_Total()
            elif choice == "2":
                category_Sum()
            elif choice == "3":
                date_Sum()
            elif choice == "-1":
                main()
        elif choice == "4":
            category_Sum()
        elif choice == "5":
            delete_expense()
        elif choice == "6":
            edit_expense()
        elif choice == "-1":
            print(" Goodbye!")
            break
        
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()