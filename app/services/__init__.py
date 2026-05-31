"""Application business logic services."""

from app.services.audio_processing import full_song_processing_pipeline, process_audio_file_pipeline
from app.services.auth_service import authenticate_google_user, authenticate_user
from app.services.crud import (
    create_password_reset_otp,
    create_song,
    create_split,
    create_user,
    get_lyrics_by_song_id,
    get_song,
    get_split_by_song_id,
    get_user,
    get_user_by_email,
    get_user_by_username,
    update_user_password,
    verify_password_reset_otp,
)
from app.services.email_service import send_otp_email
from app.services.s3_uploader import upload_file_to_s3

__all__ = [
    "create_user",
    "get_user",
    "get_user_by_email",
    "get_user_by_username",
    "update_user_password",
    "create_song",
    "get_song",
    "get_lyrics_by_song_id",
    "create_split",
    "get_split_by_song_id",
    "create_password_reset_otp",
    "verify_password_reset_otp",
    "authenticate_user",
    "authenticate_google_user",
    "send_otp_email",
    "upload_file_to_s3",
    "full_song_processing_pipeline",
    "process_audio_file_pipeline",
]
