from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
# from app.controller.user_controller import UserController
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from app.controller.firm_controller import FirmController
from app.schema.firm_schema import AddPublisherSchema, FirmCreateSchema
from fastapi import status

from app.models.users import UserModel
from app.models.kyc import KYCModel

router = APIRouter(prefix="/firm", tags=["Firm"])

firm_controller = FirmController()

    

@router.post( "/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED )
async def create_firm_api( firm_data: FirmCreateSchema, current_user: dict = Depends(get_current_user) ):
    """
    Create a new firm. Only KYC-verified users can create a firm.
    """
    try:

        user = await UserModel.get(ObjectId(current_user["user_id"]))
        if not user or not user.is_verified or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not found"
            )
            
        kyc = await KYCModel.find_one(KYCModel.user_id == ObjectId(current_user["user_id"]))
        if not kyc or kyc.kyc_status != "VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="KYC required to create firm"
            )
            
        success = await firm_controller.create_firm(firm_data, user, ObjectId(current_user["user_id"]))

        if not success:
            # Could be failure due to duplicate username, etc
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create firm."
            )

        return BaseResponse(
            status=1,
            message="Firm created successfully",
            data={"firm_username": success.firm_username}
        )

    except HTTPException as e:
        # propagate HTTPException so FastAPI can return it
        raise e

    except Exception as e:
        # catch all unexpected errors
        return BaseResponse(
            status=0,
            message=f"Internal server error: {str(e)}",
            data=None
        )
        
        
        
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
# @router.post("/{firm_username}/subscribe", response_model=BaseResponse)
# @router.post("/publisher/{publisher_username}/subscribe", response_model=BaseResponse)
# async def subscribe_to_firm(firm_username: str|None = None, publisher_username: str|None = None,current_user: dict = Depends(get_current_user)):
#     try:
#         subscription = await firm_controller.subscribe(firm_username, publisher_username, current_user["user_id"])
#         response_data = {
#             "status": 1,
#             "message": "Subscribed successfully",
#             "data": subscription
#         }
#         return response_data
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# user_controller = UserController()

# @router.post("/register", response_model=BaseResponse)
# async def register_firm(firm_data: FirmCreateSchema, current_user: dict = Depends(get_current_user)):
#     try:
#         user = await user_controller.check_username_exists(firm_data.firm_username)
#         if user:  
#             if user.is_verified == True:
#                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Username already exists")
        
#         else:
#             # firm_data["firm_user_id"] = current_user["user_id"]
            
#             user = await firm_controller.create_firm(firm_data, user_id=current_user["user_id"])
#             if not user:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Firm registration failed")
        
#         response_data = {
#             "status": 1,
#             "message": "Firm registered successfully",
#             "data": None
#         }
#         return response_data
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))