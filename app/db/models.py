from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base, JSONType


class User(Base):
    """User entity representing registered accounts and social OAuth logins."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    profile_picture_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # One-to-many relationship with processed songs
    songs = relationship("Song", back_populates="owner", cascade="all, delete-orphan")


class Song(Base):
    """Master record for a processed audio track including original URL, lyrics, and analytics."""

    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False, default="Untitled")
    song_url = Column(String(1024), nullable=False)
    lyrics = Column(JSONType, nullable=False, default=dict)
    description = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="songs")

    # One-to-many relationship with stem splits
    splits = relationship("Split", back_populates="song", cascade="all, delete-orphan")


class Split(Base):
    """Decomposed stem tracks and specialized instrument analytics."""

    __tablename__ = "splits"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(
        Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Stem Audio URLs (S3 Hosted)
    bass_audio_url = Column(String(1024), nullable=True)
    vocals_audio_url = Column(String(1024), nullable=True)
    piano_audio_url = Column(String(1024), nullable=True)
    other_audio_url = Column(String(1024), nullable=True)
    drum_audio_url = Column(String(1024), nullable=True)

    # Specialized Analytical Profiles
    bass_description = Column(JSONType, nullable=True)
    vocals_description = Column(JSONType, nullable=True)
    piano_description = Column(JSONType, nullable=True)
    drum_description = Column(JSONType, nullable=True)
    other_description = Column(JSONType, nullable=True)
    guitar_description = Column(JSONType, nullable=True)
    flute_description = Column(JSONType, nullable=True)
    violin_description = Column(JSONType, nullable=True)

    song = relationship("Song", back_populates="splits")


class PasswordResetOTP(Base):
    """Temporary OTP tokens for self-service password recovery."""

    __tablename__ = "password_reset_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    otp = Column(String(10), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
