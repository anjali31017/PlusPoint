from app.models.users import UserModel
from beanie.operators import Or, Eq

class UserController:

    async def create(self, user_data:dict) -> UserModel | None:
        try:
            print("4")
            user = UserModel(**user_data)
            print("5")
            user.password_hash = UserModel.hash_password(user_data['password'])
            print("6")
            await user.insert()
            print("7")
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
    