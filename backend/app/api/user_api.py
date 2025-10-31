from app.controller.user_controller import UserController
from app.models.users import UserModel
from fastapi import APIRouter, HTTPException  
from app.schema.user_schema import UserCreateSchema, UserResponseSchema
from app.schema.base_schema import BaseResponse
from app.controller.email_otp_controller import send_otp_email

router = APIRouter()
user_controller = UserController()

@router.post("/user/register/", response_model=BaseResponse)
async def create_user(user_data: UserCreateSchema):
    try:
        existing_user = await user_controller.get_by_username_or_email(user_data.username, user_data.email)
        if existing_user and existing_user.is_verified == True:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        elif not existing_user:
            user = await user_controller.create(user_data.dict())
            if user is None:
                raise HTTPException(status_code=400, detail="User creation failed")
        
        data =  UserResponseSchema(**user.dict(exclude={"password_hash"}))
        otp_email = await send_otp_email(user.email)  
        
        if not otp_email:
            raise HTTPException(status_code=500, detail="Failed to send OTP email")
        response_data = {
            "status": 1,
            "message": "User created, OTP sent to email",
            "data": data
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

