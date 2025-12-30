# Clinical Decision Support Multi-Agent

LangGraph-based multi-agent system for clinical decision support using pgvector semantic search.

## Architecture Overview

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
- **Input:** Query about clinical tools, documentation, drug safety, etc.
- **Output:** List of matching tools with explanations
- **Uses:** `clinical_tools` table via pgvector semantic search

### Org Matcher Agent
- **Purpose:** Find healthcare organizations with relevant AI implementations
- **Input:** Query about health systems, case studies, implementations
- **Output:** List of matching organizations with AI use cases
- **Uses:** `clinical_organizations` table via pgvector semantic search

### Workflow Advisor Agent
- **Purpose:** Synthesize recommendations combining tools and org insights
- **Input:** Complex queries requiring both tools and organizational context
- **Output:** Comprehensive workflow recommendations
- **Uses:** Both tables via pgvector semantic search

---

## Folder Structure

```
pgvectors/
├── src/
│   ├── config.py                    # Configuration
│   ├── db/                          # Database connection
│   ├── embeddings/                  # OpenAI embeddings
│   ├── seed/                        # Seed data
│   ├── queries/                     # Raw SQL queries
│   │
│   ├── agents/                      # LangGraph agents
│   │   ├── __init__.py
│   │   ├── state.py                 # Shared state definition
│   │   ├── supervisor.py            # Router agent
│   │   ├── tool_finder.py           # Tools specialist
│   │   ├── org_matcher.py           # Orgs specialist
│   │   ├── workflow_advisor.py      # Synthesizer
│   │   └── graph.py                 # LangGraph workflow
│   │
│   └── retrievers/                  # pgvector retrieval
│       ├── __init__.py
│       ├── base.py                  # Abstract interface
│       ├── tools_retriever.py       # clinical_tools
│       └── orgs_retriever.py        # clinical_organizations
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── mocks/
│   │   ├── __init__.py
│   │   ├── mock_embeddings.py       # Fake embeddings
│   │   └── mock_db.py               # Mock DB responses
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_state.py
│   │   ├── test_supervisor.py
│   │   ├── test_tool_finder.py
│   │   ├── test_org_matcher.py
│   │   └── test_retrievers.py
│   └── integration/
│       ├── __init__.py
│       └── test_graph_e2e.py
│
├── scripts/
│   └── run_agent.py                 # CLI runner
│
└── requirements.txt
```

---

## Dependencies

```txt
# Core
psycopg[binary]==3.1.18
pgvector==0.2.5
openai>=1.40.0
python-dotenv==1.0.1

# LangGraph
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-openai>=0.2.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## State Definition

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class AgentState:
    query: str
    route: Literal["tool_finder", "org_matcher", "workflow_advisor"] | None = None
    tools_results: list[dict] = field(default_factory=list)
    orgs_results: list[dict] = field(default_factory=list)
    response: str = ""
    error: str | None = None
```

---

## Testing Strategy

### Unit Tests (No Network)

| Component | Mock Strategy |
|-----------|---------------|
| Embeddings | Deterministic hash-based fake vectors |
| Database | In-memory fixture data |
| LLM | Predefined responses or langchain FakeLLM |

### Mock Embeddings

```python
def fake_embedding(text: str) -> list[float]:
    """Deterministic fake embedding from text hash."""
    import hashlib
    h = hashlib.md5(text.encode()).hexdigest()
    return [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)] * 96
```

### Mock Retriever

```python
class MockToolsRetriever:
    def __init__(self, fixture_data: list[dict]):
        self.data = fixture_data
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        return self.data[:limit]
```

### Dependency Injection

All agents receive retriever and LLM as constructor arguments:

```python
class ToolFinderAgent:
    def __init__(self, retriever: BaseRetriever, llm: BaseChatModel):
        self.retriever = retriever
        self.llm = llm
```

This allows injecting mocks for testing without network calls.

---

## Integration Tests

- Require running Docker database
- Use real pgvector queries
- Mock only OpenAI (or use recorded responses)
- Run separately: `pytest tests/integration -v`

---

## Example Usage

```python
from src.agents.graph import create_clinical_graph

graph = create_clinical_graph()

result = graph.invoke({
    "query": "How can we reduce documentation burden for physicians?"
})

print(result["response"])
# → Recommends Ambient Clinical Documentation AI, ProVation, etc.
```

---

## Implementation Order

1. [ ] `src/retrievers/base.py` - Abstract retriever interface
2. [ ] `src/retrievers/tools_retriever.py` - Tools semantic search
3. [ ] `src/retrievers/orgs_retriever.py` - Orgs semantic search
4. [ ] `src/agents/state.py` - State dataclass
5. [ ] `src/agents/supervisor.py` - Routing logic
6. [ ] `src/agents/tool_finder.py` - Tools specialist
7. [ ] `src/agents/org_matcher.py` - Orgs specialist
8. [ ] `src/agents/workflow_advisor.py` - Synthesizer
9. [ ] `src/agents/graph.py` - LangGraph workflow
10. [ ] `tests/mocks/*` - Mock implementations
11. [ ] `tests/unit/*` - Unit tests
12. [ ] `scripts/run_agent.py` - CLI runner
13. [ ] `tests/integration/*` - E2E tests

---

## Wolters Kluwer Health Alignment

This architecture demonstrates:

- **Clinical Decision Support** - Tool recommendations for clinical workflows
- **Burnout Reduction** - Finding documentation and automation solutions
- **Evidence-Based** - Semantic search over curated clinical data
- **Multi-Agent AI** - Specialist agents with clear responsibilities
- **Production Patterns** - Dependency injection, testing, clean architecture
