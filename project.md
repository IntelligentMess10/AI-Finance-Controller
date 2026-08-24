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

### Day 1 — Foundation & PostgreSQL ✅ COMPLETE
- [x] Project structure created
- [x] pyproject.toml with dependencies
- [x] config.yaml with all settings
- [x] SQLAlchemy models (SourceTransaction, CanonicalTransaction, Match, Exception, Resolution, CashPosition, ForecastEntry, AuditLog)
- [x] Database session management
- [x] Pydantic Settings with YAML loading + env var resolution
- [x] LLMProvider abstraction (MockProvider, OllamaProvider, GroqProvider, OpenAICompatibleProvider)
- [x] FastAPI app with routers
- [x] PostgreSQL installed, database `ai_finance` created, user `finance_user` with privileges
- [x] Alembic migrations run - all tables created
- [x] Synthetic data generated: 120 base transactions with 10 discrepancy types (361 total source records)
- [x] Data loaded into PostgreSQL: 117 bank, 122 ledger, 122 processor records

### Day 2 — Synthetic Data Generator ✅ COMPLETE
- [x] scripts/generate_data.py (deterministic, seeded, 120 records)
- [x] Distribution: 70 clean, 12 fee, 8 date, 6 missing ledger, 5 missing bank, 6 duplicate, 4 ref, 2 currency, 4 ambiguous, 5 processor fee
- [x] CSV outputs: bank.csv, ledger.csv, processor.csv
- [x] Ground truth: ground_truth.csv + ground_truth.parquet
- [x] scripts/load_data.py for PostgreSQL import

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

## Files Created & Tested

### Configuration
- `pyproject.toml` - Dependencies, tool config
- `config.yaml` - All settings (matching, AI, forecast, DB)
- `.env.example` - Environment variables template

### Backend Structure (Scaffolded + Migration-Ready)
```
backend/app/
├── main.py                 # FastAPI entry with lifespan
├── config.py               # Pydantic Settings from YAML + env resolution
├── db/
│   ├── base.py             # DeclarativeBase (no circular imports)
│   ├── session.py          # Async engine, session
│   ├── models.py           # All SQLAlchemy models
│   └── migrations/         # Alembic config (env.py, script.py.mako)
├── schemas/
│   └── canonical.py        # All Pydantic schemas (txn_metadata, audit_metadata)
├── api/
│   └── transactions.py     # All REST endpoints
├── services/
│   ├── llm_providers.py    # LLMProvider + Mock/Ollama/Groq/OpenAICompatible
│   ├── matching.py         # ReconciliationEngine (3-stage matching)
│   ├── cash_engine.py      # CashEngine + forecasting
│   ├── ai_investigator.py  # AIInvestigator with 4 tools
│   └── normalization.py    # Normalizer (counterparty, reference, amount, date)
└── evaluation/
    └── metrics.py          # EvaluationEngine (ground truth comparison)
```

### Data Scripts (Tested & Working)
- `scripts/generate_data.py` - Deterministic synthetic data generator (120 base txns)
- `scripts/load_data.py` - CSV → PostgreSQL loader (handles duplicates via invoice_id)

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
- `project.md` - This log

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

1. **Day 1 Evening**: Start backend API
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
   Verify at http://localhost:8000/docs and `/health`

2. **Day 2 — Normalization & Canonical Model**
   - [ ] CanonicalTransaction normalization pipeline per source
   - [ ] Run normalization on loaded data
   - [ ] Unit tests for normalization edge cases

3. **Day 3 — Deterministic Reconciliation Engine** ⚡ CORE
   - [ ] Stage 1: Exact matching (reference + amount + currency)
   - [ ] Stage 2: Strong matching (amount + counterparty + date window)
   - [ ] Stage 3: Fuzzy matching (RapidFuzz weighted scoring)
   - [ ] Configurable weights/thresholds from config.yaml
   - [ ] Exception creation with types
   - [ ] Baseline evaluation vs ground truth (target: >85% match rate, <3% false match)

4. **Day 4 — Cash Position Engine** ...

5. **Day 5 — AI Investigator Agent** ⚡ CORE ...

6. **Day 6 — Full Pipeline Integration & Evaluation** ...

7. **Day 7 — Streamlit Dashboard** ⚡ VISIBLE OUTPUT ...

8. **Day 8 — Polish & Demo Prep** ...

9. **Day 9 — Buffer & Final QA** ...

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
3. `.env` already configured with `DB_PASSWORD=finance_pass`
4. PostgreSQL running with `ai_finance` database, `finance_user`/`finance_pass`
5. Data already loaded (361 source transactions)
6. **Next command to run:**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
7. Then verify at http://localhost:8000/docs and continue with Day 2 (Normalization)

---

*Last updated: 2026-08-25 - Day 1 Morning complete: PostgreSQL setup, migrations, data generation, and data loading all successful. 361 source transactions loaded. Ready for Day 1 Evening (backend API start).*