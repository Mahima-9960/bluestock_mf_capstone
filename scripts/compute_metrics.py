# scripts/compute_metrics.py
import os
import sqlite3
import csv
import pandas as pd
from src.analytics.ratios import (compute_npm, compute_opm, compute_roe, compute_roce, 
                                   compute_roa, compute_debt_to_equity, compute_interest_coverage, 
                                   compute_net_debt, compute_asset_turnover)
from src.analytics.cagr import compute_cagr
from src.analytics.cashflow_kpis import compute_fcf, score_cfo_quality, classify_capex_intensity, classify_capital_allocation

def get_db_connection():
    # Force the engine to target your active Sprint 1 Nifty100 database
    target_path = "db/nifty100.db"
    if os.path.exists(target_path):
        return sqlite3.connect(target_path)
    raise FileNotFoundError(f"Could not locate the populated database at {target_path}")

def run_ratio_engine():
    print("🚀 Running Sprint 2 Financial Ratio Engine Engine...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create target table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_ratios (
        company_id TEXT, year TEXT, net_profit_margin_pct REAL, operating_profit_margin_pct REAL,
        return_on_equity_pct REAL, debt_to_equity REAL, interest_coverage REAL, icr_label TEXT,
        asset_turnover REAL, free_cash_flow_cr REAL, capex_cr REAL, earnings_per_share REAL,
        book_value_per_share REAL, dividend_payout_ratio_pct REAL, total_debt_cr REAL,
        cash_from_operations_cr REAL, revenue_cagr_5yr REAL, pat_cagr_5yr REAL, eps_cagr_5yr REAL,
        composite_quality_score REAL, high_leverage_flag INTEGER, PRIMARY KEY (company_id, year)
    );""")

    # Pull baseline dataset records into memory
    df_pl = pd.read_sql_query("SELECT * FROM profitandloss", conn)
    df_bs = pd.read_sql_query("SELECT * FROM balancesheet", conn)
    df_cf = pd.read_sql_query("SELECT * FROM cashflow", conn)
    df_sec = pd.read_sql_query("SELECT * FROM sectors", conn)
    
    companies = df_pl['company_id'].unique()
    capital_allocations = []
    edge_cases = []
    ratio_rows = []

    sector_map = dict(zip(df_sec['company_id'], df_sec['broad_sector']))

    for comp in companies:
        c_pl = df_pl[df_pl['company_id'] == comp].sort_values('year')
        c_bs = df_bs[df_bs['company_id'] == comp].sort_values('year')
        c_cf = df_cf[df_cf['company_id'] == comp].sort_values('year')
        sector = sector_map.get(comp, "Unknown")

        years = c_pl['year'].unique()
        for idx, yr in enumerate(years):
            r_pl = c_pl[c_pl['year'] == yr]
            r_bs = c_bs[c_bs['year'] == yr]
            r_cf = c_cf[c_cf['year'] == yr]

            if r_pl.empty or r_bs.empty:
                continue

            # Core Values Extractions
            sales = float(r_pl['sales'].values[0] or 0)
            net_profit = float(r_pl['net_profit'].values[0] or 0)
            op = float(r_pl['operating_profit'].values[0] or 0)
            other_inc = float(r_pl['other_income'].values[0] or 0)
            interest = float(r_pl['interest'].values[0] or 0)
            eps = float(r_pl['eps'].values[0] or 0)
            div_payout = float(r_pl['dividend_payout'].values[0] or 0)

            eq_cap = float(r_bs['equity_capital'].values[0] or 0)
            reserves = float(r_bs['reserves'].values[0] or 0)
            borrowings = float(r_bs['borrowings'].values[0] or 0)
            assets = float(r_bs['total_assets'].values[0] or 0)
            investments = float(r_bs['investments'].values[0] or 0)

            cfo = float(r_cf['operating_activity'].values[0] or 0) if not r_cf.empty else 0
            cfi = float(r_cf['investing_activity'].values[0] or 0) if not r_cf.empty else 0
            cff = float(r_cf['financing_activity'].values[0] or 0) if not r_cf.empty else 0

            # --- Analytical Computations ---
            npm = compute_npm(net_profit, sales)
            opm = compute_opm(op, sales)
            roe = compute_roe(net_profit, eq_cap, reserves)
            de_ratio, _ = compute_debt_to_equity(borrowings, eq_cap, reserves)
            icr, icr_label, icr_warn = compute_interest_coverage(op, other_inc, interest)
            asset_turn = compute_asset_turnover(sales, assets)
            fcf = compute_fcf(cfo, cfi)

            # High Leverage Warning suppression logic for banks
            is_financial = sector.strip().upper() == "FINANCIALS"
            high_leverage = 1 if (de_ratio and de_ratio > 5.0 and not is_financial) else 0
            if de_ratio and de_ratio > 5.0 and is_financial:
                edge_cases.append(f"[{comp} - {yr}] Suppressed high-leverage flag: Structural Banking Normalcy.")

            # --- Multi-Year CAGR Calculation Engine ---
            rev_cagr, pat_cagr, eps_cagr = None, None, None
            if idx >= 5:
                prev_sales = float(c_pl.iloc[idx-5]['sales'] or 0)
                prev_pat = float(c_pl.iloc[idx-5]['net_profit'] or 0)
                prev_eps = float(c_pl.iloc[idx-5]['eps'] or 0)
                rev_cagr, _ = compute_cagr(prev_sales, sales, 5)
                pat_cagr, _ = compute_cagr(prev_pat, net_profit, 5)
                eps_cagr, _ = compute_cagr(prev_eps, eps, 5)

            # --- Capital Flow Classifications ---
            cfo_pat = (cfo / net_profit) if net_profit != 0 else 0
            pattern = classify_capital_allocation(cfo, cfi, cff, cfo_pat)
            capital_allocations.append([comp, yr, "+" if cfo>=0 else "-", "+" if cfi>=0 else "-", "+" if cff>=0 else "-", pattern])

            # Store to execution list
            ratio_rows.append((
                comp, yr, npm, opm, roe, de_ratio, icr, icr_label, asset_turn, fcf,
                abs(cfi), eps, (eq_cap + reserves), div_payout, borrowings, cfo,
                rev_cagr, pat_cagr, eps_cagr, roe, high_leverage
            ))

    # Commit calculations to database
    cursor.executemany("""
        INSERT OR REPLACE INTO financial_ratios VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ratio_rows)
    conn.commit()

    # Save outputs
    os.makedirs("output", exist_ok=True)
    with open("output/capital_allocation.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"])
        writer.writerows(capital_allocations)

    with open("output/ratio_edge_cases.log", "w") as f:
        f.write("\n".join(edge_cases) if edge_cases else "0 structural anomalies found in this run window.")

    # Integrity row counter check
    cursor.execute("SELECT COUNT(*) FROM financial_ratios")
    total_loaded = cursor.fetchone()[0]
    print(f"✨ Success! Table [financial_ratios] populated with {total_loaded} rows.")
    conn.close()

if __name__ == "__main__":
    run_ratio_engine()