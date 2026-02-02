from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from app.models.firm import FirmModel
from app.schema.firm_schema import AddPublisherSchema
from app.models.users import UserModel, UserRole
from app.controller.util_controller import UtilController
from typing import Optional

from app.models.subscription import SubscriptionModel


class FirmController:
    
    async def create_firm(self, firm_data: FirmModel, user:UserModel, user_id: str) -> Optional[FirmModel]:
        """
        Create a firm for a user. Returns FirmModel on success, None on failure.
        No HTTPException raised here.
        """
        try:
            util_controller = UtilController()
            while True:
                username = await util_controller.generate_username(
                    firstname=None,
                    lastname=None,
                    firmname=firm_data.firm_name
                )
                existing = await util_controller.check_username_exists(username)
                if not existing:
                    break

            # 4️⃣ Prepare firm data
            firm_data_dict = firm_data.dict(exclude_unset=True)
            firm_data_dict["owner_user_id"] = user  # Link to UserModel
            firm_data_dict["firm_username"] = username
            # firm_data_dict["created_at"] = datetime.now()

            firm = FirmModel(**firm_data_dict)
            
            registered_firm = await firm.insert()
            if not registered_firm:
                return None


            # 6️⃣ Assign roles
            if UserRole.founder not in user.role:
                user.role.append(UserRole.founder)
            if UserRole.publisher not in user.role:
                user.role.append(UserRole.publisher)
            await user.save()

            return registered_firm

        except Exception as e:
            print("Error registering firm:", e)
            return None
        
    
    async def subscribe(self, firm_id:str|None, subscriber_id: str|None) -> bool:
        try:

            firm = await FirmModel.find_one(
                FirmModel.id == ObjectId(firm_id),
                FirmModel.is_deleted == False,
                FirmModel.is_active == True,
                )
            if not firm:
                raise HTTPException(status_code=404, detail="Firm not found")
            
            subscriber = await UserModel.find_one(
                UserModel.id == ObjectId(subscriber_id),
                UserModel.is_deleted == False,
                UserModel.is_active == True,
                )
            if not subscriber:
                raise HTTPException(status_code=404, detail="Subscriber (user) not found")
            
                
            subscription = await SubscriptionModel.find_one(
                SubscriptionModel.subscriber_id.id == subscriber.id,
                SubscriptionModel.firm_id.id == firm.id,
                )
            
            # print("HELOWWWWWWWWWWWWWWWWWWWWWWW 1111111111")
            event = None
            
            if subscription:
                await subscription.delete()
                await firm.update({"$inc": {"follow_count": -1}})

                response  = {
                    "status": "un-followed",
                    "data": event
                }
                # print("HELOWWWWWWWWWWWWWWWWWWWWWWW 2222222222222")
                return response
            
            subscription = SubscriptionModel(
                subscriber_id=subscriber, firm_id=firm
            )

            await subscription.insert()
            await firm.update({"$inc": {"follow_count": 1}})
            
            firm_owner = await firm.owner_user_id.fetch()
            
            event = {
                "firm_owner_id": str(firm_owner.id),
                "firm_id": str(firm.id),
                "user_id": str(subscriber.id),
            }
            response  = {
                    "status": "followed",
                    "data": event
                }
            # print("HELOWWWWWWWWWWWWWWWWWWWWWWW 3333333333333")
            return response

        except HTTPException as e:
            raise e
        except Exception as e:
            print("Error subscribing to publisher:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
        

 