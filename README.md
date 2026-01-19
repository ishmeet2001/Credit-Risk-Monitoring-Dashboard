# Credit Risk Early Warning

## Project Overview
Credit risk monitoring workflow that turns raw LendingClub accepted-loan data into a governed, explainable early-warning view. The project delivers cleaned features, rule-based risk tiers, a watchlist, and a lightweight logistic regression model to validate lift against the baseline default rate.

## What We Built
- A reproducible preprocessing pipeline that cleans and standardizes LendingClub loan fields (rates, DTI, utilization, employment length, credit history).
- Deterministic, auditable risk banding to flag high-DTI/high-utilization borrowers with recent delinquencies or inquiries.
- KPI snapshots for portfolio health plus an early-warning watchlist for downstream Tableau/Excel review.
- A baseline logistic regression model with ROC/AUC evaluation to quantify predictive lift.

## Data Flow & Outputs
1) `scripts/sample.py` — takes a raw LendingClub extract at `data/raw/appl_accepted_20072019Q3.csv`, samples 100k rows → `data/processed/sample_100k.csv`.
2) `scripts/preprocess.py` — cleans and engineers features, enforces required columns, trims outliers → `data/processed/clean_loans.csv`.
3) `scripts/risk_rules.py` — applies risk bands and watchlist rules → `data/processed/risk_segments.csv`, `data/processed/early_warning_watchlist.csv`, `data/processed/kpi_summary.csv`.
4) `analysis/logistic_regression.py` — trains a scaled logistic regression model, prints metrics, writes scored dataset → `data/processed/risk_segments_with_predictions.csv`.
5) `analysis/roc_curve.py` — plots ROC using scored data → `analysis/roc_curve.png`.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Optional: create a 100k sample if you have the raw LendingClub file
python scripts/sample.py

# Core pipeline
python scripts/preprocess.py
python scripts/risk_rules.py
python analysis/logistic_regression.py
python analysis/roc_curve.py
```

## Dashboard
- Tableau (Early Warning Watchlist): https://public.tableau.com/views/your-dashboard-link (replace with your share link; note if login is required).
- Packaged workbook: add your `.twbx` export at `analysis/early_warning_watchlist.twbx` for offline sharing/versioning.

## KPIs & Watchlist
- `data/processed/kpi_summary.csv` captures portfolio rows, baseline default rate, watchlist share, watchlist default rate, and lift vs baseline.
- `data/processed/early_warning_watchlist.csv` lists borrowers meeting elevated risk rules (DTI/utilization + recent delinquency/inquiry).

## Tech Stack
- Python (pandas, numpy)
- Scikit-learn for modeling and evaluation
- Matplotlib for ROC visualization

## Repo Structure
- `scripts/` — sampling, preprocessing, and rule-based risk scoring.
- `analysis/` — modeling and ROC evaluation assets.
- `analysis/early_warning_watchlist.twbx` — Tableau packaged workbook for the dashboard (add your file here).
- `data/processed/` — intermediate and final CSV outputs (created by the pipeline).
- `notebooks/` — profiling notebooks used to justify cleaning thresholds.
