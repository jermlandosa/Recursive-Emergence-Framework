from fastapi import FastAPI
from pydantic import BaseModel

from rve.ledger import Claim, get_session


app = FastAPI(title="RVE API")


class ClaimOut(BaseModel):
    claim_id: str
    text: str
    drift_score: float
    confidence_index: float
    provenance_completeness: float
    independence_score: int
    created_at: str
    volatility: str


@app.get("/claims", response_model=list[ClaimOut])
def list_claims():
    sess = get_session()
    rows = sess.query(Claim).order_by(Claim.created_at.desc()).all()
    return [
        ClaimOut(
            claim_id=r.claim_id,
            text=r.text,
            drift_score=r.drift_score,
            confidence_index=r.confidence_index,
            provenance_completeness=r.provenance_completeness,
            independence_score=r.independence_score,
            created_at=r.created_at.isoformat(),
            volatility=r.volatility,
        )
        for r in rows
    ]

