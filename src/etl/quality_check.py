import os
import sqlite3
import pandas as pd

def run_manual_review():
    db_path = "db/nifty100.db"
    failures_path = "output/validation_failures.csv"
    
    print("\n🔍 [STARTING MANDATORY DAY 06 DATA QUALITY AUDIT]")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file not found at {db_path}")
        return
        
    print("📊 Current Database Table Statistics:")
    tables = [
        "companies", "profitandloss", "balancesheet", "cashflow", 
        "analysis", "documents", "prosandcons", "sectors", "stock_prices", "peer_groups"
    ]
    
    with sqlite3.connect(db_path) as conn:
        for table in tables:
            try:
                count = pd.read_sql_query(f"SELECT COUNT(*) FROM {table};", conn).iloc[0, 0]
                print(f"   ↳ Table [{table:15}]: {count} records stored.")
            except Exception as e:
                print(f"   ↳ Table [{table:15}]: ❌ Error reading table ({e})")
                
    print("=" * 60)
    
    if os.path.exists(failures_path):
        print("🚨 Analyzing Logged Data Quality Violations:")
        df_fail = pd.read_csv(failures_path)
        print(f"   Total anomalies recorded: {len(df_fail)}")
        
        if not df_fail.empty:
            print("\n📌 Breakdown of Failures by Rule & Severity:")
            summary = df_fail.groupby(['rule_id', 'severity']).size().reset_index(name='count')
            for _, row in summary.iterrows():
                print(f"   - Rule {row['rule_id']} [{row['severity']}]: {row['count']} occurrences")
                
            print("\n📌 Sample Technical Exceptions (Top 5 Rows):")
            # 🛡️ Swapped 'table_name' out for 'year' and 'severity' to match validator schema perfectly
            print(df_fail[['company_id', 'year', 'field', 'rule_id', 'severity', 'issue']].head(5).to_string(index=False))
    else:
        print("✨ No validation anomaly log file discovered at output/validation_failures.csv.")
        
    print("=" * 60)
    print("🏁 [DATA QUALITY AUDIT SCRIPT COMPLETE]\n")

if __name__ == "__main__":
    run_manual_review()