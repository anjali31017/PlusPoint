from bson import ObjectId
from app.models.users import UserModel
from beanie.operators import Or, Eq

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
    
    async def get_by_username(self, username: str) -> UserModel | None:
        try:
            user = await UserModel.find_one(UserModel.username == username, UserModel.is_deleted == False)
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
