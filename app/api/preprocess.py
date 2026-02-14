"""
preprocess.py

Purpose:
- Process a single loan event in real-time
- Convert raw event data into analysis-ready features
- Designed for streaming/API use (no batch operations)

Input:
- event_dict: Dictionary containing raw loan application data

Output:
- feature_dict: Dictionary with cleaned, standardized features
"""

from __future__ import annotations
from typing import Any
import numpy as np
from datetime import datetime


def _to_percent_float(value: Any) -> float | None:
    """
    Convert strings like '13.56%' to float 13.56.
    Handles numeric inputs and missing values.
    
    Args:
        value: String, number, or None
        
    Returns:
        Float value or None if invalid
    """
    if value is None or value == "" or (isinstance(value, float) and np.isnan(value)):
        return None
    
    # Convert to string and clean
    s = str(value).strip()
    if s.lower() in ["nan", "none", ""]:
        return None
    
    # Remove % sign if present
    s = s.rstrip("%")
    
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _emp_length_to_years(value: Any) -> float | None:
    """
    Convert employment length strings to numeric years.
    
    Examples:
        '< 1 year' -> 0
        '10+ years' -> 10
        '3 years' -> 3
        '1 year' -> 1
        
    Args:
        value: Employment length string or number
        
    Returns:
        Years as float or None if invalid
    """
    if value is None or value == "" or (isinstance(value, float) and np.isnan(value)):
        return None
    
    s = str(value).strip()
    if s.lower() in ["nan", "none", ""]:
        return None
    
    # Handle special cases
    if "< 1" in s or "<1" in s:
        return 0.0
    if "10+" in s:
        return 10.0
    
    # Extract numeric part
    import re
    match = re.search(r"(\d+)", s)
    if match:
        return float(match.group(1))
    
    return None


def _calculate_credit_history_years(earliest_cr_line: Any, reference_date: str = "2019-01-01") -> float | None:
    """
    Calculate credit history length in years.
    
    Args:
        earliest_cr_line: Date string or datetime
        reference_date: Reference date for calculation (default: 2019-01-01)
        
    Returns:
        Years of credit history or None if invalid
    """
    if earliest_cr_line is None or earliest_cr_line == "":
        return None
    
    try:
        # Parse the earliest credit line date
        if isinstance(earliest_cr_line, str):
            cr_date = datetime.strptime(earliest_cr_line, "%Y-%m-%d")
        elif isinstance(earliest_cr_line, datetime):
            cr_date = earliest_cr_line
        else:
            return None
        
        # Parse reference date
        ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
        
        # Calculate years
        days_diff = (ref_date - cr_date).days
        return days_diff / 365.0
    except (ValueError, TypeError):
        return None


def preprocess_event(event_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Transform a single raw loan event into analysis-ready features.
    
    This function applies all the preprocessing logic from scripts/preprocess.py
    but operates on a single event instead of a batch DataFrame.
    
    Args:
        event_dict: Raw loan application data as dictionary
        
    Returns:
        Dictionary with cleaned, standardized features
        
    Example:
        >>> event = {
        ...     "loan_amnt": 10000,
        ...     "int_rate": "12.5%",
        ...     "dti": 25.3,
        ...     "emp_length": "3 years",
        ...     ...
        ... }
        >>> features = preprocess_event(event)
        >>> print(features["int_rate_pct"])  # 12.5
    """
    features = {}
    
    # 1) Convert percent fields to float
    features["int_rate_pct"] = _to_percent_float(event_dict.get("int_rate"))
    features["revol_util_pct"] = _to_percent_float(event_dict.get("revol_util"))
    
    # 2) DTI cleanup (cap extreme values)
    dti = event_dict.get("dti")
    if dti is not None:
        try:
            dti_float = float(dti)
            # Cap DTI to reasonable range [0, 100]
            if dti_float > 100 or dti_float < 0:
                features["dti"] = None
            else:
                features["dti"] = dti_float
        except (ValueError, TypeError):
            features["dti"] = None
    else:
        features["dti"] = None
    
    # 3) Employment length to years
    features["emp_length_yrs"] = _emp_length_to_years(event_dict.get("emp_length"))
    
    # 4) Credit history years
    features["credit_history_years"] = _calculate_credit_history_years(
        event_dict.get("earliest_cr_line")
    )
    
    # 5) Annual income (clean extreme outliers)
    annual_inc = event_dict.get("annual_inc")
    if annual_inc is not None:
        try:
            features["annual_inc"] = float(annual_inc)
        except (ValueError, TypeError):
            features["annual_inc"] = None
    else:
        features["annual_inc"] = None
    
    # 6) Loan amount
    loan_amnt = event_dict.get("loan_amnt")
    if loan_amnt is not None:
        try:
            features["loan_amnt"] = float(loan_amnt)
        except (ValueError, TypeError):
            features["loan_amnt"] = None
    else:
        features["loan_amnt"] = None
    
    # 7) Other numeric fields
    numeric_fields = [
        "installment",
        "delinq_2yrs",
        "inq_last_6mths",
        "open_acc",
        "total_acc",
    ]
    
    for field in numeric_fields:
        value = event_dict.get(field)
        if value is not None:
            try:
                features[field] = float(value)
            except (ValueError, TypeError):
                features[field] = None
        else:
            features[field] = None
    
    # 8) Categorical fields (pass through)
    features["term"] = event_dict.get("term")
    features["purpose"] = event_dict.get("purpose")
    
    # 9) Apply default imputation for optional fields
    # (In production, you'd use median values from training data)
    if features["emp_length_yrs"] is None:
        features["emp_length_yrs"] = 5.0  # Default median
    
    if features["revol_util_pct"] is None:
        features["revol_util_pct"] = 50.0  # Default median
    
    return features
