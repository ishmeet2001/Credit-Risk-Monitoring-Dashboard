from dotenv import load_dotenv
load_dotenv()
import os

import pandas as pd
import psycopg2
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB", "credit_risk")
PG_USER = os.getenv("PG_USER", "credit")
PG_PASSWORD = os.getenv("PG_PASSWORD", "risk")
S3_BUCKET = os.getenv("S3_BUCKET", "credit-risk-lake")

from app.storage.s3 import upload_file

OUT_DIR = os.getenv("DRIFT_OUT_DIR", "monitoring/reports")
os.makedirs(OUT_DIR, exist_ok=True)

FEATURE_COLS = [
    "loan_amnt", "annual_inc", "dti", "int_rate_pct", "revol_util_pct",
    "delinq_2yrs", "inq_last_6mths", "credit_history_years", "emp_length_yrs",
]

def get_conn():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD
    )

def load_df(sql: str) -> pd.DataFrame:
    conn = get_conn()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()

def main():
    print("Fetching baseline data...")
    baseline = load_df(f"""
      SELECT {",".join(FEATURE_COLS)}
      FROM risk_scored
      ORDER BY event_time ASC
      LIMIT 1000;
    """)

    print("Fetching recent data...")
    recent = load_df(f"""
      SELECT {",".join(FEATURE_COLS)}
      FROM risk_scored
      ORDER BY event_time DESC
      LIMIT 1000;
    """)

    if baseline.empty or recent.empty:
        print("Not enough data yet for drift report (need baseline + recent).")
        return

    print(f"Running drift report on {len(baseline)} baseline vs {len(recent)} recent rows...")
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=baseline, current_data=recent)

    out_path = os.path.join(OUT_DIR, "drift_report.html")
    report.save_html(out_path)
    print(f"✅ Drift report saved locally: {out_path}")

    # Upload to S3
    s3_key = f"reports/drift/drift_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html"
    s3_url = upload_file(out_path, s3_key)
    if s3_url:
        print(f"🚀 Drift report uploaded to S3: {s3_url}")
    else:
        print("❌ Failed to upload drift report to S3")

if __name__ == "__main__":
    main()
