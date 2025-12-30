# Clinical Decision Support API

Flask-based REST API for the Clinical Decision Support Multi-Agent system.

## Quick Start

```bash
# Start the API server
python scripts/run_api.py
```

Server runs on `http://localhost:5000`

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

Processes a query and returns the complete response as JSON.

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
  "tools_results": [
    {
      "name": "Ambient Clinical Documentation AI",
      "category": "Documentation",
      "description": "...",
      "problem_solved": "...",
      "similarity": 0.85
    }
  ],
  "orgs_results": []
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "reduce documentation burden"}'
```

---

### Streaming Query (SSE)

```
POST /api/query/stream
Content-Type: application/json
```

Processes a query and streams events as Server-Sent Events (SSE).

**Request Body:**
```json
{
  "query": "What tools help with drug interactions?"
}
```

**Response:** `text/event-stream`

Each event contains the node name and its output:

```
data: {"node": "supervisor", "data": {"route": "tool_finder"}}

data: {"node": "tool_finder", "data": {"tools_results": [...], "response": "..."}}

data: [DONE]
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "drug interactions"}'
```

---

## Routing Logic

The supervisor agent routes queries to specialist agents:

| Route | Triggered By |
|-------|--------------|
| `tool_finder` | Questions about clinical tools, software, documentation |
| `org_matcher` | Questions about hospitals, health systems, case studies |
| `workflow_advisor` | Complex questions requiring both tools and org context |

---

## Error Handling

**400 Bad Request:**
```json
{
  "error": "Missing 'query' field"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Error message details"
}
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| Host | `0.0.0.0` | Server bind address |
| Port | `5000` | Server port |
| Debug | `True` | Flask debug mode |

---

## Logging

All requests are logged to:
- Console (real-time)
- `logs/agent_run_YYYYMMDD_HHMMSS.log` (timestamped file)

Log format:
```
2025-12-29 22:58:45 - src.api.routes.agent - INFO - API query received: 'reduce documentation...'
```

---

## Architecture

```
Client                    Flask API                  LangGraph
  |                           |                          |
  |-- POST /api/query ------->|                          |
  |                           |-- graph.invoke() ------->|
  |                           |<-- result ---------------|
  |<-- JSON response ---------|                          |
  |                           |                          |
  |-- POST /api/query/stream->|                          |
  |                           |-- graph.stream() ------->|
  |<-- SSE: supervisor -------|<-- yield: supervisor ----|
  |<-- SSE: tool_finder ------|<-- yield: tool_finder ---|
  |<-- SSE: [DONE] -----------|<-- END ------------------|
```

---

## Files

```
src/api/
├── __init__.py          # Module exports
├── app.py               # Flask app factory
├── README.md            # This file
└── routes/
    ├── __init__.py
    ├── health.py        # GET /health
    └── agent.py         # POST /api/query, /api/query/stream

scripts/
└── run_api.py           # Entry point
```

---

## Development

### Run with auto-reload
```bash
python scripts/run_api.py
```

Debug mode is enabled by default, so changes to code will auto-reload the server.

### Test endpoints
```bash
# Health check
curl http://localhost:5000/health

# Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your question here"}'
```

---

## Production Notes

For production deployment:

1. Disable debug mode
2. Use a production WSGI server (gunicorn, uWSGI)
3. Add authentication/authorization
4. Configure rate limiting
5. Set up proper error monitoring

Example with gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.api:create_app()"
```
