import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.logger import get_logger

logger = get_logger(__name__)


def init_database():
    """Initialize database schema if needed."""
    try:
        from src.db.schema import init_schema
        init_schema()
        logger.info("Database schema initialized")
    except Exception as e:
        logger.warning(f"Schema init skipped or failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    if os.getenv("AUTO_INIT_DB", "true").lower() == "true":
        init_database()
    logger.info("FastAPI app started")
    yield
    logger.info("FastAPI app shutting down")


app = FastAPI(
    title="Clinical Decision Support API",
    description="Multi-agent system for clinical decision support using pgvector",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.routes.health import router as health_router
from src.api.routes.agent import router as agent_router
from src.api.routes.threads import router as threads_router

app.include_router(health_router)
app.include_router(agent_router, prefix="/api")
app.include_router(threads_router, prefix="/api")

logger.info("FastAPI app configured with routes: /health, /api/query, /api/threads")
