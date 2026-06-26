from typing import Optional, Tuple

def compute_cagr(start_val: float, end_val: float, n_years: int) -> Tuple[Optional[float], str]:
    if n_years <= 0: return None, "INSUFFICIENT"
    if start_val == 0: return None, "ZERO_BASE"
    if start_val > 0 and end_val <= 0: return None, "DECLINE_TO_LOSS"
    if start_val < 0 and end_val > 0: return None, "TURNAROUND"
    if start_val < 0 and end_val < 0: return None, "BOTH_NEGATIVE"
    try:
        ratio = end_val / start_val
        if ratio <= 0: return None, "INVALID_RATIO"
        return round(((ratio) ** (1 / n_years) - 1) * 100, 2), "NORMAL"
    except Exception:
        return None, "ERROR"