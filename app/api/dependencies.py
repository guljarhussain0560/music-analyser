from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db import models
from app.db.database import get_db_session
from app.services import crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")


def get_db() -> Generator[Session, None, None]:
    """Yields a transactional database session."""
    yield from get_db_session()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """Validates JWT Bearer token and returns authenticated User entity."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception from None

    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception from None

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception from None

    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception from None

    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Ensures that the authenticated user account is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
    return current_user
