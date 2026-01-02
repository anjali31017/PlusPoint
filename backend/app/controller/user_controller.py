from fastapi import HTTPException
from typing import Optional
from bson import ObjectId
from app.models.users import UserModel, UserRole
import random
from app.models.firm import FirmModel
from app.models.subscription import SubscriptionModel

class UserController:
    
    async def check_username_exists(self, username: str) -> Optional[UserModel | FirmModel]:
        try:
            print("Checking username:", username)
            
            # Querying the users collection
            username_in_users = await UserModel.find_one(
                UserModel.username == username,
                UserModel.is_deleted == False,
                UserModel.is_verified == True
                )
            if username_in_users:
                return username_in_users  # Return the user document if found

            # Querying the firms collection
            username_in_firms = await FirmModel.find_one(
                FirmModel.firm_username == username,
                FirmModel.is_deleted == False
                )
            if username_in_firms:
                return username_in_firms  # Return the firm document if found

            # If neither user nor firm is found
            return None 

        except Exception as e:
            print(f"Error checking username existence: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    
    async def generate_username(self, user_data: dict) -> str:
        try:
            # Generate a random 10-digit number
            # random_number = random.randint(10**9, 10**10 - 1)
            
            num_digits = random.randint(5, 10)
            random_number = random.randint(10**(num_digits - 1), 10**num_digits - 1)
            username = user_data["first_name"].lower() +"_"+ user_data["last_name"].lower() +"_"+ str(random_number)
            
            # user = await self.check_username_exists(username)
            # if user and user.is_verified == True:
            #     raise HTTPException(status_code=400, detail="Username already exists")
            
            return username
        except Exception as e:
            print("Error generating username:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
        
    async def create(self, user_data:dict) -> UserModel | None:
        try:
            while True:
                username = await self.generate_username(user_data)
                user = await self.check_username_exists(username)
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