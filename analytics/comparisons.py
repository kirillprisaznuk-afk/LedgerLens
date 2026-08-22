"""Period-over-period comparison of P&L results.
Supports Month-over-Month, Quarter-over-Quarter, Year-over-Year.
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from analytics.pnl import get_pnl


def pct_change(old: float, new: float) -> float:
    if old == 0:
        return 0.0
    return round((new - old) / abs(old) * 100, 2)


def compare_periods(current_start: date, current_end: date, months_back: int) -> dict:
    """Compares the current period P&L against a prior period shifted back
    by `months_back` months (1 = MoM, 3 = QoQ, 12 = YoY).
    """
    prior_start = current_start - relativedelta(months=months_back)
    prior_end = current_end - relativedelta(months=months_back)

    current = get_pnl(current_start, current_end)
    prior = get_pnl(prior_start, prior_end)

    return {
        "current_period": current["period"],
        "prior_period": prior["period"],
        "income_change_pct": pct_change(prior["total_income"], current["total_income"]),
        "expense_change_pct": pct_change(prior["total_expenses"], current["total_expenses"]),
        "profit_change_pct": pct_change(prior["net_profit"], current["net_profit"]),
        "current": current,
        "prior": prior,
    }


if __name__ == "__main__":
    result = compare_periods(date(2026, 6, 1), date(2026, 6, 30), months_back=1)
    print(f"Current: {result['current_period']} | Prior: {result['prior_period']}")
    print(f"Income change: {result['income_change_pct']}%")
    print(f"Expense change: {result['expense_change_pct']}%")
    print(f"Profit change: {result['profit_change_pct']}%")