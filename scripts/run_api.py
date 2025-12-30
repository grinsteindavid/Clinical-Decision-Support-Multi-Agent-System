#!/usr/bin/env python3
"""Entry point for the Flask API server."""

import sys
sys.path.insert(0, ".")

from src.logger import setup_app_logger

logger = setup_app_logger("clinical_ai_api")

from src.api import create_app


def main():
    logger.info("=" * 60)
    logger.info("Clinical Decision Support API")
    logger.info("=" * 60)
    
    app = create_app()
    
    host = "0.0.0.0"
    port = 5000
    
    logger.info(f"Starting Flask server on http://{host}:{port}")
    logger.info("Endpoints:")
    logger.info("  GET  /health          - Health check")
    logger.info("  POST /api/query       - Standard query (JSON response)")
    logger.info("  POST /api/query/stream - Streaming query (SSE)")
    
    app.run(host=host, port=port, debug=True, threaded=True)


if __name__ == "__main__":
    main()
