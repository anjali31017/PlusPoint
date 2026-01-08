
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.config import settings
from datetime import datetime, timedelta
from app.models.users import UserModel

async def generate_otp(length: int = 6) -> dict[str, str | datetime]:
    """Generate a numeric OTP."""
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    otp_expiry = datetime.now() + timedelta(minutes=5)
    return {
        "otp": otp,
        "expires_at": otp_expiry
    }

async def otp_email(to_email: str, otp: str) -> bool:
    """Send OTP email using SMTP."""
    subject = "PlusPoint OTP Verification"
    body = f"""
    <p>Your OTP code is: <strong>{otp}</strong></p>
    <p>This code expires in 5 minutes.</p>
    <p><small><em>"This is your secure OTP. Do not share it."</em></small></p>
    <p><span style="font-weight:900; font-size:26px; color:#1a73e8;">PlusPoint</span></p>
    
    
    """
    # <p><span style="font-weight:900; font-size:26px; color:#1a73e8;">PlusPoint</span> Stay on the pulse of trending topics!</p>

    # <p><strong>PlusPoint</strong> Stay on the plue of trending topics!</p>
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
            password=settings.SMTP_PASSWORD
        )
        # with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        #     server.starttls()
        #     server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        #     server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
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
        otp_details =  await generate_otp()
        email_sent =  await otp_email(user.email, otp_details["otp"])
        if not email_sent:
            return False
        hashed_otp = UserModel.hash_detail(otp_details["otp"])
        await user.set({
            UserModel.otp: hashed_otp,
            UserModel.otp_expires_at: otp_details["expires_at"],
            UserModel.otp_attempts: 0,
        })

        return True
    except Exception as e:
        print("Failed to send OTP email:", e)
        return False

# async def resend_otp_email(user: dict) -> bool:
#     """Resend OTP email to the user."""
#     try:
#         # user = await UserModel.find_one(UserModel.username == user['username'], UserModel.is_deleted == False)
#         # if not user:
#         #     return False
#         await send_otp_email(user)

#         return True
#     except Exception as e:
#         print("Failed to resend OTP email:", e)
#         return False

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