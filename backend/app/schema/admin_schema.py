from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class AdminSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class AdminRejctReasonSchema(BaseModel):
    reason: str
