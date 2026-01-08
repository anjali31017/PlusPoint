from pydantic import BaseModel, EmailStr

class OTPVerifySchema(BaseModel):
    username: str
    otp : str

class ResendOTPSchema(BaseModel):
    username: str