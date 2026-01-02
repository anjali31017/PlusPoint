from pydantic import BaseModel, EmailStr

class OTPVerifySchema(BaseModel):
    email: str
    otp : str

