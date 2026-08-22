"""Generates natural-language insights from P&L, KPI, comparison,
and anomaly data. Rule-based (no external LLM API), so the logic is fully
transparent and doesn't depend on internet access or paid services.
"""
from datetime import date
from analytics.pnl import get_pnl
from analytics.comparisons import compare_periods
from analytics.kpi import burn_rate_and_runway
from analytics.anomalies import detect_anomalies


def generate_insights(start_date: date, end_date: date, cash_on_hand: float) -> list:
    insights = []

    pnl = get_pnl(start_date, end_date)
    if pnl["net_profit"] < 0:
        insights.append(
            f"The company operated at a loss of €{abs(pnl['net_profit']):,.0f} "
            f"during {pnl['period']}, with a net margin of {pnl['net_margin_pct']}%."
        )
    else:
        insights.append(
            f"The company was profitable during {pnl['period']}, earning "
            f"€{pnl['net_profit']:,.0f} net profit ({pnl['net_margin_pct']}% margin)."
        )

    if pnl["expense_breakdown"]:
        top_category = max(pnl["expense_breakdown"], key=pnl["expense_breakdown"].get)
        top_amount = pnl["expense_breakdown"][top_category]
        share = (top_amount / pnl["total_expenses"] * 100) if pnl["total_expenses"] else 0
        insights.append(
            f"'{top_category}' is the largest expense category, accounting for "
            f"{share:.0f}% of total spending (€{top_amount:,.0f})."
        )

    try:
        mom = compare_periods(end_date.replace(day=1), end_date, months_back=1)
        if abs(mom["expense_change_pct"]) > 20:
            direction = "increased" if mom["expense_change_pct"] > 0 else "decreased"
            insights.append(
                f"Expenses {direction} by {abs(mom['expense_change_pct'])}% compared to "
                f"the previous month — this is a significant shift worth investigating."
            )
    except Exception:
        pass

    burn = burn_rate_and_runway(end_date, cash_on_hand=cash_on_hand, lookback_months=3)
    if burn["runway_months"] is not None:
        if burn["runway_months"] < 6:
            insights.append(
                f"At the current burn rate of €{burn['monthly_burn_rate']:,.0f}/month, "
                f"the company has only {burn['runway_months']} months of runway left — "
                f"consider reducing costs or raising funds soon."
            )
        else:
            insights.append(
                f"Current runway is {burn['runway_months']} months at the existing burn rate, "
                f"which provides a comfortable buffer."
            )

    anomalies = detect_anomalies()
    if not anomalies.empty:
        insights.append(
            f"Detected {len(anomalies)} unusual transaction(s) that deviate from typical "
            f"spending patterns in their category — review these for errors or fraud."
        )

    return insights


if __name__ == "__main__":
    results = generate_insights(date(2024, 9, 1), date(2026, 8, 31), cash_on_hand=15000)
    for i, insight in enumerate(results, 1):
        print(f"{i}. {insight}")