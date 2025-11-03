from pydantic import BaseModel, EmailStr

class OTPVerifySchema(BaseModel):
    email: EmailStr
    otp : str

