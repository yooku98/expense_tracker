from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ===============================
# POSTGRES DATABASE CONFIG
# ===============================
DATABASE_URL = "postgresql+psycopg://auto:uZuWns9xyNjXIhSpvpPj8N68T7kWwd79@dpg-d66u910gjchc738hn1p0-a/expense_tracker_yc0e"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ===============================
# DATABASE MODEL
# ===============================
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M"),
            "category": self.category,
            "amount": self.amount,
        }

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# ===============================
# ROUTES
# ===============================

@app.route("/")
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()

    summary = {}
    for e in expenses:
        summary[e.category] = summary.get(e.category, 0) + e.amount

    total = sum(summary.values()) if summary else 0

    return render_template("index.html", expenses=expenses, summary=summary, total=total)


@app.route("/add", methods=["POST"])
def add():
    category = request.form.get("category")
    amount = request.form.get("amount")

    if category and amount:
        try:
            amount = float(amount)
            new_expense = Expense(category=category, amount=amount)
            db.session.add(new_expense)
            db.session.commit()
        except Exception as e:
            print("Error adding expense:", e)

    return redirect("/")


@app.route("/api/expenses")
def api_expenses():
    expenses = Expense.query.all()
    return jsonify([e.to_dict() for e in expenses])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)