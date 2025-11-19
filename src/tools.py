from collections import defaultdict
from datetime import datetime
from .db import add_expense, get_expenses


def tool_add_expense(amount, category, description, date_str=None, currency="BRL"):
    """Adiciona uma despesa ao banco."""
    expense = add_expense(amount, category, description, date_str, currency)
    return {
        "status": "ok",
        "expense": expense,
        "message": (
            f"Despesa de {expense['amount']} {expense['currency']} "
            f"em {expense['description']} adicionada na categoria "
            f"{expense['category']} em {expense['date']}."
        ),
    }


def _in_period(e, year=None, month=None):
    if year is None and month is None:
        return True
    d = datetime.fromisoformat(e["date"])
    if year is not None and d.year != year:
        return False
    if month is not None and d.month != month:
        return False
    return True


def tool_get_top_category(year=None, month=None):
    """Retorna a categoria com maior gasto em um período."""
    expenses = get_expenses()
    if not expenses:
        return {"status": "empty", "message": "Nenhuma despesa registrada ainda."}

    totals = defaultdict(float)
    for e in expenses:
        if _in_period(e, year, month):
            totals[e["category"]] += float(e["amount"])

    if not totals:
        return {"status": "empty", "message": "Nenhuma despesa no período selecionado."}

    top_category = max(totals, key=totals.get)
    return {
        "status": "ok",
        "top_category": top_category,
        "amount": totals[top_category],
        "totals_by_category": dict(totals),
    }


def tool_get_summary(year=None, month=None):
    """Resumo por categoria em um período."""
    expenses = get_expenses()
    if not expenses:
        return {"status": "empty", "message": "Nenhuma despesa registrada ainda."}

    totals = defaultdict(float)
    for e in expenses:
        if _in_period(e, year, month):
            totals[e["category"]] += float(e["amount"])

    total_geral = sum(totals.values())

    if not totals:
        return {"status": "empty", "message": "Nenhuma despesa no período selecionado."}

    return {
        "status": "ok",
        "total": total_geral,
        "totals_by_category": dict(totals),
    }
