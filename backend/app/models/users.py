from typing import ClassVar, Optional, List
from beanie import Document, Indexed, Link
from pydantic import Field
from datetime import datetime
from enum import Enum
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class UserRole(str, Enum):
    founder = "F" #"firm_founder"
    publisher = "P" #"publisher"
    explorer = "E" #"explorer"


class UserModel(Document):
    # user_id: Optional[str] = Field(None, alias="_id")
    # user_ref_if: str = = Field(default_factory=lambda: secrets.token_hex(8))
    username: str = Indexed(str, unique=True)
    email: str = Indexed(str, unique=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password_hash: Optional[str] = None
    role: List[UserRole] = Field(default_factory=list) #['founder','builder','explorer']
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    otp: Optional[str] = None
    otp_expires_at: Optional[datetime] = None
    is_verified: bool = False
    is_active: bool = False
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"  


    # def __init__(self, password_hash: str = None):
    #     self.password_hash = password_hash

    ph: ClassVar[PasswordHasher] = PasswordHasher()  # <--- annotate as ClassVar
    
    @staticmethod
    def hash_detail(detail: str) -> str:
        return UserModel.ph.hash(detail)

    def verify_password(self, password: str) -> bool:
        try:
            return UserModel.ph.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False
        
  
    def verify_otp(self, otp: str) -> bool:
        """Verify the OTP and ensure it is not expired."""
        try:
            if self.otp_expires_at < datetime.now():
                print("OTP expired")
                return False
            return UserModel.ph.verify(self.otp, otp)
        except Exception as e:
            print("Error verifying OTP:", e)
            return False
        

    # @staticmethod
    # def hash_password(password: str) -> str:
    #     return bcrypt.hash(password)

    # def verify_password(self, password: str) -> bool:
    #     return bcrypt.verify(password, self.password_hash)