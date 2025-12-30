import json
from flask import Blueprint, request, jsonify, Response

from src.logger import get_logger
from src.agents.graph import create_clinical_graph

logger = get_logger(__name__)

agent_bp = Blueprint('agent', __name__)

_graph = None


def get_graph():
    """Lazy initialization of the graph."""
    global _graph
    if _graph is None:
        logger.info("Initializing clinical graph...")
        _graph = create_clinical_graph()
        logger.info("Clinical graph initialized")
    return _graph


@agent_bp.route('/query', methods=['POST'])
def query():
    """
    Standard query endpoint - returns complete response as JSON.
    
    Request body:
        {"query": "How can we reduce documentation burden?"}
    
    Response:
        {"route": "tool_finder", "response": "...", "tools_results": [...]}
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        logger.warning("Invalid request: missing 'query' field")
        return jsonify({"error": "Missing 'query' field"}), 400
    
    query_text = data['query']
    logger.info(f"API query received: '{query_text[:50]}...'")
    
    try:
        graph = get_graph()
        result = graph.invoke({
            "query": query_text,
            "route": None,
            "tools_results": [],
            "orgs_results": [],
            "response": "",
            "error": None
        })
        
        logger.info(f"Query processed: route={result.get('route')}, response_len={len(result.get('response', ''))}")
        
        return jsonify({
            "route": result.get("route"),
            "response": result.get("response"),
            "tools_results": result.get("tools_results", []),
            "orgs_results": result.get("orgs_results", [])
        })
        
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500


@agent_bp.route('/query/stream', methods=['POST'])
def query_stream():
    """
    Streaming query endpoint - returns Server-Sent Events (SSE).
    
    Request body:
        {"query": "How can we reduce documentation burden?"}
    
    Response:
        SSE stream with events for each graph step
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        logger.warning("Invalid stream request: missing 'query' field")
        return jsonify({"error": "Missing 'query' field"}), 400
    
    query_text = data['query']
    logger.info(f"API stream query received: '{query_text[:50]}...'")
    
    def generate():
        try:
            graph = get_graph()
            
            initial_state = {
                "query": query_text,
                "route": None,
                "tools_results": [],
                "orgs_results": [],
                "response": "",
                "error": None
            }
            
            for event in graph.stream(initial_state):
                node_name = list(event.keys())[0]
                node_output = event[node_name]
                
                logger.info(f"Stream event: {node_name}")
                
                sse_data = {
                    "node": node_name,
                    "data": node_output
                }
                yield f"data: {json.dumps(sse_data)}\n\n"
            
            logger.info("Stream completed")
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.exception(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )
