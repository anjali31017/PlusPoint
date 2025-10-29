from typing import Optional, List
from beanie import Document, Indexed, Link
from pydantic import Field
from datetime import datetime
from passlib.hash import bcrypt  
from enum import Enum

class UserRole(str, Enum):
    founder = "founder"
    builder = "builder"
    explorer = "explorer"


class User(Document):
    # user_id: Optional[str] = Field(None, alias="_id")
    # user_ref_if: str = = Field(default_factory=lambda: secrets.token_hex(8))
    username: Indexed(str, unique=True)
    email: Indexed(str, unique=True)
    first_name: str
    last_name: str
    password_hash: Optional[str] = None
    role: List[UserRole] = Field(default_factory=list) #['founder','builder','explorer']
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    otp: Optional[int] = None
    is_verified: bool = False
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"  

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)