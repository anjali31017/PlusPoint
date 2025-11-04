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
    