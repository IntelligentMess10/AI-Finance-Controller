import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy import (
    String, Text, Integer, Numeric, DateTime, Date, Enum, ForeignKey, Index, JSON, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.session import Base


class TransactionSource(str, enum.Enum):
    BANK = "bank"
    LEDGER = "ledger"
    PROCESSOR = "processor"


class TransactionDirection(str, enum.Enum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"


class MatchStatus(str, enum.Enum):
    MATCHED = "matched"
    PROBABLE_MATCH = "probable_match"
    EXCEPTION = "exception"
    DUPLICATE = "duplicate"
    MISSING_COUNTERPARTY = "missing_counterparty"


class ExceptionType(str, enum.Enum):
    AMOUNT_MISMATCH = "amount_mismatch"
    MISSING_RECORD = "missing_record"
    DUPLICATE = "duplicate"
    DATE_MISMATCH = "date_mismatch"
    CURRENCY_MISMATCH = "currency_mismatch"
    UNKNOWN_TRANSACTION = "unknown_transaction"
    PROCESSOR_FEE = "processor_fee"
    AMBIGUOUS_MATCH = "ambiguous_match"
    REFERENCE_MISMATCH = "reference_mismatch"


class ExceptionStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    UNRESOLVED = "unresolved"


class ResolutionStatus(str, enum.Enum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    UNRESOLVED = "unresolved"


class AuditAction(str, enum.Enum):
    DATA_IMPORTED = "DATA_IMPORTED"
    MATCH_CREATED = "MATCH_CREATED"
    MATCH_REJECTED = "MATCH_REJECTED"
    EXCEPTION_CREATED = "EXCEPTION_CREATED"
    AI_INVESTIGATION_STARTED = "AI_INVESTIGATION_STARTED"
    AI_EVIDENCE_RETRIEVED = "AI_EVIDENCE_RETRIEVED"
    AI_RESOLUTION_PROPOSED = "AI_RESOLUTION_PROPOSED"
    RESOLUTION_VALIDATED = "RESOLUTION_VALIDATED"
    EXCEPTION_RESOLVED = "EXCEPTION_RESOLVED"
    EXCEPTION_ESCALATED = "EXCEPTION_ESCALATED"
    CASH_RECALCULATED = "CASH_RECALCULATED"
    FORECAST_GENERATED = "FORECAST_GENERATED"


class SourceTransaction(Base):
    __tablename__ = "source_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[TransactionSource] = mapped_column(Enum(TransactionSource), nullable=False)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    counterparty: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    direction: Mapped[TransactionDirection] = mapped_column(Enum(TransactionDirection), nullable=False)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    canonical_transaction_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("canonical_transactions.id"), nullable=True)

    canonical: Mapped[Optional["CanonicalTransaction"]] = relationship(back_populates="source_transactions")

    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_source_source_id"),
        Index("ix_source_date_amount", "source", "transaction_date", "amount"),
    )


class CanonicalTransaction(Base):
    __tablename__ = "canonical_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[TransactionSource] = mapped_column(Enum(TransactionSource), nullable=False)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    counterparty: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    direction: Mapped[TransactionDirection] = mapped_column(Enum(TransactionDirection), nullable=False)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    source_transactions: Mapped[list["SourceTransaction"]] = relationship("SourceTransaction", back_populates="canonical")
    matches: Mapped[list["Match"]] = relationship(foreign_keys="Match.canonical_transaction_id", back_populates="canonical")
    matched_matches: Mapped[list["Match"]] = relationship(foreign_keys="Match.matched_transaction_id", back_populates="matched")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("canonical_transactions.id"), nullable=False)
    matched_transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("canonical_transactions.id"), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    canonical: Mapped["CanonicalTransaction"] = relationship(foreign_keys=[canonical_transaction_id], back_populates="matches")
    matched: Mapped["CanonicalTransaction"] = relationship(foreign_keys=[matched_transaction_id], back_populates="matched_matches")

    __table_args__ = (
        UniqueConstraint("canonical_transaction_id", "matched_transaction_id", name="uq_match_pair"),
    )


class Exception(Base):
    __tablename__ = "exceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("canonical_transactions.id"), nullable=False)
    type: Mapped[ExceptionType] = mapped_column(Enum(ExceptionType), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[ExceptionStatus] = mapped_column(Enum(ExceptionStatus), default=ExceptionStatus.OPEN, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transaction: Mapped["CanonicalTransaction"] = relationship()
    resolutions: Mapped[list["Resolution"]] = relationship(back_populates="exception")


class Resolution(Base):
    __tablename__ = "resolutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exception_id: Mapped[int] = mapped_column(Integer, ForeignKey("exceptions.id"), nullable=False)
    status: Mapped[ResolutionStatus] = mapped_column(Enum(ResolutionStatus), nullable=False)
    classification: Mapped[ExceptionType] = mapped_column(Enum(ExceptionType), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validated: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exception: Mapped["Exception"] = relationship(back_populates="resolutions")


class CashPosition(Base):
    __tablename__ = "cash_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    confirmed_inflows: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    confirmed_outflows: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    pending_inflows: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    pending_outflows: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    adjustments: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    expected_cash: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    bank_cash: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    variance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ForecastEntry(Base):
    __tablename__ = "forecast_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    actor: Mapped[str] = mapped_column(String(50), nullable=False)
    entity: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)