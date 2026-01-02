"""Thread management API endpoints."""

import json

from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from src.api.schemas import (
    QueryRequest,
    QueryResponse,
    ConfidenceScore,
    ThreadCreate,
    ThreadUpdate,
    ThreadResponse,
    ThreadDetailResponse,
    MessageResponse,
    SuccessResponse,
)
from src.logger import get_logger
from src.db.threads import (
    create_thread,
    get_thread,
    list_threads,
    update_thread_title,
    delete_thread,
    add_message,
    get_messages,
)
from src.db.checkpointer import PostgresCheckpointer
from src.agents.graph import create_clinical_graph

logger = get_logger(__name__)

router = APIRouter()

_graph = None
_checkpointer = None


def get_graph_with_checkpointer():
    """Get graph with PostgreSQL checkpointer."""
    global _graph, _checkpointer

    if _checkpointer is None:
        _checkpointer = PostgresCheckpointer()

    if _graph is None:
        logger.info("Initializing clinical graph with checkpointer...")
        _graph = create_clinical_graph(checkpointer=_checkpointer)
        logger.info("Clinical graph with checkpointer initialized")

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


@router.get("/threads", response_model=list[ThreadResponse])
def list_all_threads():
    """List all chat threads."""
    logger.info("Listing all threads")
    try:
        return list_threads()
    except Exception as e:
        logger.exception(f"Failed to list threads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
def create_new_thread(request: ThreadCreate):
    """Create a new chat thread."""
    logger.info(f"Creating new thread: {request.title}")
    try:
        return create_thread(request.title)
    except Exception as e:
        logger.exception(f"Failed to create thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}", response_model=ThreadDetailResponse)
def get_thread_detail(thread_id: str):
    """Get thread with messages."""
    logger.info(f"Getting thread {thread_id}")
    try:
        thread = get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        messages = get_messages(thread_id)
        thread["messages"] = messages
        return thread
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/threads/{thread_id}", response_model=ThreadResponse)
def update_thread(thread_id: str, request: ThreadUpdate):
    """Update thread title."""
    logger.info(f"Updating thread {thread_id}")
    try:
        thread = update_thread_title(thread_id, request.title)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/threads/{thread_id}", response_model=SuccessResponse)
def delete_thread_endpoint(thread_id: str):
    """Delete a thread."""
    logger.info(f"Deleting thread {thread_id}")
    try:
        deleted = delete_thread(thread_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Thread not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/threads/{thread_id}/query", response_model=QueryResponse)
def query_thread(thread_id: str, request: QueryRequest):
    """Query with thread context."""
    logger.info(f"Query in thread {thread_id}: '{request.query[:50]}...'")

    try:
        thread = get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        add_message(thread_id, "user", request.query)

        graph = get_graph_with_checkpointer()
        config = {"configurable": {"thread_id": thread_id}}

        result = graph.invoke(get_initial_state(request.query), config)

        route = result.get("route")
        response = result.get("response", "")
        confidence = result.get("confidence", {})

        add_message(thread_id, "assistant", response, route)

        if thread["title"] == "New Chat" and response:
            new_title = request.query[:50] + ("..." if len(request.query) > 50 else "")
            update_thread_title(thread_id, new_title)

        logger.info(f"Query processed: route={route}, confidence={confidence.get('overall', 0):.2f}")

        return QueryResponse(
            route=route,
            response=response,
            tools_results=result.get("tools_results", []),
            orgs_results=result.get("orgs_results", []),
            confidence=ConfidenceScore(**confidence),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to process query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/threads/{thread_id}/query/stream")
def query_thread_stream(thread_id: str, request: QueryRequest):
    """Streaming query with thread context."""
    logger.info(f"Stream query in thread {thread_id}: '{request.query[:50]}...'")

    def generate():
        try:
            thread = get_thread(thread_id)
            if not thread:
                yield {"event": "error", "data": json.dumps({"error": "Thread not found"})}
                return

            add_message(thread_id, "user", request.query)

            graph = get_graph_with_checkpointer()
            config = {"configurable": {"thread_id": thread_id}}

            final_response = ""
            final_route = ""

            for event in graph.stream(get_initial_state(request.query), config):
                node_name = list(event.keys())[0]
                node_output = event[node_name]

                logger.info(f"Stream event: {node_name}")

                if node_output.get("route"):
                    final_route = node_output["route"]
                if node_output.get("response"):
                    final_response = node_output["response"]

                yield {"event": "message", "data": json.dumps({"node": node_name, "data": node_output})}

            if final_response:
                add_message(thread_id, "assistant", final_response, final_route)

            if thread["title"] == "New Chat" and request.query:
                new_title = request.query[:50] + ("..." if len(request.query) > 50 else "")
                update_thread_title(thread_id, new_title)

            logger.info("Stream completed")
            yield {"event": "message", "data": "[DONE]"}

        except Exception as e:
            logger.exception(f"Stream error: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(generate())
