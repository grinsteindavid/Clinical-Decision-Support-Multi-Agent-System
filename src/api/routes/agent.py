import json

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from src.api.schemas import QueryRequest, QueryResponse, ConfidenceScore
from src.logger import get_logger
from src.agents.graph import create_clinical_graph

logger = get_logger(__name__)

router = APIRouter()

_graph = None


def get_graph():
    """Lazy initialization of the graph."""
    global _graph
    if _graph is None:
        logger.info("Initializing clinical graph...")
        _graph = create_clinical_graph()
        logger.info("Clinical graph initialized")
    return _graph


def get_initial_state(query_text: str) -> dict:
    """Create initial state for graph invocation."""
    return {
        "query": query_text,
        "route": None,
        "tools_results": [],
        "orgs_results": [],
        "response": "",
        "error": None,
        "confidence": {"routing": 0.0, "retrieval": 0.0, "response": 0.0, "overall": 0.0},
    }


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """Standard query endpoint - returns complete response as JSON."""
    logger.info(f"API query received: '{request.query[:50]}...'")

    try:
        graph = get_graph()
        result = graph.invoke(get_initial_state(request.query))

        confidence = result.get("confidence", {})
        logger.info(
            f"Query processed: route={result.get('route')}, "
            f"confidence={confidence.get('overall', 0):.2f}"
        )

        return QueryResponse(
            route=result.get("route"),
            response=result.get("response", ""),
            tools_results=result.get("tools_results", []),
            orgs_results=result.get("orgs_results", []),
            confidence=ConfidenceScore(**confidence),
        )

    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
def query_stream(request: QueryRequest):
    """Streaming query endpoint - returns Server-Sent Events (SSE)."""
    logger.info(f"API stream query received: '{request.query[:50]}...'")

    def generate():
        try:
            graph = get_graph()

            for event in graph.stream(get_initial_state(request.query)):
                node_name = list(event.keys())[0]
                node_output = event[node_name]

                logger.info(f"Stream event: {node_name}")

                yield {"event": "message", "data": json.dumps({"node": node_name, "data": node_output})}

            logger.info("Stream completed")
            yield {"event": "message", "data": "[DONE]"}

        except Exception as e:
            logger.exception(f"Stream error: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(generate())
