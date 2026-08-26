from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
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


from backend.app.services.cash_engine import CashEngine
from backend.app.config import get_settings

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


@router_cash.post("/position/calculate", response_model=CashPositionRead)
async def calculate_cash_position(db: AsyncSession = Depends(get_db)):
    """Calculate and store a fresh cash position."""
    settings = get_settings()
    cash_engine = CashEngine(settings.app.opening_cash)
    position = await cash_engine.calculate_position(db)
    db.add(position)
    await db.commit()
    await db.refresh(position)
    return position


@router_cash.get("/variance", response_model=Dict[str, Any])
async def get_cash_variance(db: AsyncSession = Depends(get_db)):
    """Get detailed variance breakdown for the latest cash position."""
    result = await db.execute(
        select(CashPosition).order_by(CashPosition.date.desc()).limit(1)
    )
    position = result.scalar_one_or_none()
    if not position:
        raise HTTPException(404, "Cash position not found")
    
    # Return variance breakdown
    return {
        "total_variance": float(position.variance),
        "expected_cash": float(position.expected_cash),
        "bank_cash": float(position.bank_cash),
        "opening_balance": float(position.opening_balance),
        "confirmed_inflows": float(position.confirmed_inflows),
        "confirmed_outflows": float(position.confirmed_outflows),
        "pending_inflows": float(position.pending_inflows),
        "pending_outflows": float(position.pending_outflows),
        "adjustments": float(position.adjustments),
        "variance_breakdown": {
            "expected_vs_bank": float(position.variance),
            "pending_impact": float(position.pending_inflows - position.pending_outflows),
            "adjustments_impact": float(position.adjustments),
        }
    }


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


@router_cash.get("/forecast/summary")
async def get_forecast_summary(days: int = 30, db: AsyncSession = Depends(get_db)):
    """Get forecast summary grouped by horizon."""
    from backend.app.services.cash_engine import CashEngine
    from backend.app.config import get_settings
    
    settings = get_settings()
    cash_engine = CashEngine(settings.app.opening_cash)
    entries = await db.execute(
        select(ForecastEntry).where(ForecastEntry.horizon_days <= days).order_by(ForecastEntry.forecast_date)
    )
    entries = entries.scalars().all()
    
    horizons = [7, 14, 30]
    summary = {}
    for horizon in horizons:
        if horizon <= days:
            inflows = Decimal("0")
            outflows = Decimal("0")
            for entry in entries:
                if entry.horizon_days <= horizon:
                    if entry.amount > 0:
                        inflows += entry.amount
                    else:
                        outflows += abs(entry.amount)
            summary[horizon] = {
                "inflows": float(inflows),
                "outflows": float(outflows),
                "net": float(inflows - outflows),
            }
    return summary


@router_cash.post("/adjustment")
async def add_cash_adjustment(
    amount: Decimal,
    note: str,
    db: AsyncSession = Depends(get_db)
):
    """Add a manual cash adjustment (e.g., bank fees, interest, corrections)."""
    result = await db.execute(
        select(CashPosition).order_by(CashPosition.date.desc()).limit(1)
    )
    position = result.scalar_one_or_none()
    if not position:
        raise HTTPException(404, "No cash position exists to adjust")
    
    # Create a new position with the adjustment
    new_adjustments = position.adjustments + amount
    new_expected = position.expected_cash + amount
    new_variance = position.bank_cash - (position.opening_balance + position.confirmed_inflows - position.confirmed_outflows + new_adjustments)
    
    new_position = CashPosition(
        date=date.today(),
        opening_balance=position.opening_balance,
        confirmed_inflows=position.confirmed_inflows,
        confirmed_outflows=position.confirmed_outflows,
        pending_inflows=position.pending_inflows,
        pending_outflows=position.pending_outflows,
        adjustments=new_adjustments,
        expected_cash=new_expected,
        bank_cash=position.bank_cash,
        variance=new_variance,
    )
    db.add(new_position)
    await db.commit()
    await db.refresh(new_position)
    return new_position


router_metrics = APIRouter(prefix="/metrics", tags=["metrics"])


@router_metrics.get("/", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    from backend.app.evaluation.metrics import EvaluationEngine
    evaluator = EvaluationEngine()
    return await evaluator.compute_all(db)