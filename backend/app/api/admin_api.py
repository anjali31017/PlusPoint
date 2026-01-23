
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.controller.admin_controller import AdminController
# from app.controller.admin_controller import AdminController
from app.models.token import RefreshTokenModel
from app.schema.base_schema import BaseResponse
from app.controller.email_controller import  KYC_status_email, is_user_blocked, send_otp_email
from fastapi import status

from app.schema.admin_schema import AdminRejctKYCSchema, AdminSchema

from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from app.models.admin import AdminModel
from app.controller.admin_controller import admin_required
from app.controller.user_controller import UserController
from app.models.kyc import KYCModel

router = APIRouter(prefix="/admin", tags=["Admin"])

admin_controller = AdminController()
user_controller = UserController()

@router.post("/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_user(admin_data: AdminSchema):
    try:
        
        admin = await admin_controller.create_admin(admin_data.dict())
        if admin is None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin already exists"
        )

        
        response_data = {
            "status": 1,
            "message": "Admin created",
            "data": {
                "username": admin.email
            }
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def admin_login(request: Request, data: AdminSchema):
    try:
        admin = await AdminModel.find_one(AdminModel.email == data.email, AdminModel.is_deleted == False)
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not admin.verify_password(data.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Set session
        request.session["admin_id"] = str(admin.id)
        return {
            "status": 1,
            "message": "Login successful",
            "data": {
                "email": admin.email
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




@router.get("/check-session", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def check_session(request: Request):
    try:
        admin_id = request.session.get("admin_id")
        if admin_id:
            return {
                "status": 1,
                "message": "Admin is logged in",
                "data": {
                    "admin_id": admin_id
                }
            }
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Please log in again.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/logout", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def logout(request: Request):
    request.session.clear()
    return {
                "status": 1,
                "message": "Logged out successfully",
                "data": {
                    None
                }
            }



@router.get("/dashboard", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def dashboard(admin_id: str = Depends(admin_required)):
    # Example response; in practice query KYC, firms, reports from DB
    return {
        "KYC": "/admin/kyc",
        "Firms": "/admin/firms",
        "Reports": "/admin/reports"
    }





@router.get("/kyc", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def list_kyc(admin_id: str = Depends(admin_required)):
    try:
        # if admin_id is None:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        kyc_data = await admin_controller.get_kyc()
        
        if not kyc_data or len(kyc_data) == 0:
            return {
                "status": 1,
                "message": "No KYC data to validate",
                "data": {
                    "data": []
                }
            }
        
        return {
            "status": 1,
            "message": "KYC data retrieved",
            "data": {
                "data": kyc_data,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/kyc/{user_id}/approve", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def approve_kyc(user_id: str,  background_tasks: BackgroundTasks, admin_id: str = Depends(admin_required)):
    try:
        # if admin_id is None:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        kyc = await admin_controller.approve_kyc(user_id)
        # kyc = await KYCModel.find_one(KYCModel.user_id.id == ObjectId(user_id), KYCModel.is_deleted == False)
        # print(kyc)
        # print("KYC in approve KYC:", kyc["kyc_status"])
        # print("User ID in approve KYC:", user_id)

        if kyc is None:
            return {
                "status": 1,
                "message": "No KYC data to validate",
                "data": {
                    "data": []
                }
            }
        user = await user_controller.get_user(user_id)
        background_tasks.add_task(KYC_status_email, 
                                  to_email = user.email,
                                  status=kyc.kyc_status, 
                                  reason=None)


        return {
            "status": 1,
            "message": "KYC approved",
            "data": {
                "kyc_id": str(kyc.id),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


    
    
    
@router.post("/kyc/{user_id}/reject",  response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def reject_kyc(user_id: str, data:AdminRejctKYCSchema, background_tasks: BackgroundTasks, admin_id: str = Depends(admin_required)):
    try:
        # if admin_id is None:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        kyc_record = await admin_controller.reject_kyc(user_id, data.reason)
        if kyc_record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KYC record not found")
        
        user = await user_controller.get_user(user_id)
    
        background_tasks.add_task(KYC_status_email, 
                                  to_email = user.email,
                                  status=kyc_record.kyc_status, 
                                  reason=kyc_record.rejection_reason)
        
        return {
            "status": 1,
            "message": "KYC Rejected",
            "data": {
                "kyc_id": str(kyc_record.id),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))







# Firms
# @router.get("/firms", response_model=BaseResponse, status_code=status.HTTP_200_OK)
# async def list_firms(admin_id: str = Depends(admin_required)):
#     try:
#         if admin_id is None:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
#         firm_data = await admin_controller.get_firms()
        
#         if not firm_data or len(firm_data) == 0:
#             return {
#                 "status": 1,
#                 "message": "No firm data to validate",
#                 "data": {
#                     "data": []
#                 }
#             }
        
#         return {
#             "status": 1,
#             "message": "KYC data retrieved",
#             "data": {
#                 "data": firm_data
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @router.post("/firms/{firm_id}/delete", response_model=BaseResponse, status_code=status.HTTP_200_OK)
# async def delete_firm(firm_id: str, admin_id: str = Depends(admin_required)):
#     # Delete firm, update trust factor
#     if admin_id is None:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
#     return {"message": f"Firm {firm_id} deleted"}



# Reports
@router.get("/reports", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def list_reports(admin_id: str = Depends(admin_required)):
    # if admin_id is None:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return [{"report_id": "r001", "content": "Violation post"}]

@router.post("/reports/{report_id}/action", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def handle_report(report_id: str, action: str = Form(...), admin_id: str = Depends(admin_required)):
    """
    action = "send_email", "delete_account", "delete_post"
    """
    # if admin_id is None:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    if action == "send_email":
        # Send violation email
        return {"message": f"Email sent for report {report_id}"}
    elif action == "delete_account":
        # Delete user account
        return {"message": f"Account deleted for report {report_id}"}
    elif action == "delete_post":
        # Delete post, update trust/violation
        return {"message": f"Post deleted for report {report_id}"}
    return {"message": "Invalid action"}
