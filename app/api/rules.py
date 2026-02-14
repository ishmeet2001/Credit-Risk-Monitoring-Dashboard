"""
rules.py

Purpose:
- Apply deterministic, rule-based risk assessment to a single loan event
- Generate risk tier, early warning flags, and explanations
- Designed for real-time decision making

Input:
- features: Dictionary of preprocessed loan features

Output:
- Dictionary with risk_tier, early_warning_flag, and reasons
"""

from __future__ import annotations
from typing import Any


def _get_dti_band(dti: float | None) -> str:
    """
    Classify DTI (Debt-to-Income) into risk bands.
    
    Bins: [0, 20, 30, 40, 100]
    Labels: Low, Moderate, High, Very High
    """
    if dti is None:
        return "Unknown"
    
    if dti <= 20:
        return "Low"
    elif dti <= 30:
        return "Moderate"
    elif dti <= 40:
        return "High"
    else:
        return "Very High"


def _get_util_band(revol_util_pct: float | None) -> str:
    """
    Classify revolving utilization into risk bands.
    
    Bins: [0, 30, 60, 80, 100]
    Labels: Low, Moderate, High, Very High
    """
    if revol_util_pct is None:
        return "Unknown"
    
    if revol_util_pct <= 30:
        return "Low"
    elif revol_util_pct <= 60:
        return "Moderate"
    elif revol_util_pct <= 80:
        return "High"
    else:
        return "Very High"


def _get_rate_band(int_rate_pct: float | None) -> str:
    """
    Classify interest rate into risk bands.
    
    Bins: [0, 10, 15, 20, 100]
    Labels: Low, Moderate, High, Very High
    """
    if int_rate_pct is None:
        return "Unknown"
    
    if int_rate_pct <= 10:
        return "Low"
    elif int_rate_pct <= 15:
        return "Moderate"
    elif int_rate_pct <= 20:
        return "High"
    else:
        return "Very High"


def apply_rules(features: dict[str, Any]) -> dict[str, Any]:
    """
    Apply rule-based risk assessment to preprocessed loan features.
    
    This function implements the same logic as scripts/risk_rules.py
    but operates on a single event instead of a batch DataFrame.
    
    Args:
        features: Dictionary of preprocessed loan features
        
    Returns:
        Dictionary containing:
            - risk_tier: "Watchlist", "Elevated", or "Low"
            - early_warning_flag: 1 or 0
            - reasons: List of strings explaining which rules fired
            - dti_band: Risk band for DTI
            - util_band: Risk band for revolving utilization
            - rate_band: Risk band for interest rate
            
    Example:
        >>> features = {
        ...     "dti": 35.0,
        ...     "revol_util_pct": 85.0,
        ...     "delinq_2yrs": 1,
        ...     "inq_last_6mths": 3,
        ...     ...
        ... }
        >>> decision = apply_rules(features)
        >>> print(decision["risk_tier"])  # "Watchlist"
        >>> print(decision["reasons"])  # ["High DTI (35.0)", ...]
    """
    # Extract features with defaults
    dti = features.get("dti")
    revol_util_pct = features.get("revol_util_pct")
    int_rate_pct = features.get("int_rate_pct")
    delinq_2yrs = features.get("delinq_2yrs", 0)
    inq_last_6mths = features.get("inq_last_6mths", 0)
    
    # Calculate risk bands
    dti_band = _get_dti_band(dti)
    util_band = _get_util_band(revol_util_pct)
    rate_band = _get_rate_band(int_rate_pct)
    
    # Initialize reasons list
    reasons = []
    
    # Early Warning Flag Logic
    # Condition 1: High leverage (DTI >= 30 OR revol_util >= 80)
    high_leverage = False
    if dti is not None and dti >= 30:
        high_leverage = True
        reasons.append(f"High DTI ({dti:.1f}%)")
    
    if revol_util_pct is not None and revol_util_pct >= 80:
        high_leverage = True
        reasons.append(f"Very high revolving utilization ({revol_util_pct:.1f}%)")
    
    # Condition 2: Credit stress signals (delinquencies OR recent inquiries)
    credit_stress = False
    if delinq_2yrs is not None and delinq_2yrs > 0:
        credit_stress = True
        reasons.append(f"Recent delinquencies ({int(delinq_2yrs)})")
    
    if inq_last_6mths is not None and inq_last_6mths >= 2:
        credit_stress = True
        reasons.append(f"Multiple recent credit inquiries ({int(inq_last_6mths)})")
    
    # Early warning flag = both conditions met
    early_warning_flag = 1 if (high_leverage and credit_stress) else 0
    
    # Risk Tier Assignment
    if early_warning_flag == 1:
        risk_tier = "Watchlist"
    elif dti_band in ["High", "Very High"] or util_band in ["High", "Very High"]:
        risk_tier = "Elevated"
        if dti_band in ["High", "Very High"] and "High DTI" not in " ".join(reasons):
            reasons.append(f"DTI in {dti_band} band")
        if util_band in ["High", "Very High"] and "revolving utilization" not in " ".join(reasons):
            reasons.append(f"Utilization in {util_band} band")
    else:
        risk_tier = "Low"
        if not reasons:
            reasons.append("All metrics within acceptable ranges")
    
    # Return decision
    return {
        "risk_tier": risk_tier,
        "early_warning_flag": early_warning_flag,
        "reasons": reasons,
        "dti_band": dti_band,
        "util_band": util_band,
        "rate_band": rate_band,
    }
