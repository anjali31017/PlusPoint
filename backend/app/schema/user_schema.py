from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId
from datetime import datetime

class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[list[str]] = None

class UserResponseSchema(BaseModel):
    id: PydanticObjectId
    # username: str
    # email: str
    # first_name: str
    # last_name: str
    role: list[str] = []
    # is_verified: bool
    # created_at: datetime

    class Config:
        orm_mode = True



#hash id