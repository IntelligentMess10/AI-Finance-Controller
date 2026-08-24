from dataclasses import dataclass
from decimal import Decimal
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from rapidfuzz import fuzz, process
from backend.app.config import MatchingConfig
from backend.app.db.models import CanonicalTransaction, Match, MatchStatus, Exception, ExceptionType, ExceptionStatus
from backend.app.schemas.canonical import CanonicalTransactionRead


@dataclass
class MatchCandidate:
    transaction: CanonicalTransaction
    score: float
    method: str
    evidence: List[str]


class ReconciliationEngine:
    def __init__(self, config: MatchingConfig):
        self.config = config

    def normalize_counterparty(self, name: str) -> str:
        import re
        name = name.upper().strip()
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name

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
        norm_a = self.normalize_counterparty(a)
        norm_b = self.normalize_counterparty(b)
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

    def find_exact_matches(self, transactions: List[CanonicalTransaction]) -> List[MatchCandidate]:
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
                            matches.append(MatchCandidate(
                                transaction=txn2,
                                score=1.0,
                                method="exact",
                                evidence=["Reference matches exactly", "Amount matches exactly", "Currency matches exactly"]
                            ))
                            seen.add(txn1.id)
                            seen.add(txn2.id)
        return matches

    def find_strong_matches(self, transactions: List[CanonicalTransaction], matched_ids: set) -> List[MatchCandidate]:
        matches = []
        unmatched = [t for t in transactions if t.id not in matched_ids]
        
        for i, txn1 in enumerate(unmatched):
            for txn2 in unmatched[i+1:]:
                if txn1.id in matched_ids or txn2.id in matched_ids:
                    continue
                if txn1.amount == txn2.amount:
                    cpty_score = self.counterparty_score(txn1.counterparty, txn2.counterparty)
                    dt_score = self.date_score(txn1.date, txn2.date)
                    if cpty_score >= 0.85 and dt_score >= 0.7:
                        score = 0.6 * cpty_score + 0.4 * dt_score
                        if score >= self.config.thresholds.ai_review_min:
                            evidence = ["Amount matches exactly"]
                            if cpty_score >= 0.95:
                                evidence.append("Counterparty matches closely")
                            else:
                                evidence.append(f"Counterparty similar (score: {cpty_score:.2f})")
                            if dt_score >= 0.95:
                                evidence.append("Date matches exactly")
                            else:
                                evidence.append(f"Date within {self.config.date_window_days} days")
                            matches.append(MatchCandidate(
                                transaction=txn2,
                                score=score,
                                method="strong_amount_counterparty_date",
                                evidence=evidence
                            ))
                            matched_ids.add(txn1.id)
                            matched_ids.add(txn2.id)
                            break
        return matches

    def find_fuzzy_matches(self, transactions: List[CanonicalTransaction], matched_ids: set) -> List[MatchCandidate]:
        matches = []
        unmatched = [t for t in transactions if t.id not in matched_ids]
        
        for i, txn1 in enumerate(unmatched):
            best_match = None
            best_score = 0
            
            for txn2 in unmatched[i+1:]:
                if txn1.id in matched_ids or txn2.id in matched_ids:
                    continue
                candidate = self.compute_match_score(txn1, txn2)
                if candidate.score > best_score:
                    best_score = candidate.score
                    best_match = candidate
            
            if best_match and best_match.score >= self.config.thresholds.exception:
                matches.append(best_match)
                matched_ids.add(txn1.id)
                matched_ids.add(best_match.transaction.id)
        
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
        all_matches = []
        all_exceptions = []
        matched_ids = set()
        
        if self.config.exact_enabled:
            exact_matches = self.find_exact_matches(transactions)
            for match in exact_matches:
                all_matches.append(Match(
                    canonical_transaction_id=next(t.id for t in transactions if t.id not in matched_ids),
                    matched_transaction_id=match.transaction.id,
                    score=match.score,
                    method=match.method,
                    status=MatchStatus.MATCHED,
                    evidence=match.evidence
                ))
                matched_ids.update([next(t.id for t in transactions if t.id not in matched_ids), match.transaction.id])
        
        if self.config.strong_enabled:
            strong_matches = self.find_strong_matches(transactions, matched_ids)
            for match in strong_matches:
                all_matches.append(Match(
                    canonical_transaction_id=next(t.id for t in transactions if t.id == match.transaction.id),
                    matched_transaction_id=match.transaction.id,
                    score=match.score,
                    method=match.method,
                    status=MatchStatus.PROBABLE_MATCH if match.score < self.config.thresholds.auto_match else MatchStatus.MATCHED,
                    evidence=match.evidence
                ))
        
        if self.config.fuzzy_enabled:
            fuzzy_matches = self.find_fuzzy_matches(transactions, matched_ids)
            for match in fuzzy_matches:
                if match.score >= self.config.thresholds.auto_match:
                    status = MatchStatus.MATCHED
                elif match.score >= self.config.thresholds.ai_review_min:
                    status = MatchStatus.PROBABLE_MATCH
                else:
                    status = MatchStatus.EXCEPTION
                all_matches.append(Match(
                    canonical_transaction_id=next(t.id for t in transactions if t.id == match.transaction.id),
                    matched_transaction_id=match.transaction.id,
                    score=match.score,
                    method=match.method,
                    status=status,
                    evidence=match.evidence
                ))
        
        for txn in transactions:
            if txn.id not in matched_ids:
                candidates = [m for m in all_matches if m.canonical_transaction_id == txn.id or m.matched_transaction_id == txn.id]
                exc = self.classify_exception(txn, candidates)
                if exc:
                    all_exceptions.append(exc)
        
        return {
            "matches": all_matches,
            "exceptions": all_exceptions,
            "stats": {
                "total": len(transactions),
                "matched": len([m for m in all_matches if m.status == MatchStatus.MATCHED]),
                "probable": len([m for m in all_matches if m.status == MatchStatus.PROBABLE_MATCH]),
                "exceptions": len(all_exceptions),
            }
        }