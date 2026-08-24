# AI Finance Controller - Project Log

## Project Overview
**Name**: AI Finance Controller  
**Tagline**: Run the books and the cash position.  
**Goal**: Build an AI-powered finance operations agent that closes one finance-ops loop across 100+ synthetic financial records with measurable match rate, exception handling, and cash position tracking.

## Stack Decisions (Finalized)
| Layer | Choice | Rationale |
|-------|--------|-----------|
| Frontend | Streamlit + streamlit-elements + custom CSS | 5x faster than Next.js; document Next.js migration path |
| Backend | FastAPI + Pydantic + SQLAlchemy 2.0 (async) | Master plan aligned |
| Database | PostgreSQL (local, no Docker) | Master plan aligned |
| Data Processing | Polars + RapidFuzz + Pydantic | Fast, typed, modern |
| AI | Ollama (llama3.1:8b) + Groq fallback + MockProvider | Free, offline-capable, testable |
| Currency | INR only (₹) | Simplifies normalization, matching, cash math |
| Config | Pydantic Settings (YAML + .env) | Type-safe, environment-aware |

## Sprint Plan (10 Days)

### Day 1 — Foundation & PostgreSQL ✅ SCAFFOLDED
- [x] Project structure created
- [x] pyproject.toml with dependencies
- [x] config.yaml with all settings
- [x] SQLAlchemy models (SourceTransaction, CanonicalTransaction, Match, Exception, Resolution, CashPosition, ForecastEntry, AuditLog)
- [x] Database session management
- [x] Pydantic Settings with YAML loading
- [x] LLMProvider abstraction (MockProvider, OllamaProvider, GroqProvider)
- [x] FastAPI app with routers

### Day 2 — Synthetic Data Generator 📋 READY TO BUILD
- [ ] scripts/generate_data.py (deterministic, seeded, 120 records)
- [ ] Distribution: 70 clean, 12 fee, 8 date, 6 missing ledger, 5 missing bank, 6 duplicate, 4 ref, 2 currency, 4 ambiguous, 5 processor fee
- [ ] CSV outputs: bank.csv, ledger.csv, processor.csv
- [ ] Ground truth: ground_truth.csv + ground_truth.parquet
- [ ] scripts/load_data.py for PostgreSQL import

### Day 3 — Normalization & Canonical Model
- [ ] CanonicalTransaction Pydantic model
- [ ] Normalization pipeline per source (dates, amounts, counterparty, references, direction)
- [ ] Raw data preservation for audit
- [ ] Unit tests for normalization

### Day 4 — Deterministic Reconciliation Engine ⚡ CORE
- [ ] Stage 1: Exact matching (reference + amount + currency)
- [ ] Stage 2: Strong matching (amount + counterparty + date window)
- [ ] Stage 3: Fuzzy matching (RapidFuzz weighted scoring)
- [ ] Configurable weights/thresholds from config.yaml
- [ ] Exception creation with types
- [ ] Baseline evaluation vs ground truth (target: >85% match rate, <3% false match)

### Day 5 — Cash Position Engine
- [ ] CashEngine: opening balance + confirmed inflows/outflows
- [ ] Pending items from exceptions/probable matches
- [ ] Variance calculation (expected vs bank)
- [ ] Forecast: 7/14/30 day with scheduled events
- [ ] API endpoints

### Day 6 — AI Investigator Agent ⚡ CORE
- [ ] Tool definitions (get_transaction, get_source_records, search_similar, calculate_difference)
- [ ] Structured output schema (AIResolution Pydantic model)
- [ ] Investigation loop with system prompt
- [ ] Validation pipeline: AI → Pydantic → Business Rules → DB
- [ ] Confidence threshold for auto-resolve (0.90)
- [ ] Audit logging

### Day 7 — Full Pipeline Integration & Evaluation
- [ ] POST /reconciliation/run orchestrates full flow
- [ ] GET /metrics with ground truth comparison
- [ ] Run on 120 records, capture metrics
- [ ] Target: ≥92% match rate, ≥90% accuracy, ≤2% false match, ≥70% AI resolution rate

### Day 8 — Streamlit Dashboard ⚡ VISIBLE OUTPUT
- [ ] Overview: KPIs, cash waterfall, quick actions
- [ ] Reconciliation: Filterable table with status badges
- [ ] Exceptions: Tabbed queue (Open/Investigating/Resolved/Escalated/Unresolved)
- [ ] Exception Detail: Side-by-side evidence panel (Bank|Ledger|Processor)
- [ ] Unresolved View: Honest "Human review required" display
- [ ] Cash Position: Breakdown + forecast charts
- [ ] Metrics: Confusion matrix, resolution breakdown
- [ ] Dark Bloomberg-style theme

### Day 9 — Polish & Demo Prep
- [ ] Error handling, edge cases, performance
- [ ] Demo script (3-5 min)
- [ ] Backup screen recording
- [ ] README, architecture diagram

### Day 10 — Buffer & Final QA
- [ ] Fresh DB end-to-end test
- [ ] Submission package preparation

## Files Created (Scaffold)

### Configuration
- `pyproject.toml` - Dependencies, tool config
- `config.yaml` - All settings (matching, AI, forecast, DB)
- `.env.example` - Environment variables template

### Backend Structure
```
backend/app/
├── main.py                 # FastAPI entry with lifespan
├── config.py               # Pydantic Settings from YAML
├── db/
│   ├── session.py          # Async engine, session, Base
│   └── models.py           # All SQLAlchemy models
├── schemas/
│   └── canonical.py        # All Pydantic schemas
├── api/
│   └── transactions.py     # All REST endpoints
├── services/
│   ├── llm_providers.py    # LLMProvider + Mock/Ollama/Groq
│   ├── matching.py         # ReconciliationEngine
│   ├── cash_engine.py      # CashEngine + forecasting
│   ├── ai_investigator.py  # AIInvestigator with tools
│   └── normalization.py    # Normalizer
└── evaluation/
    └── metrics.py          # EvaluationEngine
```

### Data Scripts
- `scripts/generate_data.py` - Deterministic synthetic data generator
- `scripts/load_data.py` - CSV → PostgreSQL loader

### Dashboard
- `dashboard/app.py` - Complete Streamlit app with 5 tabs
  - Overview (KPIs, cash waterfall, quick actions)
  - Reconciliation (filterable table)
  - Exceptions (tabbed queue + investigation)
  - Cash Position (breakdown + forecast)
  - Metrics (confusion matrix, resolution pie)

### Documentation
- `README.md` - Full project documentation
- `NEXTJS_MIGRATION.md` - Detailed migration guide

## Key Implementation Details

### Matching Algorithm (services/matching.py)
```python
# Weights from config.yaml
score = 0.40*amount_score + 0.25*counterparty_score + 0.20*reference_score + 0.15*date_score

# Thresholds
auto_match >= 0.90           # MATCHED
0.70 <= ai_review < 0.90     # PROBABLE_MATCH → AI investigation
< 0.70                       # EXCEPTION
```

### AI Investigation Flow (services/ai_investigator.py)
```
Exception → Retrieve source records → LLM with tools → Structured output → 
Pydantic validation → Business rule validation (recompute diffs) → 
Resolution record + Audit log → Exception status update
```

### Cash Position Formula
```
Expected Cash = Opening + Confirmed Inflows - Confirmed Outflows
Bank Cash = Expected + Pending Inflows - Pending Outflows
Variance = Bank Cash - Expected Cash
```

### Ground Truth Evaluation
- Hidden from AI during reconciliation
- Used only in `evaluation/metrics.py`
- Computes: accuracy, false_match_rate, resolution rates

## Next Steps (Priority Order)

1. **Install PostgreSQL** and create `ai_finance` database
2. **Install Ollama** and pull `llama3.1:8b` (or configure Groq API key)
3. **Run data generation**: `python scripts/generate_data.py`
4. **Load data**: `python scripts/load_data.py`
5. **Start backend**: `uvicorn backend.app.main:app --reload`
6. **Start dashboard**: `streamlit run dashboard/app.py`
7. **Test reconciliation** via API or dashboard
8. **Iterate on matching weights** based on baseline metrics
9. **Test AI investigator** with MockProvider first, then Ollama

## Competition Differentiators (Built In)

1. ✅ Honest Unresolved View - Explicit "I don't know" with evidence
2. ✅ Side-by-Side Evidence Panel - Bank | Ledger | Processor aligned
3. ✅ Audit Trail - Every decision traceable
4. ✅ Ground Truth Evaluation - Not claimed, measured
5. ✅ Deterministic Cash Math - AI never touches arithmetic
6. ✅ Professional Dark Theme UI - Looks like Bloomberg terminal
7. ✅ Local LLM - Works offline during demo (no API failure risk)

## Open Questions / Decisions Needed

- [ ] PostgreSQL installed and running?
- [ ] Ollama installed with llama3.1:8b? (needs ~8GB RAM)
- [ ] Groq API key as fallback? (free tier: 14K req/day)
- [ ] Target demo date?
- [ ] Any specific discrepancy patterns to emphasize?

## Session Continuity

To resume in a new session:
1. Read this `project.md` file
2. Check `config.yaml` for current settings
3. Run `python scripts/generate_data.py` to regenerate data if needed
4. Continue from the next unchecked item in the sprint plan above

---

*Last updated: 2026-08-24 - Scaffold complete, ready for Day 1 execution*