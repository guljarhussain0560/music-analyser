from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import get_db_session
from app.dto.schemas import HealthResponse

logger = get_logger("health")
router = APIRouter(tags=["Health & Monitoring"])


@router.get("/health", response_model=HealthResponse, summary="Application Health Check")
@router.get("/api/health", response_model=HealthResponse, summary="API Health Check")
def check_health(db: Session = Depends(get_db_session)) -> HealthResponse:
    """
    Returns real-time service health, database connectivity status, and version info.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check database query failure: {e}")
        db_status = "degraded"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        version="1.0.0",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )
