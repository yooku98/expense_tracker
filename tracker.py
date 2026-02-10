import csv
from datetime import datetime

FILE = "expenses.csv"

# Ensure file exists
def initialize_file():
    try:
        with open(FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "amount"])
    except FileExistsError:
        pass

def add_expense():
    category = input("Enter category (food, transport, etc): ").title()
    amount = float(input("Enter amount: "))
    date = datetime.now().strftime("%Y-%m-%d")

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, amount])

    print("Expense added!")

def view_expenses():
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            print(row)

def summary():
    totals = {}
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for _, category, amount in reader:
            amount = float(amount)
            totals[category] = totals.get(category, 0) + amount

    for category, total in totals.items():
        print(f"{category}: GHS {total}")

def menu():
    initialize_file()
    while True:
        print("\n=== Expense Tracker ===")
        print("1. Add expense")
        print("2. View expenses")
        print("3. Summary by category")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            summary()
        elif choice == "4":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    menu()