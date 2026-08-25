from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class TransactionSource(str, Enum):
    BANK = "bank"
    LEDGER = "ledger"
    PROCESSOR = "processor"


class TransactionDirection(str, Enum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"


class MatchStatus(str, Enum):
    MATCHED = "matched"
    PROBABLE_MATCH = "probable_match"
    EXCEPTION = "exception"
    DUPLICATE = "duplicate"
    MISSING_COUNTERPARTY = "missing_counterparty"


class ExceptionType(str, Enum):
    AMOUNT_MISMATCH = "amount_mismatch"
    MISSING_RECORD = "missing_record"
    DUPLICATE = "duplicate"
    DATE_MISMATCH = "date_mismatch"
    CURRENCY_MISMATCH = "currency_mismatch"
    UNKNOWN_TRANSACTION = "unknown_transaction"
    PROCESSOR_FEE = "processor_fee"
    AMBIGUOUS_MATCH = "ambiguous_match"
    REFERENCE_MISMATCH = "reference_mismatch"


class ExceptionStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    UNRESOLVED = "unresolved"


class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    UNRESOLVED = "unresolved"


class AuditAction(str, Enum):
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


class SourceTransactionCreate(BaseModel):
    source: TransactionSource
    source_id: str
    transaction_date: date
    amount: Decimal
    currency: str = "INR"
    counterparty: str
    description: Optional[str] = None
    reference: Optional[str] = None
    direction: TransactionDirection
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class SourceTransactionRead(SourceTransactionCreate):
    id: int
    canonical_transaction_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CanonicalTransactionCreate(BaseModel):
    source: TransactionSource
    source_id: str
    date: date
    amount: Decimal
    currency: str = "INR"
    counterparty: str
    counterparty_loose: str = ""
    description: Optional[str] = None
    reference: Optional[str] = None
    direction: TransactionDirection
    txn_metadata: Dict[str, Any] = Field(default_factory=dict)


class CanonicalTransactionRead(CanonicalTransactionCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchCreate(BaseModel):
    canonical_transaction_id: int
    matched_transaction_id: int
    score: float
    method: str
    status: MatchStatus
    evidence: List[str] = Field(default_factory=list)


class MatchRead(MatchCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExceptionCreate(BaseModel):
    transaction_id: int
    type: ExceptionType
    severity: str
    status: ExceptionStatus = ExceptionStatus.OPEN
    confidence: Optional[float] = None
    description: str
    evidence: List[str] = Field(default_factory=list)


class ExceptionRead(ExceptionCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResolutionCreate(BaseModel):
    exception_id: int
    status: ResolutionStatus
    classification: ExceptionType
    confidence: float
    explanation: str
    evidence: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    validated: bool = False


class ResolutionRead(ResolutionCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CashPositionCreate(BaseModel):
    date: date
    opening_balance: Decimal
    confirmed_inflows: Decimal = Decimal("0")
    confirmed_outflows: Decimal = Decimal("0")
    pending_inflows: Decimal = Decimal("0")
    pending_outflows: Decimal = Decimal("0")
    adjustments: Decimal = Decimal("0")
    expected_cash: Decimal
    bank_cash: Decimal
    variance: Decimal = Decimal("0")


class CashPositionRead(CashPositionCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ForecastEntryCreate(BaseModel):
    forecast_date: date
    horizon_days: int
    event_name: str
    amount: Decimal
    frequency: str
    is_recurring: bool = True


class ForecastEntryRead(ForecastEntryCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogCreate(BaseModel):
    actor: str
    entity: str
    entity_id: Optional[int] = None
    action: AuditAction
    reason: Optional[str] = None
    audit_metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditLogRead(AuditLogCreate):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AIResolution(BaseModel):
    status: ResolutionStatus
    classification: ExceptionType
    confidence: float = Field(ge=0, le=1)
    explanation: str
    evidence: List[str]
    recommended_action: Optional[str] = None


class ReconciliationRunRequest(BaseModel):
    force_rerun: bool = False


class ReconciliationRunResponse(BaseModel):
    total_records: int
    matched: int
    probable_matches: int
    exceptions: int
    processing_time_seconds: float


class MetricsResponse(BaseModel):
    total_records: int
    matched_records: int
    match_rate: float
    accuracy: float
    false_match_rate: float
    exceptions_total: int
    exceptions_resolved: int
    exceptions_escalated: int
    exceptions_unresolved: int
    processing_time_seconds: float
    cash_variance: Decimal