from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("email_service")


def get_mail_config() -> ConnectionConfig | None:
    """Builds FastMail ConnectionConfig if credentials are set."""
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        return None
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM or "notifications@musicanalyser.io",
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER or "smtp.gmail.com",
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )


async def send_otp_email(email: str, otp: str) -> bool:
    """Sends password recovery OTP email."""
    config = get_mail_config()
    if not config:
        logger.info(f"SMTP unconfigured. Generated OTP for '{email}': {otp}")
        return True

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e0e0e0; border-radius: 12px;">
        <h2 style="color: #1a1a1a; text-align: center;">AI Music Analyser</h2>
        <p style="color: #4a4a4a;">Hello,</p>
        <p style="color: #4a4a4a;">You requested a password reset. Your One-Time Password (OTP) is:</p>
        <div style="text-align: center; margin: 24px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; background-color: #f4f4f5; padding: 12px 24px; border-radius: 8px; color: #111;">
                {otp}
            </span>
        </div>
        <p style="color: #71717a; font-size: 14px;">This OTP is valid for 15 minutes. If you did not request this, please disregard this email.</p>
    </div>
    """

    message = MessageSchema(
        subject="Password Reset OTP - AI Music Analyser",
        recipients=[email],
        body=html_content,
        subtype=MessageType.html,
    )

    try:
        fm = FastMail(config)
        await fm.send_message(message)
        logger.info(f"OTP email successfully dispatched to: {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to dispatch OTP email to {email}: {e}")
        return False
