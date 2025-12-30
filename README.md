# Clinical Decision Support Multi-Agent System

A production-ready LangGraph multi-agent system for clinical decision support, leveraging pgvector for semantic search over healthcare data.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-red.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev/)

<img width="1019" height="745" alt="image" src="https://github.com/user-attachments/assets/1b90d28f-fb19-46fd-afe3-50b4f0302c71" />


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
- **Streaming API** - Real-time Server-Sent Events (SSE) for progressive responses
- **React Chat UI** - Modern streaming chat interface
- **Comprehensive Logging** - Timestamped log files for debugging and auditing
- **Docker Ready** - Full-stack containerization support

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React UI      │     │   Flask API     │     │   PostgreSQL    │
│   (Vite/nginx)  │────▶│   (gunicorn)    │────▶│   (pgvector)    │
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

- Python 3.10+
- Docker & Docker Compose
- Node.js 20+ (for UI development)
- OpenAI API Key

### 1. Clone and Setup

```bash
git clone https://github.com/grinsteindavid/pgvector-Learning-Project.git
cd pgvector-Learning-Project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 3. Start Database

```bash
docker-compose up -d
```

### 4. Initialize and Seed Database

```bash
python scripts/init_db.py
python scripts/seed_db.py
```

### 5. Run the Application

**Option A: CLI Agent**
```bash
python scripts/run_agent.py
```

**Option B: Flask API**
```bash
python scripts/run_api.py
```

**Option C: Full Stack (API + UI)**
```bash
# Terminal 1: API
python scripts/run_api.py

# Terminal 2: UI
cd ui && npm install && npm run dev
```

Access the UI at http://localhost:3000

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
  "orgs_results": [...]
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

See [API README](src/api/README.md) for complete documentation.

---

## Project Structure

```
pgvectors/
├── docker-compose.yml          # PostgreSQL + pgvector
├── docker-compose.full.yml     # Full stack (DB + API + UI)
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Test configuration
├── .env                        # Environment variables (gitignored)
│
├── api/
│   └── Dockerfile              # Flask API container
│
├── ui/                         # React frontend
│   ├── Dockerfile              # Multi-stage build
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       └── components/
│           └── Chat.tsx        # Streaming chat component
│
├── src/
│   ├── config.py               # Configuration management
│   ├── logger.py               # Centralized logging
│   │
│   ├── api/                    # Flask REST API
│   │   ├── app.py              # App factory
│   │   └── routes/
│   │       ├── health.py       # Health check
│   │       └── agent.py        # Query endpoints
│   │
│   ├── agents/                 # LangGraph agents
│   │   ├── state.py            # Agent state definition
│   │   ├── graph.py            # Workflow graph
│   │   ├── supervisor.py       # Routing agent
│   │   ├── tool_finder.py      # Clinical tools agent
│   │   ├── org_matcher.py      # Organizations agent
│   │   ├── workflow_advisor.py # Synthesis agent
│   │   └── tools.py            # LangChain tool schemas
│   │
│   ├── retrievers/             # pgvector search
│   │   ├── base.py             # Abstract retriever
│   │   ├── tools_retriever.py  # Clinical tools search
│   │   └── orgs_retriever.py   # Organizations search
│   │
│   ├── db/                     # Database layer
│   │   ├── connection.py       # Connection management
│   │   └── schema.py           # Schema initialization
│   │
│   ├── embeddings/
│   │   └── openai_embed.py     # OpenAI embeddings
│   │
│   └── seed/
│       ├── clinical_data.py    # Sample healthcare data
│       └── run_seed.py         # Seeding script
│
├── scripts/
│   ├── init_db.py              # Initialize schema
│   ├── seed_db.py              # Seed database
│   ├── run_agent.py            # CLI agent
│   ├── run_api.py              # Flask server
│   └── query_examples.py       # Example queries
│
├── tests/
│   ├── conftest.py             # Test fixtures
│   ├── mocks/
│   │   ├── mock_embeddings.py  # Fake embeddings
│   │   └── mock_db.py          # Mock retrievers
│   ├── unit/                   # Unit tests (no network)
│   └── integration/            # E2E tests (real DB + API)
│
└── logs/                       # Timestamped log files (gitignored)
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

### Full Stack

```bash
# Build and run all services
docker-compose -f docker-compose.full.yml up --build

# Access:
# - UI: http://localhost:3000
# - API: http://localhost:5000
# - PostgreSQL: localhost:5432
```

### Individual Services

```bash
# Database only
docker-compose up -d

# API only (requires running database)
docker build -f api/Dockerfile -t clinical-ai-api .
docker run -p 5000:5000 --env-file .env clinical-ai-api

# UI only (requires running API)
cd ui && docker build -t clinical-ai-ui .
docker run -p 3000:80 clinical-ai-ui
```

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

### HNSW Indexes

```sql
CREATE INDEX idx_org_embedding ON clinical_organizations 
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_tool_embedding ON clinical_tools 
    USING hnsw (embedding vector_cosine_ops);
```

---

## Development

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

## License

MIT License

---

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent framework
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity for PostgreSQL
- [OpenAI](https://openai.com) - Embeddings and LLM
- Healthcare domain context inspired by Wolters Kluwer Health
