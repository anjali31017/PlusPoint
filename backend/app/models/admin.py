from typing import ClassVar, Optional
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class AdminModel(Document):
    email: str = Indexed(str, unique=True)
    password_hash: Optional[str] = None
    is_verified: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "admins"  


    # def __init__(self, password_hash: str = None):
    #     self.password_hash = password_hash

    ph: ClassVar[PasswordHasher] = PasswordHasher()  # <--- annotate as ClassVar
    
    @staticmethod
    def hash_detail(detail: str) -> str:
        return AdminModel.ph.hash(detail)

    def verify_password(self, password: str) -> bool:
        try:
            return AdminModel.ph.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False
        
  