from pydantic import BaseModel

class KYCSchema(BaseModel):
    id_type: str
    id_last4: str
    dob: str
    name_on_id: str
    