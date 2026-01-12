from fastapi import HTTPException
from typing import Optional
from bson import ObjectId
from app.models.users import UserModel, UserRole
import random
from app.models.firm import FirmModel
from app.models.subscription import SubscriptionModel
from app.controller.email_controller import is_user_blocked
from app.controller.util_controller import UtilController

util_controller = UtilController()

class UserController:
    
    async def create(self, user_data:dict) -> UserModel | None:
        try:
            
            user_exists = await UserModel.find_one(
                UserModel.email == user_data['email'],
                UserModel.is_deleted == False
            )
            
            if user_exists and user_exists.is_verified == True:
                return None
            
            if user_exists and user_exists.is_verified == False:
                update_password = UserModel.hash_detail(user_data['password'])
                await user_exists.set({UserModel.password_hash: update_password})
                return user_exists
            print("!!!!!!!!!!!!!")
            while True:
                username = await util_controller.generate_username(
                    firstname = user_data["first_name"], 
                    lastname = user_data["last_name"] if user_data.get("last_name") else None, 
                    firmname= None,
                    )
                user = await util_controller.check_username_exists(username)
                if not user:
                    break
            user = UserModel(**user_data)
            user.username = username
            user.role = ['E']
            user.password_hash = UserModel.hash_detail(user_data['password'])
            await user.insert()
            return user
        except Exception as e:
            print(str(e))
            return None
        
    async def _find_active_user(self, user_id: str) -> UserModel | None:
        try:
            obj_id = ObjectId(user_id)
            return await UserModel.find_one(
                UserModel.id == obj_id,
                UserModel.is_deleted == False
            )
        except Exception as e:
            print("Error finding user:", e)
            return None
    
    
    async def get_user(self, id: str) -> UserModel | None:
        try:
             return await self._find_active_user(id)
        except Exception as e:
            print(str(e))
            return None
    
    async def update_user(self, user_id: str, update_data: dict) -> UserModel | None:
        try:
            user = await self._find_active_user(user_id)
            if not user:
                return None

            for key, value in update_data.items():
                setattr(user, key, value)

            await user.save()
            return user

        except Exception as e:
            print("Error updating user:", e)
            return None

    async def subscribe(self, firm_username:str|None, publisher_username: str|None, subscriber_id: str) -> bool:
        try:
            firm = None
            publisher = None
            firm_data = None
            pub_data = None
            
            if firm_username:
                firm = await FirmModel.find_one(
                    FirmModel.firm_username == firm_username,
                    FirmModel.is_deleted == False,
                    FirmModel.is_active == True,
                    )
                firm_data = firm.id
                if not firm:
                    raise HTTPException(status_code=404, detail="Firm not found")

            if publisher_username:
                publisher = await UserModel.find_one(
                    UserModel.username == publisher_username,
                    UserModel.role == UserRole.publisher,
                    UserModel.is_active == True,
                    UserModel.is_deleted == False,
                    )
                pub_data =  publisher.id
                if not publisher:
                    raise HTTPException(status_code=404, detail="Publisher (user) not found")
            
            subscriber = await UserModel.get(ObjectId(subscriber_id))
            if not subscriber:
                raise HTTPException(status_code=404, detail="Subscriber (user) not found")
            
                
                
            subscription = await SubscriptionModel.find_one(
                SubscriptionModel.subscriber_id.id == subscriber.id,
                SubscriptionModel.firm_id.id == firm_data,
                SubscriptionModel.publisher_id.id == pub_data
                )

            if subscription:
                await subscription.delete()
                return "unsubscribed"
                # raise HTTPException(status_code=200, detail="Already subscribed")
            
            subscription = SubscriptionModel(
                subscriber_id=subscriber, firm_id=firm_data, publisher_id=pub_data
            )

            await subscription.insert()
            return "subscribed"

        except HTTPException as e:
            raise e
        except Exception as e:
            print("Error subscribing to publisher:", e)
            raise HTTPException(status_code=500, detail="Internal server error")