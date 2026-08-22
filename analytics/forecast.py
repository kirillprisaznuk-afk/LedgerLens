"""Forecasts future income/expenses using a simple time series model (ARIMA).
Aggregates historical transactions into monthly totals, then projects forward.
"""
from datetime import date
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from data.database import get_session
from data.models import Transaction, Category


def _monthly_series(category_type: str) -> pd.Series:
    """Builds a monthly time series of totals for 'income' or 'expense'."""
    session = get_session()
    rows = (
        session.query(Transaction.date, Transaction.amount, Category.type)
        .join(Category, Transaction.category_id == Category.id)
        .filter(Category.type == category_type)
        .all()
    )
    session.close()

    df = pd.DataFrame(rows, columns=["date", "amount", "type"])
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].abs()
    df = df.set_index("date").resample("MS")["amount"].sum()
    return df


def forecast_series(category_type: str, periods_ahead: int = 3) -> dict:
    """Fits an ARIMA(1,1,1) model on monthly totals and forecasts forward.
    ARIMA(1,1,1) is a reasonable general-purpose default for short business
    time series without needing to manually tune parameters.
    """
    series = _monthly_series(category_type)

    if len(series) < 6:
        return {"error": "Not enough historical data to forecast (need 6+ months)."}

    model = ARIMA(series, order=(1, 1, 1))
    fitted = model.fit()
    forecast_result = fitted.forecast(steps=periods_ahead)

    history = {str(k.date()): round(v, 2) for k, v in series.items()}
    future = {str(k.date()): round(v, 2) for k, v in forecast_result.items()}

    return {
        "category_type": category_type,
        "history": history,
        "forecast": future,
    }


if __name__ == "__main__":
    print("--- Income Forecast ---")
    income_fc = forecast_series("income", periods_ahead=3)
    print(income_fc.get("forecast", income_fc.get("error")))

    print("\n--- Expense Forecast ---")
    expense_fc = forecast_series("expense", periods_ahead=3)
    print(expense_fc.get("forecast", expense_fc.get("error")))