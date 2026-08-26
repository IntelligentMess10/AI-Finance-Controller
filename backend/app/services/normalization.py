import re
import logging
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.models import SourceTransaction, CanonicalTransaction, TransactionSource, TransactionDirection
from backend.app.config import get_settings

logger = logging.getLogger(__name__)


class Normalizer:
    # Only true corporate suffixes - NOT general business words like COMPANY, ENTERPRISES
    CORPORATE_SUFFIXES = [
        'LTD', 'LIMITED', 'PVT', 'PRIVATE', 'INC', 'CORP', 
        'CORPORATION', 'LLC', 'LLP', 'CO', 'PLC'
    ]
    
    # Date formats to try (in order)
    DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y"]
    
    # Batch size for bulk operations (scalability)
    BATCH_SIZE = 500

    def __init__(self):
        self.settings = get_settings()
        # Pre-compile regex for performance
        # Match corporate suffixes at END of string OR as a sequence before the end
        # Pattern: word boundary + suffix + (optional punctuation/space) + (optional suffixes) + end of string
        suffixes = '|'.join(self.CORPORATE_SUFFIXES)
        # Match one or more suffixes at the end, possibly separated by spaces/punctuation
        self._counterparty_suffix_pattern = re.compile(
            r'(?:\s+\b(?:' + '|'.join(self.CORPORATE_SUFFIXES) + r')\b\s*[.\-,]*)+\s*$'
        )
        self._non_alphanum_space = re.compile(r'[^\w\s]')
        self._multiple_spaces = re.compile(r'\s+')
        self._amount_clean = re.compile(r'[^\d\.\-]')
        self._ref_clean = re.compile(r'[^A-Z0-9\-]')  # Only A-Z, 0-9, hyphen

    def normalize_counterparty(self, name: str) -> str:
        """Normalize counterparty name for matching.
        
        Aggressive normalization for exact/fuzzy matching:
        - Uppercase, strip punctuation, collapse whitespace
        - Remove corporate suffixes from ANYWHERE in the name
        - Preserve business words like COMPANY, ENTERPRISES, SOLUTIONS, etc.
        """
        if not name:
            return ""
        name = name.upper().strip()
        name = self._non_alphanum_space.sub(' ', name)
        name = self._multiple_spaces.sub(' ', name)
        
        # Split into words and filter out corporate suffixes
        words = name.split()
        filtered = [w for w in words if w not in self.CORPORATE_SUFFIXES]
        
        # If all words were suffixes, return empty
        if not filtered:
            return ""
        
        return ' '.join(filtered)

    def normalize_counterparty_loose(self, name: str) -> str:
        """Less aggressive normalization - keeps suffixes for display/search."""
        if not name:
            return ""
        name = name.upper().strip()
        name = self._non_alphanum_space.sub(' ', name)
        name = self._multiple_spaces.sub(' ', name)
        return name.strip()

    def normalize_reference(self, ref: Optional[str]) -> Optional[str]:
        """Normalize reference for matching. Keeps alphanumeric and hyphen only."""
        if not ref:
            return None
        ref = ref.upper().strip()
        ref = ref.replace('_', '-')  # Convert underscore to hyphen first
        ref = self._ref_clean.sub('', ref)  # Keep only A-Z, 0-9, hyphen
        return ref if ref else None

    def parse_amount(self, value: Any) -> Decimal:
        """Parse amount to Decimal. Fail-fast on invalid input."""
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            cleaned = self._amount_clean.sub('', value)
            if not cleaned:
                raise ValueError(f"Cannot parse amount from: {value!r}")
            try:
                return Decimal(cleaned)
            except InvalidOperation as e:
                raise ValueError(f"Invalid amount format: {value!r}") from e
        raise TypeError(f"Unsupported amount type: {type(value).__name__}")

    def parse_date(self, value: Any) -> date:
        """Parse date from various formats. Fail-fast on invalid input."""
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            for fmt in self.DATE_FORMATS:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        raise ValueError(f"Cannot parse date from: {value!r} (tried formats: {self.DATE_FORMATS})")

    def determine_direction(self, source: TransactionSource, amount: Decimal, raw: Dict) -> TransactionDirection:
        """Determine transaction direction from source-specific fields."""
        if source == TransactionSource.BANK:
            dr_cr = raw.get("dr_cr", "").upper()
            if dr_cr == "CR":
                return TransactionDirection.INFLOW
            elif dr_cr == "DR":
                return TransactionDirection.OUTFLOW
        elif source == TransactionSource.LEDGER:
            acc_type = raw.get("account_type", "").lower()
            if any(kw in acc_type for kw in ("receivable", "revenue", "income", "sales")):
                return TransactionDirection.INFLOW
            if any(kw in acc_type for kw in ("payable", "expense", "cost", "purchase")):
                return TransactionDirection.OUTFLOW
        elif source == TransactionSource.PROCESSOR:
            txn_type = raw.get("type", "").lower()
            if any(kw in txn_type for kw in ("payout", "refund", "disbursement", "withdrawal")):
                return TransactionDirection.OUTFLOW
            if any(kw in txn_type for kw in ("payment", "charge", "deposit", "collection", "capture")):
                return TransactionDirection.INFLOW
        # Fallback: positive amount = inflow, negative = outflow
        return TransactionDirection.INFLOW if amount > 0 else TransactionDirection.OUTFLOW

    def normalize_source_transaction(self, source_txn: SourceTransaction) -> Tuple[CanonicalTransaction, Dict[str, Any]]:
        """
        
        Returns:
            Tuple of (CanonicalTransaction, normalization_warnings)
            Warnings dict contains any non-fatal issues for logging.
        """
        warnings = {}
        
        amount = self.parse_amount(source_txn.amount)
        txn_date = self.parse_date(source_txn.transaction_date)
        counterparty_normalized = self.normalize_counterparty(source_txn.counterparty)
        counterparty_loose = self.normalize_counterparty_loose(source_txn.counterparty)
        reference = self.normalize_reference(source_txn.reference)
        direction = self.determine_direction(source_txn.source, amount, source_txn.raw_data)

        # Track if normalization changed values significantly
        if counterparty_normalized != counterparty_loose:
            warnings['counterparty_suffix_stripped'] = True
        if reference and reference != source_txn.reference.upper().strip().replace('_', '-'):
            warnings['reference_normalized'] = True

        # Preserve source-specific fields in metadata
        metadata = {
            "raw_counterparty": source_txn.counterparty,
            "raw_counterparty_loose": counterparty_loose,
            "raw_reference": source_txn.reference,
            "raw_amount": str(source_txn.amount),
            "raw_date": str(source_txn.transaction_date),
            "warnings": warnings,
        }
        
        # Add source-specific fields
        raw = source_txn.raw_data
        if source_txn.source == TransactionSource.PROCESSOR:
            if "fee" in raw:
                metadata["processor_fee"] = str(raw["fee"])
            if "net_amount" in raw:
                metadata["processor_net_amount"] = str(raw["net_amount"])
            if "gross_amount" in raw:
                metadata["processor_gross_amount"] = str(raw["gross_amount"])
            if "settlement_date" in raw:
                metadata["processor_settlement_date"] = str(raw["settlement_date"])
            if "processor_reference" in raw:
                metadata["processor_reference"] = raw["processor_reference"]
        elif source_txn.source == TransactionSource.BANK:
            if "dr_cr" in raw:
                metadata["bank_dr_cr"] = raw["dr_cr"]
        elif source_txn.source == TransactionSource.LEDGER:
            if "invoice_id" in raw:
                metadata["ledger_invoice_id"] = raw["invoice_id"]
            if "account" in raw:
                metadata["ledger_account"] = raw["account"]
            if "status" in raw:
                metadata["ledger_status"] = raw["status"]

        canonical = CanonicalTransaction(
            source=source_txn.source,
            source_id=source_txn.source_id,
            date=txn_date,
            amount=amount,
            currency=source_txn.currency or "INR",
            counterparty=counterparty_normalized,
            counterparty_loose=counterparty_loose,
            description=source_txn.description,
            reference=reference,
            direction=direction,
            txn_metadata=metadata
        )
        return canonical, warnings

    async def run(self, db: AsyncSession) -> List[CanonicalTransaction]:
        """Normalize all unnormalized source transactions.
        
        Uses batch processing for memory efficiency and scalability.
        """
        result = await db.execute(
            select(SourceTransaction).where(SourceTransaction.canonical_transaction_id.is_(None))
        )
        source_txns = result.scalars().all()
        
        if not source_txns:
            logger.info("No unnormalized transactions found")
            return []

        logger.info(f"Normalizing {len(source_txns)} source transactions...")
        
        canonical_txns = []
        warning_count = 0
        
        # Process in batches for memory efficiency and scalability
        for i in range(0, len(source_txns), self.BATCH_SIZE):
            batch = source_txns[i:i + self.BATCH_SIZE]
            batch_canonical = []
            
            for st in batch:
                try:
                    canonical, warnings = self.normalize_source_transaction(st)
                    if warnings:
                        warning_count += 1
                        logger.debug(f"Normalization warnings for {st.source_id}: {warnings}")
                    batch_canonical.append(canonical)
                except (ValueError, TypeError) as e:
                    logger.error(f"Failed to normalize {st.source_id} ({st.source}): {e}")
                    # Continue with other records - don't fail entire batch
                    continue
                
            # Bulk insert batch
            if batch_canonical:
                db.add_all(batch_canonical)
                await db.flush()
                
                # Link back to source transactions
                for st, canonical in zip(batch, batch_canonical):
                    st.canonical_transaction_id = canonical.id
                
            await db.commit()
            logger.info(f"Processed batch {i//self.BATCH_SIZE + 1}: {len(batch_canonical)} records")
        
        logger.info(f"Normalization complete: {len(canonical_txns)} canonical transactions created, {warning_count} with warnings")
        return canonical_txns