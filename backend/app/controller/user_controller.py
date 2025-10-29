from app.models.users import User
from beanie.operators import Or, Eq

class UserController:

    async def create(self, user_data:dict) -> User | None:
        try:
            user = User(**user_data)
            user.password_hash = User.hash_password(user_data['password'])
            await user.insert()
            return user
        except Exception as e:
            print(str(e))
            return None
    
    async def get_by_username_or_email(self, username: str, email: str) -> User | None:
        try:
            user = await User.find_one(
                Or(Eq(User.username, username), Eq(User.email, email)),
                Eq(User.is_deleted, False)
            )
            return user
        except Exception as e:
            print(str(e))
            return None
    