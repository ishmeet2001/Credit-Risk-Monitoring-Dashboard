"""
Comprehensive test of updated preprocessing and rules functions
"""
from api.preprocess import preprocess_event, validate_required_features
from api.rules import apply_rules
import json


def test_watchlist_event():
    """Test a high-risk event that should trigger watchlist"""
    print("=" * 70)
    print("TEST 1: WATCHLIST EVENT")
    print("=" * 70)
    
    event = {
        "loan_amnt": 12000,
        "term": "36 months",
        "int_rate": "21.5%",
        "installment": 450.2,
        "purpose": "credit_card",
        "annual_inc": 55000,
        "dti": 33.2,
        "revol_util": "85%",
        "delinq_2yrs": 1,
        "inq_last_6mths": 2,
        "open_acc": 9,
        "total_acc": 22,
        "emp_length": "3 years",
        "earliest_cr_line": "2012-05-01",
    }
    
    features = preprocess_event(event)
    ok, missing = validate_required_features(features)
    
    print(f"\n✅ Validation: {ok}")
    if missing:
        print(f"❌ Missing fields: {missing}")
    
    print("\nPreprocessed Features:")
    for k, v in features.items():
        if v is not None:
            print(f"  {k:25} = {v}")
    
    decision = apply_rules(features)
    
    print("\n🎯 Risk Decision:")
    print(f"  Risk Tier:            {decision['risk_tier']}")
    print(f"  Early Warning Flag:   {decision['early_warning_flag']}")
    print(f"  DTI Band:             {decision['dti_band']}")
    print(f"  Utilization Band:     {decision['util_band']}")
    print(f"  Interest Rate Band:   {decision['rate_band']}")
    print(f"\n  Reasons:")
    for reason in decision['reasons']:
        print(f"    - {reason}")
    
    assert decision['risk_tier'] == "Watchlist"
    assert decision['early_warning_flag'] == 1
    print("\n✅ Test PASSED\n")


def test_low_risk_event():
    """Test a low-risk event"""
    print("=" * 70)
    print("TEST 2: LOW RISK EVENT")
    print("=" * 70)
    
    event = {
        "loan_amnt": 5000,
        "term": "36 months",
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
    
    features = preprocess_event(event)
    ok, missing = validate_required_features(features)
    
    print(f"\n✅ Validation: {ok}")
    
    decision = apply_rules(features)
    
    print("\n🎯 Risk Decision:")
    print(f"  Risk Tier:            {decision['risk_tier']}")
    print(f"  Early Warning Flag:   {decision['early_warning_flag']}")
    print(f"  DTI Band:             {decision['dti_band']}")
    print(f"  Utilization Band:     {decision['util_band']}")
    print(f"  Interest Rate Band:   {decision['rate_band']}")
    
    assert decision['risk_tier'] == "Low"
    assert decision['early_warning_flag'] == 0
    print("\n✅ Test PASSED\n")


def test_elevated_risk_event():
    """Test an elevated-risk event (high DTI but no credit stress)"""
    print("=" * 70)
    print("TEST 3: ELEVATED RISK EVENT")
    print("=" * 70)
    
    event = {
        "loan_amnt": 15000,
        "term": "60 months",
        "int_rate": "16.5%",
        "installment": 375.50,
        "purpose": "debt_consolidation",
        "annual_inc": 40000,
        "dti": 38.0,  # High DTI
        "revol_util": "65%",  # Moderate-High utilization
        "delinq_2yrs": 0,  # No delinquencies
        "inq_last_6mths": 1,  # Only 1 inquiry (not >= 2)
        "open_acc": 6,
        "total_acc": 12,
        "emp_length": "3 years",
        "earliest_cr_line": "2012-06-10",
    }
    
    features = preprocess_event(event)
    ok, missing = validate_required_features(features)
    
    print(f"\n✅ Validation: {ok}")
    
    decision = apply_rules(features)
    
    print("\n🎯 Risk Decision:")
    print(f"  Risk Tier:            {decision['risk_tier']}")
    print(f"  Early Warning Flag:   {decision['early_warning_flag']}")
    print(f"  DTI Band:             {decision['dti_band']}")
    print(f"  Utilization Band:     {decision['util_band']}")
    print(f"  Interest Rate Band:   {decision['rate_band']}")
    
    assert decision['risk_tier'] == "Elevated"
    assert decision['early_warning_flag'] == 0  # No credit stress
    print("\n✅ Test PASSED\n")


def test_missing_required_fields():
    """Test validation with missing required fields"""
    print("=" * 70)
    print("TEST 4: MISSING REQUIRED FIELDS")
    print("=" * 70)
    
    event = {
        "loan_amnt": 10000,
        "term": "36 months",
        # Missing int_rate, dti, earliest_cr_line
        "purpose": "credit_card",
        "annual_inc": 50000,
    }
    
    features = preprocess_event(event)
    ok, missing = validate_required_features(features)
    
    print(f"\n❌ Validation: {ok}")
    print(f"Missing fields: {missing}")
    
    assert not ok
    assert len(missing) > 0
    print("\n✅ Test PASSED (correctly detected missing fields)\n")


def test_json_serialization():
    """Test that decision output is JSON-serializable (important for APIs)"""
    print("=" * 70)
    print("TEST 5: JSON SERIALIZATION")
    print("=" * 70)
    
    event = {
        "loan_amnt": 10000,
        "term": "36 months",
        "int_rate": "12.5%",
        "installment": 334.67,
        "purpose": "debt_consolidation",
        "annual_inc": 50000,
        "dti": 25.0,
        "revol_util": "50%",
        "delinq_2yrs": 0,
        "inq_last_6mths": 1,
        "open_acc": 8,
        "total_acc": 15,
        "emp_length": "5 years",
        "earliest_cr_line": "2010-01-15",
    }
    
    features = preprocess_event(event)
    decision = apply_rules(features)
    
    # Try to serialize to JSON
    try:
        json_output = json.dumps(decision, indent=2)
        print("\n✅ Decision is JSON-serializable:")
        print(json_output)
        print("\n✅ Test PASSED\n")
    except TypeError as e:
        print(f"\n❌ JSON serialization failed: {e}")
        raise


if __name__ == "__main__":
    test_watchlist_event()
    test_low_risk_event()
    test_elevated_risk_event()
    test_missing_required_fields()
    test_json_serialization()
    
    print("=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print("\n✅ Updated functions are working correctly!")
    print("✅ Validation logic is working!")
    print("✅ JSON serialization is working!")
    print("✅ Ready for API/streaming integration!")
    print("=" * 70)
