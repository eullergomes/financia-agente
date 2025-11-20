import json
from pathlib import Path
from datetime import date, timedelta

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


def _normalize_date(date_str: str) -> str:
    token = date_str.strip().lower()
    today = date.today()
    if token in {"hoje", "today"}:
        return today.isoformat()
    if token in {"ontem", "yesterday"}:
        return (today - timedelta(days=1)).isoformat()
    # mês passado -> primeiro dia do mês anterior (heurística simples)
    if token in {"mes passado", "mês passado"}:
        first_this_month = today.replace(day=1)
        prev_month_last_day = first_this_month - timedelta(days=1)
        return prev_month_last_day.replace(day=1).isoformat()
    # Já está em formato ISO? (YYYY-MM-DD) valida rápido
    if len(token) == 10 and token[4] == '-' and token[7] == '-':
        return token
    # fallback: hoje
    return today.isoformat()


def add_expense(amount, category, description, date_str=None, currency="BRL"):
    db = load_db()
    expenses = db.get("expenses", [])
    new_id = (expenses[-1]["id"] + 1) if expenses else 1

    if date_str is None:
        date_str = date.today().isoformat()
    else:
        date_str = _normalize_date(date_str)

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
