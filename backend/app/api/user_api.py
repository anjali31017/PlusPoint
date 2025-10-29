from app.controller.user_controller import UserController
from app.models.users import User
from fastapi import APIRouter, HTTPException  
from app.schema.user_schema import UserCreate, UserResponse

router = APIRouter()
user_controller = UserController()

@router.post("/users/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    try:
        existing_user = await user_controller.get_by_username_or_email(user_data.username, user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        user = await user_controller.create(user_data.dict())
        if user is None:
            raise HTTPException(status_code=400, detail="User creation failed")
        return UserResponse(**user.dict(exclude={"password_hash"}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

