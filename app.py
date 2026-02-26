from flask import Flask, render_template, request, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timezone
from decimal import Decimal
import os

app = Flask(__name__)

# ===============================
# SECRET KEY (required for CSRF & flash)
# ===============================
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")

# ===============================
# POSTGRES DATABASE CONFIG
# ===============================
# FIX: credentials moved out of source code — set DATABASE_URL as an environment
# variable in your Render dashboard (Settings → Environment → Add Environment Variable).
# Never commit credentials to source control; rotate the old password immediately.
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Add it in your Render dashboard under Environment Variables."
    )

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# FIX: CSRF protection added — all POST forms must include {{ csrf_token() }} in their template
csrf = CSRFProtect(app)

# ===============================
# DATABASE MODEL
# ===============================
class Expense(db.Model):
    id       = db.Column(db.Integer,      primary_key=True)
    # FIX: datetime.utcnow() deprecated in Python 3.12+ → use datetime.now(timezone.utc)
    date     = db.Column(db.DateTime(timezone=True),
                         default=lambda: datetime.now(timezone.utc))
    category = db.Column(db.String(50),   nullable=False)
    # FIX: db.Float has floating-point rounding errors with money → use Numeric(10,2)
    amount   = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            "id":       self.id,
            "date":     self.date.strftime("%Y-%m-%d %H:%M"),
            "category": self.category,
            # Numeric → float for JSON serialisation
            "amount":   float(self.amount),
        }

# FIX: db.create_all() is fine for prototypes; for production schema migrations
# switch to Flask-Migrate: https://flask-migrate.readthedocs.io/
with app.app_context():
    db.create_all()

# ===============================
# ROUTES
# ===============================

@app.route("/")
def index():
    # FIX: replaced .all() with .paginate() to avoid loading every row into memory.
    # Page size of 50 is a safe default; adjust as needed.
    page     = request.args.get("page", 1, type=int)
    per_page = 50
    pagination = Expense.query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    expenses = pagination.items

    # Summary calculated over all rows for the chart/totals widget.
    # If the table grows very large, move this to a SQL GROUP BY query.
    all_expenses = Expense.query.all()
    summary = {}
    for e in all_expenses:
        summary[e.category] = summary.get(e.category, 0) + float(e.amount)

    total = sum(summary.values()) if summary else 0

    return render_template(
        "index.html",
        expenses=expenses,
        pagination=pagination,
        summary=summary,
        total=total,
    )


@app.route("/add", methods=["POST"])
def add():
    category  = request.form.get("category", "").strip()
    amount_raw = request.form.get("amount", "").strip()

    # FIX: validate category is non-empty
    if not category:
        flash("Category cannot be empty.", "error")
        return redirect("/")

    # FIX: validate amount is a valid positive number; give user visible feedback
    try:
        amount = Decimal(amount_raw)
    except Exception:
        flash("Invalid amount — please enter a number (e.g. 25.50).", "error")
        return redirect("/")

    if amount <= 0:
        flash("Amount must be greater than zero.", "error")
        return redirect("/")

    try:
        new_expense = Expense(category=category, amount=amount)
        db.session.add(new_expense)
        db.session.commit()
        flash(f"Expense added: {category} — GHS {amount:,.2f}", "success")
    except Exception as e:
        db.session.rollback()
        # FIX: user now sees the error rather than a silent redirect
        flash(f"Could not save expense: {e}", "error")

    return redirect("/")


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    """FIX: delete route added so users can remove individual expenses from the UI."""
    expense = Expense.query.get_or_404(expense_id)
    try:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Could not delete expense: {e}", "error")
    return redirect("/")


@app.route("/api/expenses")
def api_expenses():
    # FIX: simple token-based auth — set API_TOKEN env var; pass as ?token=... or
    # Authorization: Bearer <token> header.
    # For production, replace with proper OAuth / session auth.
    api_token = os.environ.get("API_TOKEN")
    if api_token:
        provided = (
            request.args.get("token")
            or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        )
        if provided != api_token:
            return jsonify({"error": "Unauthorized"}), 401

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])


if __name__ == "__main__":
    # FIX: debug mode now controlled by environment variable, not hardcoded True
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
    # NOTE: for production on Render, use gunicorn instead of app.run():
    #   Procfile:  web: gunicorn app:app