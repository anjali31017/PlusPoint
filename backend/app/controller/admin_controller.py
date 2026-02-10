from datetime import datetime

from bson import ObjectId
from app.models.admin import AdminModel

from app.controller.util_controller import UtilController

from fastapi import Depends, Request, HTTPException, status

from app.models.kyc import KYCModel, KYCStatus
from app.models.firm import FirmModel
from app.models.users import UserModel


def admin_required(request: Request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=403, detail="Admin access required")
    return admin_id



class AdminController:
    
    async def create_admin(self, admin_data:dict) -> AdminModel | None:
        try:
            
            admin_exists = await AdminModel.find_one(
                AdminModel.email == admin_data['email'],
                AdminModel.is_deleted == False
            )
            
            if admin_exists and admin_exists.is_verified == True:
                return None
            

            admin = AdminModel(**admin_data)
            admin.password_hash = AdminModel.hash_detail(admin_data['password'])
            await admin.insert()
            return admin
        except Exception as e:
            print(str(e))
            return None


    async def get_kyc(self):
        try: 
            kyc_data = await KYCModel.find(KYCModel.kyc_status == "UNDER_REVIEW").to_list()
            if not kyc_data:
                return []

            return kyc_data
        except Exception as e:
            print("Error fetching KYC:", e)
            return []
        
    async def approve_kyc(self, user_id: str):
        try:
            
            user = await UserModel.find_one(UserModel.id == ObjectId(user_id), UserModel.is_deleted == False)

            if user is None:
                return None
            
            kyc = await KYCModel.find_one(KYCModel.user_id.id == ObjectId(user_id), 
                                          KYCModel.is_deleted == False,
                                        #   KYCModel.kyc_status == "UNDER_REVIEW" 
                                          )
            
            if kyc is None:
                return None
            
            kyc.kyc_status = KYCStatus.VERIFIED
            kyc.reviewed_at = datetime.now()
            kyc.updated_at = datetime.now()
            await kyc.save()
            
            user.status = True
            await user.save()

            
            # kyc_record = KYCModel(**kyc.dict())
            
            # print("KYC Record in approve KYC:", kyc)
            return kyc
        except Exception as e:
            print(str(e))
            return None

    async def reject_kyc(self, user_id: str, reason: str):
        try:
            kyc_record = await KYCModel.find_one(KYCModel.user_id.id == ObjectId(user_id), KYCModel.is_deleted == False,)
            if not kyc_record:
                return None
            kyc_record.kyc_status = "REJECTED"
            kyc_record.rejection_reason = reason
            kyc_record.reviewed_at = datetime.now()
            kyc_record.updated_at = datetime.now()
            kyc_record.is_active = False
            kyc_record.is_deleted = True
            await kyc_record.save()
            return kyc_record
        except Exception as e:
            print(str(e))
            return None




    async def get_firms(self):
        try: 
            firm_data = await FirmModel.find(KYCModel.verification_status == "UNDER_REVIEW").to_list()
            if not firm_data:
                return []
                
            return firm_data
        except Exception as e:
            print("Error fetching KYC:", e)
            return []