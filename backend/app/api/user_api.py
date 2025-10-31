from app.controller.user_controller import UserController
from app.models.users import UserModel
from fastapi import APIRouter, HTTPException, BackgroundTasks 
from app.schema.user_schema import UserCreateSchema, UserResponseSchema
from app.schema.base_schema import BaseResponse
from app.controller.email_otp_controller import send_otp_email

router = APIRouter()
user_controller = UserController()

@router.post("/user/register/", response_model=BaseResponse)
async def create_user(user_data: UserCreateSchema, background_tasks: BackgroundTasks):
    try:
        user = await user_controller.get_by_username_or_email(user_data.username, user_data.email)
        if user:  
            if user.is_verified == True:
                raise HTTPException(status_code=400, detail="Username or email already exists")
            
        else:
            user = await user_controller.create(user_data.dict())
            if user is None:
                raise HTTPException(status_code=400, detail="User creation failed")
        
        # await send_otp_email(user)  
        background_tasks.add_task(send_otp_email, user)
        data =  UserResponseSchema(**user.dict())
        # data =  UserResponseSchema(**user.dict(exclude={"password_hash"}))
        response_data = {
            "status": 1,
            "message": "User created, OTP sent to email",
            "data": data
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

