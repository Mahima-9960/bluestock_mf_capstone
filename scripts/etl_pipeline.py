import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import sqlite3

# Define Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'
SCHEMA_PATH = BASE_DIR / 'sql' / 'schema.sql'

def init_db():
    """Execute the DDL to create the Star Schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
    print("Star Schema Initialized.")

def clean_and_load_data():
    """Clean datasets according to Capstone rules and load via SQLAlchemy."""
    engine = create_engine(f'sqlite:///{DB_PATH}')
    
    # 1. Process Fund Master (dim_fund)
    fund_path = RAW_DIR / '01_fund_master.csv'
    if fund_path.exists():
        df_fund = pd.read_csv(fund_path)
        df_fund['amfi_code'] = df_fund['amfi_code'].astype(str)
        df_fund.to_sql('dim_fund', engine, if_exists='replace', index=False)
        print("Loaded dim_fund.")

    # 2. Process NAV History (fact_nav)
    nav_path = RAW_DIR / '02_nav_history.csv'
    if nav_path.exists():
        df_nav = pd.read_csv(nav_path)
        df_nav['amfi_code'] = df_nav['amfi_code'].astype(str)
        df_nav['date'] = pd.to_datetime(df_nav['date'], format='%d-%m-%Y', errors='coerce')
        
        # Clean: Remove duplicates and validate NAV > 0
        df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])
        df_nav = df_nav[df_nav['nav'] > 0]
        
        # Clean: Forward fill missing holidays/weekends
        df_nav = df_nav.set_index('date').groupby('amfi_code').resample('D').ffill().reset_index(level=0, drop=True).reset_index()
        df_nav.rename(columns={'date': 'nav_date'}, inplace=True)
        
        df_nav.to_sql('fact_nav', engine, if_exists='replace', index=False)
        print("Loaded fact_nav.")

    # 3. Process Investor Transactions (fact_transactions)
    tx_path = RAW_DIR / '08_investor_transactions.csv'
    if tx_path.exists():
        df_tx = pd.read_csv(tx_path)
        df_tx['amfi_code'] = df_tx['amfi_code'].astype(str)
        df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'], errors='coerce')
        
        # Clean: Standardize text and validate amounts
        df_tx['transaction_type'] = df_tx['transaction_type'].str.upper().str.strip()
        df_tx = df_tx[df_tx['amount_inr'] > 0]
        
        df_tx.to_sql('fact_transactions', engine, if_exists='replace', index=False)
        print("Loaded fact_transactions.")

    # 4. Process Scheme Performance (fact_performance)
    perf_path = RAW_DIR / '07_scheme_performance.csv'
    if perf_path.exists():
        df_perf = pd.read_csv(perf_path)
        df_perf['amfi_code'] = df_perf['amfi_code'].astype(str)
        
        # Clean: Validate numeric returns
        numeric_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'sharpe_ratio', 'expense_ratio_pct']
        for col in numeric_cols:
            df_perf[col] = pd.to_numeric(df_perf[col], errors='coerce')
            
        df_perf.to_sql('fact_performance', engine, if_exists='replace', index=False)
        print("Loaded fact_performance.")

    print("\n✅ Day 2 ETL Complete: Cleaned data loaded into SQLite Star Schema!")

if __name__ == "__main__":
    init_db()
    clean_and_load_data()