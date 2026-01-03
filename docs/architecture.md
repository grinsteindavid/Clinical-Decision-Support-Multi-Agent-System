# Architecture Overview

LangGraph-based multi-agent system for clinical decision support using pgvector semantic search.

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React UI      │     │   FastAPI       │     │   PostgreSQL    │
│   (Vite/nginx)  │────▶│   (uvicorn)     │────▶│   (pgvector)    │
│   Port 3000     │ SSE │   Port 5000     │     │   Port 5432     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     LangGraph       │
                    │   Multi-Agent       │
                    └─────────────────────┘
```

## Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SUPERVISOR AGENT                      │
│         Routes queries to specialist agents              │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│ TOOL   │   │ ORG    │   │WORKFLOW│
│ FINDER │   │ MATCHER│   │ ADVISOR│
└────────┘   └────────┘   └────────┘
    │             │             │
    ▼             ▼             ▼
 pgvector      pgvector     combines
 clinical_     clinical_    results +
 tools         orgs         reasoning
```

## Agent Descriptions

### Supervisor Agent
- **Purpose:** Classify incoming queries and route to appropriate specialist
- **Input:** User query
- **Output:** Routing decision (tool_finder | org_matcher | workflow_advisor)
- **No pgvector access** - pure routing logic

### Tool Finder Agent
- **Purpose:** Find relevant clinical decision support tools
- **Uses:** `clinical_tools` table via pgvector semantic search

### Org Matcher Agent
- **Purpose:** Find healthcare organizations with relevant AI implementations
- **Uses:** `clinical_organizations` table via pgvector semantic search

### Workflow Advisor Agent
- **Purpose:** Synthesize recommendations combining tools and org insights
- **Uses:** Both tables via pgvector semantic search

## State Definition

```python
@dataclass
class AgentState:
    query: str
    route: Literal["tool_finder", "org_matcher", "workflow_advisor"] | None = None
    tools_results: list[dict] = field(default_factory=list)
    orgs_results: list[dict] = field(default_factory=list)
    response: str = ""
    error: str | None = None
    confidence: dict = field(default_factory=lambda: {
        "routing": 0.0,
        "retrieval": 0.0,
        "response": 0.0,
        "overall": 0.0
    })
```

## Confidence Scoring

Each response includes multi-level confidence assessment:

```
┌─────────────────────────────────────────────────────────┐
│                  CONFIDENCE PIPELINE                     │
├─────────────────────────────────────────────────────────┤
│  Supervisor    →  routing confidence (JSON response)    │
│       ↓                                                  │
│  Specialist    →  retrieval confidence (avg similarity) │
│       ↓                                                  │
│  LLM Response  →  response confidence (self-assessment) │
│       ↓                                                  │
│  Graph Output  →  overall = 0.2*routing + 0.4*retrieval │
│                          + 0.4*response                 │
└─────────────────────────────────────────────────────────┘
```

### Confidence Sources

| Component | Source | Calculation |
|-----------|--------|-------------|
| **Routing** | Supervisor agent | LLM returns confidence with route choice |
| **Retrieval** | pgvector search | Average cosine similarity of top results |
| **Response** | Specialist agent | LLM self-rates answer completeness |
| **Overall** | Graph aggregation | Weighted average (20/40/40) |

## Database Layer

Uses **SQLAlchemy 2.0** ORM with psycopg (v3) driver.

```
src/db/
├── models/           # SQLAlchemy ORM models
│   ├── base.py       # Engine, session factory, Base
│   ├── organization.py
│   ├── tool.py
│   ├── thread.py
│   ├── message.py
│   └── checkpoint.py
├── schema.py         # Base.metadata.create_all()
├── checkpointer.py   # LangGraph persistence
└── threads.py        # Thread/message CRUD
```

### Approach

| Operation | Method |
|-----------|--------|
| CRUD operations | SQLAlchemy ORM |
| Vector similarity | Raw SQL via `text()` |
| Session management | Context manager with auto-commit |
| Schema changes | Alembic migrations |

### Migrations (Alembic)

```
migrations/
├── env.py              # Connects to models and database
├── script.py.mako      # Migration template
└── versions/
    └── 001_initial_schema.py
```

**Workflow:**
1. Modify model in `src/db/models/`
2. Run `make migrate-new` → generates migration
3. Review generated file in `migrations/versions/`
4. Run `make migrate` → applies to database

## Database Schema

### clinical_organizations
Healthcare systems with AI use cases.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR | Organization name |
| org_type | VARCHAR | health_system, academic_medical_center |
| description | TEXT | Detailed description (embedded) |
| embedding | vector(1536) | OpenAI text-embedding-3-small |

### clinical_tools
Clinical decision support tools.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR | Tool name |
| category | VARCHAR | CDS, Documentation, Analytics |
| description | TEXT | Full description (embedded) |
| embedding | vector(1536) | OpenAI text-embedding-3-small |

### chat_threads & chat_messages
Conversation persistence with LangGraph checkpointing.

## Testing Strategy

### Unit Tests (No Network)
- Mock embeddings with deterministic hash-based vectors
- Mock database with fixture data
- Mock LLM with predefined responses

### Integration Tests
- Require running Docker database
- Use real pgvector queries
- Run separately: `make test`
