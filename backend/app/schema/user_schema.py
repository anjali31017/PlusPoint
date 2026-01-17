from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreateSchema(BaseModel):
    # username: str = Field(..., min_length=3, max_length=50)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserProfileSchema(BaseModel):
    id: PydanticObjectId
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role : Optional[list[str]] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime

class UserProfileEditSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
class LoginSchema(BaseModel):
    email: str
    password: str
    

class RefreshSchema(BaseModel):
    refresh_token: str
    
class LogoutSchema(BaseModel):
    refresh_token: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    token: str
    password: str