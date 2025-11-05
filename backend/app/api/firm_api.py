from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks 

from app.controller.user_controller import UserController
from app.models.users import UserModel
from app.schema.user_schema import LogoutSchema, UserCreateSchema, LoginSchema, UserProfileSchema
from app.controller.token_controller import create_token_pair, get_current_user
from app.models.token import RefreshTokenModel
from app.schema.base_schema import BaseResponse
from app.controller.email_controller import send_otp_email
from app.schema.email_schema import OTPVerifySchema
from app.controller.firm_controller import FirmController
from app.schema.firm_schema import AddPublisherSchema, FirmRegisterSchema


router = APIRouter(prefix="/firm", tags=["Firm"])

firm_controller = FirmController()
user_controller = UserController()

@router.post("/register", response_model=BaseResponse)
async def register_firm(firm_data: FirmRegisterSchema, current_user: dict = Depends(get_current_user)):
    try:
        user = await user_controller.check_username_exists(firm_data.firm_username)
        if user:  
            if user.is_verified == True:
                raise HTTPException(status_code=400, detail="Username already exists")
        
        else:
            # firm_data["firm_user_id"] = current_user["user_id"]
            
            user = await firm_controller.register_firm(firm_data, user_id=current_user["user_id"])
            if not user:
                raise HTTPException(status_code=400, detail="Firm registration failed")
        
        response_data = {
            "status": 1,
            "message": "Firm registered successfully",
            "data": None
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/add-publisher", response_model=BaseResponse)
async def add_publisher(data: AddPublisherSchema, current_user: dict = Depends(get_current_user)):
    try:
        new_publisher = await firm_controller.add_publisher(data)
        response_data = {
            "status": 1,
            "message": "Publisher added successfully",
            "data": {
                "publisher_user_id": str(new_publisher.publisher_user_id.id),
                "invited_at": new_publisher.invited_at
            }
        }
        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))