from dataclasses import dataclass
from decimal import Decimal
from datetime import date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from rapidfuzz import fuzz, process
from backend.app.config import MatchingConfig
from backend.app.db.models import CanonicalTransaction, Match, MatchStatus, Exception, ExceptionType, ExceptionStatus
from backend.app.services.normalization import Normalizer


@dataclass
class MatchPair:
    """Represents a matched pair of transactions with their match candidate."""
    txn1: CanonicalTransaction
    txn2: CanonicalTransaction
    candidate: MatchCandidate


@dataclass
class MatchCandidate:
    transaction: CanonicalTransaction
    score: float
    method: str
    evidence: List[str]


class ReconciliationEngine:
    def __init__(self, config: MatchingConfig):
        self.config = config
        self.normalizer = Normalizer()

    def amount_score(self, a: Decimal, b: Decimal) -> float:
        if a == b:
            return 1.0
        diff = abs(a - b)
        tolerance = max(Decimal("0.01"), a * Decimal(str(self.config.amount_tolerance_pct)))
        if diff <= tolerance:
            return 1.0 - float(diff / tolerance) * 0.1
        return 0.0

    def date_score(self, a: date, b: date) -> float:
        diff = abs((a - b).days)
        if diff == 0:
            return 1.0
        if diff <= self.config.date_window_days:
            return 1.0 - (diff / self.config.date_window_days) * 0.3
        return 0.0

    def counterparty_score(self, a: str, b: str) -> float:
        norm_a = self.normalizer.normalize_counterparty(a)
        norm_b = self.normalizer.normalize_counterparty(b)
        if norm_a == norm_b:
            return 1.0
        ratio = fuzz.ratio(norm_a, norm_b) / 100.0
        if ratio >= 0.85:
            return ratio
        return ratio * 0.5

    def reference_score(self, a: Optional[str], b: Optional[str]) -> float:
        if not a or not b:
            return 0.5
        if a == b:
            return 1.0
        ratio = fuzz.ratio(a, b) / 100.0
        return ratio

    def compute_match_score(self, txn1: CanonicalTransaction, txn2: CanonicalTransaction) -> MatchCandidate:
        amt_score = self.amount_score(txn1.amount, txn2.amount)
        cpty_score = self.counterparty_score(txn1.counterparty, txn2.counterparty)
        ref_score = self.reference_score(txn1.reference, txn2.reference)
        dt_score = self.date_score(txn1.date, txn2.date)

        weights = self.config.weights
        total_score = (
            weights.amount * amt_score +
            weights.counterparty * cpty_score +
            weights.reference * ref_score +
            weights.date * dt_score
        )

        evidence = []
        if amt_score >= 0.99:
            evidence.append("Amount matches exactly")
        elif amt_score > 0:
            evidence.append(f"Amount close (score: {amt_score:.2f})")
        if cpty_score >= 0.85:
            evidence.append("Counterparty matches")
        elif cpty_score > 0:
            evidence.append(f"Counterparty similar (score: {cpty_score:.2f})")
        if ref_score >= 0.85:
            evidence.append("Reference matches")
        elif ref_score > 0:
            evidence.append(f"Reference similar (score: {ref_score:.2f})")
        if dt_score >= 0.99:
            evidence.append("Date matches exactly")
        elif dt_score > 0:
            evidence.append(f"Date within window (score: {dt_score:.2f})")

        return MatchCandidate(
            transaction=txn2,
            score=total_score,
            method="fuzzy_weighted",
            evidence=evidence
        )

    def find_exact_matches(self, transactions: List[CanonicalTransaction]) -> List[MatchPair]:
        matches = []
        seen = set()
        by_key = {}
        
        for txn in transactions:
            key = (txn.reference, txn.amount, txn.currency)
            if key not in by_key:
                by_key[key] = []
            by_key[key].append(txn)
        
        for key, group in by_key.items():
            if len(group) >= 2:
                for i, txn1 in enumerate(group):
                    for txn2 in group[i+1:]:
                        if txn1.id not in seen and txn2.id not in seen:
                            candidate = MatchCandidate(
                                transaction=txn2,
                                score=1.0,
                                method="exact",
                                evidence=["Reference matches exactly", "Amount matches exactly", "Currency matches exactly"]
                            )
                            matches.append(MatchPair(txn1=txn1, txn2=txn2, candidate=candidate))
                            seen.add(txn1.id)
                            seen.add(txn2.id)
        return matches

    def find_strong_matches(self, transactions: List[CanonicalTransaction], matched_ids: set) -> List[MatchPair]:
        matches = []
        unmatched = [t for t in transactions if t.id not in matched_ids]
        
        # Track locally which IDs get matched in this method
        local_matched = set()
        
        for i, txn1 in enumerate(unmatched):
            for txn2 in unmatched[i+1:]:
                if txn1.id in matched_ids or txn2.id in matched_ids or txn1.id in local_matched or txn2.id in local_matched:
                    continue
                # Use amount_score which includes tolerance
                amt_score = self.amount_score(txn1.amount, txn2.amount)
                if amt_score > 0:  # Amount within tolerance
                    cpty_score = self.counterparty_score(txn1.counterparty, txn2.counterparty)
                    dt_score = self.date_score(txn1.date, txn2.date)
                    if cpty_score >= 0.85 and dt_score >= 0.7:
                        score = 0.6 * cpty_score + 0.4 * dt_score
                        if score >= self.config.thresholds.ai_review_min:
                            evidence = ["Amount matches" + (" exactly" if amt_score >= 0.99 else f" (score: {amt_score:.2f})")]
                            if cpty_score >= 0.95:
                                evidence.append("Counterparty matches closely")
                            else:
                                evidence.append(f"Counterparty similar (score: {cpty_score:.2f})")
                            if dt_score >= 0.95:
                                evidence.append("Date matches exactly")
                            else:
                                evidence.append(f"Date within {self.config.date_window_days} days")
                            candidate = MatchCandidate(
                                transaction=txn2,
                                score=score,
                                method="strong_amount_counterparty_date",
                                evidence=evidence
                            )
                            matches.append(MatchPair(txn1=txn1, txn2=txn2, candidate=candidate))
                            local_matched.add(txn1.id)
                            local_matched.add(txn2.id)
                            break
        return matches

    def find_fuzzy_matches(self, transactions: List[CanonicalTransaction], matched_ids: set) -> List[MatchPair]:
        matches = []
        unmatched = [t for t in transactions if t.id not in matched_ids]
        
        # Track locally which IDs get matched in this method
        local_matched = set()
        
        for i, txn1 in enumerate(unmatched):
            best_match = None
            best_score = 0
            
            for txn2 in unmatched[i+1:]:
                if txn1.id in matched_ids or txn2.id in matched_ids or txn1.id in local_matched or txn2.id in local_matched:
                    continue
                candidate = self.compute_match_score(txn1, txn2)
                if candidate.score > best_score:
                    best_score = candidate.score
                    best_match = candidate
            
            if best_match and best_match.score >= self.config.thresholds.exception:
                matches.append(MatchPair(txn1=txn1, txn2=best_match.transaction, candidate=best_match))
                local_matched.add(txn1.id)
                local_matched.add(best_match.transaction.id)
        
        return matches

    def _detect_special_matches(self, transactions: List[CanonicalTransaction], matched_ids: set) -> List[MatchPair]:
        """Detect common discrepancy patterns: processor fees, date mismatches, rounding, etc."""
        matches = []
        unmatched = [t for t in transactions if t.id not in matched_ids]
        local_matched = set()
        
        for i, txn1 in enumerate(unmatched):
            if txn1.id in local_matched:
                continue
                
            for txn2 in unmatched[i+1:]:
                if txn2.id in local_matched:
                    continue
                
                # Skip if same source (we want cross-source matches)
                if txn1.source == txn2.source:
                    continue
                
                # 1. Processor fee detection: ledger amount ≈ bank amount + processor fee
                from backend.app.db.models import TransactionSource
                if (txn1.source == TransactionSource.LEDGER and txn2.source == TransactionSource.BANK) or \
                   (txn2.source == TransactionSource.LEDGER and txn1.source == TransactionSource.BANK):
                    ledger_txn = txn1 if txn1.source == TransactionSource.LEDGER else txn2
                    bank_txn = txn2 if txn2.source == TransactionSource.BANK else txn1
                    
                    # Check if processor record exists for this pair
                    processor_fee = self._find_processor_fee(ledger_txn, bank_txn, transactions)
                    if processor_fee is not None:
                        expected_bank = ledger_txn.amount - processor_fee
                        if abs(expected_bank - bank_txn.amount) <= Decimal("0.01"):
                            candidate = MatchCandidate(
                                transaction=bank_txn,
                                score=0.98,
                                method="processor_fee_match",
                                evidence=[
                                    f"Ledger amount: {ledger_txn.amount}",
                                    f"Bank amount: {bank_txn.amount}",
                                    f"Processor fee detected: {processor_fee}",
                                    f"Expected bank (ledger - fee): {expected_bank}"
                                ]
                            )
                            matches.append(MatchPair(txn1=ledger_txn, txn2=bank_txn, candidate=candidate))
                            local_matched.add(ledger_txn.id)
                            local_matched.add(bank_txn.id)
                            continue
                
                # 2. Date mismatch (1-3 days) with same amount and counterparty
                if txn1.amount == txn2.amount and txn1.counterparty == txn2.counterparty:
                    date_diff = abs((txn1.date - txn2.date).days)
                    if 1 <= date_diff <= 3:
                        candidate = MatchCandidate(
                            transaction=txn2,
                            score=0.95,
                            method="date_mismatch",
                            evidence=[
                                f"Amount matches: {txn1.amount}",
                                f"Counterparty matches: {txn1.counterparty}",
                                f"Date differs by {date_diff} day(s) (settlement delay)"
                            ]
                        )
                        matches.append(MatchPair(txn1=txn1, txn2=txn2, candidate=candidate))
                        local_matched.add(txn1.id)
                        local_matched.add(txn2.id)
                        continue
                    
                # 3. Rounding difference (±0.01)
                if abs(txn1.amount - txn2.amount) <= Decimal("0.01") and txn1.counterparty == txn2.counterparty:
                    date_diff = abs((txn1.date - txn2.date).days)
                    if date_diff <= 2:
                        candidate = MatchCandidate(
                            transaction=txn2,
                            score=0.97,
                            method="rounding_difference",
                            evidence=[
                                f"Amount differs by {(txn1.amount - txn2.amount).copy_abs()}: rounding difference",
                                f"Counterparty matches: {txn1.counterparty}",
                                f"Date within {date_diff} day(s)"
                            ]
                        )
                        matches.append(MatchPair(txn1=txn1, txn2=txn2, candidate=candidate))
                        local_matched.add(txn1.id)
                        local_matched.add(txn2.id)
                        continue
                
                # 4. Reference typo detection (same amount, counterparty, date; similar reference)
                if txn1.amount == txn2.amount and txn1.counterparty == txn2.counterparty and txn1.date == txn2.date:
                    if txn1.reference and txn2.reference:
                        ref_score = self.reference_score(txn1.reference, txn2.reference)
                        if ref_score >= 0.85:
                            candidate = MatchCandidate(
                                transaction=txn2,
                                score=0.92,
                                method="reference_typo",
                                evidence=[
                                    f"Amount matches: {txn1.amount}",
                                    f"Counterparty matches: {txn1.counterparty}",
                                    f"Date matches: {txn1.date}",
                                    f"Reference similar (typo likely): {txn1.reference} vs {txn2.reference}"
                                ]
                            )
                            return MatchPair(txn1=txn1, txn2=txn2, candidate=candidate)
        
        return matches

    def classify_exception(self, txn: CanonicalTransaction, candidates: List[MatchCandidate]) -> Exception:
        if not candidates:
            return Exception(
                transaction_id=txn.id,
                type=ExceptionType.UNKNOWN_TRANSACTION,
                severity="high",
                status=ExceptionStatus.OPEN,
                description="No potential matches found in any source",
                evidence=["No matching records found across sources"]
            )
        
        best = max(candidates, key=lambda c: c.score)
        
        if best.score < self.config.thresholds.exception:
            return Exception(
                transaction_id=txn.id,
                type=ExceptionType.UNKNOWN_TRANSACTION,
                severity="high",
                status=ExceptionStatus.OPEN,
                description=f"Best match score {best.score:.2f} below threshold",
                evidence=[f"Best candidate: {best.transaction.counterparty} - {best.transaction.amount}"]
            )
        
        if best.score < self.config.thresholds.ai_review_min:
            return Exception(
                transaction_id=txn.id,
                type=ExceptionType.AMBIGUOUS_MATCH,
                severity="medium",
                status=ExceptionStatus.OPEN,
                description=f"Ambiguous match with score {best.score:.2f}",
                evidence=best.evidence
            )
        
        return None

    async def run(self, db_session, transactions: List[CanonicalTransaction]) -> Dict[str, Any]:
        """Run reconciliation on transactions and persist results to database.
        
        Returns:
            Dict with matches, exceptions, and statistics
        """
        all_matches = []
        all_exceptions = []
        # Track matched PAIRS (not individual transactions) to allow multiple matches per transaction
        matched_pairs = set()  # Set of (txn1_id, txn2_id) tuples, ordered
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting reconciliation on {len(transactions)} transactions")
        
        # Build lookup for quick access
        txn_by_id = {txn.id: txn for txn in transactions}
        
        def is_pair_matched(txn1_id: int, txn2_id: int) -> bool:
            """Check if this pair is already matched (order-independent)."""
            pair = (min(txn1_id, txn2_id), max(txn1_id, txn2_id))
            return pair in matched_pairs
        
        def mark_pair_matched(txn1_id: int, txn2_id: int):
            """Mark a pair as matched."""
            pair = (min(txn1_id, txn2_id), max(txn1_id, txn2_id))
            matched_pairs.add(pair)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting reconciliation on {len(transactions)} transactions")
        
        # Build lookup for quick access
        txn_by_id = {txn.id: txn for txn in transactions}
        
        def is_pair_matched(txn1_id: int, txn2_id: int) -> bool:
            """Check if this pair is already matched (order-independent)."""
            pair = (min(txn1_id, txn2_id), max(txn1_id, txn2_id))
            return pair in matched_pairs
        
        def mark_pair_matched(txn1_id: int, txn2_id: int):
            """Mark a pair as matched."""
            pair = (min(txn1_id, txn2_id), max(txn1_id, txn2_id))
            matched_pairs.add(pair)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting reconciliation on {len(transactions)} transactions")
        
        if self.config.exact_enabled:
            exact_matches = self.find_exact_matches(transactions)
            logger.info(f"Exact matches found: {len(exact_matches)}")
            for pair in exact_matches:
                if is_pair_matched(pair.txn1.id, pair.txn2.id):
                    continue
                match_obj = Match(
                    canonical_transaction_id=pair.txn1.id,
                    matched_transaction_id=pair.txn2.id,
                    score=pair.candidate.score,
                    method=pair.candidate.method,
                    status=MatchStatus.MATCHED,
                    evidence=pair.candidate.evidence
                )
                db_session.add(match_obj)
                await db_session.flush()
                all_matches.append(match_obj)
                mark_pair_matched(pair.txn1.id, pair.txn2.id)
            logger.info(f"After exact matching: {len(matched_pairs)} pairs matched")
        
        # Detect special matches FIRST (processor fees, date mismatches, rounding, reference typos)
        # These should run BEFORE strong/fuzzy to catch specific patterns before generic matching
        special_matches = self._detect_special_matches(transactions, set())  # Don't filter by matched_ids
        logger.info(f"Special matches found: {len(special_matches)}")
        for pair in special_matches:
            if is_pair_matched(pair.txn1.id, pair.txn2.id):
                continue
            match_obj = Match(
                canonical_transaction_id=pair.txn1.id,
                matched_transaction_id=pair.txn2.id,
                score=pair.candidate.score,
                method=pair.candidate.method,
                status=MatchStatus.MATCHED,  # Special matches are high confidence
                evidence=pair.candidate.evidence
            )
            db_session.add(match_obj)
            await db_session.flush()
            all_matches.append(match_obj)
            mark_pair_matched(pair.txn1.id, pair.txn2.id)
        logger.info(f"After special matching: {len(matched_pairs)} pairs matched")
        
        if self.config.strong_enabled:
            strong_matches = self.find_strong_matches(transactions, set())  # Don't filter by matched_ids
            logger.info(f"Strong matches found: {len(strong_matches)}")
            for pair in strong_matches:
                if is_pair_matched(pair.txn1.id, pair.txn2.id):
                    continue
                status = MatchStatus.MATCHED if pair.candidate.score >= self.config.thresholds.auto_match else MatchStatus.PROBABLE_MATCH
                match_obj = Match(
                    canonical_transaction_id=pair.txn1.id,
                    matched_transaction_id=pair.txn2.id,
                    score=pair.candidate.score,
                    method=pair.candidate.method,
                    status=status,
                    evidence=pair.candidate.evidence
                )
                db_session.add(match_obj)
                await db_session.flush()
                all_matches.append(match_obj)
                mark_pair_matched(pair.txn1.id, pair.txn2.id)
            logger.info(f"After strong matching: {len(matched_pairs)} pairs matched")
        
        if self.config.fuzzy_enabled:
            fuzzy_matches = self.find_fuzzy_matches(transactions, set())
            logger.info(f"Fuzzy matches found: {len(fuzzy_matches)}")
            for pair in fuzzy_matches:
                if is_pair_matched(pair.txn1.id, pair.txn2.id):
                    continue
                if pair.candidate.score >= self.config.thresholds.auto_match:
                    status = MatchStatus.MATCHED
                elif pair.candidate.score >= self.config.thresholds.ai_review_min:
                    status = MatchStatus.PROBABLE_MATCH
                else:
                    status = MatchStatus.EXCEPTION
                
                match_obj = Match(
                    canonical_transaction_id=pair.txn1.id,
                    matched_transaction_id=pair.txn2.id,
                    score=pair.candidate.score,
                    method=pair.candidate.method,
                    status=status,
                    evidence=pair.candidate.evidence
                )
                db_session.add(match_obj)
                await db_session.flush()
                all_matches.append(match_obj)
                mark_pair_matched(pair.txn1.id, pair.txn2.id)
            logger.info(f"After fuzzy matching: {len(matched_pairs)} pairs matched")
        
        # Commit all matches
        await db_session.commit()
        
        # Calculate which transactions have matches
        matched_txn_ids = set()
        for m in all_matches:
            matched_txn_ids.add(m.canonical_transaction_id)
            matched_txn_ids.add(m.matched_transaction_id)
        
        # Classify exceptions for unmatched transactions
        all_exceptions = []
        for txn in transactions:
            if txn.id not in matched_txn_ids:
                candidates = []  # No matches for this transaction
                exc = self.classify_exception(txn, [])
                if exc:
                    db_session.add(exc)
                    all_exceptions.append(exc)
        
        await db_session.commit()
        
        matched_txn_count = len(matched_txn_ids)
        
        logger.info(f"Total matches created: {len(all_matches)}")
        logger.info(f"Matched transactions: {matched_txn_count}")
        logger.info(f"Probable matches: {len([m for m in all_matches if m.status == MatchStatus.PROBABLE_MATCH])}")
        logger.info(f"Exceptions: {len(all_exceptions)}")
        
        # Return stats
        return {
            "matches": all_matches,
            "exceptions": all_exceptions,
            "stats": {
                "total": len(transactions),
                "matched": matched_txn_count,
                "probable": len([m for m in all_matches if m.status == MatchStatus.PROBABLE_MATCH]),
                "exceptions": len(all_exceptions),
            }
        }

    def _find_processor_fee(self, ledger_txn: CanonicalTransaction, bank_txn: CanonicalTransaction, transactions: List[CanonicalTransaction]) -> Optional[Decimal]:
        """Find processor fee for a ledger-bank pair by looking for processor record."""
        # Search for processor record that matches the ledger/bank pair
        # Look for processor with same counterparty, similar date, and amount close to ledger amount
        ledger_amount = ledger_txn.amount
        
        from backend.app.db.models import TransactionSource
        for txn in transactions:
            if txn.source != TransactionSource.PROCESSOR:
                continue
            if txn.counterparty != ledger_txn.counterparty:
                continue
            # Check if processor amount matches ledger amount (gross amount)
            if abs(txn.amount - ledger_txn.amount) <= Decimal("1.00"):
                # Found matching processor record, extract fee from metadata
                fee_str = txn.txn_metadata.get("processor_fee")
                if fee_str is not None:
                    try:
                        return Decimal(fee_str)
                    except:
                        pass
        return None