from fastapi import APIRouter

from src.api.schemas import HealthResponse
from src.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "clinical-ai-agent"}
