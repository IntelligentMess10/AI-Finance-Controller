from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import date
from decimal import Decimal

from backend.app.db.session import get_db
from backend.app.db.models import SourceTransaction, CanonicalTransaction, Match, Exception, Resolution, CashPosition, ForecastEntry, AuditLog
from backend.app.schemas.canonical import (
    SourceTransactionCreate, SourceTransactionRead,
    CanonicalTransactionCreate, CanonicalTransactionRead,
    MatchCreate, MatchRead,
    ExceptionCreate, ExceptionRead,
    ResolutionCreate, ResolutionRead,
    CashPositionCreate, CashPositionRead,
    ForecastEntryCreate, ForecastEntryRead,
    AuditLogCreate, AuditLogRead,
    ReconciliationRunRequest, ReconciliationRunResponse,
    MetricsResponse,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=SourceTransactionRead)
async def create_transaction(txn: SourceTransactionCreate, db: AsyncSession = Depends(get_db)):
    db_txn = SourceTransaction(**txn.model_dump())
    db.add(db_txn)
    await db.commit()
    await db.refresh(db_txn)
    return db_txn


@router.get("/", response_model=List[SourceTransactionRead])
async def list_transactions(
    source: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(SourceTransaction)
    if source:
        query = query.where(SourceTransaction.source == source)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{txn_id}", response_model=SourceTransactionRead)
async def get_transaction(txn_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SourceTransaction).where(SourceTransaction.id == txn_id))
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(404, "Transaction not found")
    return txn


router_canonical = APIRouter(prefix="/canonical", tags=["canonical"])


@router_canonical.post("/", response_model=CanonicalTransactionRead)
async def create_canonical(txn: CanonicalTransactionCreate, db: AsyncSession = Depends(get_db)):
    db_txn = CanonicalTransaction(**txn.model_dump())
    db.add(db_txn)
    await db.commit()
    await db.refresh(db_txn)
    return db_txn


@router_canonical.get("/", response_model=List[CanonicalTransactionRead])
async def list_canonical(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CanonicalTransaction).offset(skip).limit(limit))
    return result.scalars().all()


router_reconciliation = APIRouter(prefix="/reconciliation", tags=["reconciliation"])


@router_reconciliation.post("/run", response_model=ReconciliationRunResponse)
async def run_reconciliation(request: ReconciliationRunRequest, db: AsyncSession = Depends(get_db)):
    from backend.app.services.matching import ReconciliationEngine
    from backend.app.services.ai_investigator import AIInvestigator
    from backend.app.services.cash_engine import CashEngine
    from backend.app.config import get_settings
    
    settings = get_settings()
    engine = ReconciliationEngine(settings.matching)
    ai = AIInvestigator(settings.ai)
    cash = CashEngine(settings.app.opening_cash)
    
    # This will be implemented in the services
    return ReconciliationRunResponse(
        total_records=0,
        matched=0,
        probable_matches=0,
        exceptions=0,
        processing_time_seconds=0.0
    )


@router_reconciliation.get("/results", response_model=List[MatchRead])
async def get_matches(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).offset(skip).limit(limit))
    return result.scalars().all()


router_exceptions = APIRouter(prefix="/exceptions", tags=["exceptions"])


@router_exceptions.get("/", response_model=List[ExceptionRead])
async def list_exceptions(status: str = None, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(Exception)
    if status:
        query = query.where(Exception.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router_exceptions.get("/{exc_id}", response_model=ExceptionRead)
async def get_exception(exc_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exception).where(Exception.id == exc_id))
    exc = result.scalar_one_or_none()
    if not exc:
        raise HTTPException(404, "Exception not found")
    return exc


@router_exceptions.post("/{exc_id}/investigate")
async def investigate_exception(exc_id: int, db: AsyncSession = Depends(get_db)):
    # AI investigation will be implemented
    return {"status": "investigation_started", "exception_id": exc_id}


router_cash = APIRouter(prefix="/cash", tags=["cash"])


@router_cash.get("/position", response_model=CashPositionRead)
async def get_cash_position(date: date = None, db: AsyncSession = Depends(get_db)):
    query = select(CashPosition)
    if date:
        query = query.where(CashPosition.date == date)
    else:
        query = query.order_by(CashPosition.date.desc()).limit(1)
    result = await db.execute(query)
    position = result.scalar_one_or_none()
    if not position:
        raise HTTPException(404, "Cash position not found")
    return position


@router_cash.get("/forecast", response_model=List[ForecastEntryRead])
async def get_forecast(days: int = 30, db: AsyncSession = Depends(get_db)):
    from datetime import date, timedelta
    target_date = date.today() + timedelta(days=days)
    result = await db.execute(
        select(ForecastEntry)
        .where(ForecastEntry.horizon_days <= days)
        .order_by(ForecastEntry.forecast_date)
    )
    return result.scalars().all()


router_metrics = APIRouter(prefix="/metrics", tags=["metrics"])


@router_metrics.get("/", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    from backend.app.evaluation.metrics import EvaluationEngine
    evaluator = EvaluationEngine()
    return await evaluator.compute_all(db)