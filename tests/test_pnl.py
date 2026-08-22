"""Tests for P&L calculations."""
from datetime import date
from analytics.pnl import get_pnl


def test_pnl_returns_expected_keys():
    result = get_pnl(date(2024, 9, 1), date(2026, 8, 31))
    expected_keys = {
        "period", "total_income", "total_expenses",
        "net_profit", "net_margin_pct",
        "income_breakdown", "expense_breakdown",
    }
    assert expected_keys.issubset(result.keys())


def test_pnl_net_profit_matches_income_minus_expenses():
    result = get_pnl(date(2024, 9, 1), date(2026, 8, 31))
    expected_profit = round(result["total_income"] - result["total_expenses"], 2)
    assert result["net_profit"] == expected_profit


def test_pnl_totals_are_non_negative():
    result = get_pnl(date(2024, 9, 1), date(2026, 8, 31))
    assert result["total_income"] >= 0
    assert result["total_expenses"] >= 0


def test_pnl_empty_period_returns_zero():
    result = get_pnl(date(2020, 1, 1), date(2020, 1, 31))
    assert result["total_income"] == 0
    assert result["total_expenses"] == 0
    assert result["net_profit"] == 0