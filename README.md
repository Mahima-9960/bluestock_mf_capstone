# 📈 Bluestock Mutual Fund Analytics Capstone

A comprehensive data engineering and advanced analytics solution built to ingest, clean, model, and analyze historical Mutual Fund Net Asset Values (NAV) and investor transaction workflows. This system tracks risk metrics, detects at-risk behavioral cohorts, and provides automated fund recommendations.

---

## 📂 Project Architecture & Directory Structure

```text
BLUESTOCK_INTERNSHIP/
├── data/
│   └── processed/            # Cleaned production-ready datasets
├── notebooks/
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 06_advanced_analytics.ipynb  # Tail risk & behavioral models
├── png/                      # Exported visualization assets
├── reports/                  # Generated analytical CSV deliverables
├── scripts/
│   ├── data_ingestion.py     # Live data fetching
│   ├── etl_pipeline.py       # SQL transformations and cleaning
│   └── recommender.py        # Rule-based matching engine
├── README.md                 # Project documentation
├── requirements.txt          # Environment dependencies
└── run_pipeline.py           # Master execution script

🛠️ Tech Stack & Core Libraries
Language: Python 3.12+

Data Manipulation: Pandas, NumPy

Data Visualization: Matplotlib, Seaborn, Power BI Desktop

Database & Orchestration: SQL (DDL Schema), Python Subprocess

🚀 Installation & Setup Instructions
1. Clone the Workspace
Bash
git clone <your-github-repository-url>
cd Bluestock_Internship
2. Configure Environment Dependencies
Ensure all foundational analytical packages are mapped correctly within your local Python architecture:

Bash
pip install -r requirements.txt

3. Run the E2E Production PipelineTo initialize data ingestion, run the database cleaning transformations, and compute the core engine metrics sequentially, execute the master pipeline script from the root directory:Bashpython run_pipeline.py

📊 Analytics & Insights Breakdown
⚡ Phase 1: Advanced Risk Quantification (VaR & CVaR)
Historical Value at Risk (95% VaR): Pinpoints the 5th percentile of the historical daily return distribution, defining the maximum expected loss with a 95% confidence interval.

Conditional Value at Risk (95% CVaR): Captures severe tail risk by computing the expected shortfall—the average magnitude of loss on days when the VaR threshold is breached.

Deliverable Location: reports/var_cvar_report.csv

⚡ Phase 2: Performance Volatility MappingEvaluates a 90-Day Rolling Sharpe Ratio ($(\text{Mean} / \text{Standard Deviation}) \times \sqrt{252}$) across core flagship funds to map asset-allocation consistency and structural stability over time.Deliverable Location: png/rolling_sharpe_chart.png

⚡ Phase 3: Investor Behavioral Cohorts
Grouped user segments by their historical transaction launch dates to establish clear structural trends regarding investment size and asset type preference.

Tracks systemic SIP Continuity metrics, flagging active accounts showing payment gaps greater than 35 days as "at-risk" churn vectors.