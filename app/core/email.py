import os
import logging
from aiosmtplib import SMTP, SMTPException

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def send_email(to: str, subject: str, body_html: str) -> None:
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping email to %s", to)
        return

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg.attach(MIMEText(body_html, "html"))

    try:
        async with SMTP(hostname=SMTP_HOST, port=SMTP_PORT, start_tls=True) as smtp:
            await smtp.login(SMTP_USER, SMTP_PASSWORD)
            await smtp.send_message(msg)
    except SMTPException as e:
        logger.error("Failed to send email to %s: %s", to, e)
        raise


async def send_invite_email(to: str, invited_by: str, token: str) -> None:
    set_password_url = f"{FRONTEND_URL}/reset-password?token={token}"
    body = f"""
    <p>You've been invited to join ConstructIQ by <strong>{invited_by}</strong>.</p>
    <p><a href="{set_password_url}" style="background:#835500;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;">Set Your Password & Get Started</a></p>
    <p>This invitation link expires in 24 hours.</p>
    <p>If you weren't expecting this invitation, you can safely ignore this email.</p>
    """
    await send_email(to, "You've been invited to ConstructIQ", body)


async def send_password_reset_email(to: str, token: str) -> None:
    reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
    body = f"""
    <p>You requested a password reset for your ConstructIQ account.</p>
    <p><a href="{reset_url}">Click here to reset your password</a></p>
    <p>This link expires in 1 hour. If you didn't request this, ignore this email.</p>
    """
    await send_email(to, "ConstructIQ — Password Reset", body)
