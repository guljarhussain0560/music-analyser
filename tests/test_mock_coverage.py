import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.dependencies import get_current_active_user
from app.core.config import settings
from app.core.security import decode_access_token
from app.db.models import User
from app.services import audio_processing, email_service, s3_uploader
from app.utils import chatbot, extract_lyrics, lyrics_aligner


def test_decode_invalid_token():
    """Tests decoding invalid token returns None."""
    assert decode_access_token("invalid.jwt.token") is None


def test_get_current_active_user_inactive():
    """Tests get_current_active_user raises 400 for inactive user."""
    inactive_user = User(
        id=1, username="inactive", email="i@e.com", hashed_password="pw", is_active=False
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(inactive_user)
    assert exc_info.value.status_code == 400


def test_s3_uploader_with_bucket(sample_wav_file):
    """Tests S3 uploader when AWS bucket is configured."""
    orig_bucket = settings.AWS_S3_BUCKET_NAME
    orig_key = settings.AWS_ACCESS_KEY_ID
    orig_secret = settings.AWS_SECRET_ACCESS_KEY
    try:
        with patch("boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_client.meta.region_name = "us-east-1"
            mock_boto.return_value = mock_client

            settings.AWS_S3_BUCKET_NAME = "prod-bucket"
            settings.AWS_ACCESS_KEY_ID = "key"
            settings.AWS_SECRET_ACCESS_KEY = "secret"

            url = s3_uploader.upload_file_to_s3(sample_wav_file, "stems/vocal.mp3")
            assert "prod-bucket.s3.us-east-1.amazonaws.com/stems/vocal.mp3" in url

            # File not found
            assert s3_uploader.upload_file_to_s3("non_existent_file.mp3") is None

            # Client error
            mock_client.upload_file.side_effect = Exception("AWS Network Error")
            assert s3_uploader.upload_file_to_s3(sample_wav_file) is None
    finally:
        settings.AWS_S3_BUCKET_NAME = orig_bucket
        settings.AWS_ACCESS_KEY_ID = orig_key
        settings.AWS_SECRET_ACCESS_KEY = orig_secret


def test_email_service_with_config():
    """Tests email service when SMTP credentials are set."""
    with patch("fastapi_mail.FastMail.send_message"):
        settings.MAIL_USERNAME = "user@test.com"
        settings.MAIL_PASSWORD = "password"

        res = asyncio.run(email_service.send_otp_email("recipient@test.com", "987654"))
        assert res is True

        settings.MAIL_USERNAME = None
        settings.MAIL_PASSWORD = None


@patch("requests.post")
def test_extract_lyrics_groq_success(mock_post, sample_wav_file):
    """Tests extract_lyrics transcription when Groq API key is present."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "language": "en",
        "duration": 2.0,
        "segments": [{"start": 0.0, "end": 2.0, "text": "Testing vocal stem"}],
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    settings.GROQ_API_KEY = "gsk_test_key"
    res = extract_lyrics.transcribe_lyrics(sample_wav_file)
    assert res["language"] == "en"
    assert "Testing vocal stem" in res["original_lrc"]
    settings.GROQ_API_KEY = ""


@patch("requests.post")
def test_lyrics_aligner_groq_success(mock_post):
    """Tests lyrics rewriter with mock Groq response."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "[00:00.00]Rewritten lyrics line"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    settings.GROQ_API_KEY = "gsk_test_key"
    res = lyrics_aligner.rewrite_lyrics_with_timestamps(
        lrc_string="[00:00.00]Original lyrics",
        language="en",
        duration=2.0,
        user_prompt="Make it poetic",
    )
    assert res == "[00:00.00]Rewritten lyrics line"
    settings.GROQ_API_KEY = ""


@patch("httpx.AsyncClient.post")
def test_chatbot_groq_success(mock_post):
    """Tests chatbot answer with mock LLM response."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Tempo represents BPM."}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    settings.GROQ_API_KEY = "gsk_test_key"
    answer = asyncio.run(chatbot.get_ai_answer("What is tempo?"))
    assert answer == "Tempo represents BPM."
    settings.GROQ_API_KEY = ""


def test_process_and_upload_stem(sample_wav_file, tmp_path):
    """Tests stem mp3 conversion and upload in mock mode."""
    settings.AWS_S3_BUCKET_NAME = ""
    mp3_dir = str(tmp_path)
    res = audio_processing.process_and_upload_stem(sample_wav_file, mp3_dir, "sess-123")
    assert res is not None
    stem_name = os.path.splitext(os.path.basename(sample_wav_file))[0]
    assert os.path.exists(os.path.join(mp3_dir, f"{stem_name}.mp3"))
