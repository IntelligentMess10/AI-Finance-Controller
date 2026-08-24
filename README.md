# AI Finance Controller

AI-powered finance operations controller for reconciliation, exception investigation, and cash position management.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Data Sources   │────▶│  Reconciliation  │────▶│  AI Investigation   │
│  (Bank/Ledger/  │     │  Engine          │     │  Agent              │
│   Processor)    │     │  (Deterministic) │     │  (LLM + Tools)      │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Streamlit      │◀────│  Results &       │◀────│  Resolution &       │
│  Dashboard      │     │  Metrics         │     │  Exception Queue    │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
```

**Core Principle**: `CODE = ACCOUNTANT` (deterministic), `AI = INVESTIGATOR` (reasoning + evidence)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Ollama (for local LLM) or Groq API key

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

## Competition Demo Flow

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
  provider: "ollama"      # ollama | groq | mock
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