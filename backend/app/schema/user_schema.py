from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId
from datetime import datetime

class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[list[str]] = None

class UserProfileSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    
class LoginSchema(BaseModel):
    email: str
    password: str
    

class RefreshSchema(BaseModel):
    refresh_token: str
    
class LogoutSchema(BaseModel):
    refresh_token: str
