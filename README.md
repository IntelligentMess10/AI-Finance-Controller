# AI Finance Controller

An AI-powered finance operations controller that automates reconciliation, investigates exceptions with reasoning, and manages cash positions—so finance teams can close faster and sleep better.

Built on the principle that **code handles the accounting** (deterministic, auditable, fast) while **AI handles the investigating** (reasoning, evidence-gathering, judgment calls). The system processes 100,000+ transactions across bank, ledger, and processor sources, achieving 94%+ match rates with full audit trails.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA INGESTION LAYER                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────┐  │
│  │   Bank CSV   │  │  Ledger CSV  │  │  Processor CSV   │  │  Historical / Manual   │
│  │  (MT940/     │  │  (ERP/GL)    │  │  (Stripe/Adyen/  │  │  Adjustments           │
│  │   BAI2)      │  │              │  │   PayPal)        │  │                        │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  └───────────┬────────────┘  │
└─────────┼─────────────────┼────────────────────┼───────────────────────┼────────────────┘
          │                 │                    │                       │
          ▼                 ▼                    ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          NORMALIZATION & CANONICAL LAYER                                │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Counterparty Fuzzy Matching  │  Date/Amount Normalization  │  Reference Parsing  │  │
│  │  Currency Conversion          │  Direction Inference        │  Metadata Preservation │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        RECONCILIATION ENGINE (Deterministic)                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │  Exact Match     │  │  Strong Match    │  │  Special Match   │  │  Fuzzy Match   │  │
│  │  (Ref+Amt+Curr)  │  │  (Amt+Cpty+Date) │  │  (Fees/Dates/    │  │  (Fuzzy Score) │  │
│  │  Score: 1.0      │  │  Score: 0.85+    │  │  Rounding)       │  │  (0.70-0.89) │  │
│  │  → MATCHED       │  │  → MATCHED       │  │  → MATCHED       │  │  → PROBABLE    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └────────────────┘  │
│                    │                     │                      │                       │  │
│                    ▼                     ▼                      ▼                       ▼  │
│           ┌─────────────────────────────────────────────────────────────────────────┐  │
│           │              UNMATCHED → EXCEPTION QUEUE (< 0.70)                       │  │
│           └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────┐
│  MATCHED (≥0.90)     │  │ PROBABLE MATCH       │  │  EXCEPTIONS (< 0.70)    │
│  Auto-accepted       │  │ (0.70-0.89)          │  │  Auto-investigated by   │
│  94%+ of matches     │  │ → Auto-Resolve Queue │  │  AI Investigator        │
└──────────────────────┘  └──────────┬───────────┘  └───────────┬──────────────┘
                                     │                             │
                    ┌────────────────┼────────────────┐           │
                    ▼                ▼                ▼           ▼
         ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
         │ AUTO-RESOLVED  │ │ ESCALATED      │ │ AI INVESTIGATOR│ │ MANUAL REVIEW  │
         │ (Conf ≥ 0.90)  │ │ (Conf < 0.90)  │ │ (LLM + Tools)  │ │ (Human)        │
         │ → MATCHED      │ │ → ESCALATED    │ │ → Resolution   │ │ → Resolution   │
         │ 94%+ resolved  │ │ → Review Queue │ │ → Conf ≥ 0.90  │ │ → Conf < 0.7   │
         └────────────────┘ └────────────────┘ └───────┬────────┘ └────────────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          RESOLUTION & CASH LAYER                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │  Resolution DB   │  │  Exception Queue │  │  Cash Engine     │  │  Forecast      │  │
│  │  (Audit Trail)   │  │  (Unresolved/    │  │  (Opening/In/Out/│  │  Forecast      │  │
│  │                  │  │  Escalated/      │  │  Pending/        │  │  (7/14/30 day) │  │
│  │                  │  │  Resolved)       │  │   Variance)      │  │                │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER (Streamlit Dashboard)                       │
│  ┌──────────┐ ┌─────────────┐ ┌───────────────┐ ┌─────────────┐ ┌──────────────────┐   │
│  │ Overview │ │ Reconciliation│ │ Probable      │ │ Exceptions  │ │ Cash Position   │   │
│  │ KPIs     │ │ Results      │ │ Matches       │ │ Queue       │ │ & Forecast      │   │
│  │          │ │ (Filters)    │ │ (Tabs: All/   │ │ (Tabs:      │ │                │   │
│  │          │ │              │ │  Resolved/    │ │  Open/Inv/   │ │                │   │
│  │          │ │              │ │  Escalated)   │ │  Resolved/   │ │                │   │
│  │          │ │              │ │  Auto-Resolve)│ │  Escalated)  │ │                │   │
│  └──────────┘ └─────────────┘ └───────────────┘ └─────────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Core Principle**: `CODE = ACCOUNTANT` (deterministic, auditable, fast) | `AI = INVESTIGATOR` (reasoning, evidence, judgment)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Ollama (for local LLM) or Groq/OpenAI API key

### Installation

```bash
# Clone and setup
cd ai-finance-controller

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install Ollama and pull model
# https://ollama.ai/download
ollama pull llama3.1:8b

# Setup PostgreSQL
createdb ai_finance
# Or use psql: CREATE DATABASE ai_finance;

# Configure environment
cp .env.example .env

# Edit .env with your database password and API keys
```

### Generate Synthetic Data

```bash
python scripts/generate_data.py
python scripts/load_data.py
python scripts/normalize.py
python scripts/reconcile.py
```

### Run Application

```bash
# Terminal 1: Backend API
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Dashboard
streamlit run dashboard/app.py
```

Visit:
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

### For Testing Exceptions

```bash
# Use open.py to set all the exceptions' status to OPEN for testing
python open.py
```

## Project Structure

```
ai-finance-controller/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── config.py            # Pydantic Settings
│   │   ├── api/                 # REST endpoints
│   │   ├── db/                  # SQLAlchemy models, session
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── matching.py      # Reconciliation engine
│   │   │   ├── normalization.py # Data normalization
│   │   │   ├── cash_engine.py   # Cash position
│   │   │   ├── ai_investigator.py # AI agent
│   │   │   └── llm_providers.py # LLM abstraction
│   │   └── evaluation/          # Metrics
│   └── tests/
├── dashboard/
│   ├── app.py                   # Streamlit entry
│   ├── pages/                   # Page components
│   └── components/              # Reusable UI
├── data/                        # Generated CSVs
├── scripts/                     # Data generation/loading
├── config.yaml                  # Configuration
└── pyproject.toml
```

## Key Features

| Feature | Status |
|---------|--------|
| Multi-source reconciliation (Bank/Ledger/Processor) | ✅ |
| Deterministic matching (Exact/Strong/Fuzzy) | ✅ |
| AI exception investigation with tools | ✅ |
| Structured AI output with validation | ✅ |
| Cash position calculation | ✅ |
| Forward cash forecasting | ✅ |
| Ground truth evaluation | ✅ |
| Audit logging | ✅ |
| Professional Streamlit dashboard | ✅ |

## Demo Flow

1. **Load Data** → 120 transactions across 3 sources
2. **Run Reconciliation** → Deterministic matching + AI investigation
3. **View Results** → 94% match rate, 91% accuracy
4. **Drill into Exceptions** → Side-by-side evidence (Bank|Ledger|Processor)
5. **See Honest Unresolved** → "Two ledger records match equally. Human review required."
6. **Cash Position** → Variance explained by unresolved exceptions
7. **Forecast** → 7/14/30 day projections

## Configuration

Edit `config.yaml`:

```yaml
matching:
  thresholds:
    auto_match: 0.90      # Auto-accept above this
    ai_review_min: 0.70   # Send to AI above this
    exception: 0.70       # Exception below this

ai:
  provider: "ollama"      # ollama | groq | OpenAI | mock
  confidence_auto_resolve: 0.90
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /reconciliation/run | Run full reconciliation |
| GET | /reconciliation/results | Get match results |
| GET | /exceptions/ | List exceptions |
| POST | /exceptions/{id}/investigate | AI investigation |
| GET | /cash/position | Current cash position |
| GET | /cash/forecast | Forward forecast |
| GET | /metrics/ | Evaluation metrics |

## Development

```bash
# Run tests
pytest backend/tests -v

# Lint
ruff check backend/
black backend/

# Type check
mypy backend/
```

## License

MIT