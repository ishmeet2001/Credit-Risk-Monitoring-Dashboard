from __future__ import annotations

import time
from typing import Any, Dict
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.api.preprocess import preprocess_event, validate_required_features
from app.api.rules import apply_rules
from app.api.schemas import ScoreRequest, ScoreResponse
from app.api.metrics import REQUESTS_TOTAL, SCORING_LATENCY, WATCHLIST_TOTAL
from app.api.db import insert_scored_row

import numpy as np

app = FastAPI(title="Credit Risk Scoring API", version="0.1.0")


def _to_python_types(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _to_python_types(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_python_types(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, (np.bool_)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return _to_python_types(obj.tolist())
    return obj


def _normalize_loan_id(event: Dict[str, Any]) -> str:
    if event.get("loan_id") is not None:
        return str(event["loan_id"])
    if event.get("id") is not None:
        return str(event["id"])
    # fallback: stable-ish
    return f"evt_{int(time.time() * 1000)}"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    t0 = time.time()
    endpoint = "/score"

    try:
        event = req.event
        loan_id = _normalize_loan_id(event)

        features = preprocess_event(event)
        ok, missing = validate_required_features(features)

        if req.reject_if_missing_required and not ok:
            REQUESTS_TOTAL.labels(endpoint=endpoint, status="rejected_missing").inc()
            return ScoreResponse(
                loan_id=loan_id,
                valid=False,
                missing_required=missing,
                features=_to_python_types(features),
                decision={
                    "risk_tier": "Rejected",
                    "early_warning_flag": 0,
                    "reasons": ["MISSING_REQUIRED_FIELDS"],
                },
            )

        decision = apply_rules(features)

        if req.persist_to_db:
            try:
                row = {
                    "loan_id": loan_id,
                    "purpose": features.get("purpose"),
                    "term": features.get("term"),
                    "loan_amnt": features.get("loan_amnt"),
                    "annual_inc": features.get("annual_inc"),
                    "dti": features.get("dti"),
                    "int_rate_pct": features.get("int_rate_pct"),
                    "revol_util_pct": features.get("revol_util_pct"),
                    "delinq_2yrs": features.get("delinq_2yrs"),
                    "inq_last_6mths": features.get("inq_last_6mths"),
                    "credit_history_years": features.get("credit_history_years"),
                    "emp_length_yrs": features.get("emp_length_yrs"),
                    "dti_band": decision.get("dti_band"),
                    "util_band": decision.get("util_band"),
                    "rate_band": decision.get("rate_band"),
                    "early_warning_flag": decision.get("early_warning_flag"),
                    "risk_tier": decision.get("risk_tier"),
                    "reasons": ",".join(decision.get("reasons", [])),
                }
                insert_scored_row(row)
            except Exception as e:
                print(f"Failed to persist: {e}")
                # Optional: REQUESTS_TOTAL.labels(endpoint=endpoint, status="db_error").inc()

        if decision.get("risk_tier") == "Watchlist":
            WATCHLIST_TOTAL.labels(source="api").inc()

        REQUESTS_TOTAL.labels(endpoint=endpoint, status="ok").inc()
        return ScoreResponse(
            loan_id=loan_id,
            valid=True,
            missing_required=[],
            features=_to_python_types(features),
            decision=_to_python_types(decision),
        )

    except Exception:
        REQUESTS_TOTAL.labels(endpoint=endpoint, status="error").inc()
        raise

    finally:
        SCORING_LATENCY.labels(endpoint=endpoint).observe(time.time() - t0)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
