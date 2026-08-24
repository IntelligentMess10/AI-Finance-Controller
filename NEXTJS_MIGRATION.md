# Next.js Migration Guide

This document outlines the migration path from Streamlit to Next.js for the AI Finance Controller dashboard.

## Current Streamlit Architecture

```
dashboard/
├── app.py                 # Single-page app with tabs
├── pages/                 # (Not used - all in app.py)
├── components/            # Inline components in app.py
├── styles/                # Inline CSS in app.py
└── utils/
    └── api_client.py      # API wrapper
```

## Target Next.js Architecture

```
frontend/
├── app/
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Dashboard overview
│   ├── reconciliation/
│   │   └── page.tsx       # Reconciliation table
│   ├── exceptions/
│   │   ├── page.tsx       # Exception queue
│   │   └── [id]/
│   │       └── page.tsx   # Exception detail
│   ├── cash/
│   │   └── page.tsx       # Cash position & forecast
│   └── metrics/
│       └── page.tsx       # Evaluation metrics
├── components/
│   ├── ui/                # Base components (Button, Card, Badge, Table)
│   ├── charts/            # Chart wrappers (Recharts)
│   ├── kpi-cards.tsx      # KPI metric cards
│   ├── evidence-panel.tsx # Side-by-side evidence view
│   ├── match-table.tsx    # Reconciliation table
│   ├── exception-queue.tsx# Exception list with tabs
│   └── cash-waterfall.tsx # Cash breakdown chart
├── lib/
│   ├── api.ts             # API client with React Query
│   ├── utils.ts           # Formatters, helpers
│   └── theme.ts           # Tailwind config extensions
├── types/
│   └── api.ts             # TypeScript types from OpenAPI
└── hooks/
    └── use-api.ts         # Custom hooks for data fetching
```

## Migration Steps

### Phase 1: Setup & Types (Week 1)
1. Initialize Next.js 14+ with TypeScript, Tailwind, ESLint
2. Generate TypeScript types from FastAPI OpenAPI schema:
   ```bash
   npx openapi-typescript http://localhost:8000/openapi.json -o frontend/types/api.ts
   ```
3. Set up TanStack Query (React Query) for server state
4. Create base UI components using shadcn/ui or custom

### Phase 2: Core Pages (Week 2)
1. **Overview Page**: KPI cards, cash waterfall chart, quick actions
2. **Reconciliation Page**: Filterable table with virtualization (tanstack-table)
3. **Exceptions Page**: Tabbed queue with status filters
4. **Exception Detail Page**: Side-by-side evidence panel (critical)
5. **Cash Page**: Position breakdown + forecast charts
6. **Metrics Page**: Confusion matrix, resolution breakdown

### Phase 3: Polish (Week 3)
1. Dark theme matching Streamlit custom CSS
2. Real-time updates via WebSocket or polling
3. Keyboard shortcuts, accessibility
4. Print/export functionality
5. Performance optimization

## Component Mapping

| Streamlit Component | Next.js Equivalent |
|---------------------|-------------------|
| `st.metric` | `<KPICard />` |
| `st.dataframe` | `<DataTable />` (tanstack-table) |
| `st.tabs` | `<Tabs />` (Radix UI) |
| `st.selectbox` | `<Select />` (Radix UI) |
| `st.button` | `<Button />` |
| `st.markdown(unsafe_allow_html=True)` | Custom components with Tailwind |
| `st.plotly_chart` | `<Recharts />` or `<Chart.js />` |
| `st.columns` | CSS Grid / Flexbox |
| `st.expander` | `<Accordion />` (Radix UI) |

## API Client Migration

```typescript
// frontend/lib/api.ts
import { useQuery, useMutation } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  getMetrics: () => fetch(`${API_BASE}/metrics/`).then(r => r.json()),
  getCashPosition: () => fetch(`${API_BASE}/cash/position`).then(r => r.json()),
  getForecast: (days: number) => fetch(`${API_BASE}/cash/forecast?days=${days}`).then(r => r.json()),
  getMatches: (params) => fetch(`${API_BASE}/reconciliation/results?${new URLSearchParams(params)}`).then(r => r.json()),
  getExceptions: (status?: string) => fetch(`${API_BASE}/exceptions/${status ? `?status=${status}` : ''}`).then(r => r.json()),
  investigateException: (id: number) => fetch(`${API_BASE}/exceptions/${id}/investigate`, { method: 'POST' }).then(r => r.json()),
  runReconciliation: () => fetch(`${API_BASE}/reconciliation/run`, { method: 'POST', body: JSON.stringify({ force_rerun: true }) }).then(r => r.json()),
};

// Hooks
export function useMetrics() {
  return useQuery({ queryKey: ['metrics'], queryFn: api.getMetrics, refetchInterval: 30000 });
}

export function useCashPosition() {
  return useQuery({ queryKey: ['cash'], queryFn: api.getCashPosition });
}
```

## Styling Migration

### Streamlit CSS → Tailwind Classes

```css
/* Streamlit */
.metric-card { background: linear-gradient(135deg, #1E2329 0%, #252A32 100%); border: 1px solid #2D333B; }

/* Tailwind */
.bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700
```

### Color Palette

```typescript
// tailwind.config.ts
colors: {
  finance: {
    bg: '#0E1117',
    card: '#1E2329',
    border: '#2D333B',
    text: '#E6EDF3',
    muted: '#8B949E',
    accent: '#00D4AA',
    warning: '#F0B429',
    danger: '#FF6B6B',
    info: '#58A6FF',
  }
}
```

## Evidence Panel (Critical Component)

The side-by-side evidence view is the most important component for the competition demo.

```tsx
// components/evidence-panel.tsx
interface EvidencePanelProps {
  exceptionId: number;
  bankRecord: SourceTransaction;
  ledgerRecord: SourceTransaction;
  processorRecord: SourceTransaction;
  aiResolution: AIResolution;
}

export function EvidencePanel({ exceptionId, bankRecord, ledgerRecord, processorRecord, aiResolution }: EvidencePanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <SourceCard title="BANK" record={bankRecord} color="info" />
      <SourceCard title="LEDGER" record={ledgerRecord} color="accent" />
      <SourceCard title="PROCESSOR" record={processorRecord} color="warning" />
    </div>
  );
}

function SourceCard({ title, record, color }: { title: string; record: SourceTransaction; color: string }) {
  return (
    <Card className="border-l-4" style={{ borderLeftColor: `var(--color-finance-${color})` }}>
      <CardHeader>
        <CardTitle className="text-sm font-mono">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 font-mono text-sm">
        <div><span className="text-muted">Amount:</span> {formatINR(record.amount)}</div>
        <div><span className="text-muted">Date:</span> {record.date}</div>
        <div><span className="text-muted">Counterparty:</span> {record.counterparty}</div>
        <div><span className="text-muted">Ref:</span> {record.reference}</div>
      </CardContent>
    </Card>
  );
}
```

## API Compatibility

The FastAPI backend requires **zero changes** for Next.js migration:
- REST endpoints remain identical
- OpenAPI schema auto-generates TypeScript types
- CORS already configured for all origins

## Deployment

```yaml
# docker-compose.yml (add to existing)
frontend:
  build: ./frontend
  ports:
    - "3000:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://backend:8000
  depends_on:
    - backend
```

## Effort Estimate

| Phase | Streamlit (Current) | Next.js (Target) |
|-------|---------------------|------------------|
| Setup | 2 hrs | 8 hrs |
| Core Pages | 16 hrs | 40 hrs |
| Polish | 8 hrs | 24 hrs |
| **Total** | **26 hrs** | **72 hrs** |

**Recommendation**: Keep Streamlit for competition submission. Migrate to Next.js post-competition if productizing.