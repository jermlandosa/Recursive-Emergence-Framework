from fastapi import FastAPI, HTTPException

from rve.ledger import Claim, User, get_session


app = FastAPI(title="RVE API")


def get_user(email: str) -> User:
    s = get_session()
    u = s.query(User).filter_by(email=email).one_or_none()
    if not u:
        raise HTTPException(401, "Unknown user")
    return u


@app.get("/claims")
def list_claims(email: str):
    s = get_session()
    u = get_user(email)
    rows = (
        s.query(Claim)
        .filter(Claim.user_id == u.id)
        .order_by(Claim.created_at.desc())
        .all()
    )
    return [
        {
            "claim_id": r.claim_id,
            "text": r.text,
            "drift_score": r.drift_score,
            "confidence_index": r.confidence_index,
            "provenance_completeness": r.provenance_completeness,
            "independence_score": r.independence_score,
            "created_at": r.created_at.isoformat(),
            "volatility": r.volatility,
        }
        for r in rows
    ]

