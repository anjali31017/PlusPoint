import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.config import settings
from datetime import datetime, timedelta
from app.models.users import UserModel
import secrets


async def generate_otp(length: int = 6) -> dict[str, str | datetime]:
    """Generate a numeric OTP."""
    otp = "".join([str(random.randint(0, 9)) for _ in range(length)])
    otp_expiry = datetime.now() + timedelta(minutes=5)
    return {"otp": otp, "expires_at": otp_expiry}


async def otp_email(to_email: str, otp: str) -> bool:
    """Send OTP email using SMTP."""
    subject = "PlusPoint OTP Verification"
    body = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
        <p>Dear User,</p>
        <p>Your One-Time Password (OTP) for PlusPoint verification is:</p>
        <p style="text-align:center;margin:20px 0;">
            <span style="display:inline-block;padding:10px 20px;background-color:#1a73e8;color:#fff;font-weight:bold;font-size:18px;border-radius:5px;">
                {otp}
            </span>
        </p>
        <p><small>This OTP will expire in 5 minutes.</small></p>
        <p><small><em>Do not share this code with anyone. Keep it secure.</em></small></p>
        <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint</p>
    </div>
    """

    message = MIMEMultipart()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
        )
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False


def is_user_blocked(user: dict) -> bool:
    try:
        if user.otp_blocked_until and user.otp_blocked_until > datetime.now():
            return True
        return False
    except Exception as e:
        print("Error checking user block status:", e)
        return False


async def send_otp_email(user: dict) -> bool:
    """Wrapper function to send OTP email."""
    try:
        otp_details = await generate_otp()
        email_sent = await otp_email(user.email, otp_details["otp"])
        if not email_sent:
            return False
        hashed_otp = UserModel.hash_detail(otp_details["otp"])
        await user.set(
            {
                UserModel.otp: hashed_otp,
                UserModel.otp_expires_at: otp_details["expires_at"],
                UserModel.otp_attempts: 0,
            }
        )

        return True
    except Exception as e:
        print("Failed to send OTP email:", e)
        return False


async def verify_otp(user: dict, otp: str) -> bool:
    """Verify the provided OTP against the stored hashed OTP."""
    try:
        if user.otp_expires_at < datetime.now():
            return False  # OTP expired

        is_valid = UserModel.verify_otp(otp, user.otp)
        return is_valid
    except Exception as e:
        print("OTP verification failed:", e)
        return False


def generate_reset_token():
    try:
        return secrets.token_urlsafe(32)
    except Exception as e:
        print("Error generating reset token:", e)
        return None


async def reset_password_email(to_email: str, link: str) -> bool:

    subject = "PlusPoint Reset Password."
    body = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
        <p>Dear User,</p>
        <p>We received a request to reset your PlusPoint password. Click the link below to proceed:</p>
        <p style="text-align:center;margin:20px 0;">
            <a href="{link}" style="display:inline-block;padding:10px 20px;background-color:#1a73e8;color:#fff;text-decoration:none;border-radius:5px;font-weight:bold;">
                Reset Password
            </a>
        </p>
        <p><small>This link will expire in 15 minutes.</small></p>
        <p><small><em>Please do not share this link with anyone. Keep it secure.</em></small></p>
        <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint</p>
    </div>
    """
    message = MIMEMultipart()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
        )
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False


async def KYC_status_email(to_email: str, status: str, reason: str | None) -> bool:

    subject = "KYC Status Update"
    if status.lower() == "verified":

        body = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
            <p>Dear User,</p>
            <p>We are pleased to inform you that your KYC has been <strong style="color:green;">ACCEPTED</strong>.</p>
            <p>You now have full access to all <strong>PlusPoint</strong> features.</p>
            <p><small><em>Congratulations!</em></small></p>
            <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint</p>
        </div>
        """

    elif status.lower() == "rejected":

        body = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
            <p>Dear User,</p>
            <p>We regret to inform you that your KYC has been <strong style="color:red;">REJECTED</strong>.</p>
            <p>Please complete your KYC again to continue using PlusPoint features.</p>
            <p><strong>Reason for rejection:</strong> {reason or 'Not specified'}</p>
            <p><small><em>If you have any questions, please contact us at <a href="mailto:support@example.com">support@pluspoint.com</a>.</em></small></p>
            <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint</p>
        </div>
        """

    else:
        body = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
            <p>Dear User,</p>
            <p>Your KYC status is: <strong>{status}</strong>.</p>
            <p><small><em>Please contact <a href="mailto:support@example.com">support@example.com</a> for more details.</em></small></p>
            <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint</p>
        </div>
        """

    message = MIMEMultipart()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
        )
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False


async def report_action_email(
    to_email: str,
    firm: dict | None = None,
    article: dict | None = None,
    reason: str | None = None,
) -> bool:

    # Subject
    subject = "Notice of Account or Content Removal"

    # Body construction
    if firm:
        body = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
            <p>Dear {firm.firm_name},</p>
            <p>We’re writing to inform you that your firm account <strong>{firm.firm_username}</strong> has been removed from our platform.</p>
            <p><strong>Reason for removal:</strong><br>{reason or 'No specific reason provided.'}</p>
            <p>If you believe this action was made in error or would like to appeal, please contact us at <a href="mailto:support@pluspoint.com">support@pluspoint.com</a>.</p>
            <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint Support Team</p>
        </div>
        """
    elif article:
        body = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
            <p>Dear User,</p>
            <p>We’re writing to inform you that your article titled <strong>"{article.title}"</strong> has been removed from our platform.</p>
            <p><strong>Reason for removal:</strong><br>{reason or 'No specific reason provided.'}</p>
            <p>If you believe this action was made in error or would like to appeal, please contact us at <a href="mailto:support@pluspoint.com">support@pluspoint.com</a>.</p>
            <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint Support Team</p>
        </div>
        """
    else:
        body = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
            <p>Dear User,</p>
            <p>We’re writing to inform you that some content associated with your account has been removed from our platform.</p>
            <p><strong>Reason for removal:</strong><br>{reason or 'No specific reason provided.'}</p>
            <p>If you believe this action was made in error or would like to appeal, please contact us at <a href="mailto:support@pluspoint.com">support@pluspoint.com</a>.</p>
            <p style="margin-top:20px;font-weight:900;font-size:26px;color:#1a73e8;">PlusPoint Support Team</p>
        </div>
        """

    message = MIMEMultipart()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
        )

        return True
    except Exception as e:
        print("Error sending email:", e)
        return False
