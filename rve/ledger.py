from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from .config import get_db_url


Base = declarative_base()


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), unique=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    volatility = Column(String(16), default="stable", index=True)
    provenance_completeness = Column(Float, default=0.0)
    independence_score = Column(Integer, default=0)
    drift_score = Column(Float, default=0.0, index=True)
    confidence_index = Column(Float, default=0.0, index=True)
    meta = Column(Text, default="{}")
    histories = relationship(
        "DriftHistory", back_populates="claim", cascade="all, delete-orphan"
    )
    artifacts = relationship(
        "Artifact", back_populates="claim", cascade="all, delete-orphan"
    )


Index("idx_claims_scores", Claim.drift_score, Claim.confidence_index)


class DriftHistory(Base):
    __tablename__ = "drift_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id_fk = Column(Integer, ForeignKey("claims.id"), index=True)
    t = Column(DateTime, default=datetime.utcnow, index=True)
    drift = Column(Float, nullable=False)
    claim = relationship("Claim", back_populates="histories")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id_fk = Column(Integer, ForeignKey("claims.id"), index=True)
    kind = Column(String(32))
    path_or_url = Column(Text, nullable=False)
    hash = Column(String(128))
    has_method_doc = Column(Boolean, default=False)
    has_timestamp = Column(Boolean, default=False)
    has_chain = Column(Boolean, default=False)
    is_reproducible = Column(Boolean, default=False)
    claim = relationship("Claim", back_populates="artifacts")


def get_engine():
    return create_engine(get_db_url(), future=True)


def get_session():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def next_claim_human_id(sess) -> str:
    count = sess.query(Claim).count() + 1
    return f"CLM-{count:04d}"


def add_claim(
    sess,
    text: str,
    volatility: str = "stable",
    prov_fields: int = 0,
    prov_total: int = 6,
    independent_sources: int = 1,
):
    pc = prov_fields / float(max(prov_total, 1))
    ind = max(0, min(3, independent_sources))
    drift = max(0.0, min(5.0, 3.0 - (pc * 2.0) - (0.4 * ind)))
    conf = max(
        0.0,
        min(1.0, (0.6 * pc + 0.4 * (ind / 3.0)) * (1.0 - (drift / 10.0))),
    )
    claim = Claim(
        claim_id=next_claim_human_id(sess),
        text=text,
        volatility=volatility,
        provenance_completeness=pc,
        independence_score=ind,
        drift_score=drift,
        confidence_index=conf,
        meta="{}",
    )
    sess.add(claim)
    sess.flush()
    sess.add(DriftHistory(claim_id_fk=claim.id, drift=drift))
    sess.commit()
    return claim


def append_drift(sess, claim: Claim, drift_value: float):
    claim.drift_score = float(drift_value)
    sess.add(DriftHistory(claim_id_fk=claim.id, drift=float(drift_value)))
    sess.commit()
    return claim

