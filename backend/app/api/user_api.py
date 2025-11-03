from fastapi import APIRouter, HTTPException, BackgroundTasks 

from app.controller.user_controller import UserController
from app.models.users import UserModel
from app.schema.user_schema import UserCreateSchema, UserResponseSchema
from app.schema.base_schema import BaseResponse
from app.controller.email_otp_controller import send_otp_email
from app.schema.email_schema import OTPVerifySchema


router = APIRouter(prefix="/user", tags=["User"])
user_controller = UserController()

@router.post("/register", response_model=BaseResponse)
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
        
        background_tasks.add_task(send_otp_email, user)
        
        response_data = {
            "status": 1,
            "message": "User created, OTP sent to email",
            "data": UserResponseSchema(**user.dict())
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify/otp/", response_model=BaseResponse)
async def verify_user_otp(otp_data: OTPVerifySchema):
    try:
        user = await UserModel.find_one(UserModel.id == otp_data.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.verify_otp(otp_data.otp):
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        await user.set({UserModel.is_verified: True})

        return {
            "status": 1,
            "message": "OTP verified successfully",
            "data": UserResponseSchema(**user.dict())
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
