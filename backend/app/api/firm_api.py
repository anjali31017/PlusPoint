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

@router.post("/register", response_model=BaseResponse)
async def register_firm(firm_data: FirmRegisterSchema):
    try:
        success = await firm_controller.register_firm(firm_data)
        if not success:
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
async def add_publisher(data: AddPublisherSchema):
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