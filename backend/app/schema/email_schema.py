from beanie import PydanticObjectId
from pydantic import BaseModel

class OTPVerifySchema(BaseModel):
    id: PydanticObjectId
    otp : str

