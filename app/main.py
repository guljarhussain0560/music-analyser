import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    analytics_router,
    auth_router,
    chatbot_router,
    health_router,
    process_router,
)
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging
from app.db.database import init_db

# Initialize structured logging
setup_logging()
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for initialization, APM error tracking, and graceful shutdown."""
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode")

    # Initialize Sentry APM error tracking if DSN is configured
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.APP_ENV,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            )
            logger.info("Sentry APM and error tracking initialized successfully")
        except Exception as e:
            logger.warning(f"Failed initializing Sentry APM: {e}")

    try:
        init_db()
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="High-Throughput Asynchronous Music Analysis, Source Separation & Synchronized Lyric Processing API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_and_timing_middleware(request: Request, call_next):
    """Structured request logging and response latency tracking middleware."""
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration}ms)")
    response.headers["X-Response-Time-Ms"] = str(duration)
    return response


# Root Endpoint
@app.get("/", tags=["Health"])
def root_endpoint():
    """Root entrypoint returning service metadata and documentation links."""
    return {
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
        "health_url": "/health",
    }


# Global Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"Domain exception on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "message": exc.message, "code": exc.__class__.__name__},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled internal server error on {request.url.path}: {str(exc)}")
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk

            sentry_sdk.capture_exception(exc)
        except Exception:
            pass
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# Include API Routers
app.include_router(health_router, tags=["Health"])
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(process_router, prefix=settings.API_V1_PREFIX, tags=["Audio Processing"])
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX, tags=["Audio Analytics"])
app.include_router(chatbot_router, prefix=settings.API_V1_PREFIX, tags=["Chatbot"])
