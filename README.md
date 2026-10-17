# Expense Tracker

A personal expense tracker with two front ends that share the same idea: log spending by category, then see where the money goes.

1. **Web app** (`app.py`) — Flask + PostgreSQL dashboard showing spending by category and all expenses, plus a JSON API.
2. **CLI** (`tracker.py`) — terminal menu that stores expenses in a local `expenses.csv`. It can be packaged as a standalone Windows `.exe` with PyInstaller.

Amounts are in Ghana cedis (GHS).

**Live demo:** none yet. The Flask app needs a Python host and a Postgres database (Render, Railway or Fly.io). GitHub Pages can only serve static files, so the Pages URL just shows this README.

## Web app

- Dashboard (`/`): spending-by-category summary, grand total, and a table of all expenses, with a dark/light toggle
- `POST /add` (category + amount, validated) and `POST /delete/<id>` routes
- `GET /api/expenses` returns all expenses as JSON. If `API_TOKEN` is set, it also requires `?token=` or `Authorization: Bearer <token>`

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | yes | PostgreSQL connection string (the app refuses to start without it) |
| `SECRET_KEY` | yes in production | Flask session/CSRF key |
| `API_TOKEN` | no | Protects `/api/expenses` |

**Known gap:** the dashboard template has no add/delete forms yet, so new expenses can't be entered from the web UI. `CSRFProtect` is on, so any form added later must include `{{ csrf_token() }}`. Calling the POST routes without a token returns 400. The CLI stores data in its own CSV and does not share the web app's database.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/expenses
export SECRET_KEY=change-me
flask --app app run
```

Tables are created on startup (`db.create_all()`). For production, run it with `gunicorn app:app`.

## CLI

```bash
python tracker.py
```

The menu offers: add an expense, view all, summary by category, delete, exit. Data is saved to `expenses.csv` next to the script.

Build a single-file executable:

```bash
pip install pyinstaller
pyinstaller tracker.spec      # output in dist/
```

## Structure

```
app.py              Flask web app (model, routes, JSON API)
templates/index.html  Dashboard template
tracker.py          CLI version (CSV storage)
tracker.spec        PyInstaller build spec for the CLI
requirements.txt    Web app dependencies
```

`build/` and `dist/` (PyInstaller output) are gitignored. Build the executable locally, or attach it to a GitHub Release, instead of committing it.
