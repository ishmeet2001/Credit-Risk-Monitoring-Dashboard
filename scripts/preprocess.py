"""
Purpose:
- Clean and standardize sampled LendingClub loan data
- Apply governed exclusions based on data profiling
- Create analysis ready features for credit risk monitoring

Inputs:
- data/processed/sample_100k.csv

Outputs:
- data/processed/clean_loans.csv

Notes:
- This script is deterministic and reproducible
- All cleaning decisions are justified by prior data profiling
"""


from __future__ import annotations

import sys
import pandas as pd
import numpy as np


INPUT_PATH = "data/processed/sample_100k.csv"
OUTPUT_PATH = "data/processed/clean_loans.csv"

# Columns we expect to exist in the sampled file 
EXPECTED_COLUMNS = {
    "loan_amnt",
    "term",
    "int_rate",
    "installment",
    "purpose",
    "annual_inc",
    "dti",
    "revol_util",
    "delinq_2yrs",
    "inq_last_6mths",
    "open_acc",
    "total_acc",
    "emp_length",
    "earliest_cr_line",
    "loan_status",
}


def _require_columns(df: pd.DataFrame, expected: set[str]) -> None:
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def _to_percent_float(series: pd.Series) -> pd.Series:
    """
    Convert strings like '13.56%' to float 13.56.
    Handles numeric inputs and missing values.
    """
    s = series.astype(str).str.strip()
    s = s.replace({"nan": np.nan, "None": np.nan, "": np.nan})
    s = s.str.rstrip("%")
    return pd.to_numeric(s, errors="coerce")


def _emp_length_to_years(series: pd.Series) -> pd.Series:
    """
    Convert employment length strings to numeric years.
    Examples:
      '< 1 year' -> 0
      '10+ years' -> 10
      '3 years' -> 3
      '1 year' -> 1
    """
    s = series.astype(str).str.strip()
    s = s.replace({"nan": np.nan, "None": np.nan, "": np.nan})
    s = s.replace({"< 1 year": "0", "10+ years": "10"})
    extracted = s.str.extract(r"(\d+)", expand=False)
    return pd.to_numeric(extracted, errors="coerce")


def main() -> int:
    print(f"[preprocess] Reading: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    print(f"[preprocess] Loaded shape: {df.shape}")

    _require_columns(df, EXPECTED_COLUMNS)

    # 1) Target definition 
    valid_statuses = {"Fully Paid", "Charged Off"}
    before = len(df)
    df = df[df["loan_status"].isin(valid_statuses)].copy()
    print(f"[preprocess] Filter loan_status to {valid_statuses}: {before} -> {len(df)}")

    df["default"] = (df["loan_status"] == "Charged Off").astype(int)
    df.drop(columns=["loan_status"], inplace=True)

    # 2) Standardize numeric fields 
    df["int_rate_pct"] = _to_percent_float(df["int_rate"])
    df["revol_util_pct"] = _to_percent_float(df["revol_util"])

    # DTI: profiling showed extreme values 
    df["dti"] = pd.to_numeric(df["dti"], errors="coerce")
    df.loc[df["dti"] > 100, "dti"] = np.nan
    df.loc[df["dti"] < 0, "dti"] = np.nan

    # annual_inc can have extreme outliers
    df["annual_inc"] = pd.to_numeric(df["annual_inc"], errors="coerce")

    # 3) Employment length
    df["emp_length_yrs"] = _emp_length_to_years(df["emp_length"])

    # 4) Credit history length (years)
    df["earliest_cr_line"] = pd.to_datetime(df["earliest_cr_line"], errors="coerce")
    reference_date = pd.Timestamp("2019-01-01")
    df["credit_history_years"] = (reference_date - df["earliest_cr_line"]).dt.days / 365.0

    # 5) Missing handling 
    required = ["loan_amnt", "annual_inc", "dti", "int_rate_pct", "credit_history_years"]
    before = len(df)
    df = df.dropna(subset=required).copy()
    print(f"[preprocess] Drop rows missing required {required}: {before} -> {len(df)}")

    # Impute optional fields
    if df["emp_length_yrs"].isna().any():
        df["emp_length_yrs"] = df["emp_length_yrs"].fillna(df["emp_length_yrs"].median())
    if df["revol_util_pct"].isna().any():
        df["revol_util_pct"] = df["revol_util_pct"].fillna(df["revol_util_pct"].median())

    # 6) Final dataset 
    final_cols = [
        "loan_amnt",
        "term",
        "installment",
        "purpose",
        "annual_inc",
        "dti",
        "int_rate_pct",
        "revol_util_pct",
        "delinq_2yrs",
        "inq_last_6mths",
        "open_acc",
        "total_acc",
        "emp_length_yrs",
        "credit_history_years",
        "default",
    ]

    # Ensure final columns exist
    missing_final = [c for c in final_cols if c not in df.columns]
    if missing_final:
        raise ValueError(f"Final columns missing after processing: {missing_final}")

    df_final = df[final_cols].copy()

    numeric_cols = [
        "loan_amnt",
        "installment",
        "annual_inc",
        "dti",
        "int_rate_pct",
        "revol_util_pct",
        "delinq_2yrs",
        "inq_last_6mths",
        "open_acc",
        "total_acc",
        "emp_length_yrs",
        "credit_history_years",
        "default",
    ]
    for c in numeric_cols:
        df_final[c] = pd.to_numeric(df_final[c], errors="coerce")

    # drop any rows that became NaN in numeric columns after coercion
    before = len(df_final)
    df_final = df_final.dropna(subset=numeric_cols).copy()
    print(f"[preprocess] Final numeric coercion drop: {before} -> {len(df_final)}")

    print(f"[preprocess] Writing: {OUTPUT_PATH}")
    df_final.to_csv(OUTPUT_PATH, index=False)

    print(f"[preprocess] Done. Final shape: {df_final.shape}")
    print(f"[preprocess] Default rate: {df_final['default'].mean():.4f}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[preprocess] ERROR: {e}", file=sys.stderr)
        raise
