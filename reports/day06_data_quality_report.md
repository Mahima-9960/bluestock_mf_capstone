# Day 06 - Data Quality Audit Report

## Identified Edge Cases & Pipeline Behavior

1. **stock_prices (Time-Series Truncation):** * **Issue:** The incoming dataset had 5,520 rows, but the pipeline only loaded 92 rows.
   * **Reason:** The `stock_prices` table holds monthly historical time-series data (multiple rows per company symbol). However, our current validator evaluates uniqueness based on `company_id` alone. This caused the engine to flag all subsequent dates as duplicate primary key violations (`DQ-01/02`) and drop 5,428 rows. 
   * **Fix Needed:** A composite primary key structure targeting `(company_id, price_date)` is required in the next sprint.

2. **Relational Inconsistencies (DQ-03 Critical Gaps):** * **Issue:** 162 total critical foreign key exceptions were logged.
   * **Reason:** Ticker symbols present in the supplementary sheets (like `analysis.xlsx` and `prosandcons.xlsx`) do not exist in the primary master `companies.xlsx` registry. The data integrity gate successfully blocked these rows to protect database cleanliness.

3. **Financial Math & Subsidies Variances (DQ-05 / DQ-11 Warnings):** * **OPM Mismatches (233 rows):** Discovered minor operational rounding variances between our standard formula calculation and the reported corporate metrics.
   * **Abnormal Tax Rates (90 rows):** Real-world outliers like `ADANIENT` (-64%) and `ADANIGREEN` (-75%) triggered anomalies due to valid corporate deferred tax credits and green energy subsidies.