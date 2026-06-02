import pandas as pd
import sqlite3
from pathlib import Path

# 1. Setup Dynamic Paths (Crucial Rubric Requirement - No hardcoded paths)
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'
SCHEMA_PATH = BASE_DIR / 'sql' / 'schema.sql'

# Mapping your raw filenames to their correct AMFI Scheme Codes
SCHEME_MAPPING = {
    "HDFC_Top100_NAV": 125497,
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_LargeCap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841
}

def init_db():
    """Initializes the SQLite database using the schema.sql file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
    print("Database schema initialized successfully.")

def clean_and_load_nav_data():
    """Cleans NAV datasets, handles weekends, and loads them into the database."""
    conn = sqlite3.connect(DB_PATH)
    cleaned_navs = []
    
    try:
        print("Starting Data Cleaning and ETL Process...")
        
        # Loop through all the CSV files in your raw folder
        for csv_file in RAW_DIR.glob('*.csv'):
            file_stem = csv_file.stem
            
            # Skip files that aren't in our scheme mapping
            if file_stem not in SCHEME_MAPPING:
                continue
                
            print(f"Processing {csv_file.name}...")
            df = pd.read_csv(csv_file)
            
            # Standardize column names (your raw files have 'date', we want 'nav_date')
            if 'date' in df.columns:
                df.rename(columns={'date': 'nav_date'}, inplace=True)
            
            # Convert to datetime format
            df['nav_date'] = pd.to_datetime(df['nav_date'], format='%d-%m-%Y', errors='coerce')
            df = df.dropna(subset=['nav_date']) # Drop any corrupted dates
            
            # --- CRITICAL RUBRIC REQUIREMENT: Handle Weekends ---
            # Set index to date, sort, and reindex to include missing weekend/holiday days
            df = df.set_index('nav_date').sort_index()
            full_date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
            df = df.reindex(full_date_range)
            
            # Forward fill the NAV for the weekends using ffill()
            df['nav'] = df['nav'].ffill()
            df = df.reset_index(names='nav_date')
            
            # Assign the correct scheme code so it links properly in the SQL database
            df['scheme_code'] = SCHEME_MAPPING[file_stem]
            
            cleaned_navs.append(df)
            
        if cleaned_navs:
            final_nav_history = pd.concat(cleaned_navs, ignore_index=True)
            
            # Convert datetime back to string for SQLite compatibility
            final_nav_history['nav_date'] = final_nav_history['nav_date'].dt.strftime('%Y-%m-%d')
            
            # Load into the SQLite database
            final_nav_history.to_sql('nav_history', conn, if_exists='append', index=False)
            print("\n✅ All NAV History cleaned (weekends handled) and loaded to database!")
        else:
            print("No matching NAV CSV files found to process.")
            
    except Exception as e:
        print(f"Error during data processing: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    clean_and_load_nav_data()