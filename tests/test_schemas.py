import pytest
from pydantic import ValidationError

from app.dto.schemas import (
    ChatRequest,
    SongCreateDTO,
    SplitCreateDTO,
    UserCreate,
)


def test_user_create_valid():
    """Asserts valid UserCreate payload passes validation."""
    user = UserCreate(
        email="musician@example.com",
        username="soundengineer",
        password="SecurePassword999",
        name="Alex River",
    )
    assert user.email == "musician@example.com"
    assert user.username == "soundengineer"


def test_user_create_invalid_email():
    """Asserts UserCreate rejects invalid email formats."""
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", username="testuser", password="password123")


def test_user_create_short_username():
    """Asserts UserCreate enforces minimum username length."""
    with pytest.raises(ValidationError):
        UserCreate(
            email="user@example.com",
            username="ab",  # Less than 3 chars
            password="password123",
        )


def test_song_create_dto():
    """Asserts SongCreateDTO defaults lyrics to dict."""
    dto = SongCreateDTO(
        title="Midnight Symphony", owner_id=1, song_url="https://example.com/audio.mp3"
    )
    assert dto.title == "Midnight Symphony"
    assert dto.lyrics == {}
    assert dto.description is None


def test_split_create_dto():
    """Asserts SplitCreateDTO correctly structures instrument fields."""
    dto = SplitCreateDTO(
        song_id=42,
        vocals_audio_url="https://s3.amazonaws.com/vocals.mp3",
        bass_description={"low_end_power": 0.85},
    )
    assert dto.song_id == 42
    assert dto.vocals_audio_url == "https://s3.amazonaws.com/vocals.mp3"
    assert dto.bass_description == {"low_end_power": 0.85}


def test_chat_request_validation():
    """Asserts ChatRequest rejects empty query strings."""
    with pytest.raises(ValidationError):
        ChatRequest(question="")
