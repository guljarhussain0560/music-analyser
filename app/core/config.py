import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Protobuf environment compatibility for tensorflow
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # --- Application ---
    APP_NAME: str = "AI Music Analyser"
    APP_ENV: str = "development"
    PORT: int = 8080
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api"

    # --- CORS ---
    CORS_ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        if not self.CORS_ALLOWED_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    # --- Database ---
    DATABASE_URL: str = Field(
        default="sqlite:///./music_analyser.db", description="SQLAlchemy database connection string"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        if not v:
            return "sqlite:///./music_analyser.db"
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+psycopg2://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # --- Security & JWT ---
    SECRET_KEY: str = Field(
        default="dev-insecure-secret-key-change-in-production-min-32-chars",
        description="Cryptographic secret key for signing JWT tokens",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAY: int = 30

    # --- OAuth (Google) ---
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    # --- External AI & Transcription (Groq) ---
    GROQ_API_KEY: str | None = None
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"
    GROQ_LLM_MODEL: str = "llama-3.1-8b-instant"

    # --- AWS S3 Storage ---
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_S3_BUCKET_NAME: str | None = None
    AWS_REGION: str = "us-east-1"

    # --- Spotify API ---
    SPOTIPY_CLIENT_ID: str | None = None
    SPOTIPY_CLIENT_SECRET: str | None = None

    # --- YouTube Cookies ---
    YT_COOKIES_PATH: str | None = "./cookies.txt"

    # --- Transactional Email ---
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = "notifications@musicanalyser.io"
    MAIL_PORT: int = 587
    MAIL_SERVER: str | None = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # --- Frontend URL ---
    FRONTEND_URL: str = "http://localhost:5173"


# Global singleton instance
settings = Settings()
