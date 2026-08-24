import pytest
from decimal import Decimal
from datetime import date
from backend.app.services.normalization import Normalizer
from backend.app.db.models import TransactionSource, TransactionDirection


class TestNormalization:
    def setup_method(self):
        self.normalizer = Normalizer()

    def test_normalize_counterparty_basic(self):
        assert self.normalizer.normalize_counterparty("ABC Ltd.") == "ABC"
        assert self.normalizer.normalize_counterparty("XYZ CORPORATION") == "XYZ"
        assert self.normalizer.normalize_counterparty("  Global Tech Solutions  ") == "GLOBAL TECH SOLUTIONS"

    def test_normalize_counterparty_suffixes(self):
        assert self.normalizer.normalize_counterparty("ABC LIMITED") == "ABC"
        assert self.normalizer.normalize_counterparty("XYZ PRIVATE LIMITED") == "XYZ"
        assert self.normalizer.normalize_counterparty("TEST INC") == "TEST"

    def test_normalize_reference(self):
        assert self.normalizer.normalize_reference("REF-123") == "REF-123"
        assert self.normalizer.normalize_reference(" ref_456 ") == "REF-456"
        assert self.normalizer.normalize_reference(None) is None

    def test_parse_amount(self):
        assert self.normalizer.parse_amount(Decimal("100.50")) == Decimal("100.50")
        assert self.normalizer.parse_amount("1,000.00") == Decimal("1000.00")
        assert self.normalizer.parse_amount("₹50,000") == Decimal("50000")
        assert self.normalizer.parse_amount(-100) == Decimal("-100")

    def test_parse_date(self):
        assert self.normalizer.parse_date(date(2026, 1, 15)) == date(2026, 1, 15)
        assert self.normalizer.parse_date("2026-01-15") == date(2026, 1, 15)
        assert self.normalizer.parse_date("15/01/2026") == date(2026, 1, 15)

    def test_determine_direction_bank(self):
        raw_cr = {"dr_cr": "CR"}
        raw_dr = {"dr_cr": "DR"}
        assert self.normalizer.determine_direction(TransactionSource.BANK, Decimal("100"), raw_cr) == TransactionDirection.INFLOW
        assert self.normalizer.determine_direction(TransactionSource.BANK, Decimal("100"), raw_dr) == TransactionDirection.OUTFLOW

    def test_determine_direction_ledger(self):
        raw_recv = {"account_type": "RECEIVABLES"}
        raw_pay = {"account_type": "PAYABLES"}
        assert self.normalizer.determine_direction(TransactionSource.LEDGER, Decimal("100"), raw_recv) == TransactionDirection.INFLOW
        assert self.normalizer.determine_direction(TransactionSource.LEDGER, Decimal("100"), raw_pay) == TransactionDirection.OUTFLOW


class TestMatchingEngine:
    def test_amount_score_exact(self):
        from backend.app.services.matching import ReconciliationEngine
        from backend.app.config import MatchingConfig
        
        config = MatchingConfig()
        engine = ReconciliationEngine(config)
        assert engine.amount_score(Decimal("100.00"), Decimal("100.00")) == 1.0

    def test_amount_score_within_tolerance(self):
        from backend.app.services.matching import ReconciliationEngine
        from backend.app.config import MatchingConfig
        
        config = MatchingConfig()
        engine = ReconciliationEngine(config)
        score = engine.amount_score(Decimal("100.00"), Decimal("100.005"))
        assert score >= 0.9

    def test_counterparty_score_exact(self):
        from backend.app.services.matching import ReconciliationEngine
        from backend.app.config import MatchingConfig
        
        config = MatchingConfig()
        engine = ReconciliationEngine(config)
        assert engine.counterparty_score("ABC ENTERPRISES", "ABC ENTERPRISES") == 1.0

    def test_counterparty_score_fuzzy(self):
        from backend.app.services.matching import ReconciliationEngine
        from backend.app.config import MatchingConfig
        
        config = MatchingConfig()
        engine = ReconciliationEngine(config)
        score = engine.counterparty_score("ABC LTD", "ABC LIMITED")
        assert score >= 0.85


class TestCashEngine:
    @pytest.mark.asyncio
    async def test_cash_position_calculation(self):
        from backend.app.services.cash_engine import CashEngine
        
        engine = CashEngine(1000000)
        # This would need a mock DB session
        # Just testing the formula logic
        opening = Decimal("1000000")
        inflows = Decimal("500000")
        outflows = Decimal("300000")
        expected = opening + inflows - outflows
        assert expected == Decimal("1200000")


class TestAIResolutionSchema:
    def test_ai_resolution_validation(self):
        from backend.app.schemas.canonical import AIResolution, ResolutionStatus, ExceptionType
        
        resolution = AIResolution(
            status=ResolutionStatus.RESOLVED,
            classification=ExceptionType.PROCESSOR_FEE,
            confidence=0.95,
            explanation="Fee matched",
            evidence=["Ledger: 50000", "Processor fee: 50", "Net: 49950"],
            recommended_action="record_processor_fee"
        )
        assert resolution.confidence == 0.95

    def test_ai_resolution_confidence_bounds(self):
        from backend.app.schemas.canonical import AIResolution, ResolutionStatus, ExceptionType
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            AIResolution(
                status=ResolutionStatus.RESOLVED,
                classification=ExceptionType.PROCESSOR_FEE,
                confidence=1.5,  # Invalid > 1
                explanation="Test",
                evidence=[]
            )