import json
from pathlib import Path
from datetime import date

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.json"


def _init_db():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"expenses": []}, f, ensure_ascii=False, indent=2)


def load_db():
    _init_db()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_expense(amount, category, description, date_str=None, currency="BRL"):
    db = load_db()
    expenses = db.get("expenses", [])
    new_id = (expenses[-1]["id"] + 1) if expenses else 1

    if date_str is None:
        date_str = date.today().isoformat()

    expense = {
        "id": new_id,
        "amount": float(amount),
        "currency": currency,
        "category": category,
        "description": description,
        "date": date_str,
    }

    expenses.append(expense)
    db["expenses"] = expenses
    save_db(db)
    return expense


def get_expenses():
    return load_db().get("expenses", [])
