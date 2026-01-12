from typing import List, Optional
from pydantic import BaseModel

class PublisherSchema(BaseModel):
    publisher_id: str


class FirmCreateSchema(BaseModel):
    firm_name: str
    publishers: Optional[List[PublisherSchema]] = None
    bio: Optional[str] = None

class AddPublisherSchema(BaseModel):
    firm_username: str
    publisher_username: str 