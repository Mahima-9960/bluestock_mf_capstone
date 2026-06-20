import os
import re
import math
import pandas as pd
from typing import List, Dict, Tuple

class DataValidator:
    def __init__(self):
        self.failures: List[Dict] = []
        self.seen_violations = set()

    def log_failure(self, company_id: str, year: str, field: str, rule_id: str, issue: str, severity: str):
        violation_key = (company_id, str(year), rule_id, field)
        if violation_key not in self.seen_violations:
            self.seen_violations.add(violation_key)
            self.failures.append({
                'company_id': company_id, 'year': year, 'field': field,
                'rule_id': rule_id, 'issue': issue, 'severity': severity
            })

    def validate_dataset(self, df: pd.DataFrame, table_name: str, companies_universe: set = None) -> Tuple[pd.DataFrame, bool]:
        errors_before = len(self.failures)
        rows_to_drop = set()

        if df.empty:
            return df, False

        seen_pks = set()

        # 🛡️ Inline helper to turn missing/NaN cell values safely into 0.0
        def safe_float(val) -> float:
            if pd.isna(val) or str(val).strip().lower() in ['nan', 'null', '']:
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        for idx, row in df.iterrows():
            comp_id = str(row.get('company_id', row.get('id', 'UNKNOWN'))).strip().upper()
            raw_yr = str(row.get('year', row.get('Year', 'SNAPSHOT'))).strip()

            # --- DQ-01 & DQ-02: Primary Key Duplication ---
            pk_key = comp_id if table_name in ['companies', 'analysis', 'sectors'] else (comp_id, raw_yr)
            if pk_key in seen_pks:
                self.log_failure(comp_id, raw_yr, 'PRIMARY_KEY', 'DQ-01/02', f'Duplicate primary key within {table_name}.', 'CRITICAL')
                rows_to_drop.add(idx)
                continue
            seen_pks.add(pk_key)

            # --- DQ-03: Foreign Key Integrity ---
            if companies_universe and table_name != 'companies' and comp_id not in companies_universe:
                self.log_failure(comp_id, raw_yr, 'company_id', 'DQ-03', f'Orphaned ticker token [{comp_id}].', 'CRITICAL')
                rows_to_drop.add(idx)
                continue

            # --- DQ-04: Balance Sheet Equator ---
            if table_name == 'balancesheet':
                tl = safe_float(row.get('total_liabilities'))
                ta = safe_float(row.get('total_assets'))
                if abs(tl - ta) > (0.01 * max(ta, 1)):
                    self.log_failure(comp_id, raw_yr, 'total_liabilities/assets', 'DQ-04', f'Unbalanced entries: Assets ({ta}) != Liabilities ({tl})', 'WARNING')

            # --- DQ-05: Operating Margin Math ---
            if table_name == 'profitandloss':
                sales = safe_float(row.get('sales'))
                op = safe_float(row.get('operating_profit'))
                reported_opm = safe_float(row.get('opm_percentage'))
                if sales > 0:
                    raw_opm = (op / sales) * 100
                    if not math.isnan(raw_opm) and not math.isinf(raw_opm):
                        calculated_opm = round(raw_opm)
                        if abs(calculated_opm - reported_opm) > 2:
                            self.log_failure(comp_id, raw_yr, 'opm_percentage', 'DQ-05', f'OPM mismatch: Calculated ({calculated_opm}%) vs Reported ({reported_opm}%)', 'WARNING')

            # --- DQ-06: Revenue Floor ---
            if table_name == 'profitandloss':
                if safe_float(row.get('sales')) <= 0:
                    self.log_failure(comp_id, raw_yr, 'sales', 'DQ-06', 'Zero or negative sales baseline.', 'WARNING')

            # --- DQ-07: Cash Flow Reconciliation ---
            if table_name == 'cashflow':
                cfo = safe_float(row.get('operating_activity'))
                cfi = safe_float(row.get('investing_activity'))
                cff = safe_float(row.get('financing_activity'))
                reported_ncf = safe_float(row.get('net_cash_flow'))
                if abs((cfo + cfi + cff) - reported_ncf) > 10:
                    self.log_failure(comp_id, raw_yr, 'net_cash_flow', 'DQ-09', 'Statement disconnect on Net Cash Flow.', 'WARNING')

            # --- DQ-11: Tax Bracket Boundaries ---
            if table_name == 'profitandloss':
                tax = safe_float(row.get('tax_percentage'))
                if tax < 0 or tax > 60:
                    self.log_failure(comp_id, raw_yr, 'tax_percentage', 'DQ-11', f'Abnormal corporate tax rate: {tax}%', 'WARNING')

            # --- DQ-12: Dividend Cap Boundary ---
            if table_name == 'profitandloss':
                payout = safe_float(row.get('dividend_payout'))
                if payout > 200:
                    self.log_failure(comp_id, raw_yr, 'dividend_payout', 'DQ-12', f'Extreme dividend distribution: {payout}%', 'WARNING')

            # --- DQ-13: URL Syntax ---
            if table_name == 'documents':
                url = str(row.get('Annual_Report', row.get('annual_report', '')))
                if url.lower() != 'null' and url.strip() != '' and not re.match(r'^https?://', url):
                    self.log_failure(comp_id, raw_yr, 'Annual_Report', 'DQ-13', 'Malformed report link pattern.', 'WARNING')

            # --- DQ-14: Net Profit vs EPS ---
            if table_name == 'profitandloss':
                net_profit = safe_float(row.get('net_profit'))
                eps = safe_float(row.get('eps'))
                if net_profit > 0 and eps <= 0:
                    self.log_failure(comp_id, raw_yr, 'eps', 'DQ-14', 'Positive net profit with flat/negative EPS.', 'WARNING')

        cleaned_df = df.drop(index=list(rows_to_drop)).copy()
        has_critical_failures = any(f['severity'] == 'CRITICAL' for f in self.failures[errors_before:])
        
        return cleaned_df, has_critical_failures

    def save_failures(self, output_path: str = "output/validation_failures.csv"):
        if self.failures:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pd.DataFrame(self.failures).to_csv(output_path, index=False)
            print(f"💾 Validation exceptions log saved safely to: {output_path}")
        else:
            print("✨ Perfect data run! 0 anomalies identified.")