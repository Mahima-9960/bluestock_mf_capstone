import os
import re
import pandas as pd
from typing import List, Dict, Tuple

class DataValidator:
    def __init__(self):
        # Master list tracking all data quality exceptions across the pipeline
        self.failures: List[Dict] = []
        # Prevent logging duplicate errors for the exact same field row
        self.seen_violations = set()

    def log_failure(self, company_id: str, year: str, field: str, rule_id: str, issue: str, severity: str):
        """Appends a unique structured data violation to our tracking log[cite: 1]."""
        violation_key = (company_id, str(year), rule_id, field)
        if violation_key not in self.seen_violations:
            self.seen_violations.add(violation_key)
            self.failures.append({
                'company_id': company_id,
                'year': year,
                'field': field,
                'rule_id': rule_id,
                'issue': issue,
                'severity': severity
            })

    def validate_dataset(self, df: pd.DataFrame, table_name: str, companies_universe: set = None) -> Tuple[pd.DataFrame, bool]:
        """
        Runs the core Data Quality rules across rows. Drops rows with CRITICAL 
        errors and retains WARNING records for logging output[cite: 1].
        """
        errors_before = len(self.failures)
        rows_to_drop = set()

        if df.empty:
            return df, False

        seen_pks = set()

        for idx, row in df.iterrows():
            # Standardize local trackers safely
            comp_id = str(row.get('company_id', row.get('id', 'UNKNOWN'))).strip().upper()
            raw_yr = str(row.get('year', row.get('Year', 'SNAPSHOT'))).strip()

            # --- DQ-01 & DQ-02: Primary Key Duplication Checks[cite: 1] ---
            pk_key = comp_id if table_name in ['companies', 'analysis', 'sectors'] else (comp_id, raw_yr)
            if pk_key in seen_pks:
                self.log_failure(comp_id, raw_yr, 'PRIMARY_KEY', 'DQ-01/02', f'Duplicate primary key detected within {table_name}.', 'CRITICAL')
                rows_to_drop.add(idx)
                continue
            seen_pks.add(pk_key)

            # --- DQ-03: Foreign Key Integrity Mapping[cite: 1] ---
            if companies_universe and table_name != 'companies' and comp_id not in companies_universe:
                self.log_failure(comp_id, raw_yr, 'company_id', 'DQ-03', f'Orphaned ticker token [{comp_id}] breaks relational boundaries.', 'CRITICAL')
                rows_to_drop.add(idx)
                continue

            # --- DQ-04: Balance Sheet Equator Verification[cite: 1] ---
            if table_name == 'balancesheet':
                tl = float(row.get('total_liabilities', 0))
                ta = float(row.get('total_assets', 0))
                if abs(tl - ta) > (0.01 * max(ta, 1)): # 1% allowable delta threshold[cite: 1]
                    self.log_failure(comp_id, raw_yr, 'total_liabilities/assets', 'DQ-04', f'Unbalanced accounting entries: Assets ({ta}) != Liabilities ({tl})', 'WARNING')

            # --- DQ-05: Operating Margin Formula Alignment[cite: 1] ---
            if table_name == 'profitandloss':
                sales = float(row.get('sales', 0))
                op = float(row.get('operating_profit', 0))
                reported_opm = float(row.get('opm_percentage', 0))
                if sales > 0:
                    calculated_opm = round((op / sales) * 100)
                    if abs(calculated_opm - reported_opm) > 2: # 2% variance cap[cite: 1]
                        self.log_failure(comp_id, raw_yr, 'opm_percentage', 'DQ-05', f'Math mismatch: Calculated OPM ({calculated_opm}%) vs Reported ({reported_opm}%)', 'WARNING')

            # --- DQ-06: Revenue Floor Validation[cite: 1] ---
            if table_name == 'profitandloss':
                if float(row.get('sales', 0)) <= 0:
                    self.log_failure(comp_id, raw_yr, 'sales', 'DQ-06', 'Zero or negative sales baseline detected.', 'WARNING')

            # --- DQ-07: Cash Flow Equation Reconciliation ---
            if table_name == 'cashflow':
                cfo = float(row.get('operating_activity', 0))
                cfi = float(row.get('investing_activity', 0))
                cff = float(row.get('financing_activity', 0))
                reported_ncf = float(row.get('net_cash_flow', 0))
                if abs((cfo + cfi + cff) - reported_ncf) > 10: # 10 Cr validation threshold[cite: 1]
                    self.log_failure(comp_id, raw_yr, 'net_cash_flow', 'DQ-09', f'Statement disconnect: Activities sum ({cfo+cfi+cff}) != Reported NCF ({reported_ncf})', 'WARNING')

            # --- DQ-11: Tax Bracket Boundaries[cite: 1] ---
            if table_name == 'profitandloss':
                tax = float(row.get('tax_percentage', 0))
                if tax < 0 or tax > 60: # Valid standard bracket bounds up to 60%[cite: 1]
                    self.log_failure(comp_id, raw_yr, 'tax_percentage', 'DQ-11', f'Abnormal corporate tax rate noted: {tax}%', 'WARNING')

            # --- DQ-12: Dividend Cap Boundary[cite: 1] ---
            if table_name == 'profitandloss':
                payout = float(row.get('dividend_payout', 0))
                if payout > 200: # Over 200% flag triggers check[cite: 1]
                    self.log_failure(comp_id, raw_yr, 'dividend_payout', 'DQ-12', f'Extreme dividend distribution out of reserves: {payout}%', 'WARNING')

            # --- DQ-13: Document Repository URL Syntax[cite: 1] ---
            if table_name == 'documents':
                url = str(row.get('Annual_Report', ''))
                if url.lower() != 'null' and url.strip() != '' and not re.match(r'^https?://', url):
                    self.log_failure(comp_id, raw_yr, 'Annual_Report', 'DQ-13', 'Malformed or broken report link scheme pattern.', 'WARNING')

            # --- DQ-14: Net Profit vs EPS Arithmetic Check ---
            if table_name == 'profitandloss':
                net_profit = float(row.get('net_profit', 0))
                eps = float(row.get('eps', 0))
                if net_profit > 0 and eps <= 0:
                    self.log_failure(comp_id, raw_yr, 'eps', 'DQ-14', 'Directional sign conflict: Positive net profit with flat/negative EPS.', 'WARNING')

        # Drop indices flagged with structural critical flaws
        cleaned_df = df.drop(index=list(rows_to_drop)).copy()
        has_critical_failures = any(f['severity'] == 'CRITICAL' for f in self.failures[errors_before:])
        
        return cleaned_df, has_critical_failures

    def save_failures(self, output_path: str = "output/validation_failures.csv"):
        """Exports full runtime data validation errors out to a tracking report file[cite: 1]."""
        if self.failures:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pd.DataFrame(self.failures).to_csv(output_path, index=False)
            print(f"💾 Validation exceptions log saved safely to: {output_path}[cite: 1]")
        else:
            print("✨ Perfect data run! 0 anomalies identified.")