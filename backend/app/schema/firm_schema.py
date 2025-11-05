from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class PublisherSchema(BaseModel):
    publisher_id: str


class FirmRegisterSchema(BaseModel):
    firm_name: str
    firm_username: str
    publishers: Optional[List[PublisherSchema]] = None

class AddPublisherSchema(BaseModel):
    firm_id: str
    publisher_user_id: str 