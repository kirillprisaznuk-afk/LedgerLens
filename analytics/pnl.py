"""Profit & Loss calculations.
Aggregates transactions by category/type over a given date range.
"""
from datetime import date
from sqlalchemy import func
from data.database import get_session
from data.models import Transaction, Category


def get_pnl(start_date: date, end_date: date) -> dict:
    """Returns a P&L breakdown for the given period:
    - total income
    - total expenses
    - net profit
    - expense/income breakdown by category
    """
    session = get_session()

    rows = (
        session.query(
            Category.name,
            Category.type,
            func.sum(Transaction.amount).label("total"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.date >= start_date, Transaction.date <= end_date)
        .group_by(Category.name, Category.type)
        .all()
    )

    session.close()

    income_breakdown = {}
    expense_breakdown = {}
    total_income = 0.0
    total_expenses = 0.0

    for name, cat_type, total in rows:
        total = float(total)
        if cat_type == "income":
            income_breakdown[name] = total
            total_income += total
        else:
            expense_breakdown[name] = abs(total)
            total_expenses += abs(total)

    net_profit = total_income - total_expenses
    margin = (net_profit / total_income * 100) if total_income else 0.0

    return {
        "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "net_margin_pct": round(margin, 2),
        "income_breakdown": income_breakdown,
        "expense_breakdown": expense_breakdown,
    }


if __name__ == "__main__":
    result = get_pnl(date(2024, 9, 1), date(2026, 8, 31))
    for key, value in result.items():
        print(f"{key}: {value}")
