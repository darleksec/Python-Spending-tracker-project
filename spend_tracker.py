from datetime import datetime
import json

#in mem storage for expenses

expenses  = []

def add_expense():
    try: 
        amount = float(input("Enter amount:"))
        
        category = input("Catergory: ")
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
    
    
    except ValueError:
        print("ValueError , invalid value")

def view_expenses(category=None, date=None):
    if not expenses:
        print("No expenses recorded yet.\n")    
        return

    shown = False


    print("\n--- Your Expenses ---")
    print("\n-- Date   |category| amount |payment method--")
    for i, exp in enumerate(expenses, start=1):

        if category and exp["category"].lower() != category.lower():
            continue
        
        if date and exp["date"]!=date:
            continue

        print(
            f"{i}. {exp['date']} | {exp['category']} | "
            f"${exp['amount']:.2f} | {exp['payment']}"
        )
        shown = True
    
    if not shown:
        print("Error:  no matching expenses")
    print()

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
    print("-1. Exit")

def show_Sum_menu():
    print("\nSums menu\n")
    print("1. Total Sum")
    print("2. Category Sum")
    print("3. Date Sum")
    print("-1. Back")
    

def main():
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
        elif choice == "-1":
            print(" Goodbye!")
            break
        
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()