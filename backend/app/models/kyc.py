from beanie import Document, Link, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional
from app.models.users import UserModel


class KYCModel(Document):

    user_id: Link["UserModel"]
    kyc_status: str = Field(default="NOT_STARTED") # NOT_STARTED | PENDING_REVIEW | VERIFIED | REJECTED
    id_type: Optional[str] = None # AADHAAR | VOTER_ID | DRIVING_LICENSE
    id_last4: Optional[str] = None
    id_fingerprint: str = Indexed(str, unique=True)
    dob: Optional[str] = None  # YYYY-MM-DD
    name_on_id: Optional[str] = None
    id_document_path: Optional[str] = None  # encrypted / temp storage
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "kyc"
