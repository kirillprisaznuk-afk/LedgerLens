"""FinOps dashboard - main Streamlit entry point."""
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics.pnl import get_pnl
from analytics.cashflow import get_cash_flow
from analytics.comparisons import compare_periods
from analytics.kpi import burn_rate_and_runway
from analytics.forecast import forecast_series
from analytics.anomalies import detect_anomalies
from analytics.insights import generate_insights

st.set_page_config(page_title="FinOps Dashboard", layout="wide")
st.title("FinOps — Financial Intelligence Dashboard")

st.sidebar.header("Period selection")
start_date = st.sidebar.date_input("Start date", value=date(2024, 9, 1))
end_date = st.sidebar.date_input("End date", value=date(2026, 8, 31))
cash_on_hand = st.sidebar.number_input("Current cash on hand (€)", value=15000, step=500)

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

pnl = get_pnl(start_date, end_date)
cash_flow = get_cash_flow(start_date, end_date)
burn = burn_rate_and_runway(end_date, cash_on_hand=cash_on_hand, lookback_months=3)

tab_overview, tab_ai = st.tabs(["Overview", "AI Insights"])

with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income", f"€{pnl['total_income']:,.0f}")
    col2.metric("Total Expenses", f"€{pnl['total_expenses']:,.0f}")
    col3.metric("Net Profit", f"€{pnl['net_profit']:,.0f}", f"{pnl['net_margin_pct']}% margin")
    col4.metric(
        "Runway",
        f"{burn['runway_months']} months" if burn["runway_months"] else "Profitable",
    )

    st.divider()

    st.subheader("Expense Breakdown by Category")
    if pnl["expense_breakdown"]:
        exp_df = pd.DataFrame(
            list(pnl["expense_breakdown"].items()), columns=["Category", "Amount"]
        ).sort_values("Amount", ascending=False)
        st.plotly_chart(px.bar(exp_df, x="Category", y="Amount", color="Category"), use_container_width=True)
    else:
        st.info("No expense data for this period.")

    st.subheader("Income Breakdown by Category")
    if pnl["income_breakdown"]:
        inc_df = pd.DataFrame(list(pnl["income_breakdown"].items()), columns=["Category", "Amount"])
        st.plotly_chart(px.pie(inc_df, names="Category", values="Amount"), use_container_width=True)
    else:
        st.info("No income data for this period.")

    st.subheader("Cash Flow by Account")
    cf_df = pd.DataFrame(list(cash_flow["by_account"].items()), columns=["Account", "Net Flow"])
    st.dataframe(cf_df, use_container_width=True)

    st.subheader("Month-over-Month Comparison")
    mom = compare_periods(end_date.replace(day=1), end_date, months_back=1)
    c1, c2, c3 = st.columns(3)
    c1.metric("Income change", f"{mom['income_change_pct']}%")
    c2.metric("Expense change", f"{mom['expense_change_pct']}%")
    c3.metric("Profit change", f"{mom['profit_change_pct']}%")

with tab_ai:
    st.subheader("Automated Insights")
    insights = generate_insights(start_date, end_date, cash_on_hand=cash_on_hand)
    for insight in insights:
        st.write(f"- {insight}")

    st.divider()

    st.subheader("Revenue & Expense Forecast (next 3 months)")
    income_fc = forecast_series("income", periods_ahead=3)
    expense_fc = forecast_series("expense", periods_ahead=3)

    if "error" not in income_fc:
        fig = go.Figure()
        hist_dates = list(income_fc["history"].keys())
        hist_vals = list(income_fc["history"].values())
        fut_dates = list(income_fc["forecast"].keys())
        fut_vals = list(income_fc["forecast"].values())

        fig.add_trace(go.Scatter(x=hist_dates, y=hist_vals, name="Income (actual)", mode="lines"))
        fig.add_trace(go.Scatter(x=fut_dates, y=fut_vals, name="Income (forecast)", mode="lines", line=dict(dash="dash")))

        if "error" not in expense_fc:
            hist_dates_e = list(expense_fc["history"].keys())
            hist_vals_e = list(expense_fc["history"].values())
            fut_dates_e = list(expense_fc["forecast"].keys())
            fut_vals_e = list(expense_fc["forecast"].values())
            fig.add_trace(go.Scatter(x=hist_dates_e, y=hist_vals_e, name="Expenses (actual)", mode="lines"))
            fig.add_trace(go.Scatter(x=fut_dates_e, y=fut_vals_e, name="Expenses (forecast)", mode="lines", line=dict(dash="dash")))

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(income_fc["error"])

    st.divider()

    st.subheader("Detected Anomalies")
    anomalies = detect_anomalies()
    if anomalies.empty:
        st.success("No anomalies detected in the current dataset.")
    else:
        st.dataframe(
            anomalies[["date", "description", "amount", "category"]],
            use_container_width=True,
        )