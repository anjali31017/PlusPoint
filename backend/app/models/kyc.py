from beanie import Document, Link, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional
from app.models.users import UserModel
from enum import Enum

class KYCStatus(str, Enum):
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    
class KYCModel(Document):

    user_id: Link["UserModel"]
    kyc_status: KYCStatus = KYCStatus.UNDER_REVIEW 
    id_type: Optional[str] = None # AADHAAR | VOTER_ID | DRIVING_LICENSE
    id_last4: Optional[str] = None
    id_fingerprint: str = Indexed(str, unique=True)
    dob: Optional[str] = None  # YYYY-MM-DD
    name_on_id: Optional[str] = None
    id_document_path: Optional[str] = None  # encrypted / temp storage
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    is_active: bool = True
    kyc_consent: bool = False
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "kyc"
