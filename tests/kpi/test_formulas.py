# tests/kpi/test_formulas.py
import pytest
from src.analytics.ratios import compute_npm, compute_opm, compute_roe, compute_debt_to_equity, compute_interest_coverage
from src.analytics.cagr import compute_cagr
from src.analytics.cashflow_kpis import score_cfo_quality, classify_capex_intensity

# === DAY 08: Profitability Ratio Tests ===
def test_npm_normal():
    assert compute_npm(15, 100) == 15.0

def test_npm_zero_sales():
    assert compute_npm(15, 0) is None

def test_opm_normal():
    assert compute_opm(20, 100) == 20.0

def test_roe_normal():
    assert compute_roe(20, 50, 50) == 20.0

def test_roe_negative_equity():
    assert compute_roe(20, -10, -5) is None

# === DAY 09: Leverage & Efficiency Tests ===
def test_debt_to_equity_normal():
    ratio, _ = compute_debt_to_equity(50, 50, 50)
    assert ratio == 0.5

def test_debt_to_equity_zero_borrowings():
    ratio, _ = compute_debt_to_equity(0, 50, 50)
    assert ratio == 0.0

def test_icr_normal():
    icr, label, warn = compute_interest_coverage(30, 10, 10)
    assert icr == 4.0
    assert not warn

def test_icr_debt_free():
    icr, label, warn = compute_interest_coverage(30, 10, 0)
    assert icr is None
    assert label == "Debt Free"

def test_icr_warning_threshold():
    icr, label, warn = compute_interest_coverage(10, 2, 10)
    assert icr == 1.2
    assert warn

# === DAY 10: CAGR Engine Flag Tests ===
def test_cagr_normal():
    val, flag = compute_cagr(100, 144, 2)
    assert val == 20.0
    assert flag == "NORMAL"

def test_cagr_insufficient_years():
    val, flag = compute_cagr(100, 144, 0)
    assert val is None
    assert flag == "INSUFFICIENT"

def test_cagr_zero_base():
    val, flag = compute_cagr(0, 144, 5)
    assert val is None
    assert flag == "ZERO_BASE"

def test_cagr_decline_to_loss():
    val, flag = compute_cagr(100, -20, 3)
    assert val is None
    assert flag == "DECLINE_TO_LOSS"

def test_cagr_turnaround():
    val, flag = compute_cagr(-50, 100, 3)
    assert val is None
    assert flag == "TURNAROUND"

def test_cagr_both_negative():
    val, flag = compute_cagr(-50, -10, 3)
    assert val is None
    assert flag == "BOTH_NEGATIVE"

# === DAY 11: Cash Flow KPI Tests ===
def test_cfo_quality_high():
    ratio, label = score_cfo_quality(120, 100)
    assert ratio == 1.2
    assert label == "High Quality"

def test_cfo_quality_risk():
    ratio, label = score_cfo_quality(30, 100)
    assert label == "Accrual Risk"

def test_capex_intensity_asset_light():
    intensity, label = classify_capex_intensity(-2, 100)
    assert intensity == 2.0
    assert label == "Asset Light"

def test_capex_intensity_heavy():
    intensity, label = classify_capex_intensity(-12, 100)
    assert label == "Capital Intensive"