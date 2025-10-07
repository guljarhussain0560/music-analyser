from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# === User & Authentication Schemas ===


class UserCreate(BaseModel):
    """Schema for new user registration."""

    email: EmailStr = Field(..., description="Valid user email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=6, description="Plaintext password")
    name: str | None = Field(None, max_length=100, description="Full name")
    profile_picture_url: str | None = Field(None, description="Avatar image URL")


class UserCredentials(BaseModel):
    """Schema for username/password signin."""

    username: str = Field(..., description="Registered username or email")
    password: str = Field(..., description="Account password")


class UserResponse(BaseModel):
    """Public user profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    name: str | None = None
    profile_picture_url: str | None = None
    is_active: bool = True
    created_at: datetime | None = None


class Token(BaseModel):
    """Bearer access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Token response with optional expiration metadata."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class GoogleToken(BaseModel):
    """Google OAuth ID credential token payload."""

    credential: str = Field(..., description="Google ID token string from frontend")


class ForgotPasswordRequest(BaseModel):
    """Initiates password reset OTP flow."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Completes password reset using verified OTP."""

    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6)


class MessageResponse(BaseModel):
    """Standard message confirmation response."""

    message: str


# === Audio Processing Schemas ===


class SongRequest(BaseModel):
    """Payload for URL-based song processing."""

    url: str = Field(..., description="YouTube or Spotify track URL")
    id: int = Field(..., description="User ID requesting the processing")


class SongCreateDTO(BaseModel):
    """Data transfer object for creating a master song record."""

    title: str = Field(default="Untitled")
    owner_id: int
    song_url: str
    lyrics: dict[str, Any] | None = Field(default_factory=dict)
    description: dict[str, Any] | None = None


class SongResponseDTO(BaseModel):
    """Master song response including global librosa audio analytics."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    owner_id: int
    song_url: str
    lyrics: dict[str, Any] = Field(default_factory=dict)
    description: dict[str, Any] | None = None
    created_at: datetime | None = None


class SplitCreateDTO(BaseModel):
    """Data transfer object for storing split stems and instrument analytics."""

    song_id: int
    bass_audio_url: str | None = None
    vocals_audio_url: str | None = None
    piano_audio_url: str | None = None
    other_audio_url: str | None = None
    drum_audio_url: str | None = None
    bass_description: dict[str, Any] | None = None
    vocals_description: dict[str, Any] | None = None
    piano_description: dict[str, Any] | None = None
    drum_description: dict[str, Any] | None = None
    other_description: dict[str, Any] | None = None
    guitar_description: dict[str, Any] | None = None
    flute_description: dict[str, Any] | None = None
    violin_description: dict[str, Any] | None = None


class SplitResponseDTO(BaseModel):
    """Stem separation and analytics response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    song_id: int
    bass_audio_url: str | None = None
    vocals_audio_url: str | None = None
    piano_audio_url: str | None = None
    other_audio_url: str | None = None
    drum_audio_url: str | None = None
    bass_description: dict[str, Any] | None = None
    vocals_description: dict[str, Any] | None = None
    piano_description: dict[str, Any] | None = None
    drum_description: dict[str, Any] | None = None
    other_description: dict[str, Any] | None = None
    guitar_description: dict[str, Any] | None = None
    flute_description: dict[str, Any] | None = None
    violin_description: dict[str, Any] | None = None


# === Individual Instrument Analytics DTOs ===


class BassInfoDTO(BaseModel):
    bass_audio_url: str | None = None
    bass_description: dict[str, Any] | None = None


class VocalsInfoDTO(BaseModel):
    vocals_audio_url: str | None = None
    vocals_description: dict[str, Any] | None = None


class PianoInfoDTO(BaseModel):
    piano_audio_url: str | None = None
    piano_description: dict[str, Any] | None = None


class DrumInfoDTO(BaseModel):
    drum_audio_url: str | None = None
    drum_description: dict[str, Any] | None = None


class OtherInfoDTO(BaseModel):
    other_audio_url: str | None = None
    other_description: dict[str, Any] | None = None


class GuitarInfoDTO(BaseModel):
    guitar_description: dict[str, Any] | None = None


class FluteInfoDTO(BaseModel):
    flute_description: dict[str, Any] | None = None


class ViolinInfoDTO(BaseModel):
    violin_description: dict[str, Any] | None = None


# === Chatbot & Lyrics Rewriter Schemas ===


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question about music theory or analysis",
    )


class ChatResponse(BaseModel):
    answer: str


class RewriteRequest(BaseModel):
    prompt: str = Field(
        ..., min_length=1, max_length=1000, description="Rewrite instructions for lyrics"
    )


class RewriteResponse(BaseModel):
    lyrics: str


class HealthResponse(BaseModel):
    """System health and status monitoring response."""

    status: str = "ok"
    version: str = "1.0.0"
    app_name: str
    environment: str
    database: str = "connected"
    timestamp: datetime
