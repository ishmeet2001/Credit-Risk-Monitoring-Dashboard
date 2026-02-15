from __future__ import annotations

import os
from typing import Any, Dict

import psycopg2
import numpy as np
from psycopg2.extensions import register_adapter, AsIs

# Register adapters for numpy types
register_adapter(np.int64, AsIs)
register_adapter(np.float64, AsIs)
register_adapter(np.int32, AsIs)
register_adapter(np.float32, AsIs)
register_adapter(np.bool_, AsIs)

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_DB = os.getenv("PG_DB", "credit_risk")
PG_USER = os.getenv("PG_USER", "credit")
PG_PASSWORD = os.getenv("PG_PASSWORD", "risk")


def get_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )


INSERT_SQL = """
INSERT INTO risk_scored (
  loan_id, purpose, term,
  loan_amnt, annual_inc, dti, int_rate_pct, revol_util_pct,
  delinq_2yrs, inq_last_6mths, credit_history_years, emp_length_yrs,
  dti_band, util_band, rate_band,
  early_warning_flag, risk_tier, reasons
) VALUES (
  %(loan_id)s, %(purpose)s, %(term)s,
  %(loan_amnt)s, %(annual_inc)s, %(dti)s, %(int_rate_pct)s, %(revol_util_pct)s,
  %(delinq_2yrs)s, %(inq_last_6mths)s, %(credit_history_years)s, %(emp_length_yrs)s,
  %(dti_band)s, %(util_band)s, %(rate_band)s,
  %(early_warning_flag)s, %(risk_tier)s, %(reasons)s
);
"""


def insert_scored_row(row: Dict[str, Any]) -> None:
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_SQL, row)
    finally:
        conn.close()
