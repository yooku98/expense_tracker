# app.py - Flask Web App Version
from flask import Flask, render_template, request, redirect, jsonify
import csv
from datetime import datetime
import os

app = Flask(__name__)

EXPENSES_FILE = 'expenses.csv'


def read_expenses():
    """Read all expenses from CSV"""
    expenses = []
    try:
        with open(EXPENSES_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                expenses.append(row)
    except FileNotFoundError:
        pass
    return expenses

def add_expense(category, amount):
    """Add a new expense to CSV"""
    file_exists = os.path.isfile(EXPENSES_FILE)
    
    # Check if file exists AND has content
    write_header = not file_exists or os.path.getsize(EXPENSES_FILE) == 0

    with open(EXPENSES_FILE, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write header row once at the beginning
        if write_header:
            writer.writerow(["date", "category", "amount"])

        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M'), category, amount])

def get_summary():
    """Calculate spending by category"""
    expenses = read_expenses()
    summary = {}
    for expense in expenses:
        category = expense['category']
        amount = float(expense['amount'])
        summary[category] = summary.get(category, 0) + amount
    return summary

@app.route('/')
def index():
    """Home page showing all expenses"""
    expenses = read_expenses()
    summary = get_summary()
    total = sum(summary.values()) if summary else 0
    return render_template('index.html', expenses=expenses, summary=summary, total=total)

@app.route('/add', methods=['POST'])
def add():
    """Add new expense"""
    category = request.form.get('category')
    amount = request.form.get('amount')
    
    if category and amount:
        try:
            amount = float(amount)
            add_expense(category, amount)
        except ValueError:
            pass
    
    return redirect('/')

@app.route('/api/expenses')
def api_expenses():
    """API endpoint for expenses (optional - for charts)"""
    return jsonify(read_expenses())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)