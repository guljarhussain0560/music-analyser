"""FastAPI sub-routers."""

from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chatbot import router as chatbot_router
from app.api.routes.health import router as health_router
from app.api.routes.process import router as process_router

__all__ = [
    "auth_router",
    "process_router",
    "analytics_router",
    "chatbot_router",
    "health_router",
]
