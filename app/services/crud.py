from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db import models
from app.dto import schemas

# === User CRUD Operations ===


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_pwd = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        name=user.name,
        hashed_password=hashed_pwd,
        profile_picture_url=user.profile_picture_url,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: int, new_password: str) -> models.User | None:
    user = get_user(db, user_id)
    if user:
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
    return user


# === Song CRUD Operations ===


def create_song(db: Session, song: schemas.SongCreateDTO) -> models.Song:
    db_song = models.Song(
        title=song.title,
        owner_id=song.owner_id,
        song_url=song.song_url,
        lyrics=song.lyrics if song.lyrics is not None else {},
        description=song.description if song.description is not None else {},
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def get_song(db: Session, song_id: int) -> models.Song | None:
    return db.query(models.Song).filter(models.Song.id == song_id).first()


def get_lyrics_by_song_id(db: Session, song_id: int) -> models.Song | None:
    return db.query(models.Song).filter(models.Song.id == song_id).first()


# === Split CRUD Operations ===


def create_split(db: Session, split: schemas.SplitCreateDTO) -> models.Split:
    db_split = models.Split(
        song_id=split.song_id,
        bass_audio_url=split.bass_audio_url,
        vocals_audio_url=split.vocals_audio_url,
        piano_audio_url=split.piano_audio_url,
        other_audio_url=split.other_audio_url,
        drum_audio_url=split.drum_audio_url,
        bass_description=split.bass_description,
        vocals_description=split.vocals_description,
        piano_description=split.piano_description,
        other_description=split.other_description,
        drum_description=split.drum_description,
        guitar_description=split.guitar_description,
        flute_description=split.flute_description,
        violin_description=split.violin_description,
    )
    db.add(db_split)
    db.commit()
    db.refresh(db_split)
    return db_split


def get_split_by_song_id(db: Session, song_id: int) -> models.Split | None:
    return db.query(models.Split).filter(models.Split.song_id == song_id).first()


# === Password Reset OTP CRUD ===


def create_password_reset_otp(
    db: Session, email: str, otp: str, expires_minutes: int = 15
) -> models.PasswordResetOTP:
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
    record = models.PasswordResetOTP(email=email, otp=otp, expires_at=expires_at, is_used=False)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def verify_password_reset_otp(db: Session, email: str, otp: str) -> bool:
    now = datetime.utcnow()
    record = (
        db.query(models.PasswordResetOTP)
        .filter(
            models.PasswordResetOTP.email == email,
            models.PasswordResetOTP.otp == otp,
            models.PasswordResetOTP.is_used.is_(False),
            models.PasswordResetOTP.expires_at >= now,
        )
        .first()
    )
    if record:
        record.is_used = True
        db.commit()
        return True
    return False
