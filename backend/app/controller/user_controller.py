from http.client import HTTPException
from typing import Optional
from bson import ObjectId
from app.models.users import UserModel
from beanie.operators import Or, Eq

from app.models.firm import FirmModel

class UserController:

    async def create(self, user_data:dict) -> UserModel | None:
        try:
            user = UserModel(**user_data)
            user.password_hash = UserModel.hash_detail(user_data['password'])
            await user.insert()
            return user
        except Exception as e:
            print(str(e))
            return None
    async def check_username_exists(self, username: str) -> Optional[UserModel | FirmModel]:
        try:
            print("Checking username:", username)
            
            # Querying the users collection
            username_in_users = await UserModel.find_one({"username": username, "is_deleted": False})
            if username_in_users:
                return username_in_users  # Return the user document if found

            # Querying the firms collection
            username_in_firms = await FirmModel.find_one({"firm_username": username, "is_deleted": False})
            if username_in_firms:
                return username_in_firms  # Return the firm document if found

            # If neither user nor firm is found
            return None 

        except Exception as e:
            print(f"Error checking username existence: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")


    # async def check_username_exists(self, username: str) -> Optional[UserModel | FirmModel]:
    #     try:
    #         print("!!!!!!!!!!", username)
    #         username_in_users = await UserModel.find_one(UserModel.username == username)
    #         if username_in_users:
    #             return username_in_users  

    #         username_in_firms = await FirmModel.find_one(FirmModel.firm_username == username)
    #         if username_in_firms:
    #             return username_in_firms  

    #         else:
    #             return None 

    #     except Exception as e:
    #         print(f"Error checking username existence: {str(e)}")
    #         raise HTTPException(status_code=500, detail="Internal server error")
                                
    # async def check_username_exists(self, username: str) -> bool:
    #     try:
    #         username_in_users = await UserModel.find_one({"username": username})
    #         username_in_firms = await FirmModel.find_one({"firm_username": username})
    #         if username_in_users or username_in_firms:
    #             return True              
    #         return False  

    #     except Exception as e:
    #         print(f"Error checking username existence: {str(e)}")
    #         raise HTTPException(status_code=500, detail="Internal server error")
        
        
    # async def get_by_username(self, username: str) -> UserModel | None:
    #     try:
    #         user = await UserModel.find_one(UserModel.username == username, UserModel.is_deleted == False)
    #         return user
    #     except Exception as e:
    #         print(str(e))
    #         return None
    
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
