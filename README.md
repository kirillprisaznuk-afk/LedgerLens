# FinOps — AI-Powered Financial Intelligence Platform

FinOps is a financial and operational intelligence tool for small businesses. It ingests raw transaction data, builds automated financial statements (P&L, Cash Flow), calculates key business KPIs, and uses lightweight machine learning to forecast trends, detect anomalies, and generate plain-language insights — all through an interactive dashboard.

## Features

- **Data ingestion**: CSV import with validation, cleaning, and automatic transaction categorization via keyword matching.
- **Financial reporting**: Automated Profit & Loss statements and Cash Flow statements, with month-over-month / quarter-over-quarter / year-over-year comparisons.
- **KPIs**: Net margin, burn rate, runway, and break-even point calculations.
- **AI layer**: ARIMA-based revenue/expense forecasting, Isolation Forest anomaly detection on transactions, and a rule-based natural-language insight generator.
- **Dashboard**: Interactive Streamlit interface with filterable charts, KPI cards, and an AI Insights tab.

## Tech Stack

Python · SQLAlchemy (SQLite) · pandas · Streamlit · Plotly · scikit-learn · statsmodels · pytest

## Architecture

```
finops/
├── data/          # DB models, database connection, seed data, CSV loader
├── analytics/     # P&L, cash flow, comparisons, KPIs, forecasting, anomalies, insights
├── tests/         # pytest test suite for financial calculation logic
└── app.py         # Streamlit dashboard entry point
```

The project separates data access, business logic, and presentation into distinct layers — analytics functions never touch the UI directly, and the UI never queries the database directly. This makes each layer independently testable.

## Getting Started

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt

python -m data.database        # create tables
python -m data.seed_data       # seed accounts/categories
python -m data.generate_test_data  # generate sample transactions
python -m data.loader          # load transactions into the database

python -m streamlit run app.py
```

## Running Tests

```bash
python -m pytest
```

## Known Simplifications (MVP scope)

- Gross margin is currently equivalent to net margin since no separate COGS category exists yet.
- Categorization uses keyword matching rather than a trained ML classifier — planned as a future improvement.
- Insights are rule-based rather than LLM-generated, to keep the project free of external API dependencies.

## Author

Built as a portfolio project to demonstrate applied skills in Python, SQL, financial analysis, and data-driven product thinking.
