from datetime import datetime
from beanie import PydanticObjectId
from fastapi import HTTPException
from app.models.firm import FirmModel, PublisherInfo
from app.schema.firm_schema import AddPublisherSchema
from app.models.users import UserModel

class FirmController:
    
    async def register_firm(self, firm_data) -> bool:
        try:
            firm = FirmModel(**firm_data.dict())
            await firm.insert()
            return True
        except Exception as e:
            print("Error registering firm:", e)
            return False
    
    async def add_publisher(self, data: AddPublisherSchema) -> PublisherInfo:
        try:
            publisher = await UserModel.get(PydanticObjectId(data.publisher_user_id))
            if not publisher:
                raise HTTPException(status_code=404, detail="Publisher (user) not found")

            firm = await FirmModel.get(PydanticObjectId(data.firm_id))
            if not firm:
                raise HTTPException(status_code=404, detail="Firm not found")

            for existing_pub in firm.publishers or []:
                if str(existing_pub.publisher_user_id.id) == data.publisher_user_id:
                    raise HTTPException(status_code=400, detail="Publisher already added to firm")

            new_publisher = PublisherInfo(
                publisher_user_id=publisher,
                invited_at=datetime.now()
            )
            if firm.publishers is None:
                firm.publishers = []
                
            firm.publishers.append(new_publisher)
            await firm.save()

            return new_publisher
        except HTTPException as e:  
            raise e
        except Exception as e:
            print("Error adding publisher to firm:", e)
            raise HTTPException(status_code=500, detail="Internal server error")