# Bluestock Mutual Fund Analytics - Data Dictionary

This document outlines the Star Schema design for the Mutual Fund Analytics SQLite Database (`bluestock_mf.db`).

## 1. Dimension Tables

### `dim_fund` (Fund Master)
Stores static metadata for all mutual fund schemes.
* **amfi_code** (TEXT) - Primary Key. Unique identifier from AMFI.
* **fund_house** (TEXT) - Name of the Asset Management Company.
* **scheme_name** (TEXT) - Full official name of the mutual fund.
* **category** (TEXT) - Equity, Debt, or Hybrid.
* **sub_category** (TEXT) - Large Cap, Mid Cap, Liquid, etc.
* **expense_ratio_pct** (REAL) - Annual fee charged by the AMC (%).
* **risk_category** (TEXT) - SEBI defined risk level.

## 2. Fact Tables

### `fact_nav` (NAV History)
Stores daily Net Asset Value tracking.
* **amfi_code** (TEXT) - Foreign Key linked to `dim_fund`.
* **nav_date** (DATE) - Date of the NAV record.
* **nav** (REAL) - Net Asset Value in INR.

### `fact_transactions` (Investor Transactions)
Stores individual investor purchase and redemption records.
* **transaction_id** (TEXT) - Primary Key. Unique transaction ID.
* **investor_id** (TEXT) - Identifier for the retail investor.
* **amfi_code** (TEXT) - Foreign Key linked to `dim_fund`.
* **transaction_date** (DATE) - Date the transaction was executed.
* **transaction_type** (TEXT) - Type of order (SIP, LUMPSUM, REDEMPTION).
* **amount_inr** (REAL) - Transaction value in INR.
* **state / city** (TEXT) - Geographic location of the investor.
* **kyc_status** (TEXT) - Verification status of the investor.

### `fact_performance` (Scheme Performance Metrics)
Stores computed financial metrics and risk ratios.
* **amfi_code** (TEXT) - Primary Key / Foreign Key linked to `dim_fund`.
* **return_1yr_pct / 3yr_pct / 5yr_pct** (REAL) - Absolute/CAGR returns.
* **sharpe_ratio** (REAL) - Risk-adjusted return metric.
* **alpha / beta** (REAL) - Market comparison metrics.
* **max_drawdown_pct** (REAL) - Peak-to-trough maximum historical drop.