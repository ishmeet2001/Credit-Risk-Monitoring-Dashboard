"""
risk_rules.py

Purpose:
- Apply deterministic, rule-based risk banding
- Create an early-warning watchlist for credit risk monitoring
- Produce datasets for Excel validation and Tableau visualization

Inputs:
- data/processed/clean_loans.csv

Outputs:
- data/processed/risk_segments.csv
- data/processed/early_warning_watchlist.csv

Notes:
- This file contains no machine learning
- Rules are explainable, auditable, and business-driven
"""

import pandas as pd
import numpy as np


INPUT_PATH = "data/processed/clean_loans.csv"
SEGMENTS_PATH = "data/processed/risk_segments.csv"
WATCHLIST_PATH = "data/processed/early_warning_watchlist.csv"


def main() -> None:
    print("[risk_rules] Loading clean dataset")
    df = pd.read_csv(INPUT_PATH)
    print("[risk_rules] Shape:", df.shape)

    
    # DTI risk bands
    df["dti_band"] = pd.cut(
        df["dti"],
        bins=[0, 20, 30, 40, 100],
        labels=["Low", "Moderate", "High", "Very High"],
        right=True
    )

    # Revolving utilization risk bands
    df["util_band"] = pd.cut(
        df["revol_util_pct"],
        bins=[0, 30, 60, 80, 100],
        labels=["Low", "Moderate", "High", "Very High"],
        right=True
    )

    # Interest rate risk bands
    df["rate_band"] = pd.cut(
        df["int_rate_pct"],
        bins=[0, 10, 15, 20, 100],
        labels=["Low", "Moderate", "High", "Very High"],
        right=True
    )

    df["early_warning_flag"] = (
        (
            (df["dti"] >= 30) |
            (df["revol_util_pct"] >= 80)
        )
        &
        (
            (df["delinq_2yrs"] > 0) |
            (df["inq_last_6mths"] >= 2)
        )
    ).astype(int)

    
    def assign_risk_tier(row):
        if row["early_warning_flag"] == 1:
            return "Watchlist"
        elif (
            row["dti_band"] in ["High", "Very High"]
            or row["util_band"] in ["High", "Very High"]
        ):
            return "Elevated"
        else:
            return "Low"

    df["risk_tier"] = df.apply(assign_risk_tier, axis=1)

   
    risk_columns = [
        "loan_amnt",
        "purpose",
        "annual_inc",
        "dti",
        "dti_band",
        "revol_util_pct",
        "util_band",
        "int_rate_pct",
        "rate_band",
        "delinq_2yrs",
        "inq_last_6mths",
        "credit_history_years",
        "early_warning_flag",
        "risk_tier",
        "default"
    ]

    df[risk_columns].to_csv(SEGMENTS_PATH, index=False)
    print("[risk_rules] Risk segments saved to:", SEGMENTS_PATH)

    
    watchlist = df[df["early_warning_flag"] == 1].copy()

    watchlist.to_csv(WATCHLIST_PATH, index=False)
    print("[risk_rules] Early-warning watchlist saved to:", WATCHLIST_PATH)
    print("[risk_rules] Watchlist size:", watchlist.shape[0])


    kpi = pd.DataFrame([{
        "portfolio_rows": len(df),
        "baseline_default_rate": float(df["default"].mean()),
        "watchlist_rows": int(watchlist.shape[0]),
        "watchlist_share": float(watchlist.shape[0] / len(df)),
        "watchlist_default_rate": float(watchlist["default"].mean()) if watchlist.shape[0] > 0 else np.nan,
        "lift_vs_baseline": float(watchlist["default"].mean() / df["default"].mean()) if watchlist.shape[0] > 0 else np.nan
    }])

    kpi.to_csv("data/processed/kpi_summary.csv", index=False)
    print("[risk_rules] KPI summary saved to: data/processed/kpi_summary.csv")


if __name__ == "__main__":
    main()
