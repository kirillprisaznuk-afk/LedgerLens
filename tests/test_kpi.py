"""Tests for KPI calculations."""
from datetime import date
from analytics.kpi import break_even_point, burn_rate_and_runway


def test_break_even_point_basic_math():
    result = break_even_point(fixed_costs=8000, price_per_unit=50, variable_cost_per_unit=20)
    # 8000 / (50 - 20) = 266.67 units
    assert result["break_even_units"] == 266.7
    assert result["contribution_margin_per_unit"] == 30.0


def test_break_even_point_invalid_pricing():
    result = break_even_point(fixed_costs=1000, price_per_unit=10, variable_cost_per_unit=15)
    assert "error" in result


def test_burn_rate_returns_expected_keys():
    result = burn_rate_and_runway(date(2026, 8, 31), cash_on_hand=15000, lookback_months=3)
    expected_keys = {"period_analyzed", "monthly_burn_rate", "cash_on_hand", "runway_months"}
    assert expected_keys.issubset(result.keys())


def test_burn_rate_runway_is_none_when_profitable():
    result = burn_rate_and_runway(date(2026, 8, 31), cash_on_hand=15000, lookback_months=3)
    if result["monthly_burn_rate"] <= 0:
        assert result["runway_months"] is None