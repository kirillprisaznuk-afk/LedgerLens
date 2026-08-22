"""Cash Flow calculation.
Unlike P&L (which shows profitability), this shows actual cash movement
per account over a period - critical because profit and cash are not the same thing.
"""
from datetime import date
from sqlalchemy import func
from data.database import get_session
from data.models import Transaction, Account


def get_cash_flow(start_date: date, end_date: date) -> dict:
    session = get_session()

    rows = (
        session.query(
            Account.name,
            func.sum(Transaction.amount).label("net_flow"),
        )
        .join(Account, Transaction.account_id == Account.id)
        .filter(Transaction.date >= start_date, Transaction.date <= end_date)
        .group_by(Account.name)
        .all()
    )

    session.close()

    by_account = {name: round(float(flow), 2) for name, flow in rows}
    total_net_cash_flow = round(sum(by_account.values()), 2)

    inflow = sum(v for v in by_account.values() if v > 0)
    outflow = sum(v for v in by_account.values() if v < 0)

    return {
        "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "total_net_cash_flow": total_net_cash_flow,
        "total_inflow": round(inflow, 2),
        "total_outflow": round(outflow, 2),
        "by_account": by_account,
    }


if __name__ == "__main__":
    result = get_cash_flow(date(2024, 9, 1), date(2026, 8, 31))
    for key, value in result.items():
        print(f"{key}: {value}")