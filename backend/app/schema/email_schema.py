from pydantic import BaseModel, EmailStr

class OTPRequest(BaseModel):
    email: EmailStr

