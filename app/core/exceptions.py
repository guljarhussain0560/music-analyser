from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger("exceptions")


class AppException(Exception):
    """Base domain exception for AI Music Analyser application."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppException):
    """Raised when an entity is not found in database."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)},
        )


class AuthenticationError(AppException):
    """Raised for authentication or credential validation failures."""

    def __init__(self, message: str = "Invalid credentials or expired token"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={"authenticate": "Bearer"},
        )


class AudioProcessingError(AppException):
    """Raised when stem separation, feature extraction or transcode fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Audio processing error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class TranscriptionError(AppException):
    """Raised when Groq Whisper speech-to-text fails."""

    def __init__(self, message: str):
        super().__init__(
            message=f"Transcription error: {message}", status_code=status.HTTP_502_BAD_GATEWAY
        )


class DownloaderError(AppException):
    """Raised when YouTube/Spotify audio download fails."""

    def __init__(self, message: str):
        super().__init__(
            message=f"Download error: {message}", status_code=status.HTTP_400_BAD_REQUEST
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers centralized exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        logger.error(f"AppException on {request.method} {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail, "details": {}},
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception):
        logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "An unexpected internal server error occurred.",
                "details": {},
            },
        )
