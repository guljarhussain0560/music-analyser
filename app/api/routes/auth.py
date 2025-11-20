import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.core.logging import get_logger
from app.db import models
from app.dto import schemas
from app.services import auth_service, crud, email_service

logger = get_logger("routes.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user account."""
    if crud.get_user_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.get_user_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    return crud.create_user(db=db, user=user_in)


@router.post("/signin", response_model=schemas.Token)
def signin(credentials: schemas.UserCredentials, db: Session = Depends(get_db)):
    """Authenticates user and returns JWT Bearer access token."""
    return auth_service.authenticate_user(db, credentials)


@router.post("/google", response_model=schemas.Token)
def google_login(token_payload: schemas.GoogleToken, db: Session = Depends(get_db)):
    """Authenticates user via Google OAuth 2.0 ID token."""
    return auth_service.authenticate_google_user(db, token_payload)


@router.get("/users/me", response_model=schemas.UserResponse)
def read_current_user_profile(current_user: models.User = Depends(get_current_active_user)):
    """Returns the authenticated user's profile."""
    return current_user


@router.post("/forgot-password", response_model=schemas.MessageResponse)
async def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generates and emails an OTP for password reset."""
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        # Prevent user enumeration by returning confirmation
        return {"message": "If this email is registered, a password reset OTP has been sent."}

    otp = str(secrets.randbelow(900000) + 100000)
    crud.create_password_reset_otp(db, email=request.email, otp=otp, expires_minutes=15)
    await email_service.send_otp_email(request.email, otp)
    return {"message": "If this email is registered, a password reset OTP has been sent."}


@router.post("/reset-password", response_model=schemas.MessageResponse)
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    """Verifies OTP and resets user password."""
    is_valid = crud.verify_password_reset_otp(db, email=request.email, otp=request.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code.")

    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    crud.update_user_password(db, user_id=user.id, new_password=request.new_password)
    return {"message": "Password has been successfully reset. You can now log in."}
