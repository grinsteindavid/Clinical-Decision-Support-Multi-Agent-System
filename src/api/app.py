from flask import Flask
from flask_cors import CORS

from src.logger import get_logger

logger = get_logger(__name__)


def create_app():
    """Flask application factory."""
    app = Flask(__name__)
    
    CORS(app)
    
    from src.api.routes.health import health_bp
    from src.api.routes.agent import agent_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(agent_bp, url_prefix='/api')
    
    logger.info("Flask app created with routes: /health, /api/query, /api/query/stream")
    
    return app
