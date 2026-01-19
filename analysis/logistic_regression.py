import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
import numpy as np

df = pd.read_csv("data/processed/risk_segments.csv")

features = [
    "loan_amnt",
    "int_rate_pct",
    "dti",
    "revol_util_pct",
    "credit_history_years",
    "delinq_2yrs",
    "inq_last_6mths",
]

X = df[features]
y = df["default"]

# Handle missing values
X = X.fillna(0)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

lr = LogisticRegression(max_iter=200)
lr.fit(X_train_scaled, y_train)

y_pred_proba = lr.predict_proba(X_test_scaled)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)

print("\nAUC Score:", round(auc, 4))
print("\nClassification Report:\n")
print(classification_report(y_test, (y_pred_proba > 0.5).astype(int)))

importance = pd.DataFrame({
    "feature": features,
    "coefficient": lr.coef_[0],
    "abs_importance": np.abs(lr.coef_[0])
}).sort_values(by="abs_importance", ascending=False)

print("\n Feature Importance (by coefficient magnitude):\n")
print(importance)


df["pred_default_prob"] = lr.predict_proba(scaler.transform(X))[:, 1]
df.to_csv("data/processed/risk_segments_with_predictions.csv", index=False)

print("\n Saved predictions → data/processed/risk_segments_with_predictions.csv")