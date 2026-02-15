# app/api/rules.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np


def _band(value: float, bins: list[float], labels: list[str]) -> str | None:
    """
    A tiny helper to reproduce your pd.cut bands for single values.
    Returns None if value is missing or out of range.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    # Use pandas cut on a single-element series to match pd.cut behavior
    s = pd.Series([value])
    out = pd.cut(s, bins=bins, labels=labels, right=True)
    v = out.iloc[0]
    return None if pd.isna(v) else str(v)


def apply_rules(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply your deterministic risk rules to ONE feature dict.
    Mirrors scripts/risk_rules.py, but returns 'reasons' for explainability.
    """
    dti = features.get("dti")
    util = features.get("revol_util_pct")
    rate = features.get("int_rate_pct")
    delinq_2yrs = features.get("delinq_2yrs")
    inq_last_6mths = features.get("inq_last_6mths")

    # Bands (same bins/labels as your batch script)
    dti_band = _band(dti, [0, 20, 30, 40, 100], ["Low", "Moderate", "High", "Very High"])
    util_band = _band(util, [0, 30, 60, 80, 100], ["Low", "Moderate", "High", "Very High"])
    rate_band = _band(rate, [0, 10, 15, 20, 100], ["Low", "Moderate", "High", "Very High"])

    # Early warning logic (same boolean structure as your batch script)
    cond_a = False
    if dti is not None and not (isinstance(dti, float) and pd.isna(dti)):
        cond_a = cond_a or (dti >= 30)
    if util is not None and not (isinstance(util, float) and pd.isna(util)):
        cond_a = cond_a or (util >= 80)

    cond_b = False
    if delinq_2yrs is not None and not (isinstance(delinq_2yrs, float) and pd.isna(delinq_2yrs)):
        cond_b = cond_b or (delinq_2yrs > 0)
    if inq_last_6mths is not None and not (isinstance(inq_last_6mths, float) and pd.isna(inq_last_6mths)):
        cond_b = cond_b or (inq_last_6mths >= 2)

    early_warning_flag = int(cond_a and cond_b)

    # Reasons (this is the new “next level” part)
    reasons: List[str] = []
    if early_warning_flag == 1:
        if dti is not None and not (isinstance(dti, float) and pd.isna(dti)) and dti >= 30:
            reasons.append("DTI>=30")
        if util is not None and not (isinstance(util, float) and pd.isna(util)) and util >= 80:
            reasons.append("REVOL_UTIL>=80")
        if delinq_2yrs is not None and not (isinstance(delinq_2yrs, float) and pd.isna(delinq_2yrs)) and delinq_2yrs > 0:
            reasons.append("DELINQ_2YRS>0")
        if inq_last_6mths is not None and not (isinstance(inq_last_6mths, float) and pd.isna(inq_last_6mths)) and inq_last_6mths >= 2:
            reasons.append("INQ_LAST_6MTHS>=2")

    # Risk tier (same priority order as your batch script)
    if early_warning_flag == 1:
        risk_tier = "Watchlist"
    elif (dti_band in {"High", "Very High"}) or (util_band in {"High", "Very High"}):
        risk_tier = "Elevated"
    else:
        risk_tier = "Low"

    return {
        "dti_band": dti_band,
        "util_band": util_band,
        "rate_band": rate_band,
        "early_warning_flag": early_warning_flag,
        "risk_tier": risk_tier,
        "reasons": reasons,
    }
