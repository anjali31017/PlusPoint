from bson import ObjectId
from fastapi import APIRouter, Depends, File, UploadFile,Form
from app.models.kyc import KYCModel
from fastapi import APIRouter, Depends, HTTPException
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from fastapi import status
from app.schema.kyc_schema import KYCSchema
from app.controller.kyc_controller import KYCController
import os

router = APIRouter(prefix="/kyc", tags=["kyc"])

UPLOAD_FOLDER = "backend/images/kyc"


kyc_controller = KYCController()

@router.post( "/create", response_model=BaseResponse, status_code=status.HTTP_201_CREATED )
# async def create_kyc( kyc_data: KYCSchema, id_document: UploadFile = File(...), current_user: dict = Depends(get_current_user) ):
async def create_kyc( 
                    id_type: str = Form(...),
                    id_last4: str = Form(...),
                    dob: str= Form(...),
                    name_on_id: str= Form(...),
                    id_document: UploadFile = File(...), 
                    current_user: dict = Depends(get_current_user) 
                ):
    """
    Accepts KYC data as JSON/dict.
    Stores the info in UserKYCModel with status 
    """
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
        
        existing_kyc = await KYCModel.find_one(KYCModel.user_id.id == ObjectId(current_user["user_id"]))
        if existing_kyc:
            if existing_kyc.kyc_status == "VERIFIED" or existing_kyc.kyc_status == "UNDER_REVIEW":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="KYC already done or under review"
                    )
        
        fingerprint = kyc_controller.generate_id_fingerprint( id_type, id_last4, dob, name_on_id )
        duplicate = await KYCModel.find_one(
            KYCModel.id_fingerprint == fingerprint,
            KYCModel.kyc_status != "REJECTED"
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="KYC with same ID already exists"
            )
        
        success = await kyc_controller.create_kyc( 
                                                  id_type, 
                                                  id_last4, 
                                                  dob, 
                                                  name_on_id ,
                                                  fingerprint, 
                                                  id_document, 
                                                  current_user 
                                                  )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create KYC record."
            )
            
        return BaseResponse(
        status=1,
        message="KYC done successfully",
        data="Sent for verification"
        )


    except Exception as e:
    # catch all unexpected errors
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
