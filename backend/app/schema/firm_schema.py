from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# class PublisherSchema(BaseModel):
#     publisher_user_id: str

class FirmCreateSchema(BaseModel):
    firm_name: str
    # publishers: Optional[List[PublisherSchema]] = None
    bio: Optional[str] = None

class AddPublisherSchema(BaseModel):
    firm_id: str
    publisher_id: str 
    
class FirmSchema(BaseModel):
    firm_username: str
    firm_name: str
    # publishers: List[PublisherSchema] = []
    bio: Optional[str] = None
    verification_status: Optional[str] = None
    trust_score: Optional[int] = None
    violations_count: Optional[int] = None
    created_at: datetime