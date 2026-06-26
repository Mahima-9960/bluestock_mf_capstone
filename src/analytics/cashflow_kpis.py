from typing import Optional, Tuple

def compute_fcf(operating_activity: float, investing_activity: float) -> float:
    return operating_activity + investing_activity

def score_cfo_quality(cfo_avg_5yr: float, pat_avg_5yr: float) -> Tuple[Optional[float], str]:
    if pat_avg_5yr == 0: return None, "Accrual Risk"
    ratio = cfo_avg_5yr / pat_avg_5yr
    return ratio, "High Quality" if ratio > 1.0 else ("Moderate" if ratio >= 0.5 else "Accrual Risk")

def classify_capex_intensity(investing_activity: float, sales: float) -> Tuple[Optional[float], str]:
    if sales == 0: return None, "Unknown"
    intensity = (abs(investing_activity) / sales) * 100
    return intensity, "Asset Light" if intensity < 3.0 else ("Moderate" if intensity <= 8.0 else "Capital Intensive")

def classify_capital_allocation(cfo: float, cfi: float, cff: float, cfo_pat_ratio: float) -> str:
    pat = ("+" if cfo >= 0 else "-", "+" if cfi >= 0 else "-", "+" if cff >= 0 else "-")
    if pat == ("+", "-", "-"): return "Shareholder Returns" if cfo_pat_ratio > 1.0 else "Reinvestor"
    if pat == ("+", "+", "-"): return "Liquidating Assets"
    if pat == ("-", "+", "+"): return "Distress Signal"
    if pat == ("-", "-", "+"): return "Growth Funded by Debt"
    if pat == ("+", "+", "+"): return "Cash Accumulator"
    if pat == ("-", "-", "-"): return "Pre-Revenue"
    return "Mixed"