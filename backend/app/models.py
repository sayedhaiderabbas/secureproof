from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    original_filename: Mapped[str] = mapped_column(String(255))
    evidence_type: Mapped[str] = mapped_column(String(20))
    file_size: Mapped[int] = mapped_column(Integer)
    sha256_hash: Mapped[str] = mapped_column(String(64), index=True)
    storage_reference: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    status: Mapped[str] = mapped_column(String(30), default="READY")

    analysis: Mapped["Analysis | None"] = relationship(back_populates="evidence", uselist=False, cascade="all, delete-orphan")
    blockchain_proof: Mapped["BlockchainProof | None"] = relationship(back_populates="evidence", uselist=False, cascade="all, delete-orphan")
    verifications: Mapped[list["Verification"]] = relationship(back_populates="evidence", cascade="all, delete-orphan")
    events: Mapped[list["IncidentEvent"]] = relationship(back_populates="evidence", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[str] = mapped_column(ForeignKey("evidence.id"), unique=True)
    incident_category: Mapped[str] = mapped_column(String(100))
    risk_level: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text)
    indicators: Mapped[str] = mapped_column(Text)
    recommendations: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    evidence: Mapped[Evidence] = relationship(back_populates="analysis")


class BlockchainProof(Base):
    __tablename__ = "blockchain_proofs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[str] = mapped_column(ForeignKey("evidence.id"), unique=True)
    evidence_hash: Mapped[str] = mapped_column(String(64))
    network: Mapped[str] = mapped_column(String(80))
    contract_address: Mapped[str] = mapped_column(String(100))
    transaction_hash: Mapped[str] = mapped_column(String(100))
    block_number: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    status: Mapped[str] = mapped_column(String(30), default="CONFIRMED")
    evidence: Mapped[Evidence] = relationship(back_populates="blockchain_proof")


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[str] = mapped_column(ForeignKey("evidence.id"))
    expected_hash: Mapped[str] = mapped_column(String(64))
    actual_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[str] = mapped_column(String(30))
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    evidence: Mapped[Evidence] = relationship(back_populates="verifications")


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[str] = mapped_column(ForeignKey("evidence.id"))
    event_type: Mapped[str] = mapped_column(String(60))
    description: Mapped[str] = mapped_column(Text)
    transaction_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    evidence: Mapped[Evidence] = relationship(back_populates="events")
