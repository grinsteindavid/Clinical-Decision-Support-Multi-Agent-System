# Clinical Decision Support API

FastAPI-based REST API for the Clinical Decision Support Multi-Agent system.

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "clinical-ai-agent"
}
```

---

### Standard Query

```
POST /api/query
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "How can we reduce documentation burden for physicians?"
}
```

**Response:**
```json
{
  "route": "tool_finder",
  "response": "Based on your query, I recommend...",
  "tools_results": [...],
  "orgs_results": [],
  "confidence": {
    "routing": 0.9,
    "retrieval": 0.48,
    "response": 0.85,
    "overall": 0.73
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "reduce documentation burden"}' | jq
```

---

### Streaming Query (SSE)

```
POST /api/query/stream
Content-Type: application/json
```

Streams events as Server-Sent Events (SSE).

**Response:** `text/event-stream`
```
data: {"node": "supervisor", "data": {"route": "tool_finder"}}
data: {"node": "tool_finder", "data": {"tools_results": [...], "response": "..."}}
data: [DONE]
```

---

### Thread Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/threads` | List all threads |
| POST | `/api/threads` | Create new thread |
| GET | `/api/threads/:id` | Get thread with messages |
| PATCH | `/api/threads/:id` | Update thread title |
| DELETE | `/api/threads/:id` | Delete thread |
| POST | `/api/threads/:id/query` | Query with thread context |
| POST | `/api/threads/:id/query/stream` | Streaming with thread |

---

## Routing Logic

| Route | Triggered By |
|-------|--------------|
| `tool_finder` | Questions about clinical tools, software, documentation |
| `org_matcher` | Questions about hospitals, health systems, case studies |
| `workflow_advisor` | Complex questions requiring both tools and org context |

---

## Confidence Scores

All query responses include confidence metrics:

```json
{
  "confidence": {
    "routing": 0.9,
    "retrieval": 0.48,
    "response": 0.85,
    "overall": 0.73
  }
}
```

| Field | Description | Weight |
|-------|-------------|--------|
| `routing` | How confident the supervisor is in the route choice | 20% |
| `retrieval` | Average similarity score of retrieved results | 40% |
| `response` | LLM's self-assessment of answer quality | 40% |
| `overall` | Weighted average of above scores | - |

### Interpretation

| Overall Score | Meaning |
|---------------|---------|
| ≥0.7 | High confidence - reliable answer |
| 0.4-0.7 | Medium confidence - review recommended |
| <0.4 | Low confidence - answer may be incomplete |

---

## Error Handling

**400 Bad Request:**
```json
{"error": "Missing 'query' field"}
```

**500 Internal Server Error:**
```json
{"error": "Error message details"}
```

---

## Example Workflows

### Create Thread and Query

```bash
# 1. Create a new thread
THREAD_ID=$(curl -s -X POST http://localhost:5000/api/threads \
  -H "Content-Type: application/json" \
  -d '{"title": "Documentation Help"}' | jq -r '.id')

# 2. Query within the thread
curl -s -X POST "http://localhost:5000/api/threads/$THREAD_ID/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What tools reduce documentation burden?"}' | jq

# 3. Check thread messages
curl -s "http://localhost:5000/api/threads/$THREAD_ID" | jq '.messages'

# 4. Delete thread when done
curl -X DELETE "http://localhost:5000/api/threads/$THREAD_ID"
```

### Streaming Response

```bash
curl -N -X POST http://localhost:5000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Find AI tools for cardiology"}'
```
