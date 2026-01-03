# Clinical Decision Support Multi-Agent System

A LangGraph multi-agent system for clinical decision support, leveraging pgvector for semantic search over healthcare data.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev/)

<img width="877" height="749" alt="image" src="https://github.com/user-attachments/assets/e132526a-de05-49ef-8b2f-9d40c5144439" />


---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Database Schema](#database-schema)
- [Development](#development)

---

## Overview

This system provides intelligent clinical decision support through a multi-agent architecture:

| Agent | Responsibility |
|-------|----------------|
| **Supervisor** | Routes queries to specialist agents |
| **Tool Finder** | Searches clinical tools and software |
| **Org Matcher** | Finds healthcare organizations with AI implementations |
| **Workflow Advisor** | Synthesizes comprehensive recommendations |

### Key Features

- **Semantic Search** - pgvector-powered similarity search over clinical data
- **Multi-Agent Routing** - Intelligent query classification and delegation
- **Confidence Scores** - Multi-level confidence assessment (routing, retrieval, response)
- **Streaming API** - Real-time Server-Sent Events (SSE) for progressive responses
- **React Chat UI** - Modern streaming chat interface with thread persistence
- **LangGraph Checkpoints** - PostgreSQL-backed conversation state persistence
- **Docker Ready** - Separate dev/prod configurations

---

## Architecture

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
                    │                     │
                    │  ┌───────────────┐  │
                    │  │  Supervisor   │  │
                    │  └───────┬───────┘  │
                    │          │          │
                    │  ┌───────┴───────┐  │
                    │  ▼       ▼       ▼  │
                    │ Tool   Org   Workflow│
                    │ Finder Matcher Advisor│
                    └─────────────────────┘
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key

### 1. Clone and Configure

```bash
git clone https://github.com/grinsteindavid/Clinical-Decision-Support-Multi-Agent-System.git
cd Clinical-Decision-Support-Multi-Agent-System

cp .env.example .env
# Edit .env with your OpenAI API key
```

### 2. Start Development Environment

```bash
make dev
```

This starts all services with hot-reload:
- **UI**: http://localhost:3000
- **API**: http://localhost:5000
- **PostgreSQL**: localhost:5432

### 3. Seed Database (optional)

```bash
make init-db
make seed-db
```

### Available Commands

```bash
make dev       # Start development environment (hot-reload)
make prod      # Start production environment
make down      # Stop all containers
make logs      # View container logs
make test      # Run test suite
make clean     # Remove containers, volumes, and cache
```

---

## API Reference

### Health Check

```
GET /health
```

### Standard Query

```
POST /api/query
Content-Type: application/json

{"query": "How can we reduce documentation burden?"}
```

**Response:**
```json
{
  "route": "tool_finder",
  "response": "Based on your query...",
  "tools_results": [...],
  "orgs_results": [...],
  "confidence": {
    "routing": 0.9,
    "retrieval": 0.48,
    "response": 0.85,
    "overall": 0.73
  }
}
```

### Streaming Query (SSE)

```
POST /api/query/stream
Content-Type: application/json

{"query": "What tools help with drug interactions?"}
```

**Response:** Server-Sent Events stream
```
data: {"node": "supervisor", "data": {"route": "tool_finder"}}
data: {"node": "tool_finder", "data": {"response": "..."}}
data: [DONE]
```

See [API Documentation](docs/api.md) for complete reference.

---

## Project Structure

```
pgvectors/
├── .env.example                 # Environment template
├── Makefile                     # Dev/prod commands
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Dev/test dependencies
├── pytest.ini                   # Test configuration
│
├── compose/                     # Docker Compose configs
│   ├── docker-compose.yml       # Base services
│   ├── docker-compose.dev.yml   # Dev overrides (hot-reload)
│   └── docker-compose.prod.yml  # Prod overrides (optimized)
│
├── docker/                      # Dockerfiles
│   ├── api/
│   │   ├── Dockerfile           # Production API
│   │   └── Dockerfile.dev       # Development API
│   └── ui/
│       ├── Dockerfile           # Production UI (nginx)
│       ├── Dockerfile.dev       # Development UI (vite)
│       └── nginx.conf           # Production nginx config
│
├── docs/                        # Documentation
│   ├── api.md                   # API reference
│   └── architecture.md          # System design
│
├── scripts/                     # CLI utilities
│   ├── init_db.py               # Initialize schema
│   ├── seed_db.py               # Seed database
│   ├── run_agent.py             # CLI agent
│   └── query_examples.py        # Example queries
│
├── src/                         # Python application
│   ├── config.py                # Configuration
│   ├── logger.py                # Logging setup
│   ├── api/                     # FastAPI REST API
│   │   ├── app.py               # App factory
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── routes/
│   │       ├── health.py        # Health endpoint
│   │       ├── agent.py         # Query endpoints
│   │       └── threads.py       # Thread management
│   ├── agents/                  # LangGraph agents
│   │   ├── state.py             # State definition
│   │   ├── graph.py             # Workflow graph
│   │   ├── supervisor.py        # Router agent
│   │   ├── tool_finder.py       # Tools agent
│   │   ├── org_matcher.py       # Orgs agent
│   │   ├── workflow_advisor.py  # Synthesis agent
│   │   └── tools.py             # LangChain tool definitions
│   ├── db/                      # Database layer (SQLAlchemy)
│   │   ├── models/              # ORM models
│   │   │   ├── base.py          # Engine & session factory
│   │   │   ├── organization.py  # ClinicalOrganization
│   │   │   ├── tool.py          # ClinicalTool
│   │   │   ├── thread.py        # ChatThread
│   │   │   ├── message.py       # ChatMessage
│   │   │   └── checkpoint.py    # LangGraphCheckpoint
│   │   ├── schema.py            # Schema init
│   │   ├── checkpointer.py      # LangGraph checkpoints
│   │   └── threads.py           # Thread persistence
│   ├── retrievers/              # pgvector search
│   │   ├── base.py              # Abstract retriever
│   │   ├── tools_retriever.py   # Tools search
│   │   └── orgs_retriever.py    # Orgs search
│   ├── embeddings/
│   │   └── openai_embed.py      # OpenAI embeddings
│   └── seed/                    # Database seeding
│       ├── clinical_data.py     # Sample clinical data
│       └── run_seed.py          # Seed runner
│
├── migrations/                  # Alembic migrations
│   ├── env.py                   # Migration environment
│   └── versions/                # Migration files
│
├── tests/                       # Test suite
│   ├── conftest.py              # Fixtures
│   ├── mocks/                   # Mock implementations
│   ├── unit/                    # Unit tests
│   └── integration/             # E2E tests
│
├── ui/                          # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── components/
│       │   ├── Chat.tsx         # Chat interface
│       │   └── Sidebar.tsx      # Thread list
│       ├── hooks/
│       │   └── useThreads.ts    # Thread state
│       └── types/
│           └── thread.ts        # TypeScript types
│
└── logs/                        # Log files (gitignored)
```

---

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/vectordb` |

### Logging

Logs are written to `logs/agent_run_YYYYMMDD_HHMMSS.log` and console.

```python
from src.logger import get_logger
logger = get_logger(__name__)
logger.info("Processing query...")
```

---

## Testing

### Unit Tests (No Network)

```bash
pytest tests/unit -v
```

### Integration Tests (Requires DB + API Key)

```bash
RUN_INTEGRATION_TESTS=1 pytest tests/integration -v
```

### Test Coverage

- 29 unit tests with mocked embeddings and database
- 3 integration tests for end-to-end flow
- Live log output during test execution

---

## Docker Deployment

### Development (Hot-Reload)

```bash
make dev
# Or manually:
docker compose -f compose/docker-compose.yml -f compose/docker-compose.dev.yml up
```

Features:
- Source code mounted as volumes
- Flask debug mode with auto-reload
- Vite dev server with HMR
- Logs visible in terminal

### Production (Optimized)

```bash
make prod
# Or manually:
docker compose -f compose/docker-compose.yml -f compose/docker-compose.prod.yml up -d
```

Features:
- Multi-stage builds (smaller images)
- uvicorn with 4 workers
- nginx serving static assets
- Health checks enabled

### Access

| Service | Dev | Prod |
|---------|-----|------|
| UI | http://localhost:3000 | http://localhost:3000 |
| API | http://localhost:5000 | http://localhost:5000 |
| PostgreSQL | localhost:5432 | localhost:5432 |

---

## Database Schema

### clinical_organizations

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR(255) | Organization name |
| org_type | VARCHAR(50) | health_system, academic_medical_center |
| specialty | VARCHAR(100) | Primary specialty focus |
| description | TEXT | Detailed description (embedded) |
| city, state | VARCHAR | Location |
| services | JSONB | Service capabilities |
| ai_use_cases | TEXT[] | AI applications in use |
| embedding | vector(1536) | OpenAI text-embedding-3-small |

### clinical_tools

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR(255) | Tool name |
| category | VARCHAR(100) | CDS, Documentation, Analytics |
| description | TEXT | Full description (embedded) |
| target_users | TEXT[] | Intended user roles |
| problem_solved | TEXT | Problem addressed |
| embedding | vector(1536) | OpenAI text-embedding-3-small |

### chat_threads

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| title | VARCHAR(255) | Thread title |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update |

### chat_messages

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| thread_id | UUID | Foreign key to chat_threads |
| role | VARCHAR(20) | 'user' or 'assistant' |
| content | TEXT | Message content |
| route | VARCHAR(50) | Agent route used |
| created_at | TIMESTAMPTZ | Creation timestamp |

### HNSW Indexes

```sql
CREATE INDEX idx_org_embedding ON clinical_organizations 
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_tool_embedding ON clinical_tools 
    USING hnsw (embedding vector_cosine_ops);
```

---

## Development

### Dev vs Prod

| Aspect | Development | Production |
|--------|-------------|------------|
| API Server | FastAPI (uvicorn reload) | uvicorn (4 workers) |
| UI Server | Vite dev server | nginx + static |
| Code | Volume mounts | Built into image |
| Debugging | Enabled | Disabled |

### Adding New Agents

1. Create agent file in `src/agents/`
2. Define agent class with `run(state: AgentState)` method
3. Register in `src/agents/graph.py`
4. Add routing logic in `src/agents/supervisor.py`

### Adding New Retrievers

1. Create retriever in `src/retrievers/`
2. Extend `BaseRetriever` abstract class
3. Implement `search(query, limit)` method
4. Add to `src/retrievers/__init__.py`

### Code Style

- Functions and files should be short and focused
- One concept per file
- Descriptive naming based on responsibility
- Logging for all significant operations

---

## Confidence Scores

Each API response includes confidence metrics:

| Score | Weight | Source |
|-------|--------|--------|
| **Routing** | 20% | Supervisor agent's certainty in route choice |
| **Retrieval** | 40% | Average pgvector similarity of retrieved results |
| **Response** | 40% | LLM's self-assessment of answer quality |
| **Overall** | - | Weighted average of above |

### Confidence Levels

| Range | Level | UI Color |
|-------|-------|----------|
| ≥70% | High | Green |
| 40-70% | Medium | Yellow |
| <40% | Low | Red |

---

## Useful Commands

### Docker

```bash
# Start development environment
make dev

# Start production environment
make prod

# View logs (all services)
make logs

# Stop all services
make down

# Full cleanup (containers + volumes)
make clean
```

### Database

```bash
# Initialize schema (auto on startup, or manual)
make init-db

# Seed sample data
make seed-db

# Connect to PostgreSQL
docker exec -it pgvector_db psql -U postgres -d vectordb
```

### Migrations (Alembic)

```bash
# Run pending migrations
make migrate

# Generate new migration after model changes
make migrate-new
# → Prompts for migration message
# → Creates migrations/versions/xxx_message.py

# Rollback last migration
make migrate-down

# Check current migration status
docker compose -f compose/docker-compose.yml -f compose/docker-compose.dev.yml exec api alembic current
```

### Testing

```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests (requires running services)
RUN_INTEGRATION_TESTS=1 pytest tests/integration -v

# Run all tests with coverage
pytest --cov=src tests/
```

### API Testing

```bash
# Health check
curl http://localhost:5000/health

# Query with confidence scores
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find documentation tools"}'

# Create a thread
curl -X POST http://localhost:5000/api/threads \
  -H "Content-Type: application/json" \
  -d '{"title": "My Chat"}'

# Query in thread
curl -X POST http://localhost:5000/api/threads/{thread_id}/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What tools reduce burnout?"}'
```

### Container Management

```bash
# Restart API (picks up code changes)
docker compose -f compose/docker-compose.yml -f compose/docker-compose.dev.yml restart api

# View API logs
docker logs clinical_ai_api --tail 50 -f

# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Execute command in container
docker exec clinical_ai_api python -c "from src.agents.graph import create_clinical_graph; print('OK')"
```

---

## License

MIT License

---

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent framework
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity for PostgreSQL
- [OpenAI](https://openai.com) - Embeddings and LLM
- Healthcare domain context inspired by Wolters Kluwer Health
