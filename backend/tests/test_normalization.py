import pytest
from decimal import Decimal
from datetime import date
from backend.app.services.normalization import Normalizer


class TestNormalizer:
    def setup_method(self):
        self.normalizer = Normalizer()

    # Counterparty normalization tests
    def test_normalize_counterparty_basic(self):
        assert self.normalizer.normalize_counterparty("ABC Ltd.") == "ABC"
        assert self.normalizer.normalize_counterparty("XYZ CORPORATION") == "XYZ"
        assert self.normalizer.normalize_counterparty("  Global Tech Solutions  ") == "GLOBAL TECH SOLUTIONS"

    def test_normalize_counterparty_suffixes(self):
        assert self.normalizer.normalize_counterparty("ABC LIMITED") == "ABC"
        assert self.normalizer.normalize_counterparty("XYZ PRIVATE LIMITED") == "XYZ"
        assert self.normalizer.normalize_counterparty("TEST INC") == "TEST"
        assert self.normalizer.normalize_counterparty("COMPANY LTD ENTERPRISES") == "COMPANY ENTERPRISES"

    def test_normalize_counterparty_edge_cases(self):
        assert self.normalizer.normalize_counterparty("") == ""
        assert self.normalizer.normalize_counterparty(None) == ""
        assert self.normalizer.normalize_counterparty("  ") == ""
        assert self.normalizer.normalize_counterparty("LTD") == ""  # Only suffix
        assert self.normalizer.normalize_counterparty("LTD COMPANY") == "COMPANY"  # Not at word boundary

    def test_normalize_counterparty_loose(self):
        # Less aggressive - keeps suffixes
        assert self.normalizer.normalize_counterparty_loose("ABC Ltd.") == "ABC LTD"
        assert self.normalizer.normalize_counterparty_loose("XYZ PRIVATE LIMITED") == "XYZ PRIVATE LIMITED"

    # Reference normalization tests
    def test_normalize_reference(self):
        assert self.normalizer.normalize_reference("REF-123") == "REF-123"
        assert self.normalizer.normalize_reference(" ref_456 ") == "REF-456"
        assert self.normalizer.normalize_reference(None) is None
        assert self.normalizer.normalize_reference("") is None

    # Amount parsing tests
    def test_parse_amount_valid(self):
        assert self.normalizer.parse_amount(Decimal("100.50")) == Decimal("100.50")
        assert self.normalizer.parse_amount(100) == Decimal("100")
        assert self.normalizer.parse_amount("1,000.00") == Decimal("1000.00")
        assert self.normalizer.parse_amount("₹50,000") == Decimal("50000")
        assert self.normalizer.parse_amount("-100.50") == Decimal("-100.50")

    def test_parse_amount_invalid(self):
        with pytest.raises(ValueError):
            self.normalizer.parse_amount("abc")
        with pytest.raises(ValueError):
            self.normalizer.parse_amount("")
        with pytest.raises(TypeError):
            self.normalizer.parse_amount([])

    # Date parsing tests
    def test_parse_date_valid(self):
        assert self.normalizer.parse_date(date(2026, 1, 15)) == date(2026, 1, 15)
        assert self.normalizer.parse_date("2026-01-15") == date(2026, 1, 15)
        assert self.normalizer.parse_date("15/01/2026") == date(2026, 1, 15)
        assert self.normalizer.parse_date("15-01-2026") == date(2026, 1, 15)
        assert self.normalizer.parse_date("15.01.2026") == date(2026, 1, 15)

    def test_parse_date_invalid(self):
        with pytest.raises(ValueError):
            self.normalizer.parse_date("invalid")
        with pytest.raises(ValueError):
            self.normalizer.parse_date("")

    # Direction determination tests
    def test_direction_bank(self):
        assert self.normalizer.determine_direction("bank", Decimal("100"), {"dr_cr": "CR"}) == "inflow"
        assert self.normalizer.determine_direction("bank", Decimal("100"), {"dr_cr": "DR"}) == "outflow"

    def test_direction_ledger(self):
        assert self.normalizer.determine_direction("ledger", Decimal("100"), {"account_type": "RECEIVABLES"}) == "inflow"
        assert self.normalizer.determine_direction("ledger", Decimal("100"), {"account_type": "PAYABLES"}) == "outflow"
        assert self.normalizer.determine_direction("ledger", Decimal("100"), {"account_type": "REVENUE"}) == "inflow"
        assert self.normalizer.determine_direction("ledger", Decimal("100"), {"account_type": "EXPENSE"}) == "outflow"

    def test_direction_processor(self):
        assert self.normalizer.determine_direction("processor", Decimal("100"), {"type": "payment"}) == "inflow"
        assert self.normalizer.determine_direction("processor", Decimal("100"), {"type": "refund"}) == "outflow"
        assert self.normalizer.determine_direction("processor", Decimal("100"), {"type": "payout"}) == "outflow"
        assert self.normalizer.determine_direction("processor", Decimal("100"), {"type": "charge"}) == "inflow"

    def test_direction_fallback(self):
        assert self.normalizer.determine_direction("unknown", Decimal("100"), {}) == "inflow"
        assert self.normalizer.determine_direction("unknown", Decimal("-50"), {}) == "outflow"

    # Reference normalization
    def test_normalize_reference(self):
        assert self.normalizer.normalize_reference("REF-123") == "REF-123"
        assert self.normalizer.normalize_reference(" ref_456 ") == "REF-456"
        assert self.normalizer.normalize_reference(None) is None


class TestNormalizerIntegration:
    """Integration-style tests with mock SourceTransaction objects."""
    
    def setup_method(self):
        self.normalizer = Normalizer()

    def test_normalize_bank_transaction(self):
        from backend.app.db.models import SourceTransaction, TransactionSource, TransactionDirection
        
        st = SourceTransaction(
            source=TransactionSource.BANK,
            source_id="1",
            transaction_date=date(2026, 1, 15),
            amount=Decimal("1000.00"),
            currency="INR",
            counterparty="ABC LTD.",
            description="Test payment",
            reference="BNK001",
            direction=TransactionDirection.INFLOW,
            raw_data={"dr_cr": "CR", "original_id": 1}
        )
        
        canonical, warnings = self.normalizer.normalize_source_transaction(st)
        
        assert canonical.counterparty == "ABC"
        assert canonical.counterparty_loose == "ABC LTD"
        assert canonical.amount == Decimal("1000.00")
        assert canonical.direction == TransactionDirection.INFLOW
        assert canonical.reference == "BNK001"
        assert "warnings" in canonical.txn_metadata

    def test_normalize_ledger_transaction(self):
        from backend.app.db.models import SourceTransaction, TransactionSource, TransactionDirection
        
        st = SourceTransaction(
            source=TransactionSource.LEDGER,
            source_id="INV001",
            transaction_date=date(2026, 1, 15),
            amount=Decimal("5000.00"),
            currency="INR",
            counterparty="VENDOR PVT LTD",
            description="Invoice payment",
            reference="INV001",
            direction=TransactionDirection.OUTFLOW,
            raw_data={"invoice_id": "INV001", "account_type": "PAYABLES", "status": "POSTED"}
        )
        
        canonical, warnings = self.normalizer.normalize_source_transaction(st)
        
        assert canonical.counterparty == "VENDOR"
        assert canonical.counterparty_loose == "VENDOR PVT LTD"
        assert canonical.direction == TransactionDirection.OUTFLOW
        assert warnings.get("counterparty_suffix_stripped") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])