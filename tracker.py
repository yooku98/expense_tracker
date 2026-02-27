import csv
import os
from datetime import datetime

# FIX: path is now always relative to this script's location, not the CWD
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.csv")


def initialize_file():
    """Create the CSV with a header row if it does not already exist."""
    try:
        with open(FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "amount"])
    except FileExistsError:
        pass


def add_expense():
    # FIX: strip whitespace so " Food" and "Food" are the same category
    category = input("Enter category (food, transport, etc): ").strip().title()
    if not category:
        print("Category cannot be empty.")
        return

    # FIX: loop until the user enters a valid positive number instead of crashing
    while True:
        try:
            amount = float(input("Enter amount: GHS "))
            if amount <= 0:
                print("Amount must be greater than zero. Try again.")
                continue
            break
        except ValueError:
            print("Invalid amount — please enter a number (e.g. 25.50).")

    date = datetime.now().strftime("%Y-%m-%d")

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, amount])

    print(f"Expense added: {category} — GHS {amount:,.2f}")


def view_expenses():
    # FIX: graceful error if file is missing or empty
    try:
        with open(FILE, "r") as f:
            # FIX: use DictReader so columns are accessed by name, not position
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            print("No expenses recorded yet.")
            return

        # FIX: formatted output instead of raw Python list
        print(f"\n{'Date':<12}  {'Category':<20}  {'Amount':>10}")
        print("-" * 46)
        for row in rows:
            try:
                amount = float(row["amount"])
                print(f"{row['date']:<12}  {row['category']:<20}  GHS {amount:>8,.2f}")
            except (ValueError, KeyError):
                print(f"  [malformed row: {row}]")

    except FileNotFoundError:
        print("No expense file found. Add an expense first.")
    except Exception as e:
        print(f"Error reading expenses: {e}")


def summary():
    # FIX: graceful error handling throughout
    try:
        with open(FILE, "r") as f:
            # FIX: DictReader — no more fragile tuple unpacking that crashes on bad rows
            reader = csv.DictReader(f)
            totals = {}
            skipped = 0
            for row in reader:
                try:
                    category = row["category"]
                    amount   = float(row["amount"])
                    totals[category] = totals.get(category, 0) + amount
                except (ValueError, KeyError):
                    skipped += 1  # malformed row — skip silently, report at end

    except FileNotFoundError:
        print("No expense file found. Add an expense first.")
        return
    except Exception as e:
        print(f"Error reading expenses: {e}")
        return

    if not totals:
        print("No expenses recorded yet.")
        return

    print("\n=== Summary by Category ===")
    for category, total in sorted(totals.items()):
        # FIX: formatted with thousands separator and 2 decimal places
        print(f"  {category:<20}  GHS {total:>10,.2f}")

    # FIX: grand total added
    print("-" * 38)
    print(f"  {'TOTAL':<20}  GHS {sum(totals.values()):>10,.2f}")

    if skipped:
        print(f"\n  ({skipped} malformed row(s) were skipped)")


def delete_expense():
    """FIX: delete functionality — lists expenses and lets the user pick one to remove."""
    try:
        with open(FILE, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print("No expense file found.")
        return

    if not rows:
        print("No expenses to delete.")
        return

    print(f"\n{'#':<4}  {'Date':<12}  {'Category':<20}  {'Amount':>10}")
    print("-" * 52)
    for i, row in enumerate(rows, 1):
        try:
            amount = float(row["amount"])
            print(f"{i:<4}  {row['date']:<12}  {row['category']:<20}  GHS {amount:>8,.2f}")
        except (ValueError, KeyError):
            print(f"{i:<4}  [malformed row]")

    while True:
        choice = input("\nEnter row number to delete (or 0 to cancel): ").strip()
        try:
            idx = int(choice)
        except ValueError:
            print("Please enter a number.")
            continue
        if idx == 0:
            print("Cancelled.")
            return
        if 1 <= idx <= len(rows):
            removed = rows.pop(idx - 1)
            # Rewrite the file without the deleted row
            with open(FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "category", "amount"])
                writer.writeheader()
                writer.writerows(rows)
            print(f"Deleted: {removed['category']} — GHS {float(removed['amount']):,.2f}")
            return
        print(f"Please enter a number between 1 and {len(rows)}.")


def menu():
    initialize_file()
    while True:
        print("\n=== Expense Tracker ===")
        print("1. Add expense")
        print("2. View expenses")
        print("3. Summary by category")
        print("4. Delete an expense")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            summary()
        elif choice == "4":
            delete_expense()
        elif choice == "5":
            break
        else:
            print("Invalid choice — enter 1 to 5.")


if __name__ == "__main__":
    menu()