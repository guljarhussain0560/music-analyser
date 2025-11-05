from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger
from app.core.security import create_access_token, generate_secure_token, verify_password
from app.dto import schemas
from app.services import crud

logger = get_logger("auth_service")


def authenticate_user(db: Session, credentials: schemas.UserCredentials) -> dict[str, str]:
    """Validates username/password and generates JWT token."""
    user = crud.get_user_by_username(db, username=credentials.username)
    if not user:
        user = crud.get_user_by_email(db, email=credentials.username)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise AuthenticationError("Incorrect username or password")

    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_google_user(db: Session, token: schemas.GoogleToken) -> dict[str, str]:
    """Verifies Google OAuth ID token, provisions account securely, and generates JWT."""
    if not settings.GOOGLE_CLIENT_ID:
        raise AuthenticationError("Google OAuth client ID is not configured")

    try:
        id_info = id_token.verify_oauth2_token(
            token.credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        email = id_info.get("email")
        name = id_info.get("name")
        picture = id_info.get("picture")

        if not email:
            raise AuthenticationError("Google token does not contain a verified email")

    except ValueError as e:
        logger.error(f"Invalid Google ID token: {e}")
        raise AuthenticationError("Invalid Google authentication token")

    user = crud.get_user_by_email(db, email=email)
    if not user:
        # Generate cryptographically secure random password hash for OAuth user
        user_in = schemas.UserCreate(
            email=email,
            username=email.split("@")[0] + "_" + generate_secure_token(6),
            name=name,
            profile_picture_url=picture,
            password=generate_secure_token(32),
        )
        user = crud.create_user(db, user_in)
        logger.info(f"Created new user via Google OAuth: {user.email}")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
