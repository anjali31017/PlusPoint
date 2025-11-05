from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class PublisherResponse(BaseModel):
    publisher_id: str


class FirmRegisterSchema(BaseModel):
    firm_user_id: str
    firm_name: str
    publishers: Optional[List[PublisherResponse]] = None

class AddPublisherSchema(BaseModel):
    firm_id: str
    publisher_user_id: str 