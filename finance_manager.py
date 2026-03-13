import json
import os
import uuid
from datetime import datetime
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "transactions.json")

def load_data():
    """Load transactions from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        print("Error reading the data file. Starting with an empty dataset.")
        return []

def save_data(data):
    """Save transactions to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError:
        print("Error saving data to file.")

def get_valid_date(prompt):
    """Prompt user for a valid date in YYYY-MM-DD format."""
    while True:
        date_str = input(prompt)
        try:
            valid_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return str(valid_date)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def get_valid_amount(prompt):
    """Prompt user for a valid positive amount."""
    while True:
        try:
            amount = float(input(prompt))
            if amount <= 0:
                print("Amount must be greater than zero.")
            else:
                return amount
        except ValueError:
            print("Invalid amount. Please enter a valid number.")

def add_transaction(data, transaction_type):
    """Add a new income or expense record."""
    print(f"\n--- Add {transaction_type.capitalize()} ---")
    date = get_valid_date("Enter date (YYYY-MM-DD): ")
    amount = get_valid_amount("Enter amount: ")
    category = input("Enter category (e.g., Food, Salary, Rent): ").strip()
    description = input("Enter description (optional): ").strip()

    record = {
        "id": str(uuid.uuid4()),
        "date": date,
        "amount": amount,
        "type": transaction_type,
        "category": category,
        "description": description
    }
    
    data.append(record)
    save_data(data)
    print(f"{transaction_type.capitalize()} added successfully!")

def view_transactions(data):
    """Display all recorded transactions."""
    print("\n--- All Transactions ---")
    if not data:
        print("No transactions found.")
        return
        
    print(f"{'Date':<12} | {'Type':<8} | {'Amount':<10} | {'Category':<15} | {'Description'}")
    print("-" * 70)
    for record in data:
        print(f"{record['date']:<12} | {record['type']:<8} | ${record['amount']:<9.2f} | {record['category']:<15} | {record['description']}")

def show_monthly_summary(data):
    """Calculate and display total income, expenses, and balance."""
    print("\n--- Financial Summary ---")
    if not data:
        print("No transactions found to summarize.")
        return
        
    total_income = sum(item['amount'] for item in data if item['type'] == 'income')
    total_expense = sum(item['amount'] for item in data if item['type'] == 'expense')
    balance = total_income - total_expense
    
    print(f"Total Income:   ${total_income:.2f}")
    print(f"Total Expenses: ${total_expense:.2f}")
    print(f"Current Balance: ${balance:.2f}")
    
    print("\n--- Expenses by Category ---")
    expenses_by_category = {}
    for item in data:
        if item['type'] == 'expense':
            category = item['category']
            expenses_by_category[category] = expenses_by_category.get(category, 0) + item['amount']
            
    if expenses_by_category:
        for category, amount in expenses_by_category.items():
            print(f"{category:<15}: ${amount:.2f}")
    else:
        print("No expenses recorded yet.")

def show_charts(data):
    """Generate and display charts using Matplotlib."""
    if not MATPLOTLIB_AVAILABLE:
        print("\nMatplotlib is not installed. Please install it using 'pip install matplotlib' to view charts.")
        return

    expenses = [item for item in data if item['type'] == 'expense']
    
    if not expenses:
        print("\nNot enough expense data to generate charts.")
        return

    # Prepare data for category pie chart
    expenses_by_category = {}
    for item in expenses:
        category = item['category']
        expenses_by_category[category] = expenses_by_category.get(category, 0) + item['amount']
        
    categories = list(expenses_by_category.keys())
    amounts = list(expenses_by_category.values())
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Pie chart: Expenses by Category
    ax1.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    ax1.set_title("Expenses by Category")
    
    # Bar chart: Expenses by Category
    ax2.bar(categories, amounts, color='skyblue')
    ax2.set_title("Expenses Bar Chart")
    ax2.set_xlabel("Categories")
    ax2.set_ylabel("Amount ($)")
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    print("\nClose the chart window to return to the menu.")
    plt.show()

def main():
    """Main function to run the Finance Manager."""
    print("Welcome to Personal Finance Manager")
    
    data = load_data()
    
    while True:
        print("\n" + "="*30)
        print("           MAIN MENU")
        print("="*30)
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View All Transactions")
        print("4. Show Summary")
        print("5. Show Charts")
        print("6. Exit")
        print("="*30)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            add_transaction(data, 'income')
        elif choice == '2':
            add_transaction(data, 'expense')
        elif choice == '3':
            view_transactions(data)
        elif choice == '4':
            show_monthly_summary(data)
        elif choice == '5':
            show_charts(data)
        elif choice == '6':
            print("Exiting Personal Finance Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()
