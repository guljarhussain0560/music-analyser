from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "AI Music Analyser"
    APP_ENV: str = "development"
    DEBUG: bool = False
    PORT: int = 8080
    API_V1_PREFIX: str = "/api"

    # Security & JWT
    SECRET_KEY: str = "insecure-default-change-me-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAY: int = 7
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days

    # Database
    DATABASE_URL: str = "sqlite:///./music_analyser.db"

    # Sentry APM & Error Tracking
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # AI & Transcription Service (Groq API)
    GROQ_API_KEY: str = ""
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"
    GROQ_LLM_MODEL: str = "llama3-8b-8192"

    # Cloud Storage (AWS S3)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""

    # Spotify API (Metadata Fetching)
    SPOTIPY_CLIENT_ID: str = ""
    SPOTIPY_CLIENT_SECRET: str = ""

    # YouTube Audio Acquisition
    YT_COOKIES_PATH: str = "cookies.txt"

    # Email & Password Reset (SMTP)
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "no-reply@musicanalyser.io"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:8080"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @property
    def cors_origins(self) -> list[str]:
        if not self.BACKEND_CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
