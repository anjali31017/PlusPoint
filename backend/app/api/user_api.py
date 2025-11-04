from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks 

from app.controller.user_controller import UserController
from app.models.users import UserModel
from app.schema.user_schema import LogoutSchema, UserCreateSchema, LoginSchema
from app.controller.token_controller import create_token_pair, get_current_user
from app.models.token import RefreshTokenModel
from app.schema.base_schema import BaseResponse
from app.controller.email_controller import send_otp_email
from app.schema.email_schema import OTPVerifySchema


router = APIRouter(prefix="/user", tags=["User"])

user_controller = UserController()


@router.get("/check-username")
async def check_username(username: str):
    try:
        user = await user_controller.get_by_username(username)
        return {"available": user is None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/register", response_model=BaseResponse)
async def create_user(user_data: UserCreateSchema, background_tasks: BackgroundTasks):
    try:
        user = await user_controller.get_by_username(user_data.username)
        if user:  
            if user.is_verified == True:
                raise HTTPException(status_code=400, detail="Username already exists")
            
        else:
            user = await user_controller.create(user_data.dict())
            if user is None:
                raise HTTPException(status_code=400, detail="User creation failed")
        
        background_tasks.add_task(send_otp_email, user)
        
        response_data = {
            "status": 1,
            "message": "User created, OTP sent to email",
            "data": {
                "email": user.username
            }
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/verify-otp", response_model=BaseResponse)
async def verify_user_otp(otp_data: OTPVerifySchema):
    try:
        user = await UserModel.find_one(UserModel.email == otp_data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.verify_otp(otp_data.otp):
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        await user.set({UserModel.is_verified: True, UserModel.is_active: True})

        access_token, refresh_token = await create_token_pair(user)
        if not access_token or not refresh_token:
            raise HTTPException(status_code=500, detail="Token generation failed")
    
        return {
            "status": 1,
            "message": "OTP verified successfully",
            "data": {
            "access_token": access_token,
            "refresh_token": refresh_token
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/login", response_model=BaseResponse)
async def login(data: LoginSchema):
    user = await UserModel.find_one(UserModel.email == data.email)
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token, refresh_token = await create_token_pair(user)
    if not access_token or not refresh_token:
        raise HTTPException(status_code=500, detail="Token generation failed")
    
    return {
        "status": 1,
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    }



@router.post("/logout", response_model=BaseResponse)
async def logout(data: LogoutSchema):
    try:
        token_doc = await RefreshTokenModel.find_one(
            RefreshTokenModel.token == data.refresh_token,
            RefreshTokenModel.is_revoked == False
            )
        if not token_doc:
            raise HTTPException(status_code=404, detail="Refresh token not found")
        
        token_doc.is_revoked = True
        await token_doc.save()

        return {
            "status": 1,
            "message": "Logout successful",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"msg": f"Hello user {current_user['user_id']} with roles {current_user['role']}"}