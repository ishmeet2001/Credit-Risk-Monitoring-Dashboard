"""
test_refactor.py

Purpose:
- Test the refactored preprocessing and rules functions
- Validate that single-event processing works correctly
- Demonstrate the API for real-time use

Run:
    python app/test_refactor.py
"""

from api.preprocess import preprocess_event
from api.rules import apply_rules


def test_single_event():
    """Test processing a single loan event."""
    
    # Sample event (one row as dict)
    event = {
        "loan_amnt": 10000,
        "term": " 36 months",
        "int_rate": "12.5%",
        "installment": 334.67,
        "purpose": "debt_consolidation",
        "annual_inc": 50000,
        "dti": 35.2,
        "revol_util": "85.5%",
        "delinq_2yrs": 1,
        "inq_last_6mths": 3,
        "open_acc": 8,
        "total_acc": 15,
        "emp_length": "5 years",
        "earliest_cr_line": "2010-01-15",
    }
    
    print("=" * 60)
    print("TEST: Single Event Processing")
    print("=" * 60)
    
    # Step 1: Preprocess
    print("\n[1] Preprocessing event...")
    features = preprocess_event(event)
    
    print("\nExtracted Features:")
    for key, value in features.items():
        print(f"  {key:25} = {value}")
    
    # Step 2: Apply rules
    print("\n[2] Applying risk rules...")
    decision = apply_rules(features)
    
    print("\nRisk Decision:")
    print(f"  Risk Tier:            {decision['risk_tier']}")
    print(f"  Early Warning Flag:   {decision['early_warning_flag']}")
    print(f"  DTI Band:             {decision['dti_band']}")
    print(f"  Utilization Band:     {decision['util_band']}")
    print(f"  Interest Rate Band:   {decision['rate_band']}")
    
    print("\nReasons:")
    for reason in decision['reasons']:
        print(f"  - {reason}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("=" * 60)


def test_low_risk_event():
    """Test a low-risk loan event."""
    
    event = {
        "loan_amnt": 5000,
        "term": " 36 months",
        "int_rate": "8.5%",
        "installment": 157.89,
        "purpose": "home_improvement",
        "annual_inc": 75000,
        "dti": 15.0,
        "revol_util": "25%",
        "delinq_2yrs": 0,
        "inq_last_6mths": 0,
        "open_acc": 10,
        "total_acc": 20,
        "emp_length": "10+ years",
        "earliest_cr_line": "2005-03-20",
    }
    
    print("\n" + "=" * 60)
    print("TEST: Low Risk Event")
    print("=" * 60)
    
    features = preprocess_event(event)
    decision = apply_rules(features)
    
    print(f"\nRisk Tier: {decision['risk_tier']}")
    print(f"Early Warning: {decision['early_warning_flag']}")
    print(f"Reasons: {', '.join(decision['reasons'])}")
    
    assert decision['risk_tier'] == "Low", "Expected Low risk tier"
    print("\n✅ Low risk test passed!")


def test_elevated_risk_event():
    """Test an elevated-risk loan event."""
    
    event = {
        "loan_amnt": 15000,
        "term": " 60 months",
        "int_rate": "16.5%",
        "installment": 375.50,
        "purpose": "credit_card",
        "annual_inc": 40000,
        "dti": 38.0,  # High DTI
        "revol_util": "65%",  # Moderate utilization
        "delinq_2yrs": 0,  # No delinquencies
        "inq_last_6mths": 1,  # Only 1 inquiry
        "open_acc": 6,
        "total_acc": 12,
        "emp_length": "3 years",
        "earliest_cr_line": "2012-06-10",
    }
    
    print("\n" + "=" * 60)
    print("TEST: Elevated Risk Event")
    print("=" * 60)
    
    features = preprocess_event(event)
    decision = apply_rules(features)
    
    print(f"\nRisk Tier: {decision['risk_tier']}")
    print(f"Early Warning: {decision['early_warning_flag']}")
    print(f"Reasons: {', '.join(decision['reasons'])}")
    
    assert decision['risk_tier'] == "Elevated", "Expected Elevated risk tier"
    assert decision['early_warning_flag'] == 0, "Should not trigger early warning (no credit stress)"
    print("\n✅ Elevated risk test passed!")


if __name__ == "__main__":
    # Run all tests
    test_single_event()
    test_low_risk_event()
    test_elevated_risk_event()
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. ✅ Refactored preprocessing into preprocess_event()")
    print("  2. ✅ Refactored rules into apply_rules()")
    print("  3. ✅ Tested with sample events")
    print("  4. 🚀 Ready for Step 2: Real-time streaming!")
    print("=" * 60)
