"""
Quick Reference: Using the Refactored API

This shows how to use the new event-based functions in your code.
"""

from app.api import preprocess_event, apply_rules

# ============================================================
# Example 1: Process a single loan application
# ============================================================

# Raw loan application data (from API, Kafka, etc.)
loan_application = {
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

# Step 1: Preprocess the event
features = preprocess_event(loan_application)

# Step 2: Apply risk rules
decision = apply_rules(features)

# Step 3: Use the decision
print(f"Risk Tier: {decision['risk_tier']}")
print(f"Early Warning: {decision['early_warning_flag']}")
print(f"Reasons: {decision['reasons']}")

# ============================================================
# Example 2: API endpoint (FastAPI example)
# ============================================================

"""
from fastapi import FastAPI
from app.api import preprocess_event, apply_rules

app = FastAPI()

@app.post("/assess-risk")
def assess_risk(loan_data: dict):
    features = preprocess_event(loan_data)
    decision = apply_rules(features)
    return {
        "risk_tier": decision["risk_tier"],
        "early_warning": decision["early_warning_flag"],
        "reasons": decision["reasons"],
        "bands": {
            "dti": decision["dti_band"],
            "utilization": decision["util_band"],
            "interest_rate": decision["rate_band"],
        }
    }
"""

# ============================================================
# Example 3: Kafka consumer (streaming example)
# ============================================================

"""
from kafka import KafkaConsumer
import json
from app.api import preprocess_event, apply_rules

consumer = KafkaConsumer(
    'loan-applications',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    loan_event = message.value
    
    # Process the event
    features = preprocess_event(loan_event)
    decision = apply_rules(features)
    
    # Take action based on decision
    if decision['early_warning_flag'] == 1:
        send_alert(loan_event, decision)
    
    # Log to database
    save_decision(loan_event, features, decision)
"""

# ============================================================
# Example 4: Batch processing (still works!)
# ============================================================

"""
import pandas as pd
from app.api import preprocess_event, apply_rules

# Read CSV
df = pd.read_csv('data/new_loans.csv')

# Process each row
results = []
for _, row in df.iterrows():
    event = row.to_dict()
    features = preprocess_event(event)
    decision = apply_rules(features)
    results.append({
        **event,
        **decision
    })

# Save results
pd.DataFrame(results).to_csv('data/assessed_loans.csv', index=False)
"""
