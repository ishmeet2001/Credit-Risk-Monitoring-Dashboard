from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    event: Dict[str, Any] = Field(..., description="Raw loan application event as key/value JSON")
    reject_if_missing_required: bool = True
    persist_to_db: bool = False


class ScoreResponse(BaseModel):
    loan_id: str
    valid: bool
    missing_required: list[str] = []
    features: Dict[str, Any]
    decision: Dict[str, Any]
