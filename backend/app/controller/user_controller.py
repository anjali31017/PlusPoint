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
    
    async def get_by_username_or_email(self, username: str, email: str) -> UserModel | None:
        try:
            user = await UserModel.find_one(
                Or(Eq(UserModel.username, username), Eq(UserModel.email, email)),
                Eq(UserModel.is_deleted, False)
            )
            return user
        except Exception as e:
            print(str(e))
            return None
    