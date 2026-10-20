"""Credit Decision Engine REST API (FastAPI)

Author: Ari Hendrawan (https://github.com/Arihkun)
"""

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from engine import DecisionEngine

app = FastAPI(
    title="Credit Decision Engine (CDE) API",
    description="Deterministic credit underwriting and rule evaluation engine built on GoRules Zen concepts.",
    version="2.4.1",
)

engine = DecisionEngine()


class ApplicantPayload(BaseModel):
    applicant_id: str = Field(..., example="APP-2026-9081")
    applicant_age: int = Field(..., ge=18, le=100, example=29)
    monthly_income: float = Field(..., gt=0, example=15000000.0)
    monthly_debt_obligations: float = Field(..., ge=0, example=3500000.0)
    credit_score: int = Field(..., ge=300, le=850, example=782)
    delinquency_history_count: int = Field(..., ge=0, example=0)
    loan_requested_idr: Optional[float] = Field(None, example=25000000.0)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "credit-decision-engine",
        "policy_version": engine.policy.get("version", "2.4.1"),
    }


@app.post("/api/v1/decide")
def evaluate_credit_application(payload: ApplicantPayload):
    try:
        result = engine.evaluate(payload.model_dump())
        return {
            "applicant_id": payload.applicant_id,
            "evaluation": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
