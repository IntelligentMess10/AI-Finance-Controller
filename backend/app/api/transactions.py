from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import date
from decimal import Decimal
import time
import builtins

from backend.app.db.session import get_db
from backend.app.db.models import (
    SourceTransaction, CanonicalTransaction, Match, Exception, Resolution, 
    CashPosition, ForecastEntry, AuditLog, ResolutionStatus, MatchStatus,
    ExceptionStatus, ExceptionType, TransactionSource
)
from backend.app.schemas.canonical import (
    SourceTransactionCreate, SourceTransactionRead,
    CanonicalTransactionCreate, CanonicalTransactionRead,
    MatchCreate, MatchRead,
    ExceptionCreate, ExceptionRead,
    ResolutionCreate, ResolutionRead,
    CashPositionCreate, CashPositionRead,
    ForecastEntryCreate, ForecastEntryRead,
    AuditLogCreate, AuditLogRead,
    ReconciliationRunRequest, ReconciliationRunResponse, ReconciliationStats,
    PaginatedMatchResponse, MetricsResponse,
)

from backend.app.db.session import get_db
from backend.app.db.models import (
    SourceTransaction, CanonicalTransaction, Match, Exception, Resolution, 
    CashPosition, ForecastEntry, AuditLog, ResolutionStatus, MatchStatus,
    ExceptionStatus, ExceptionType, TransactionSource
)
from backend.app.services import ai_investigator
from backend.app.services.matching import ReconciliationEngine
from backend.app.services.ai_investigator import AIInvestigator
from backend.app.services.cash_engine import CashEngine
from backend.app.config import get_settings

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

# Separate router for exceptions without /reconciliation prefix
router_exceptions = APIRouter(prefix="/exceptions", tags=["exceptions"])


@router_reconciliation.post("/run", response_model=None)
async def run_reconciliation(request: dict, db: AsyncSession = Depends(get_db)):
    """Run full reconciliation pipeline."""
    import time
    from backend.app.services.matching import ReconciliationEngine
    from backend.app.services.ai_investigator import AIInvestigator
    from backend.app.services.cash_engine import CashEngine
    from backend.app.config import get_settings
    from backend.app.schemas.canonical import ReconciliationRunResponse, ReconciliationStats
    from backend.app.schemas.canonical import ReconciliationRunResponse, ReconciliationStats
    from backend.app.schemas.canonical import PaginatedMatchResponse
    
    start_time = time.time()
    settings = get_settings()
    engine = ReconciliationEngine(settings.matching)
    ai = AIInvestigator(settings.ai)
    cash = CashEngine(settings.app.opening_cash)
    
    # 1. Get all canonical transactions
    from sqlalchemy import select
    from backend.app.db.models import CanonicalTransaction
    result = await db.execute(select(CanonicalTransaction))
    transactions = list(result.scalars().all())
    
    if not transactions:
        return {
            "stats": ReconciliationStats(
                total_records=0, matched=0, probable_matches=0, exceptions=0,
                processing_time_seconds=0.0
            ).model_dump(),
            matches: [],
            exceptions: [],
            cash_position: None,
            forecast_summary: {}
            }
    
    # Run reconciliation
    engine = ReconciliationEngine(settings.matching)
    ai = AIInvestigator(settings.ai)
    cash = CashEngine(settings.app.opening_cash)
    
    result = await engine.run(db, transactions)
    all_matches = result["matches"]
    all_exceptions = result["exceptions"]
    
    # AI investigation for exceptions
    ai = AIInvestigator(settings.ai)
    
    for exc in result["exceptions"]:
        try:
            exc_result = await db.execute(select(Exception).where(Exception.id == exc.id))
            exc_obj = exc_result.scalar_one_or_none()
            if exc_obj:
                resolution = await ai.investigate(db, exc_obj)
                if resolution.confidence < settings.ai.confidence_auto_resolve:
                    resolution.status = ResolutionStatus.ESCALATED
                    resolution.explanation += f" [Auto-escalated: confidence {resolution.confidence:.2f} below threshold {settings.ai.confidence_auto_resolve}]"
                
                resolution.validated = True
                db.add(resolution)
                await db.commit()
                await db.refresh(resolution)
                
                exc_obj.status = resolution.status
                await db.commit()
        except builtins.Exception as e:
            # Auto-escalate on any error
            await ai_investigator.close()
            raise HTTPException(500, f"Investigation failed: {str(e)}")
    
    # Calculate cash position
    cash_position = await cash.calculate_position(db)
    
    # Generate forecast
    forecast_entries = await cash.generate_forecast(db)
    
    # Prepare response
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Prepare response
    matches = result["matches"]
    exceptions = result["exceptions"]
    
    # Get matches with details
    match_objects = []
    for m in matches:
        match_obj = await db.get(Match, m.id)
        if match_obj:
            match_objects.append(match_obj)
    
    exception_objects = []
    for exc in exceptions:
        exc_obj = await db.get(Exception, exc.id)
        if exc_obj:
            exception_objects.append(exc_obj)
    
    # Get cash position
    cash_position = await db.get(CashPosition, cash_position.id) if cash_position else None
    
    # Get forecast summary
    forecast_entries = await db.execute(select(ForecastEntry))
    forecast_entries = forecast_entries.scalars().all()
    
    horizons = [7, 14, 30]
    forecast_summary = {}
    for horizon in [7, 14, 30]:
        inflows = sum(e.amount for e in forecast_entries if e.horizon_days <= horizon and e.amount > 0)
        outflows = sum(abs(e.amount) for e in forecast_entries if e.horizon_days <= horizon and e.amount < 0)
        forecast_summary[horizon] = {
            "inflows": float(inflows),
            "outflows": float(outflows),
            "net": float(inflows - outflows)
        }
    
    # Build response
    matched_count = len([m for m in matches if m.status == MatchStatus.MATCHED])
    probable_count = len([m for m in matches if m.status == MatchStatus.PROBABLE_MATCH])
    
    stats = ReconciliationStats(
        total_records=len(transactions),
        matched=len([m for m in matches if m.status == MatchStatus.MATCHED]),
        probable_matches=len([m for m in matches if m.status == MatchStatus.PROBABLE_MATCH]),
        exceptions=len(exceptions),
        processing_time_seconds=time.time() - start_time
    )
    
    return {
        "stats": stats.model_dump(),
        matches: match_objects,
        exceptions: exception_objects,
        cash_position: cash_position.model_dump() if cash_position else None,
        forecast_summary: forecast_summary
    }


@router_reconciliation.get("/results", response_model=List[MatchRead])
async def get_matches(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).offset(skip).limit(limit))
    return result.scalars().all()


@router_reconciliation.get("/results/paginated", response_model=PaginatedMatchResponse)
async def get_matches_paginated(page: int = 1, limit: int = 50, status: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Match)
    if status:
        query = query.where(Match.status == status)
    # Get total count
    from sqlalchemy import func
    count_result = await db.execute(select(func.count(Match.id)))
    total = count_result.scalar()
    
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return PaginatedMatchResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )


@router_reconciliation.get("/exceptions", response_model=List[ExceptionRead])
async def get_exceptions(status: str = None, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(Exception)
    if status:
        query = query.where(Exception.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router_reconciliation.post("/exceptions/{exc_id}/investigate", response_model=dict)
async def investigate_exception_reconciliation(exc_id: int, db: AsyncSession = Depends(get_db)):
    """Investigate an exception using AI investigator (under /reconciliation prefix)."""
    settings = get_settings()
    ai_investigator = AIInvestigator(settings.ai)
    
    try:
        # Get the exception
        result = await db.execute(select(Exception).where(Exception.id == exc_id))
        exc = result.scalar_one_or_none()
        if not exc:
            raise HTTPException(404, "Exception not found")
        
        # Run AI investigation
        resolution = await ai_investigator.investigate(db, exc)
        
        # Validate confidence threshold
        if resolution.confidence < settings.ai.confidence_auto_resolve:
            resolution.status = ResolutionStatus.ESCALATED
            resolution.explanation += f" [Auto-escalated: confidence {resolution.confidence:.2f} below threshold {settings.ai.confidence_auto_resolve}]"
        
        # Mark as validated and save
        resolution.validated = True
        db.add(resolution)
        await db.commit()
        await db.refresh(resolution)
        
        # Update exception status
        exc_obj = await db.get(Exception, exc_id)
        exc_obj.status = resolution.status
        await db.commit()
        
        return {
            "status": "completed",
            "exception_id": exc_id,
            "resolution_id": resolution.id,
            "status": resolution.status.value,
            "classification": resolution.classification.value,
            "confidence": resolution.confidence,
            "explanation": resolution.explanation,
            "evidence": resolution.evidence,
            "recommended_action": resolution.recommended_action,
        }
    except builtins.Exception as e:
        # Auto-escalate on any error
        await ai_investigator.close()
        raise HTTPException(500, f"Investigation failed: {str(e)}")


# Separate router for exceptions without /reconciliation prefix
router_exceptions = APIRouter(prefix="/exceptions", tags=["exceptions"])


@router_exceptions.post("/{exc_id}/investigate", response_model=dict)
async def investigate_exception(exc_id: int, db: AsyncSession = Depends(get_db)):
    """Investigate an exception using AI investigator (under /exceptions prefix)."""
    settings = get_settings()
    ai_investigator = AIInvestigator(settings.ai)
    
    try:
        # Get the exception
        result = await db.execute(select(Exception).where(Exception.id == exc_id))
        exc = result.scalar_one_or_none()
        if not exc:
            raise HTTPException(404, "Exception not found")
        
        # Run AI investigation
        resolution = await ai_investigator.investigate(db, exc)
        
        # Validate confidence threshold
        if resolution.confidence < settings.ai.confidence_auto_resolve:
            resolution.status = ResolutionStatus.ESCALATED
            resolution.explanation += f" [Auto-escalated: confidence {resolution.confidence:.2f} below threshold {settings.ai.confidence_auto_resolve}]"
        
        # Mark as validated and save
        resolution.validated = True
        db.add(resolution)
        await db.commit()
        await db.refresh(resolution)
        
        # Update exception status
        exc_obj = await db.get(Exception, exc_id)
        exc_obj.status = resolution.status
        await db.commit()
        
        return {
            "status": "completed",
            "exception_id": exc_id,
            "resolution_id": resolution.id,
            "status": resolution.status.value,
            "classification": resolution.classification.value,
            "confidence": resolution.confidence,
            "explanation": resolution.explanation,
            "evidence": resolution.evidence,
            "recommended_action": resolution.recommended_action,
        }
    except builtins.Exception as e:
        # Auto-escalate on any error
        await ai_investigator.close()
        raise HTTPException(500, f"Investigation failed: {str(e)}")


router_metrics = APIRouter(prefix="/metrics", tags=["metrics"])


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
            inflows = sum(e.amount for e in entries if e.horizon_days <= horizon and e.amount > 0)
            outflows = abs(sum(e.amount for e in entries if e.horizon_days <= horizon and e.amount < 0))
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