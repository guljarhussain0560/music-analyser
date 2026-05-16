import asyncio

import pytest

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.dto import schemas
from app.services import auth_service, email_service, s3_uploader


def test_s3_uploader_mock_and_custom_name(sample_wav_file):
    """Tests S3 uploader in mock mode and custom object naming."""
    settings.AWS_S3_BUCKET_NAME = ""
    url = s3_uploader.upload_file_to_s3(sample_wav_file, "custom/path/audio.mp3")
    assert "custom/path/audio.mp3" in url


def test_email_service_dispatch():
    """Tests email dispatch helper synchronously."""
    result = asyncio.run(email_service.send_otp_email("test@example.com", "123456"))
    assert result is True


def test_auth_service_inactive_user(db_session, test_user):
    """Tests auth rejection when user is marked inactive."""
    test_user.is_active = False
    db_session.commit()

    creds = schemas.UserCredentials(username=test_user.username, password="SecretPassword123!")
    with pytest.raises(AuthenticationError):
        auth_service.authenticate_user(db_session, creds)


def test_forgot_and_reset_password_flow(client, db_session, test_user):
    """Tests password reset request and reset confirmation endpoints."""
    # Request OTP
    res = client.post("/api/auth/forgot-password", json={"email": test_user.email})
    assert res.status_code == 200

    # Non-existent email also returns confirmation to prevent enumeration
    res_unknown = client.post("/api/auth/forgot-password", json={"email": "unknown@example.com"})
    assert res_unknown.status_code == 200

    # Invalid OTP reset attempt
    res_bad = client.post(
        "/api/auth/reset-password",
        json={"email": test_user.email, "otp": "000000", "new_password": "BrandNewPassword123!"},
    )
    assert res_bad.status_code == 400
