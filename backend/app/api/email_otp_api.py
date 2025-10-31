# from fastapi import APIRouter, HTTPException
# from app.schema.email_schema import OTPRequest
# from app.api.email_otp_api import generate_otp, send_otp_email
# from app.schema.base_schema import BaseResponse

# router = APIRouter()

# @router.post("/email/otp", response_model=BaseResponse, status_code=200)
# async def send_otp(request: OTPRequest):
#     otp = generate_otp()

#     sent = send_otp_email(request.email, otp)
#     if not sent:
#         raise HTTPException(status_code=500, detail="Failed to send OTP")

#     # Normally, you'd store OTP in Redis/DB with an expiry time
#     return BaseResponse(status=1, message="OTP sent successfully")
