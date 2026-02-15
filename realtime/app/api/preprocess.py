# app/api/preprocess.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import pandas as pd
import numpy as np


# Keep the same reference date you used in batch preprocessing
REFERENCE_DATE = pd.Timestamp("2019-01-01")


def _to_percent_float(x: Any) -> float | np.nan:
    """
    Convert values like '13.56%' to float 13.56.
    Accepts numeric values, strings, and missing values.
    """
    if x is None:
        return np.nan
    if isinstance(x, (int, float, np.number)):
        return float(x)
    s = str(x).strip()
    if s in {"", "nan", "None"}:
        return np.nan
    if s.endswith("%"):
        s = s[:-1]
    return pd.to_numeric(s, errors="coerce")


def _emp_length_to_years(x: Any) -> float | np.nan:
    """
    Convert employment length strings to numeric years.
    Examples: '< 1 year' -> 0, '10+ years' -> 10, '3 years' -> 3
    """
    if x is None:
        return np.nan
    s = str(x).strip()
    if s in {"", "nan", "None"}:
        return np.nan
    s = s.replace("< 1 year", "0").replace("10+ years", "10")
    extracted = pd.Series([s]).str.extract(r"(\d+)", expand=False).iloc[0]
    return pd.to_numeric(extracted, errors="coerce")


def _safe_float(x: Any) -> float | np.nan:
    if x is None:
        return np.nan
    return pd.to_numeric(x, errors="coerce")


def preprocess_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Turn one raw LendingClub-like event into clean features used by rules/models.

    IMPORTANT: This function is pure (no file I/O).
    It mirrors your scripts/preprocess.py logic.
    """
    # Required-ish fields (same as your batch "required" list)
    loan_amnt = _safe_float(event.get("loan_amnt"))
    annual_inc = _safe_float(event.get("annual_inc"))
    dti = _safe_float(event.get("dti"))
    int_rate_pct = _to_percent_float(event.get("int_rate"))
    revol_util_pct = _to_percent_float(event.get("revol_util"))

    # DTI cleaning (same constraints as batch)
    if pd.notna(dti):
        if dti > 100 or dti < 0:
            dti = np.nan

    emp_length_yrs = _emp_length_to_years(event.get("emp_length"))

    earliest_cr_line = pd.to_datetime(event.get("earliest_cr_line"), errors="coerce")
    credit_history_years = np.nan
    if pd.notna(earliest_cr_line):
        credit_history_years = (REFERENCE_DATE - earliest_cr_line).days / 365.0

    # Optional numeric fields used by rules
    delinq_2yrs = _safe_float(event.get("delinq_2yrs"))
    inq_last_6mths = _safe_float(event.get("inq_last_6mths"))
    open_acc = _safe_float(event.get("open_acc"))
    total_acc = _safe_float(event.get("total_acc"))
    installment = _safe_float(event.get("installment"))

    term = event.get("term")
    purpose = event.get("purpose")

    # Target (only if present; for streaming scoring you'll often NOT have this)
    loan_status = event.get("loan_status")
    default: Optional[int] = None
    if loan_status in {"Fully Paid", "Charged Off"}:
        default = int(loan_status == "Charged Off")

    features = {
        "loan_amnt": loan_amnt,
        "term": term,
        "installment": installment,
        "purpose": purpose,
        "annual_inc": annual_inc,
        "dti": dti,
        "int_rate_pct": int_rate_pct,
        "revol_util_pct": revol_util_pct,
        "delinq_2yrs": delinq_2yrs,
        "inq_last_6mths": inq_last_6mths,
        "open_acc": open_acc,
        "total_acc": total_acc,
        "emp_length_yrs": emp_length_yrs,
        "credit_history_years": credit_history_years,
        "default": default,
    }

    return features


def validate_required_features(features: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    For real-time scoring you can choose to reject events missing critical fields.
    Mirrors your batch dropna(subset=required) behavior.
    """
    required = ["loan_amnt", "annual_inc", "dti", "int_rate_pct", "credit_history_years"]
    missing = []
    for k in required:
        v = features.get(k)
        if v is None or (isinstance(v, float) and pd.isna(v)):
            missing.append(k)
    return (len(missing) == 0, missing)
