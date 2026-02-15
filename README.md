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

## Real-Time Monitoring & Observability
This project includes a real-time Kafka consumer pipeline instrumented with Prometheus and Grafana.
- **Metrics**: Throughput, P95 Latency, E2E Lag, and Heartbeats are exposed on port `9101`.
- **Dashboards**: A pre-configured Grafana dashboard provides real-time visibility into pipeline health.
- **Drift Detection**: Automated data drift reports are generated every 30 minutes and persisted to S3.
- **Alerting**: Automated alerts for high lag (>5s) and high DB error rates (>5%).

See [MONITORING_UPDATES.md](./MONITORING_UPDATES.md) for full implementation details.

## Repo Structure
```
credit-risk-early-warning/
├─ scripts/                 # Batch processing scripts
├─ realtime/                # Real-time pipeline (API, Consumer, Infra)
│  ├─ app/                  # Business logic (preprocess, rules)
│  ├─ streaming/            # Kafka consumer & metrics
│  └─ infra/                # Docker compose, Prometheus, Grafana, Alerts
├─ monitoring/              # Drift detection jobs
├─ analysis/                # ML modeling and evaluation
├─ data/                    # Local data storage (raw/processed)
├─ MONITORING_UPDATES.md    # Detailed docs on recent instrumentation
├─ requirements.txt
└─ README.md
```
