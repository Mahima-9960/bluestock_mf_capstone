import os
import sys
import time
import sqlite3
import pandas as pd
from datetime import datetime

# Adjust system path to handle relative module routing cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.normaliser import normalize_ticker, normalize_year
from etl.validator import DataValidator

class ETLEngine:
    def __init__(self):
        self.db_path = "db/nifty100.db"
        self.validator = DataValidator()
        self.audit_records = []
        os.makedirs("output", exist_ok=True)

    def clear_database_tables(self):
        """Safely flushes any data from previous partial runs to avoid duplicate key conflicts."""
        print("🧹 Clearing existing data from database tables for a clean run...")
        tables = [
            "peer_groups", "stock_prices", "sectors", "prosandcons", 
            "documents", "analysis", "cashflow", "balancesheet", "profitandloss", "companies"
        ]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF;")
            for table in tables:
                cursor.execute(f"DELETE FROM {table};")
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.commit()
        print("✨ Database tables cleared perfectly.")

    def run_pipeline(self):
        print("\n🏁 [STARTING AUTOMATED MASTER MICRO-ETL PIPELINE RUN]")
        
        self.clear_database_tables()
        
        parent_file = "companies.xlsx"
        if not os.path.exists(parent_file):
            print(f"❌ CRITICAL CONFIG ERROR: Core file '{parent_file}' missing from root workspace.")
            return

        start_time = time.time()
        print(f"\n📖 Reading corporate master directory: {parent_file}...")
        
        df_comp = pd.read_excel(parent_file, header=1)
        df_comp['id'] = df_comp['id'].apply(normalize_ticker)
        df_comp = df_comp.drop_duplicates(subset=['id'])
        
        companies_universe = set(df_comp['id'].tolist())
        
        with sqlite3.connect(self.db_path) as conn:
            df_comp.to_sql('companies', conn, if_exists='append', index=False)
            
        self.audit_records.append({
            'table_name': 'companies', 'rows_in': len(df_comp), 'rows_out': len(df_comp),
            'rejected': 0, 'timestamp': datetime.now().isoformat(), 'runtime_s': round(time.time() - start_time, 4)
        })
        print(f"   ↳ 🎉 Success: Loaded {len(df_comp)} parent corporate entities.")

        child_datasets = [
            {'file': 'profitandloss.xlsx', 'table': 'profitandloss', 'has_year': True, 'header_skip': 1},
            {'file': 'balancesheet.xlsx', 'table': 'balancesheet', 'has_year': True, 'header_skip': 1},
            {'file': 'cashflow.xlsx', 'table': 'cashflow', 'has_year': True, 'header_skip': 1},
            {'file': 'analysis.xlsx', 'table': 'analysis', 'has_year': False, 'header_skip': 1},
            {'file': 'documents.xlsx', 'table': 'documents', 'has_year': True, 'header_skip': 1},
            {'file': 'prosandcons.xlsx', 'table': 'prosandcons', 'has_year': False, 'header_skip': 1},
            {'file': 'sectors.xlsx', 'table': 'sectors', 'has_year': False, 'header_skip': 0},
            {'file': 'stock_prices.xlsx', 'table': 'stock_prices', 'has_year': False, 'header_skip': 0},
            {'file': 'peer_groups.xlsx', 'table': 'peer_groups', 'has_year': False, 'header_skip': 0}
        ]

        for child in child_datasets:
            file_name = child['file']
            table_name = child['table']
            
            if not os.path.exists(file_name):
                print(f"⚠️ Warning: File '{file_name}' not located. Skipping.")
                continue
                
            start_time = time.time()
            print(f"🔄 Processing table: [{table_name}]")
            print(f"   ⏳ Reading '{file_name}' into engine memory...")
            
            if child['header_skip'] == 1:
                df = pd.read_excel(file_name, header=1)
            else:
                df = pd.read_excel(file_name)

            print(f"   ⏳ Parsing and running data quality rules on {len(df)} rows...")
            rows_in = len(df)
            
            # 🛡️ Harmonize ID columns perfectly across all child datasets
            if 'company_id' in df.columns:
                df['company_id'] = df['company_id'].apply(normalize_ticker)
            elif 'id' in df.columns:
                df['company_id'] = df['id'].apply(normalize_ticker)
            
            # Drop the loose raw 'id' column for child tables so it doesn't conflict with SQL schemas
            if 'id' in df.columns:
                df.drop(columns=['id'], inplace=True, errors='ignore')

            if child['has_year']:
                year_col = 'year' if 'year' in df.columns else 'Year'
                df['year'] = df[year_col].apply(normalize_year)
                if year_col != 'year':
                    df.drop(columns=[year_col], inplace=True)
                    
            if table_name == 'documents' and 'Annual_Report' in df.columns:
                df.rename(columns={'Annual_Report': 'annual_report'}, inplace=True)

            cleaned_df, failed_critical = self.validator.validate_dataset(df, table_name, companies_universe)

            if child['has_year'] and not cleaned_df.empty:
                cleaned_df = cleaned_df.drop_duplicates(subset=['company_id', 'year'])
            elif table_name in ['analysis', 'sectors'] and not cleaned_df.empty:
                cleaned_df = cleaned_df.drop_duplicates(subset=['company_id'])

            rows_out = len(cleaned_df)
            rejected = rows_in - rows_out
            
            print(f"   ⏳ Storing records securely inside database...")
            with sqlite3.connect(self.db_path) as conn:
                cleaned_df.to_sql(table_name, conn, if_exists='append', index=False)
                
            runtime = round(time.time() - start_time, 4)
            self.audit_records.append({
                'table_name': table_name, 'rows_in': rows_in, 'rows_out': rows_out,
                'rejected': rejected, 'timestamp': datetime.now().isoformat(), 'runtime_s': runtime
            })
            print(f"   ↳ ✅ Complete! Loaded {rows_out} records (Dropped {rejected}).")

        pd.DataFrame(self.audit_records).to_csv("output/load_audit.csv", index=False)
        self.validator.save_failures("output/validation_failures.csv")
        
        print("\n🏆 [MASTER PIPELINE LOAD COMPLETED SUCCESSFULLY]")

if __name__ == "__main__":
    engine = ETLEngine()
    engine.run_pipeline()