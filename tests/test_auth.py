from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.security import verify_password
from app.db import models


def test_signup_successful(client: TestClient):
    """Tests user registration endpoint."""
    payload = {
        "email": "newuser@example.com",
        "username": "newuser123",
        "password": "StrongPassword789!",
        "name": "New User",
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser123"
    assert "password" not in data  # Ensure password hash is not exposed


def test_signup_duplicate_email_rejected(client: TestClient, test_user):
    """Tests duplicate email registration rejection."""
    payload = {
        "email": test_user.email,
        "username": "differentusername",
        "password": "Password123!",
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 400
    res_data = response.json()
    err_msg = res_data.get("detail") or res_data.get("message") or ""
    assert "Email already registered" in err_msg


def test_signin_success(client: TestClient, test_user):
    """Tests signin with username and password."""
    payload = {"username": test_user.username, "password": "SecretPassword123!"}
    response = client.post("/api/auth/signin", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signin_invalid_password(client: TestClient, test_user):
    """Tests signin with wrong password."""
    payload = {"username": test_user.username, "password": "WrongPassword!"}
    response = client.post("/api/auth/signin", json=payload)
    assert response.status_code == 401


def test_get_current_user_profile(client: TestClient, auth_headers, test_user):
    """Tests protected route /users/me with valid Bearer token."""
    response = client.get("/api/auth/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_current_user_unauthorized(client: TestClient):
    """Tests protected route access without token is rejected."""
    response = client.get("/api/auth/users/me")
    assert response.status_code == 401


@patch("google.oauth2.id_token.verify_oauth2_token")
def test_google_auth_flow(mock_verify, client: TestClient, db_session):
    """Tests Google OAuth login and provisioning with randomized secure password."""
    mock_verify.return_value = {
        "email": "googleuser@gmail.com",
        "name": "Google User",
        "picture": "https://lh3.googleusercontent.com/avatar.jpg",
    }

    # Configure mock Google Client ID
    from app.core.config import settings

    settings.GOOGLE_CLIENT_ID = "mock-google-client-id"

    payload = {"credential": "mock-valid-google-id-token"}
    response = client.post("/api/auth/google", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    # Verify user was created in DB with a secure password hash (not hardcoded dummy string)
    user = db_session.query(models.User).filter_by(email="googleuser@gmail.com").first()
    assert user is not None
    assert user.name == "Google User"
    assert user.profile_picture_url == "https://lh3.googleusercontent.com/avatar.jpg"
    assert not verify_password("dummypassword_from_google_signup", user.hashed_password)
