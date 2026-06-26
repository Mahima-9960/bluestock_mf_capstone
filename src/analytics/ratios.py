import math
from typing import Optional, Tuple

def compute_npm(net_profit: float, sales: float) -> Optional[float]:
    if sales == 0: return None
    return (net_profit / sales) * 100

def compute_opm(operating_profit: float, sales: float) -> Optional[float]:
    if sales == 0: return None
    return (operating_profit / sales) * 100

def compute_roe(net_profit: float, equity_capital: float, reserves: float) -> Optional[float]:
    denominator = equity_capital + reserves
    if denominator <= 0: return None
    return (net_profit / denominator) * 100

def compute_roce(operating_profit: float, other_income: float, equity_capital: float, reserves: float, borrowings: float) -> Optional[float]:
    ebit = operating_profit + other_income
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0: return None
    return (ebit / capital_employed) * 100

def compute_roa(net_profit: float, total_assets: float) -> Optional[float]:
    if total_assets == 0: return None
    return (net_profit / total_assets) * 100

def compute_debt_to_equity(borrowings: float, equity_capital: float, reserves: float) -> Tuple[Optional[float], bool]:
    if borrowings == 0: return 0.0, False
    equity = equity_capital + reserves
    if equity <= 0: return None, False
    return (borrowings / equity), False

def compute_interest_coverage(operating_profit: float, other_income: float, interest: float) -> Tuple[Optional[float], str, bool]:
    ebit = operating_profit + other_income
    if interest == 0: return None, "Debt Free", False
    icr = ebit / interest
    return icr, "", (icr < 1.5)

def compute_net_debt(borrowings: float, investments: float) -> float:
    return borrowings - investments

def compute_asset_turnover(sales: float, total_assets: float) -> Optional[float]:
    if total_assets == 0: return None
    return sales / total_assets