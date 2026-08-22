"""KPI calculations built on top of P&L and Cash Flow data.
- Gross/Net margin
- Burn rate & runway
- Break-even point
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from analytics.pnl import get_pnl


def gross_net_margin(start_date: date, end_date: date) -> dict:
    pnl = get_pnl(start_date, end_date)
    income = pnl["total_income"]
    expenses = pnl["total_expenses"]

    # Gross margin here treats all direct costs as "cost of sales" is not
    # separated in this simplified model, so gross margin == net margin
    # unless a COGS category is introduced later. Kept as its own function
    # so it's easy to refine once COGS categories exist.
    net_margin_pct = pnl["net_margin_pct"]

    return {
        "period": pnl["period"],
        "net_margin_pct": net_margin_pct,
        "net_profit": pnl["net_profit"],
    }


def burn_rate_and_runway(end_date: date, cash_on_hand: float, lookback_months: int = 3) -> dict:
    """Burn rate = average monthly net loss over the lookback window.
    Runway = how many months the current cash balance can sustain that burn.
    """
    start_date = end_date - relativedelta(months=lookback_months)
    pnl = get_pnl(start_date, end_date)

    net_over_window = pnl["net_profit"]
    monthly_burn = -(net_over_window / lookback_months)  # positive = burning cash

    if monthly_burn <= 0:
        runway_months = None  # company is profitable, no burn
    else:
        runway_months = round(cash_on_hand / monthly_burn, 1)

    return {
        "period_analyzed": pnl["period"],
        "monthly_burn_rate": round(monthly_burn, 2),
        "cash_on_hand": cash_on_hand,
        "runway_months": runway_months,
    }


def break_even_point(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> dict:
    """Classic break-even formula:
    units needed = fixed costs / (price - variable cost per unit)
    """
    contribution_margin = price_per_unit - variable_cost_per_unit
    if contribution_margin <= 0:
        return {"error": "Price must exceed variable cost per unit."}

    units_needed = fixed_costs / contribution_margin
    revenue_needed = units_needed * price_per_unit

    return {
        "fixed_costs": fixed_costs,
        "contribution_margin_per_unit": round(contribution_margin, 2),
        "break_even_units": round(units_needed, 1),
        "break_even_revenue": round(revenue_needed, 2),
    }


if __name__ == "__main__":
    print("--- Margin ---")
    print(gross_net_margin(date(2024, 9, 1), date(2026, 8, 31)))

    print("\n--- Burn Rate & Runway ---")
    print(burn_rate_and_runway(date(2026, 8, 31), cash_on_hand=15000, lookback_months=3))

    print("\n--- Break-even Point ---")
    print(break_even_point(fixed_costs=8000, price_per_unit=50, variable_cost_per_unit=20))