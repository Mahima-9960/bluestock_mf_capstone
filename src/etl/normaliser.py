import re
import pandas as pd

def normalize_ticker(ticker: any) -> str:
    """Standardizes asset tickers into consistent unique uppercase foreign key strings."""
    if pd.isna(ticker) or ticker is None:
        return ""
    return str(ticker).strip().upper()

def normalize_year(year_val: any) -> str:
    """
    Transforms messy variations of financial year endings (e.g., 'Mar 2024', 'Dec-12', '2015')
    into a standardized string index pattern (YYYY-MM). Default fallback to March ending.
    """
    if pd.isna(year_val) or year_val is None:
        return ""
    
    val_str = str(year_val).strip()
    
    # Check for direct YYYY string formatting (e.g., '2015')
    if re.match(r'^\d{4}$', val_str):
        return f"{val_str}-03" # Default to Indian standard FY March close
        
    months_map = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
        'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }
    
    # Pattern matching for variations like 'Mar 2024', 'Mar-2024', 'Mar-24', 'Sep-20'
    match = re.search(r'([A-Za-z]{3})[- ]*(\d{2,4})', val_str)
    if match:
        month_str = match.group(1).lower()[:3]
        year_digits = match.group(2)
        
        month_num = months_map.get(month_str, '03')
        if len(year_digits) == 2:
            # Handle standard century window break safely
            year_num = f"20{year_digits}" if int(year_digits) <= 50 else f"19{year_digits}"
        else:
            year_num = year_digits
            
        return f"{year_num}-{month_num}"
        
    return val_str